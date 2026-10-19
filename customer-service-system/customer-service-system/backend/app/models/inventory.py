"""库存状态与收藏商品到货通知。"""
from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ProductInventoryState(Base):
    __tablename__ = "product_inventory_states"
    __table_args__ = (UniqueConstraint("product_id", name="uq_product_inventory_state"),)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    stock: Mapped[int] = mapped_column(default=0)
    available: Mapped[bool] = mapped_column(Boolean, default=False)


class CustomerRestockMessage(Base):
    __tablename__ = "customer_restock_messages"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    product_name: Mapped[str] = mapped_column(String(100))
    stock: Mapped[int] = mapped_column()
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
