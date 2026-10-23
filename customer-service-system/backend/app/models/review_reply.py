"""注册用户对商品评价的回复。"""

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CustomerReviewReply(Base):
    __tablename__ = "customer_review_replies"
    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_customer_review_reply_user"),
        {"comment": "注册用户对商品评价的回复"},
    )

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
