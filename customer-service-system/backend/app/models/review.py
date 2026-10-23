"""电商核心表：评价"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Review(Base):
    """评价表

    content 为买家文字评价；img 为可选的买家晒图相对路径。
    后续多模态章节会把图片转成文字描述，再写入向量库。
    """

    __tablename__ = "reviews"
    __table_args__ = {"comment": "评价表"}

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, comment="商品ID"
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id"), nullable=True, comment="关联订单ID"
    )
    rating: Mapped[int] = mapped_column(nullable=False, comment="评分1-5")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评价正文")
    # 相对路径，例如 /uploads/review_samples/broken_box.jpg；无图则为空
    img: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="评价图片相对路径"
    )
    merchant_reply: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="商家回复"
    )
