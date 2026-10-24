"""Idempotent commerce import and durable reply delivery for local support tickets."""
import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, ProxyHandler

from fastapi import HTTPException
from models import EcommerceTicket, EcommerceConversation, EcommerceMessage, Message, MessageRole, Ticket, TicketCategory, TicketStatus
from sqlalchemy import or_

_lock = threading.RLock()
_last_attempt = 0.0
_last_success = None
_error = None
CLOSED = {"completed", "rejected"}
KINDS = {"refund": "退款", "return": "退货退款", "exchange": "换货"}


def request(path, body=None):
    token = os.getenv("ECOMMERCE_BRIDGE_TOKEN", "")
    if not token:
        raise HTTPException(503, "未配置电商集成凭证")
    url = os.getenv("ECOMMERCE_BASE_URL", "http://127.0.0.1:8001").rstrip("/") + "/api/internal/support" + path
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=data, headers={"X-Support-Token": token, "Content-Type": "application/json"})
    try:
        with build_opener(ProxyHandler({})).open(req, timeout=8) as response:
            result = json.load(response)
    except HTTPError as exc:
        try:
            result = json.load(exc)
            detail = result.get("detail") or result.get("message") or "电商操作失败"
        except (ValueError, AttributeError):
            detail = "电商操作失败"
        raise HTTPException(exc.code, detail) from None
    except (URLError, TimeoutError, OSError):
        raise HTTPException(503, "电商服务未连接；已保存的工单和消息仍可查看") from None
    if isinstance(result, dict) and "code" in result:
        if result["code"] != 200:
            raise HTTPException(409, result.get("message", "电商操作失败"))
        result = result.get("data")
    return result


def source_time(value):
    if not value:
        return datetime.utcnow()
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=8)))
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def import_record(db, data):
    link = db.query(EcommerceTicket).filter_by(after_sale_id=data["id"]).first()
    fresh = link is None
    if fresh:
        ticket = Ticket(
            title=f"{KINDS.get(data['service_type'], '售后')} · {data['product_name']} · {data['order_no']}"[:200],
            customer_name=(data.get("user_name") or data.get("username") or str(data["user_id"]))[:100],
            customer_email=data.get("customer_email") or "",
            category=TicketCategory.REFUND if data["service_type"] != "exchange" else TicketCategory.PRODUCT,
            created_at=source_time(data["create_time"]),
        )
        db.add(ticket)
        db.flush()
        link = EcommerceTicket(ticket_id=ticket.id, after_sale_id=data["id"], snapshot=data)
        db.add(link)
        db.add(Message(ticket_id=ticket.id, role=MessageRole.USER,
                       content=f"【电商售后申请 #{data['id']}】\n订单：{data['order_no']}\n商品：{data['product_name']}\n类型：{KINDS.get(data['service_type'], '售后')}\n原因：{data['reason']}\n说明：{data.get('description') or '无'}",
                       created_at=source_time(data["create_time"])))
    else:
        ticket = link.ticket
    old_status = (link.snapshot or {}).get("status")
    changed = fresh or link.snapshot != data
    new_customer_message = False
    for item in data.get("messages", []):
        delivery = db.query(EcommerceMessage).filter_by(source_message_id=item["id"]).first()
        if delivery is None and item.get("client_message_id"):
            delivery = db.query(EcommerceMessage).filter_by(client_message_id=item["client_message_id"]).first()
            if delivery:
                delivery.source_message_id, delivery.error = item["id"], None
        if delivery:
            continue
        role = MessageRole.USER if item["sender_role"] == "customer" else MessageRole.SYSTEM if item["sender_role"] == "system" else MessageRole.AGENT
        message = Message(ticket_id=ticket.id, role=role, content=item["content"], created_at=source_time(item["create_time"]))
        db.add(message)
        db.flush()
        db.add(EcommerceMessage(message_id=message.id, source_message_id=item["id"], client_message_id=item.get("client_message_id")))
        new_customer_message |= role == MessageRole.USER
    if data["status"] in CLOSED:
        ticket.status = TicketStatus.RESOLVED
    elif data.get("conversation_closed"):
        ticket.status, ticket.need_human = TicketStatus.PENDING, 0
    elif fresh or old_status in CLOSED or new_customer_message:
        ticket.status = TicketStatus.PENDING
    if data["status"] not in CLOSED and not data.get("conversation_closed") and data.get("handling_mode") in {"human_requested", "human"}:
        ticket.status, ticket.need_human = TicketStatus.ESCALATED, 1
        cancel_ai_outbox(db, ticket.id)
    if changed:
        source_updated = max([source_time(data.get("update_time") or data["create_time"])] + [source_time(m["create_time"]) for m in data.get("messages", [])])
        ticket.updated_at = source_updated if fresh else max(ticket.updated_at, source_updated)
    if data.get("conversation_closed"):
        cancel_closed_outbox(db, ticket.id)
    link.snapshot, link.synced_at = data, datetime.utcnow()
    db.flush()
    return ticket


