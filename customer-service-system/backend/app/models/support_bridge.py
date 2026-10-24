"""Idempotent delivery of customer-service replies into existing after-sale chats."""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SupportMessageDelivery(Base):
    __tablename__ = "support_message_deliveries"

    client_message_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    after_sale_id: Mapped[int] = mapped_column(ForeignKey("after_sale_requests.id"), nullable=False)
    message_id: Mapped[int] = mapped_column(ForeignKey("after_sale_messages.id"), nullable=False)
