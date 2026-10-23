"""电商核心表：订单"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Order(Base):
    """订单表

    运营分析接口只读；Agent 不得修改既有订单。用户侧提交的演示订单由商城接口创建。
    """

    __tablename__ = "orders"
    __table_args__ = {"comment": "订单表"}

    order_no: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, comment="订单号"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, comment="商品ID"
    )
    variant_key: Mapped[str] = mapped_column(
        String(80), nullable=False, default="", server_default="", comment="下单 SKU 编号"
    )
    variant_name: Mapped[str | None] = mapped_column(
        String(160), nullable=True, comment="下单规格快照"
    )
    buyer_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="买家昵称"
    )
    buyer_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, comment="注册买家用户ID"
    )
    shipping_address: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="下单时的收货地址快照"
    )
    tracking_no: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="商家发货物流单号"
    )
    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="最近一次发货时间"
    )
    checkout_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True, comment="同次结算批次")
    payment_deadline_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="付款截止时间")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="付款时间")
    received_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="确认收货时间")
    quantity: Mapped[int] = mapped_column(nullable=False, default=1, comment="购买数量")
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="实付金额"
    )
    # unpaid=待付款，paid=已支付，shipped=已发货，completed=已收货，cancelled=已取消
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="completed", comment="订单状态"
    )
