"""Private, local service bridge; customer/order data stays in the commerce database."""
import ipaddress
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.dependencies.auth import DbSession
from app.models.after_sale import AfterSaleMessage, AfterSaleRequest
from app.models.support_bridge import SupportMessageDelivery
from app.models.user import User
from app.models.customer_support import SupportConversation, SupportChatMessage, SupportChatDelivery
from app.models.staff_inbox import StaffInboxEvent
from app.services import customer_support_service as support
from app.schemas.after_sale import AfterSaleExchangeShipmentUpdate, AfterSaleProcess
from app.services import merchant_operations_service
from app.api.ecommerce import _after_sale_data, _after_sale_message_data


def verify_bridge(request: Request, x_support_token: Annotated[str | None, Header()] = None):
    try:
        local = ipaddress.ip_address(request.client.host).is_loopback
    except (ValueError, AttributeError):
        local = False
    configured = settings.SUPPORT_BRIDGE_TOKEN
    if not local or not configured or not secrets.compare_digest(x_support_token or "", configured):
        raise HTTPException(403, "客服集成凭证无效或请求并非来自本机")


router = APIRouter(prefix="/internal/support", tags=["本地客服集成"], dependencies=[Depends(verify_bridge)])


def operator(db):
    user = db.query(User).filter(User.id == settings.SUPPORT_OPERATOR_ID, User.status == 1).first()
    if not user or user.role not in {"admin", "user"}:
        raise HTTPException(503, "请配置有效的客服集成操作账号")
    return user


def snapshot(db, record):
    user = db.query(User).filter(User.id == record.user_id).first()
    result = _after_sale_data(record, user.username if user else "", user.name if user else "")
    conversation = db.query(SupportConversation).filter_by(after_sale_id=record.id).first()
    result.update(support.state(conversation))
    result["conversation_closed"] = bool(result.get("conversation_closed") or (conversation and conversation.closed))
    result.update(
        customer_email=user.email or "" if user else "",
        processed_by=record.processed_by,
        update_time=record.update_time.isoformat() if record.update_time else None,
    )
    order = record.order
    result["order"] = None if not order else {
        "id": order.id, "order_no": order.order_no, "status": order.status,
        "quantity": order.quantity, "amount": str(order.amount),
        "tracking_no": order.tracking_no, "shipping_address": order.shipping_address,
        "variant_name": order.variant_name,
    }
    messages = db.query(AfterSaleMessage).filter_by(after_sale_id=record.id).order_by(AfterSaleMessage.create_time, AfterSaleMessage.id).all()
    result["messages"] = [
        {**_after_sale_message_data(m), "read_by_customer": m.read_by_customer, "read_by_staff": m.read_by_staff}
        for m in messages
    ]
    deliveries = {d.message_id: d.client_message_id for d in db.query(SupportMessageDelivery).filter_by(after_sale_id=record.id).all()}
    for item in result["messages"]:
        item["client_message_id"] = deliveries.get(item["id"])
    return result


def find_record(db, source_id):
    record = db.query(AfterSaleRequest).filter_by(id=source_id).first()
    if not record:
        raise HTTPException(404, "售后记录不存在")
    return record


@router.get("/after-sales")
def export_after_sales(db: DbSession, after_id: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200)):
    rows = db.query(AfterSaleRequest).filter(AfterSaleRequest.id > after_id).order_by(AfterSaleRequest.id).limit(limit).all()
    return {"records": [snapshot(db, row) for row in rows], "next_cursor": rows[-1].id if len(rows) == limit else None}


@router.get("/after-sales/{source_id}")
def get_after_sale(source_id: int, db: DbSession):
    return snapshot(db, find_record(db, source_id))


@router.post("/after-sales/{source_id}/process")
def process_after_sale(source_id: int, payload: AfterSaleProcess, db: DbSession):
    record = merchant_operations_service.process_after_sale(db, operator(db), source_id, payload)
    if record.status in {"completed", "rejected"}:
        conversation = db.query(SupportConversation).filter_by(after_sale_id=source_id).first()
        if conversation:
            conversation.closed = True
            db.query(StaffInboxEvent).filter_by(event_type="human_support", target_id=conversation.id, is_read=False).update({"is_read": True}, synchronize_session=False)
            db.commit()
    return snapshot(db, record)


@router.post("/after-sales/{source_id}/exchange-shipment")
def exchange_shipment(source_id: int, payload: AfterSaleExchangeShipmentUpdate, db: DbSession):
    record = merchant_operations_service.exchange_shipment(db, operator(db), source_id, payload)
    return snapshot(db, record)


class BridgeMessage(BaseModel):
    ai_generated: bool = False
    client_message_id: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=20000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value):
        if not value.strip():
            raise ValueError("消息内容不能为空")
        return value.strip()