def import_conversation(db, data):
    link = db.query(EcommerceConversation).filter_by(conversation_id=data["id"]).first()
    fresh = link is None
    if fresh:
        ticket = Ticket(title=data["title"][:200], customer_name=data["user_name"][:100], customer_email=data.get("customer_email") or "", category=TicketCategory.OTHER, created_at=source_time(data["create_time"]))
        db.add(ticket)
        db.flush()
        link = EcommerceConversation(ticket_id=ticket.id, conversation_id=data["id"], snapshot=data)
        db.add(link)
    else:
        ticket = link.ticket
    for item in data["messages"]:
        source_key = f"conversation:{data['id']}:message:{item['id']}"
        delivery = db.query(EcommerceMessage).filter_by(source_key=source_key).first()
        if not delivery and item.get("client_message_id"):
            delivery = db.query(EcommerceMessage).filter_by(client_message_id=item["client_message_id"]).first()
        if delivery:
            delivery.source_key, delivery.error = source_key, None
            continue
        role = MessageRole.USER if item["sender_role"] == "customer" else MessageRole.SYSTEM if item["sender_role"] == "system" else MessageRole.AGENT
        message = Message(ticket_id=ticket.id, role=role, content=item["content"], created_at=source_time(item["create_time"]))
        db.add(message)
        db.flush()
        db.add(EcommerceMessage(message_id=message.id, source_key=source_key, client_message_id=item.get("client_message_id")))
    if data["conversation_closed"]:
        ticket.status, ticket.need_human = TicketStatus.RESOLVED, 0
    elif data["handling_mode"] in {"human_requested", "human"}:
        ticket.status, ticket.need_human = TicketStatus.ESCALATED, 1
        cancel_ai_outbox(db, ticket.id)
    elif not data["messages"] or data["messages"][-1]["sender_role"] == "customer":
        ticket.status = TicketStatus.AI_PROCESSING
    else:
        ticket.status = TicketStatus.WAITING_USER
    if fresh or data != link.snapshot:
        updated = source_time(data["update_time"])
        ticket.updated_at = updated if fresh else max(ticket.updated_at, updated)
    if data.get("conversation_closed"):
        cancel_closed_outbox(db, ticket.id)
    link.snapshot = data
    db.flush()
    return ticket


def cancel_closed_outbox(db, ticket_id):
    queue_replies(db, ticket_id, commit=False)
    pending = db.query(EcommerceMessage).join(Message).filter(Message.ticket_id == ticket_id, EcommerceMessage.source_message_id.is_(None), EcommerceMessage.source_key.is_(None)).all()
    for delivery in pending:
        delivery.source_key = f"cancelled:closed:{delivery.message_id}"
        delivery.error = "会话已结束，本条未送达的回复已取消"


def cancel_ai_outbox(db, ticket_id):
    pending = db.query(EcommerceMessage).join(Message).filter(Message.ticket_id == ticket_id, Message.ai_model.is_not(None), EcommerceMessage.source_message_id.is_(None), EcommerceMessage.source_key.is_(None)).all()
    for delivery in pending:
        delivery.source_key = f"cancelled:handoff:{delivery.message_id}"
        delivery.error = "已取消：买家已申请人工，AI回复未发送"


def queue_replies(db, ticket_id=None, commit=True):
    """Assign a stable key before contacting commerce, so a timeout cannot duplicate a reply."""
    q = db.query(Message).outerjoin(EcommerceTicket, Message.ticket_id == EcommerceTicket.ticket_id).outerjoin(EcommerceConversation, Message.ticket_id == EcommerceConversation.ticket_id).outerjoin(EcommerceMessage, Message.id == EcommerceMessage.message_id).filter(or_(EcommerceTicket.id.is_not(None), EcommerceConversation.id.is_not(None)), Message.role == MessageRole.AGENT, EcommerceMessage.id.is_(None))
    if ticket_id is not None:
        q = q.filter(Message.ticket_id == ticket_id)
    prefix = hashlib.sha256(os.getenv("ECOMMERCE_BRIDGE_TOKEN", "").encode()).hexdigest()[:16]
    for message in q.all():
        db.add(EcommerceMessage(message_id=message.id, client_message_id=f"support:{prefix}:{message.id}"))
    if commit:
        db.commit()
    else:
        db.flush()


