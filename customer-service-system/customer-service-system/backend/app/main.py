from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from app.config import UPLOAD_DIR
from app.models import (  # noqa: F401  注册全部模型
    User,
    Product,
    Order,
    Review,
    CustomerReviewReply,
    DiagnosisReport,
    AlertNotification,
    AfterSaleRequest,
    AfterSaleMessage,
    CartItem,
    FavoriteProduct,
    CustomerMessage,
    CustomerShipmentMessage,
    CustomerAddress,
    StaffInboxEvent,
)
from app.observability.models import (  # noqa: F401
    AgentRun,
    AgentRunStep,
    AgentFeedback,
)
from app.database import Base, engine, SessionLocal
from app.services.after_sale_risk_service import sync_all_after_sale_risks
from app.services.inventory_service import sync_all_inventory
from app.api import api
from starlette.middleware.cors import CORSMiddleware
from app.common.exceptions import (
    BusinessException,
    business_exception_handler,
    http_excpetion_hadler,
    validation_excpetion_hadler,
    global_excpetion_hadler,
)

Base.metadata.create_all(bind=engine)  # 自动帮我们创数据库表

# create_all 不会修改已有表；启动时补齐兼容旧数据库所需的可空字段。
_ADDITIVE_COLUMNS = {
    "agent_runs": {"answer_text": "TEXT NULL", "answer_context": "JSON NULL"},
    "customer_favorite_products": {"restock_waiting": "BOOLEAN NOT NULL DEFAULT 0"},
    "users": {"last_seen_at": "DATETIME NULL"},
    "products": {
        "image_url": "VARCHAR(500) NULL",
        "image_urls": "JSON NULL",
        "tags": "JSON NULL",
        "ai_detail": "TEXT NULL",
        "original_price": "NUMERIC(10, 2) NULL",
        "discount_percent": "NUMERIC(5, 2) NOT NULL DEFAULT 0",
    },
    "reviews": {"merchant_reply": "TEXT NULL"},
    "orders": {
        "buyer_user_id": "INT NULL",
        "shipping_address": "TEXT NULL",
        "tracking_no": "VARCHAR(100) NULL",
    },
    "after_sale_requests": {
        "return_shipped": "BOOLEAN NOT NULL DEFAULT 0",
        "return_tracking_no": "VARCHAR(100) NULL",
        "exchange_shipping_address": "TEXT NULL",
        "exchange_tracking_no": "VARCHAR(100) NULL",
        "service_rating": "INTEGER NULL",
        "service_feedback": "TEXT NULL",
    },
    "diagnosis_reports": {"evidence": "JSON NULL", "source_run_id": "INT NULL"},
    "alert_notifications": {"report_id": "INT NULL", "dedupe_key": "VARCHAR(64) NULL"},
    "platform_logs": {
        "rollback_data": "TEXT NULL",
        "rollback_of_id": "INT NULL",
        "rollback_log_id": "INT NULL",
        "rolled_back_at": "DATETIME NULL",
    },
}
with engine.begin() as connection:
    for table_name, columns in _ADDITIVE_COLUMNS.items():
        existing = {
            column["name"]
            for column in inspect(connection).get_columns(table_name)
        }
        for column_name, column_definition in columns.items():
            if column_name not in existing:
                connection.exec_driver_sql(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                )
    connection.exec_driver_sql(
        "UPDATE products SET original_price = price WHERE original_price IS NULL"
    )
    for table, column, index_name in (
        ("diagnosis_reports", "source_run_id", "ix_diagnosis_reports_source_run_id"),
        ("alert_notifications", "dedupe_key", "ix_alert_notifications_dedupe_key"),
    ):
        indexes = {item["name"] for item in inspect(connection).get_indexes(table)}
        if index_name not in indexes:
            connection.exec_driver_sql(f"CREATE INDEX {index_name} ON {table} ({column})")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 为已有售后补齐集中异常预警；只写提醒，不自动改变商品复核或销售状态。
    with SessionLocal() as db:
        sync_all_after_sale_risks(db)
        sync_all_inventory(db)
        db.commit()
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端源，不要直接写 ["*"]
    allow_credentials=True,  # ✅ 关键：允许前端携带 Authorization token
    allow_methods=["*"],  # 允许所有请求方法 GET POST PUT DELETE OPTIONS
    allow_headers=["*"],  # 允许所有请求头（包含Authorization）
)

app.include_router(api)

# 注册异常处理器
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(HTTPException, http_excpetion_hadler)
app.add_exception_handler(RequestValidationError, validation_excpetion_hadler)
# 全局的异常兜底，必须放在最后注册！！
app.add_exception_handler(Exception, global_excpetion_hadler)

# 挂载静态的文件目录  http://127.0.0.1:8000/uploads/xxx.jpg
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"message": "FastAPI工程正在运行中"}
