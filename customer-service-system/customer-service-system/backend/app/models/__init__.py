"""导出电商相关模型，便于 create_all 时被导入注册。"""

from app.models.alert_notification import AlertNotification
from app.models.after_sale import AfterSaleMessage, AfterSaleRequest
from app.models.after_sale_risk import ProductAfterSaleRiskState
from app.models.diagnosis_report import DiagnosisReport
from app.models.order import Order
from app.models.platform_log import PlatformLog
from app.models.product import Product
from app.models.review import Review
from app.models.review_reply import CustomerReviewReply
from app.models.community import DirectConversation, DirectMessage, ReviewComment, ReviewReplyNotification
from app.models.inventory import ProductInventoryState, CustomerRestockMessage
from app.models.shopping import (
    CartItem,
    CustomerAddress,
    CustomerMessage,
    CustomerShipmentMessage,
    FavoriteProduct,
)
from app.models.staff_inbox import StaffInboxEvent
from app.models.user import User
from app.models.demo_login import DemoLoginCredential

__all__ = [
    "User",
    "DemoLoginCredential",
    "Product",
    "Order",
    "Review",
    "CustomerReviewReply",
    "DirectConversation", "DirectMessage", "ReviewComment", "ReviewReplyNotification",
    "ProductInventoryState", "CustomerRestockMessage",
    "DiagnosisReport",
    "AlertNotification",
    "AfterSaleRequest",
    "AfterSaleMessage",
    "ProductAfterSaleRiskState",
    "PlatformLog",
    "CartItem",
    "CustomerAddress",
    "FavoriteProduct",
    "CustomerMessage",
    "CustomerShipmentMessage",
    "StaffInboxEvent",
]
