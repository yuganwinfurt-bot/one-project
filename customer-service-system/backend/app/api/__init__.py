from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.files import router as files_router
from app.api.nl2sql import router as nl2sql_router
from app.api.chat import router as chat_router
from app.api.semantic import router as semantic_router
from app.api.route import router as route_router
from app.api.observability import router as observability_router
from app.api.ecommerce import router as ecommerce_router
from app.api.patrol import router as patrol_router
from app.api.platform_logs import router as platform_logs_router
from app.api.customer_store import router as customer_store_router
from app.api.community import router as community_router

api = APIRouter(prefix="/api")

api.include_router(auth_router)
api.include_router(user_router)
api.include_router(files_router)
api.include_router(nl2sql_router)
api.include_router(chat_router)
api.include_router(semantic_router)
api.include_router(route_router)
api.include_router(observability_router)
api.include_router(ecommerce_router)
api.include_router(patrol_router)
api.include_router(platform_logs_router)
api.include_router(customer_store_router)
api.include_router(community_router)
from app.api.mall import router as mall_router
api.include_router(mall_router)
from app.api.support_bridge import router as support_bridge_router
api.include_router(support_bridge_router)
from app.api.customer_support import router as customer_support_router, staff_router as support_tickets_router
api.include_router(customer_support_router)
api.include_router(support_tickets_router)
