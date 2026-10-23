from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.common.exceptions import BusinessException
from app.common.response import Response
from app.dependencies.auth import CurrentProductEditor, CurrentUser, DbSession
from app.models.community import DirectConversation, DirectMessage, ReviewReplyNotification
from app.models.order import Order
from app.models.review import Review
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.community_service import (
    add_review_comment, comment_data, direct_inbox, get_direct_conversation, review_owner_id, time_text,
)

router = APIRouter(prefix="/community", tags=["用户资料、私聊与评价互动"])


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def clean_content(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("内容不能为空")
        return value


class CommentCreate(MessageCreate):
    reply_to_user_id: int | None = Field(default=None, ge=1)


class ConversationCreate(BaseModel):
    user_id: int = Field(ge=1)


@router.get("/users/{user_id}")
def get_customer_profile(user_id: int, _staff: CurrentProductEditor, db: DbSession):
    user = db.query(User).filter_by(id=user_id, role="customer").first()
    if not user:
        raise BusinessException(message="用户资料不存在", code=404)
    order_count, spent = db.query(func.count(Order.id), func.sum(Order.amount)).filter(
        Order.buyer_user_id == user.id, Order.status.in_(("paid", "shipped", "completed"))
    ).one()
    return Response.success(data={
        **UserResponse.from_user(user).model_dump(), "create_time": time_text(user.create_time),
        "order_count": order_count, "order_amount": float(spent or 0),
    })


@router.post("/conversations")
def create_direct_conversation(payload: ConversationCreate, staff: CurrentProductEditor, db: DbSession):
    customer = db.query(User).filter_by(id=payload.user_id, role="customer", status=1).first()
    if not customer:
        raise BusinessException(message="该用户不能接收私聊", code=404)
    record = db.query(DirectConversation).filter_by(staff_id=staff.id, customer_id=customer.id).first()
    if not record:
        record = DirectConversation(staff_id=staff.id, customer_id=customer.id)
        db.add(record)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            record = db.query(DirectConversation).filter_by(staff_id=staff.id, customer_id=customer.id).one()
    return Response.success(data={"conversation_id": record.id})


@router.get("/conversations")
def list_direct_conversations(user: CurrentUser, db: DbSession):
    return Response.success(data={"list": direct_inbox(db, user)})


@router.get("/conversations/{conversation_id}/messages")
def get_direct_messages(conversation_id: int, user: CurrentUser, db: DbSession):
    record = get_direct_conversation(db, conversation_id, user)
    rows = db.query(DirectMessage).filter_by(conversation_id=record.id).order_by(DirectMessage.id).all()
    unread = 0
    result = []
    for message in rows:
        if message.sender_id != user.id and not message.is_read:
            unread += 1
            message.is_read = True
        sender = db.get(User, message.sender_id)
        result.append({"id": message.id, "sender_id": sender.id, "sender_name": sender.name or sender.username,
                       "content": message.content, "create_time": time_text(message.create_time)})
    if unread:
        db.commit()
    return Response.success(data={"list": result, "unread_count": unread})


@router.post("/conversations/{conversation_id}/messages")
def send_direct_message(conversation_id: int, payload: MessageCreate, user: CurrentUser, db: DbSession):
    record = get_direct_conversation(db, conversation_id, user)
    peer_id = record.customer_id if record.staff_id == user.id else record.staff_id
    if not db.query(User.id).filter_by(id=peer_id, status=1).first():
        raise BusinessException(message="对方账号暂时无法接收消息")
    message = DirectMessage(conversation_id=record.id, sender_id=user.id, content=payload.content)
    db.add(message)
    db.commit()
    return Response.success(data={"id": message.id}, message="私聊消息已发送")


@router.post("/reviews/{review_id}/comments")
def create_review_comment(review_id: int, payload: CommentCreate, user: CurrentUser, db: DbSession):
    review = db.get(Review, review_id)
    if not review:
        raise BusinessException(message="评价不存在", code=404)
    comment = add_review_comment(db, review, user, payload.content, payload.reply_to_user_id)
    db.commit()
    return Response.success(data=comment_data(db, comment, review_owner_id(db, review)), message="评论已发布")


@router.post("/notifications/{notification_id}/read")
def read_review_notification(notification_id: int, user: CurrentUser, db: DbSession):
    record = db.query(ReviewReplyNotification).filter_by(id=notification_id, user_id=user.id).first()
    if not record:
        raise BusinessException(message="通知不存在", code=404)
    record.is_read = True
    db.commit()
    return Response.success()