@router.post("/after-sales/{source_id}/messages")
def send_message(source_id: int, payload: BridgeMessage, db: DbSession):
    existing = db.query(SupportMessageDelivery).filter_by(client_message_id=payload.client_message_id).first()
    if existing:
        message = db.get(AfterSaleMessage, existing.message_id)
        if existing.after_sale_id != source_id or not message or message.content != payload.content:
            raise HTTPException(409, "消息标识与原消息不一致")
        return _after_sale_message_data(message)
    record = find_record(db, source_id)
    conversation = support.for_after_sale(db, record)
    conversation = support.get_conversation(db, conversation.id, lock=True)
    if conversation.closed:
        raise HTTPException(409, "本次会话已结束，请发起新的咨询")
    if payload.ai_generated and conversation.handling_mode != "ai":
        raise HTTPException(409, "买家已申请人工，不能发送AI回复")
    if not payload.ai_generated:
        support.claim(db, conversation)
    message = merchant_operations_service.send_after_sale_message(db, operator(db), source_id, payload, commit=False)
    message.sender_name = "AI 客服" if payload.ai_generated else "人工客服"
    if payload.ai_generated:
        message.sender_role = "assistant"
    db.add(SupportMessageDelivery(client_message_id=payload.client_message_id, after_sale_id=source_id, message_id=message.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(SupportMessageDelivery).filter_by(client_message_id=payload.client_message_id).first()
        if not existing:
            raise
        message = db.get(AfterSaleMessage, existing.message_id)
        if existing.after_sale_id != source_id or not message or message.content != payload.content:
            raise HTTPException(409, "消息标识与原消息不一致")
    return _after_sale_message_data(message)


@router.post("/after-sales/{source_id}/read")
def mark_read(source_id: int, db: DbSession):
    find_record(db, source_id)
    db.query(AfterSaleMessage).filter_by(after_sale_id=source_id, sender_role="customer", read_by_staff=False).update({"read_by_staff": True}, synchronize_session=False)
    db.commit()
    return {"ok": True}


@router.get("/conversations")
def export_conversations(db: DbSession, after_id: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200)):
    records = db.query(SupportConversation).filter(SupportConversation.after_sale_id.is_(None), SupportConversation.id > after_id, db.query(SupportChatMessage.id).filter(SupportChatMessage.conversation_id == SupportConversation.id).exists()).order_by(SupportConversation.id).limit(limit).all()
    result = []
    for record in records:
        item = support.snapshot(db, record)
        deliveries = {d.message_id: d.client_message_id for d in db.query(SupportChatDelivery).filter_by(conversation_id=record.id).all()}
        for message in item["messages"]:
            message["client_message_id"] = deliveries.get(message["id"])
        result.append(item)
    return {"records": result, "next_cursor": records[-1].id if len(records) == limit else None}


@router.post("/conversations/{conversation_id}/messages")
def reply_to_conversation(conversation_id: int, payload: BridgeMessage, db: DbSession):
    conversation = support.get_conversation(db, conversation_id, lock=True)
    if conversation.after_sale_id:
        raise HTTPException(400, "请使用售后消息接口")
    existing = db.query(SupportChatDelivery).filter_by(client_message_id=payload.client_message_id).first()
    if existing:
        message = db.get(SupportChatMessage, existing.message_id)
        if existing.conversation_id != conversation_id or message.content != payload.content:
            raise HTTPException(409, "消息标识与原消息不一致")
        return support.message_data(message)
    conversation = support.get_conversation(db, conversation.id, lock=True)
    if conversation.closed:
        raise HTTPException(409, "本次会话已结束，请发起新的咨询")
    if payload.ai_generated and conversation.handling_mode != "ai":
        raise HTTPException(409, "买家已申请人工，不能发送AI回复")
    if not payload.ai_generated:
        support.claim(db, conversation)
    message = support.add_message(db, conversation, "assistant" if payload.ai_generated else "staff", payload.content, "AI 客服" if payload.ai_generated else "人工客服")
    db.add(SupportChatDelivery(client_message_id=payload.client_message_id, conversation_id=conversation.id, message_id=message.id))
    db.commit()
    return support.message_data(message)


@router.post("/conversations/{conversation_id}/claim")
def claim_conversation(conversation_id: int, db: DbSession):
    conversation = support.get_conversation(db, conversation_id, lock=True)
    support.claim(db, conversation)
    db.commit()
    return support.snapshot(db, conversation) if not conversation.after_sale_id else snapshot(db, find_record(db, conversation.after_sale_id))


@router.post("/conversations/{conversation_id}/resolve")
def resolve_conversation(conversation_id: int, db: DbSession):
    conversation = support.get_conversation(db, conversation_id, lock=True)
    if conversation.after_sale_id:
        raise HTTPException(409, "请在售后处理卡片中完成售后")
    if not conversation.closed:
        support.add_message(db, conversation, "system", "客服已结束本次咨询；如有新问题，可以发起新咨询。", "售后工单系统")
        conversation.closed = True
    db.query(StaffInboxEvent).filter_by(event_type="human_support", target_id=conversation_id, is_read=False).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return support.snapshot(db, conversation)


class EndHumanSession(BaseModel):
    reason: str = Field(default="问题已解决", max_length=1000)


@router.post("/conversations/{conversation_id}/end-human")
def end_human_session(conversation_id: int, body: EndHumanSession, db: DbSession):
    conversation = support.get_conversation(db, conversation_id, lock=True)
    support.end_conversation(db, conversation, "staff", body.reason)
    db.commit()
    return snapshot(db, find_record(db, conversation.after_sale_id)) if conversation.after_sale_id else support.snapshot(db, conversation)
