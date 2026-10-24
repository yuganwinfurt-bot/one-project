"""后台与 AI 共用的售后操作；AI 批量执行时由外层统一提交事务。"""
from datetime import datetime

from app.common.exceptions import BusinessException
from app.models.after_sale import AfterSaleMessage, AfterSaleRequest
from app.models.order import Order
from app.models.product import Product
from app.services.after_sale_service import CLOSED_STATUSES, completion_blocked_reason
from app.services.after_sale_risk_service import sync_product_after_sale_risk
from app.services.inventory_service import sync_product_inventory
from app.services.platform_log_service import record_changes
from app.services.product_variant_service import adjust_product_stock, available_stock, select_variant


def process_after_sale(db, editor, after_sale_id, payload, *, commit=True):
    record = db.query(AfterSaleRequest).filter_by(id=after_sale_id).populate_existing().with_for_update().first()
    if not record:
        raise BusinessException(message='售后申请不存在', code=404)
    before = {'status': record.status, 'admin_note': record.admin_note}
    if payload.action in {'approve', 'reject'}:
        if record.status != 'pending':
            raise BusinessException(message='该申请已处理，无法重复审核')
        if payload.action == 'reject' and not payload.admin_note:
            raise BusinessException(message='请填写拒绝原因')
        if payload.action == 'approve' and record.service_type == 'exchange':
            product = db.query(Product).filter_by(id=record.product_id).with_for_update().first()
            if not product or available_stock(product, select_variant(product, record.order.variant_key)) < record.order.quantity:
                raise BusinessException(message='换货库存不足，请先补货或与买家沟通改为退款/退货退款')
        record.status = 'approved' if payload.action == 'approve' else 'rejected'
    else:
        blocked = completion_blocked_reason(record)
        if blocked:
            raise BusinessException(message=blocked)
        record.status = 'completed'
    if payload.admin_note is not None:
        record.admin_note = payload.admin_note
    record.processed_by, record.processed_at = editor.id, datetime.now()
    kind = {'refund': '退款', 'return': '退货退款', 'exchange': '换货'}.get(record.service_type, '售后')
    text = {
        'approve': f'你的{kind}申请已同意，售后处理中',
        'reject': f'你的{kind}申请审核未通过。会话已关闭，记录仍可查看；如需重新申请，请从订单的“更多”进入。你也可以评价本次售后服务',
        'complete': f'{kind}售后已完成。沟通通道已关闭，对话记录仍可查看，请为本次售后服务评分',
    }[payload.action]
    db.add(AfterSaleMessage(after_sale_id=record.id, user_id=record.user_id, sender_user_id=editor.id,
                            sender_role='system', sender_name='售后保障',
                            content=text + '。' + (f'处理说明：{record.admin_note}' if record.admin_note else ''),
                            read_by_customer=False, read_by_staff=True))
    sync_product_after_sale_risk(db, record.product_id, editor.id)
    record_changes(db, editor, '售后', record.order_no, [('处理', before, {'status': record.status, 'admin_note': record.admin_note})])
    db.flush()
    if commit:
        db.commit()
        db.refresh(record)
    return record


def exchange_shipment(db, editor, after_sale_id, payload, *, commit=True):
    record = db.query(AfterSaleRequest).filter_by(id=after_sale_id).populate_existing().with_for_update().first()
    if not record:
        raise BusinessException(message='售后申请不存在', code=404)
    if record.service_type != 'exchange' or record.status != 'approved':
        raise BusinessException(message='请先同意换货申请')
    if not (record.return_shipped and record.return_tracking_no):
        raise BusinessException(message='请等待用户寄回商品并提交物流单号')
    if record.exchange_tracking_no:
        raise BusinessException(message='换货商品物流单号已提交')
    order = db.query(Order).filter_by(id=record.order_id).with_for_update().first()
    if not order or order.status == 'cancelled':
        raise BusinessException(message='原订单不存在或已取消')
    product = db.query(Product).filter_by(id=record.product_id).with_for_update().first()
    if not product or available_stock(product, select_variant(product, order.variant_key)) < order.quantity:
        raise BusinessException(message='换货库存不足，请先补货；退款和退货退款不受库存限制')
    adjust_product_stock(product, -order.quantity, order.variant_key)
    sync_product_inventory(db, product.id, editor.id)
    record.exchange_tracking_no = payload.exchange_tracking_no
    order.status, order.shipped_at = 'shipped', datetime.now()
    db.add(AfterSaleMessage(after_sale_id=record.id, user_id=record.user_id, sender_user_id=editor.id,
                            sender_role='system', sender_name='售后保障',
                            content='商家已提交换货发货物流信息，详见售后卡片。', read_by_customer=False, read_by_staff=True))
    record_changes(db, editor, '售后', record.order_no, [('换货物流', None, payload.exchange_tracking_no)])
    db.flush()
    if commit:
        db.commit()
        db.refresh(record)
    return record


def send_after_sale_message(db, editor, after_sale_id, payload, *, commit=True):
    record = db.query(AfterSaleRequest).filter_by(id=after_sale_id).with_for_update().first()
    if not record:
        raise BusinessException(message='售后申请不存在', code=404)
    if record.status in CLOSED_STATUSES:
        raise BusinessException(message='售后会话已关闭，不能继续发送消息')
    from app.models.customer_support import SupportConversation
    conversation = db.query(SupportConversation).filter_by(after_sale_id=record.id).with_for_update().first()
    if conversation and conversation.closed:
        raise BusinessException(message='本次人工会话已结束，不能继续发送消息')
    message = AfterSaleMessage(after_sale_id=record.id, user_id=record.user_id, sender_user_id=editor.id,
                               sender_role=editor.role, sender_name=editor.name or editor.username,
                               content=payload.content, read_by_customer=False, read_by_staff=True)
    db.add(message)
    record_changes(db, editor, '售后', record.order_no, [('发送消息', None, payload.content)])
    db.flush()
    if commit:
        db.commit()
        db.refresh(message)
    return message
