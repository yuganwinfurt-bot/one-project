"""订单通知随业务事务一起保存，读取消息不会再次生成提醒。"""

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.staff_inbox import StaffInboxEvent


ORDER_PAID_EVENT = "order_paid"


def notify_order_paid(db: Session, order: Order, product_name: str) -> None:
    """仅由新订单创建流程调用；与订单一同提交或回滚，不独立提交。"""
    if order.status != "paid":
        return
    db.flush()
    existing = db.query(StaffInboxEvent.id).filter_by(
        event_type=ORDER_PAID_EVENT, target_id=order.id,
    ).first()
    if existing:
        return
    db.add(StaffInboxEvent(
        event_type=ORDER_PAID_EVENT,
        target_id=order.id,
        title="新订单待发货",
        content=(
            f"订单号：{order.order_no}\n"
            f"买家：{order.buyer_name}\n"
            f"商品：{product_name} × {order.quantity}\n"
            f"实付：¥{order.amount:.2f}\n"
            "买家已提交演示订单，请及时查看订单并安排发货。"
        ),
    ))
    # Session 关闭自动 flush；显式写入以保证同一事务再次调用时可去重。
    db.flush()


def resolve_order_paid_notice(db: Session, order_id: int) -> None:
    """已发货或转入售后时，不再保留未读的待发货提醒。"""
    db.query(StaffInboxEvent).filter_by(
        event_type=ORDER_PAID_EVENT, target_id=order_id, is_read=False,
    ).update({StaffInboxEvent.is_read: True}, synchronize_session="fetch")
