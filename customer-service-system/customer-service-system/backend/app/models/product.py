"""电商核心表：商品"""

from decimal import Decimal

from sqlalchemy import JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    """商品表

    review_status 仅表示是否待人工复核，与上下架无关。
    Agent 允许在人工确认后把商品标为 pending_review，
    禁止修改 shelf_status（上下架）。
    """

    __tablename__ = "products"
    __table_args__ = {"comment": "商品表"}

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="商品名称")
    category: Mapped[str] = mapped_column(String(50), nullable=False, comment="类目")
    tags: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, comment="商品标签列表"
    )
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="商品描述")
    image_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="商家上传的商品主图"
    )
    image_urls: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, comment="商品图片列表，第一张为主图"
    )
    ai_detail: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="AI生成的商品详情文案（JSON）"
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="售价"
    )
    original_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True, comment="商品原价"
    )
    discount_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0, comment="优惠百分比"
    )
    stock: Mapped[int] = mapped_column(nullable=False, default=0, comment="库存数量")
    # on_sale=在售，off_shelf=下架（Agent 禁止修改）
    shelf_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="on_sale", comment="上下架状态"
    )
    # normal=正常，pending_review=待人工复核（Agent 可在确认后写入）
    review_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="normal", comment="人工复核状态"
    )