def deliver_replies(db, ticket_id=None):
    queue_replies(db, ticket_id)
    q = db.query(EcommerceMessage).join(Message).filter(EcommerceMessage.source_message_id.is_(None), EcommerceMessage.source_key.is_(None))
    if ticket_id is not None:
        q = q.filter(Message.ticket_id == ticket_id)
    for delivery in q.order_by(EcommerceMessage.id).all():
        link = db.query(EcommerceTicket).filter_by(ticket_id=delivery.message.ticket_id).first()
        chat = None if link else db.query(EcommerceConversation).filter_by(ticket_id=delivery.message.ticket_id).one()
        try:
            path = f"/after-sales/{link.after_sale_id}/messages" if link else f"/conversations/{chat.conversation_id}/messages"
            result = request(path, {
                "content": delivery.message.content, "client_message_id": delivery.client_message_id,
                "ai_generated": bool(delivery.message.ai_model),
            })
            if link:
                delivery.source_message_id = result["id"]
            else:
                delivery.source_key = f"conversation:{chat.conversation_id}:message:{result['id']}"
            delivery.error = None
            if delivery.message.ticket.status != TicketStatus.ESCALATED:
                delivery.message.ticket.status = TicketStatus.WAITING_USER
        except HTTPException as exc:
            delivery.error = str(exc.detail)
            db.commit()
            if exc.status_code >= 500:
                break
            continue
        db.commit()


def publish(db, ticket_id):
    with _lock:
        deliver_replies(db, ticket_id)
        db.expire_all()


def sync(db, force=False):
    global _last_attempt, _last_success, _error
    with _lock:
        if not force and time.monotonic() - _last_attempt < 5:
            return status()
        _last_attempt = time.monotonic()
        try:
            # Import first to recover reply acknowledgments lost after a timeout.
            cursor = 0
            while True:
                page = request(f"/after-sales?after_id={cursor}&limit=100")
                for data in page["records"]:
                    import_record(db, data)
                cursor = page.get("next_cursor")
                if not cursor:
                    break
            cursor = 0
            while True:
                page = request(f"/conversations?after_id={cursor}&limit=100")
                for data in page["records"]:
                    import_conversation(db, data)
                cursor = page.get("next_cursor")
                if not cursor:
                    break
            db.commit()
            deliver_replies(db)
            db.expire_all()
            _last_success, _error = datetime.utcnow().isoformat() + "Z", None
        except HTTPException as exc:
            db.rollback()
            _error = str(exc.detail)
        except Exception:
            db.rollback()
            _error = "售后同步失败，已保存的工单保持不变，请稍后重试"
            import logging
            logging.getLogger(__name__).exception("Commerce ticket sync failed")
        return status()


def status():
    return {"connected": _last_success is not None and _error is None, "last_sync": _last_success, "error": _error}


def snapshot(ticket):
    if ticket.ecommerce_source:
        return ticket.ecommerce_source.snapshot
    return ticket.ecommerce_conversation.snapshot if ticket.ecommerce_conversation else None


def require_open(ticket):
    data = snapshot(ticket)
    if data and (data["status"] in CLOSED or data.get("conversation_closed")):
        raise HTTPException(409, "本次客服会话已结束，记录可查看，不能继续回复")


def action(db, ticket, name, payload):
    with _lock:
        link = ticket.ecommerce_source
        if not link:
            raise HTTPException(400, "此工单不是电商售后工单")
        # Never close a conversation while a local reply is still awaiting delivery.
        deliver_replies(db, ticket.id)
        pending = db.query(EcommerceMessage).join(Message).filter(Message.ticket_id == ticket.id, EcommerceMessage.source_message_id.is_(None), EcommerceMessage.source_key.is_(None)).count()
        if pending:
            raise HTTPException(409, "还有未送达买家的回复，请恢复连接并重试发送后再处理售后")
        result = request(f"/after-sales/{link.after_sale_id}/{name}", payload)
        import_record(db, result)
        db.commit()
        db.refresh(ticket)
        return ticket
