"""Customer consultation and human handoff; separate from refund business state."""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class SupportConversation(Base):
    __tablename__ = "support_conversations"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    after_sale_id: Mapped[int | None] = mapped_column(ForeignKey("after_sale_requests.id"), unique=True, nullable=True)
    title: Mapped[str] = mapped_column(String(200), default="售后咨询")
    handling_mode: Mapped[str] = mapped_column(String(24), default="ai")
    human_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    human_requested_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed: Mapped[bool] = mapped_column(Boolean, default=False)


class SupportChatMessage(Base):
    __tablename__ = "support_chat_messages"
    conversation_id: Mapped[int] = mapped_column(ForeignKey("support_conversations.id"), index=True)
    sender_role: Mapped[str] = mapped_column(String(20))
    sender_name: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    read_by_customer: Mapped[bool] = mapped_column(Boolean, default=False)


class SupportAIRequest(Base):
    __tablename__ = "support_ai_requests"
    request_key: Mapped[str] = mapped_column(String(64), unique=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("support_conversations.id"), index=True)
    last_message_id: Mapped[int] = mapped_column(Integer)
    reply_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class SupportChatDelivery(Base):
    __tablename__ = "support_chat_deliveries"
    client_message_id: Mapped[str] = mapped_column(String(120), unique=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("support_conversations.id"))
    message_id: Mapped[int] = mapped_column(ForeignKey("support_chat_messages.id"))
