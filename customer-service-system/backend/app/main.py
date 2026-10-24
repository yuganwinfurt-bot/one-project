from contextlib import asynccontextmanager, suppress
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from app.config import UPLOAD_DIR
from app.models import (  # noqa: F401  注册全部模型
    User,
    DemoLoginCredential,
    Product,
    Order,
    Review,
    CustomerReviewReply,
    DiagnosisReport,
    AlertNotification,
    AfterSaleRequest,
    AfterSaleMessage,
    CartItem,
    CartVariantItem,
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
from app.services.demo_login_service import initialize_demo_credentials
from app.api import api
from app.services.mall_service import initialize as initialize_mall, expire_groups, expire_shipped_orders
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
    "support_ai_requests": {"claimed_at": "DATETIME NULL", "error": "TEXT NULL"},
    "demo_login_credentials": {"is_customer_demo": "BOOLEAN NOT NULL DEFAULT 0"},
    "agent_runs": {"answer_text": "TEXT NULL", "answer_context": "JSON NULL"},
    "customer_favorite_products": {"restock_waiting": "BOOLEAN NOT NULL DEFAULT 0"},
    "mall_coupon_claims": {"terms": "JSON NULL", "reserved_checkout_id": "VARCHAR(32) NULL"},
    "users": {"last_seen_at": "DATETIME NULL"},
    "products": {
        "image_url": "VARCHAR(500) NULL",
        "image_urls": "JSON NULL",
        "tags": "JSON NULL",
        "ai_detail": "TEXT NULL",
        "original_price": "NUMERIC(10, 2) NULL",
        "discount_percent": "NUMERIC(5, 2) NOT NULL DEFAULT 0",
        "variant_name": "VARCHAR(40) NULL",
        "variants": "JSON NULL",
    },
    "reviews": {"merchant_reply": "TEXT NULL"},
    "orders": {
        "buyer_user_id": "INT NULL",
        "shipping_address": "TEXT NULL",
        "tracking_no": "VARCHAR(100) NULL",
        "shipped_at": "DATETIME NULL",
        "checkout_id": "VARCHAR(32) NULL",
        "payment_deadline_at": "DATETIME NULL",
        "paid_at": "DATETIME NULL",
        "received_at": "DATETIME NULL",
        "variant_key": "VARCHAR(80) NOT NULL DEFAULT ''",
        "variant_name": "VARCHAR(160) NULL",
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
        ("orders", "checkout_id", "ix_orders_checkout_id"),
    ):
        indexes = {item["name"] for item in inspect(connection).get_indexes(table)}
        if index_name not in indexes:
            connection.exec_driver_sql(f"CREATE INDEX {index_name} ON {table} ({column})")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 为已有售后补齐集中异常预警；只写提醒，不自动改变商品复核或销售状态。
    with SessionLocal() as db:
        initialize_mall(db)
        initialize_demo_credentials(db)
        sync_all_after_sale_risks(db)
        sync_all_inventory(db)
        db.commit()
    def settle_groups():
        with SessionLocal() as db:
            from app.services.order_lifecycle_service import expire_unpaid_orders
            expire_unpaid_orders(db)
            expire_groups(db)
            expire_shipped_orders(db)

    async def group_clock():
        while True:
            try:
                await asyncio.to_thread(settle_groups)
            except Exception:
                logging.getLogger(__name__).exception("订单/团购到期处理失败，稍后自动重试")
            await asyncio.sleep(60)

    group_task = asyncio.create_task(group_clock())
    from app.services.customer_support_service import ai_clock
    support_ai_task = asyncio.create_task(ai_clock())
    try:
        yield
    finally:
        support_ai_task.cancel()
        with suppress(asyncio.CancelledError):
            await support_ai_task
        group_task.cancel()
        with suppress(asyncio.CancelledError):
            await group_task


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:35173",
    "http://127.0.0.1:35173",
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
