"""订单售后申请。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.order import Order


class AfterSaleRequest(Base):
    __tablename__ = "after_sale_requests"
    __table_args__ = {"comment": "订单售后申请"}

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    order_no: Mapped[str] = mapped_column(String(32), nullable=False, comment="订单号快照")
    product_id: Mapped[int] = mapped_column(nullable=False, comment="商品ID快照")
    product_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="商品名称快照")
    service_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="refund/return/exchange")
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    return_shipped: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    return_tracking_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    exchange_shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    exchange_tracking_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_rating: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="售后服务评分1-5")
    service_feedback: Mapped[str | None] = mapped_column(Text, nullable=True, comment="售后服务评价内容")
    processed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    order: Mapped[Order] = relationship(lazy="selectin")


class AfterSaleMessage(Base):
    __tablename__ = "after_sale_messages"
    __table_args__ = {"comment": "订单售后沟通消息"}

    after_sale_id: Mapped[int] = mapped_column(
        ForeignKey("after_sale_requests.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    sender_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    sender_role: Mapped[str] = mapped_column(String(20), nullable=False)
    sender_name: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    read_by_customer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_by_staff: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
