"""用户侧购物车、收藏与收货地址。"""

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CartItem(Base):
    __tablename__ = "customer_cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_customer_cart_product"),
        {"comment": "用户购物车"},
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)


class CartVariantItem(Base):
    """多规格商品独立购物车行，避免重建已有购物车表。"""

    __tablename__ = "customer_cart_variant_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", "variant_key", name="uq_customer_cart_variant"),
        {"comment": "用户多规格商品购物车"},
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    variant_key: Mapped[str] = mapped_column(String(80), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)


class FavoriteProduct(Base):
    __tablename__ = "customer_favorite_products"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_customer_favorite_product"),
        {"comment": "用户商品收藏"},
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    restock_waiting: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")


class CustomerMessage(Base):
    __tablename__ = "customer_messages"
    __table_args__ = {"comment": "用户站内消息"}

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    # 保留商品编号和名称快照，避免商品后续下架或删除后消息失去上下文。
    product_id: Mapped[int] = mapped_column(nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    previous_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class CustomerShipmentMessage(Base):
    __tablename__ = "customer_shipment_messages"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_customer_shipment_message_order"),
        {"comment": "用户订单发货提醒"},
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order_no: Mapped[str] = mapped_column(String(32), nullable=False)
    product_id: Mapped[int] = mapped_column(nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"
    __table_args__ = {"comment": "用户收货地址"}

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    receiver_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    province: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    district: Mapped[str] = mapped_column(String(50), nullable=False)
    detail: Mapped[str] = mapped_column(String(200), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
