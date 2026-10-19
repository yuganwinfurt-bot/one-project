"""商家与用户私聊、评价追加内容及回复通知。"""
from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DirectConversation(Base):
    __tablename__ = "direct_conversations"
    __table_args__ = (UniqueConstraint("staff_id", "customer_id", name="uq_direct_participants"),)
    staff_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)


class DirectMessage(Base):
    __tablename__ = "direct_messages"
    conversation_id: Mapped[int] = mapped_column(ForeignKey("direct_conversations.id"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)


class ReviewComment(Base):
    __tablename__ = "review_comments"
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reply_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text)


class ReviewReplyNotification(Base):
    __tablename__ = "review_reply_notifications"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product_name: Mapped[str] = mapped_column(String(100))
    actor_name: Mapped[str] = mapped_column(String(50))
    actor_role: Mapped[str] = mapped_column(String(20))
    review_content: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
