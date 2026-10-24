from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.dependencies.auth import CurrentUser, CurrentProductEditor, DbSession
from app.common.response import Response
from app.api.customer_store import _require_customer
from app.models.customer_support import SupportConversation, SupportChatMessage
from app.models.after_sale import AfterSaleRequest
from app.models.user import User
from app.services import customer_support_service as service

router = APIRouter(prefix="/customer/support", tags=["AI客服与人工接待"])


class Text(BaseModel):
    content: str = Field(min_length=1, max_length=20000)


class HumanRequest(BaseModel):
    reason: str = Field(default="对AI回答不满意，希望人工协助", max_length=1000)


@router.get("/conversations")
def list_conversations(user: CurrentUser, db: DbSession):
    _require_customer(user)
    records = db.query(SupportConversation).filter_by(user_id=user.id, after_sale_id=None).order_by(SupportConversation.id.desc()).all()
    return Response.success(data=[service.snapshot(db, item) for item in records])


@router.post("/conversations")
def create_conversation(user: CurrentUser, db: DbSession):
    _require_customer(user)
    # Reuse the active general consultation; creating it twice must not split a chat.
    db.query(User).filter_by(id=user.id).with_for_update().one()
    conversation = db.query(SupportConversation).filter_by(user_id=user.id, after_sale_id=None, closed=False).first()
    if not conversation:
        conversation = SupportConversation(user_id=user.id)
        db.add(conversation)
        db.flush()
    db.commit()
    return Response.success(data=service.snapshot(db, conversation))


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, user: CurrentUser, db: DbSession):
    _require_customer(user)
    conversation = service.get_conversation(db, conversation_id, user.id)
    messages = service.rows(db, conversation)
    for message in messages:
        message.read_by_customer = True
    db.commit()
    return Response.success(data=service.snapshot(db, conversation))


@router.post("/conversations/{conversation_id}/messages")
def send_message(conversation_id: int, body: Text, user: CurrentUser, db: DbSession):
    _require_customer(user)
    conversation = service.get_conversation(db, conversation_id, user.id, lock=True)
    message = service.add_message(db, conversation, "customer", body.content, user.name or user.username)
    if conversation.title == "售后咨询":
        conversation.title = body.content.strip()[:100]
    prepared = service.prepare_ai(db, conversation)
    result = {"message": service.message_data(message), "ai_pending": bool(prepared)}
    db.commit()
    return Response.success(data=result)


@router.post("/conversations/{conversation_id}/ai-prepare")
def prepare_reply(conversation_id: int, user: CurrentUser, db: DbSession):
    _require_customer(user)
    conversation = service.get_conversation(db, conversation_id, user.id, lock=True)
    result = service.prepare_ai(db, conversation)
    db.commit()
    return Response.success(data={"ai_pending": bool(result)})


@router.post("/conversations/{conversation_id}/human")
def human_request(conversation_id: int, body: HumanRequest, user: CurrentUser, db: DbSession):
    _require_customer(user)
    conversation = service.get_conversation(db, conversation_id, user.id, lock=True)
    service.request_human(db, conversation, body.reason)
    db.commit()
    return Response.success(data=service.snapshot(db, conversation))


class CloseConversation(BaseModel):
    reason: str = Field(default="问题已解决", max_length=1000)


@router.post("/conversations/{conversation_id}/close")
def close_conversation(conversation_id: int, body: CloseConversation, user: CurrentUser, db: DbSession):
    _require_customer(user)
    conversation = service.get_conversation(db, conversation_id, user.id, lock=True)
    service.end_conversation(db, conversation, "customer", body.reason)
    db.commit()
    return Response.success(data=service.snapshot(db, conversation))


staff_router = APIRouter(prefix="/ecommerce", tags=["统一售后工单"])


@staff_router.get("/support-tickets")
def support_tickets(_staff: CurrentProductEditor, db: DbSession, page: int = 1, page_size: int = 10, keywords: str = "", status: str = "", product_id: int | None = None):
    from app.api.ecommerce import _after_sale_data
    records = []
    for record, user in db.query(AfterSaleRequest, User).join(User, User.id == AfterSaleRequest.user_id).all():
        item = {**_after_sale_data(record, user.username, user.name), "record_type": "after_sale"}
        conversation = db.query(SupportConversation).filter_by(after_sale_id=record.id).first()
        item.update(service.state(conversation))
        records.append(item)
    for conversation in db.query(SupportConversation).filter_by(after_sale_id=None).all():
        if service.rows(db, conversation):
            item = service.snapshot(db, conversation)
            item["order_no"] = f"咨询 #{conversation.id}"
            records.append(item)
    key = keywords.strip().lower()
    records = [r for r in records if (not status or r["status"] == status) and (not product_id or r["product_id"] == product_id) and (not key or key in " ".join(str(r.get(k) or "") for k in ("order_no", "product_name", "user_name", "username", "reason")).lower())]
    records.sort(key=lambda r: (str(r.get("create_time") or "").replace("T", " "), r["id"]), reverse=True)
    size, page = min(100, max(1, page_size)), max(1, page)
    return Response.success(data={"list": records[(page-1)*size:page*size], "total": len(records)})
