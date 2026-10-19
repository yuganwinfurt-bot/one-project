"""电商核心表：订单"""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
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
    quantity: Mapped[int] = mapped_column(nullable=False, default=1, comment="购买数量")
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="实付金额"
    )
    # paid=已支付，shipped=已发货，completed=买家已确认收货，cancelled=已取消
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="completed", comment="订单状态"
    )
