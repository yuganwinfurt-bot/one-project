import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database import Base


class TicketStatus(str, enum.Enum):
    PENDING = "pending"
    AI_PROCESSING = "ai_processing"
    WAITING_USER = "waiting_user"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, enum.Enum):
    ORDER = "order"
    REFUND = "refund"
    ACCOUNT = "account"
    PRODUCT = "product"
    COMPLAINT = "complaint"
    OTHER = "other"


class MessageRole(str, enum.Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Sentiment(str, enum.Enum):
    NORMAL = "normal"
    ANXIOUS = "anxious"
    ANGRY = "angry"
    COMPLAINT = "complaint"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(200), nullable=False)
    category = Column(Enum(TicketCategory), default=TicketCategory.OTHER)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(Enum(TicketStatus), default=TicketStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sentiment = Column(Enum(Sentiment), nullable=True)
    ai_category = Column(Enum(TicketCategory), nullable=True)
    ai_priority = Column(Enum(TicketPriority), nullable=True)
    need_human = Column(Integer, default=0)
    analysis_reason = Column(Text, nullable=True)
    analysis_status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    analyzed_at = Column(DateTime, nullable=True)

    messages = relationship("Message", back_populates="ticket", order_by="Message.created_at")
    ecommerce_source = relationship("EcommerceTicket", back_populates="ticket", uselist=False)
    ecommerce_conversation = relationship("EcommerceConversation", back_populates="ticket", uselist=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    source_kb_ids = Column(String(500), default="")
    ai_model = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="messages")
    ecommerce_delivery = relationship("EcommerceMessage", back_populates="message", uselist=False)

    @property
    def delivery_status(self):
        if self.ecommerce_delivery:
            if (self.ecommerce_delivery.source_key or "").startswith("cancelled:"):
                return "cancelled"
            return "sent" if self.ecommerce_delivery.source_message_id or self.ecommerce_delivery.source_key else "pending"
        return None

    @property
    def delivery_error(self):
        return self.ecommerce_delivery.error if self.ecommerce_delivery else None


class EcommerceTicket(Base):
    __tablename__ = "ecommerce_tickets"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), unique=True, nullable=False)
    after_sale_id = Column(Integer, unique=True, nullable=False)
    snapshot = Column(JSON, nullable=False)
    synced_at = Column(DateTime, default=datetime.utcnow)
    ticket = relationship("Ticket", back_populates="ecommerce_source")


class EcommerceMessage(Base):
    __tablename__ = "ecommerce_messages"
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), unique=True, nullable=False)
    source_message_id = Column(Integer, unique=True, nullable=True)
    source_key = Column(String(160), unique=True, nullable=True)
    client_message_id = Column(String(120), unique=True, nullable=True)
    error = Column(Text, nullable=True)
    message = relationship("Message", back_populates="ecommerce_delivery")


class EcommerceConversation(Base):
    __tablename__ = "ecommerce_conversations"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), unique=True, nullable=False)
    conversation_id = Column(Integer, unique=True, nullable=False)
    snapshot = Column(JSON, nullable=False)
    ticket = relationship("Ticket", back_populates="ecommerce_conversation")


class AgentReplyRequest(Base):
    __tablename__ = "agent_reply_requests"
    id = Column(String(64), primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    last_message_id = Column(Integer, nullable=False)
    reply_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    category = Column(Enum(TicketCategory), default=TicketCategory.OTHER)
    content = Column(Text, nullable=False)
    keywords = Column(String(500), default="")
    enabled = Column(Integer, default=1)
    embedding = Column(Text, nullable=True, default=None)  # JSON-serialized float list
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TicketSummary(Base):
    __tablename__ = "ticket_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), unique=True, nullable=False)
    problem = Column(Text, default="")
    category = Column(String(50), default="")
    sentiment = Column(String(50), default="")
    resolution = Column(Text, default="")
    final_status = Column(String(50), default="")
    need_human = Column(Integer, default=0)
    escalation_reason = Column(Text, default="")
    knowledge_used = Column(Integer, default=0)
    summary_text = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
