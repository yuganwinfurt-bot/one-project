"""保存商品上一次售后风险级别，避免同一风险反复推送。"""
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductAfterSaleRiskState(Base):
    __tablename__ = "product_after_sale_risk_states"
    __table_args__ = (UniqueConstraint("product_id", name="uq_product_after_sale_risk"),)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    level: Mapped[str] = mapped_column(String(20), default="normal")
