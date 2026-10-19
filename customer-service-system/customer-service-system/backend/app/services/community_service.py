from sqlalchemy import func, or_
from sqlalchemy.orm import aliased

from app.common.exceptions import BusinessException
from app.models.community import DirectConversation, DirectMessage, ReviewComment, ReviewReplyNotification
from app.models.order import Order
from app.models.product import Product
from app.models.review_reply import CustomerReviewReply
from app.models.user import User


def time_text(value):
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


def review_owner_id(db, review):
    return db.query(Order.buyer_user_id).filter(Order.id == review.order_id).scalar() if review.order_id else None


def comment_data(db, record, owner_id):
    actor = db.get(User, record.user_id)
    recipient = db.get(User, record.reply_to_user_id) if record.reply_to_user_id else None
    return {
        "id": f"comment-{record.id}", "review_id": record.review_id,
        "user_id": actor.id, "user_name": actor.name or actor.username,
        "user_role": actor.role, "avatar": actor.avatar,
        "reply_to_user_id": record.reply_to_user_id,
        "reply_to_name": (recipient.name or recipient.username) if recipient else None,
        "kind": "append" if actor.id == owner_id and record.reply_to_user_id in {None, owner_id} else "reply",
        "content": record.content, "create_time": time_text(record.create_time),
    }


def add_review_comment(db, review, actor, content, reply_to_user_id=None):
    owner_id = review_owner_id(db, review)
    target_id = reply_to_user_id if reply_to_user_id is not None else owner_id
    if target_id is not None and target_id != owner_id:
        participated = (
            db.query(ReviewComment.id).filter_by(review_id=review.id, user_id=target_id).first()
            or db.query(CustomerReviewReply.id).filter_by(review_id=review.id, user_id=target_id).first()
        )
        if not participated:
            raise BusinessException(message="只能回复此评论中的参与用户", code=400)
    record = ReviewComment(review_id=review.id, user_id=actor.id, reply_to_user_id=target_id, content=content)
    db.add(record)
    # 保留历史商家回复；此字段仍供旧页面和“已回复”筛选使用，新回复逐条存在 ReviewComment。
    if actor.role in {"admin", "user"} and target_id == owner_id and not review.merchant_reply:
        review.merchant_reply = content
    notify_review_reply(db, review, actor, content, target_id)
    db.flush()
    return record


def notify_review_reply(db, review, actor, content, target_id):
    if target_id is not None and target_id != actor.id:
        product = db.get(Product, review.product_id)
        db.add(ReviewReplyNotification(
            user_id=target_id, review_id=review.id, product_id=review.product_id,
            product_name=product.name if product else "商品", actor_name=actor.name or actor.username,
            actor_role=actor.role, review_content=review.content, content=content,
        ))


def notification_data(record):
    return {
        "id": f"review-reply-{record.id}", "notification_id": record.id, "type": "review_reply",
        "review_id": record.review_id, "product_id": record.product_id, "product_name": record.product_name,
        "actor_name": record.actor_name, "actor_role": record.actor_role,
        "review_content": record.review_content, "content": record.content, "is_read": record.is_read,
        "create_time": time_text(record.create_time),
    }


def get_direct_conversation(db, conversation_id, user):
    record = db.query(DirectConversation).filter(
        DirectConversation.id == conversation_id,
        or_(DirectConversation.staff_id == user.id, DirectConversation.customer_id == user.id),
    ).first()
    if not record:
        raise BusinessException(message="私聊不存在或无权访问", code=404)
    return record


def direct_inbox(db, user):
    latest_ids = db.query(DirectMessage.conversation_id, func.max(DirectMessage.id).label("message_id")).group_by(DirectMessage.conversation_id).subquery()
    latest = aliased(DirectMessage)
    rows = db.query(DirectConversation, latest).outerjoin(
        latest_ids, latest_ids.c.conversation_id == DirectConversation.id
    ).outerjoin(latest, latest.id == latest_ids.c.message_id).filter(
        or_(DirectConversation.staff_id == user.id, DirectConversation.customer_id == user.id)
    ).all()
    unread = dict(db.query(DirectMessage.conversation_id, func.count(DirectMessage.id)).join(
        DirectConversation, DirectConversation.id == DirectMessage.conversation_id
    ).filter(
        or_(DirectConversation.staff_id == user.id, DirectConversation.customer_id == user.id),
        DirectMessage.sender_id != user.id, DirectMessage.is_read.is_(False),
    ).group_by(DirectMessage.conversation_id).all())
    result = []
    for conversation, message in rows:
        peer = db.get(User, conversation.customer_id if conversation.staff_id == user.id else conversation.staff_id)
        result.append({
            "id": f"direct-{conversation.id}", "conversation_id": conversation.id, "type": "direct_chat",
            "peer_id": peer.id, "peer_name": peer.name or peer.username, "peer_avatar": peer.avatar,
            "peer_role": peer.role, "preview": message.content if message else "点击开始私聊",
            "create_time": time_text(message.create_time if message else conversation.create_time),
            "unread_count": int(unread.get(conversation.id, 0)), "is_read": not unread.get(conversation.id, 0),
        })
    return sorted(result, key=lambda item: (item["create_time"] or "", item["conversation_id"]), reverse=True)
