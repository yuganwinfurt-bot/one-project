"""待付款结算：同一批商品一起付款/取消，库存与优惠券在同一事务里恢复。"""
from datetime import datetime, timedelta

from app.common.exceptions import BusinessException
from app.models.mall import CouponClaim, OrderPromotion
from app.models.order import Order
from app.models.product import Product
from app.services.mall_service import settings_data
from app.services.product_variant_service import adjust_product_stock


def payment_deadline(db, now=None):
    return (now or datetime.now()) + timedelta(minutes=settings_data(db, 'order')['unpaid_timeout_minutes'])


def checkout_orders(db, order_id, user_id=None):
    query = db.query(Order).filter(Order.id == order_id)
    if user_id is not None:
        query = query.filter(Order.buyer_user_id == user_id)
    target = query.first()
    if not target:
        raise BusinessException(message='找不到属于你的订单', code=404)
    group = db.query(Order).filter(Order.buyer_user_id == target.buyer_user_id)
    group = group.filter(Order.checkout_id == target.checkout_id) if target.checkout_id else group.filter(Order.id == target.id)
    return group.order_by(Order.id).populate_existing().with_for_update().all()


def _cancel_locked(db, orders):
    if all(order.status == 'cancelled' for order in orders):
        return False
    if any(order.status != 'unpaid' for order in orders):
        raise BusinessException(message='只有待付款订单可以取消，已付款订单请申请售后')
    product_ids = sorted({order.product_id for order in orders})
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).order_by(Product.id).populate_existing().with_for_update()}
    for order in orders:
        product = products.get(order.product_id)
        if not product:
            raise BusinessException(message='订单商品不存在，无法返还库存，请联系管理员')
        adjust_product_stock(product, order.quantity, order.variant_key or None)
        order.status = 'cancelled'
    db.flush()
    claims = {row[0] for row in db.query(OrderPromotion.coupon_claim_id).filter(
        OrderPromotion.order_id.in_([order.id for order in orders]),
        OrderPromotion.coupon_claim_id.isnot(None),
    )}
    for claim_id in sorted(claims):
        claim = db.query(CouponClaim).filter_by(id=claim_id).populate_existing().with_for_update().first()
        still_used = db.query(OrderPromotion.id).join(Order, Order.id == OrderPromotion.order_id).filter(
            OrderPromotion.coupon_claim_id == claim_id, Order.status != 'cancelled',
        ).first()
        if claim and not still_used:
            claim.used_at = None
            claim.reserved_checkout_id = None
    from app.services.inventory_service import sync_product_inventory
    from app.services.after_sale_risk_service import sync_product_after_sale_risk
    for product_id in product_ids:
        sync_product_inventory(db, product_id)
        sync_product_after_sale_risk(db, product_id)
    return True


def cancel_checkout(db, order_id, user_id):
    try:
        orders = checkout_orders(db, order_id, user_id)
        _cancel_locked(db, orders)
        db.commit()
        return orders
    except Exception:
        db.rollback()
        raise


def pay_checkout(db, order_id, user_id, now=None):
    """本地演示付款，不调用支付网关；生产支付应改由已验签回调调用此状态流转。"""
    now = now or datetime.now()
    try:
        orders = checkout_orders(db, order_id, user_id)
        if all(order.status in {'paid', 'shipped', 'completed'} for order in orders):
            return orders
        if any(order.status != 'unpaid' for order in orders):
            raise BusinessException(message='订单已取消或状态已变化，请刷新订单列表')
        if any(order.payment_deadline_at and order.payment_deadline_at <= now for order in orders):
            _cancel_locked(db, orders)
            db.commit()
            raise BusinessException(message='订单已超过付款时间并自动取消，库存和优惠券已返还')
        from app.services.staff_inbox_service import notify_order_paid
        from app.services.after_sale_risk_service import sync_product_after_sale_risk
        claim_ids = {row[0] for row in db.query(OrderPromotion.coupon_claim_id).filter(
            OrderPromotion.order_id.in_([order.id for order in orders]), OrderPromotion.coupon_claim_id.isnot(None),
        )}
        for claim_id in sorted(claim_ids):
            claim = db.query(CouponClaim).filter_by(id=claim_id).populate_existing().with_for_update().first()
            if not claim or claim.used_at or claim.reserved_checkout_id != orders[0].checkout_id:
                raise BusinessException(message='订单优惠券占用状态已变化，请刷新后联系商家处理')
            claim.used_at = now
            claim.reserved_checkout_id = None
        for order in orders:
            order.status = 'paid'
            order.paid_at = now
            product = db.get(Product, order.product_id)
            notify_order_paid(db, order, product.name if product else '商品')
        db.flush()
        for product_id in sorted({order.product_id for order in orders}):
            sync_product_after_sale_risk(db, product_id)
        db.commit()
        return orders
    except Exception:
        db.rollback()
        raise


def expire_unpaid_orders(db, now=None, user_id=None):
    now = now or datetime.now()
    query = db.query(Order.id).filter(
        Order.status == 'unpaid', Order.payment_deadline_at <= now,
    )
    if user_id is not None:
        query = query.filter(Order.buyer_user_id == user_id)
    ids = [row[0] for row in query.order_by(Order.id)]
    handled = set()
    changed = 0
    try:
        for order_id in ids:
            if order_id in handled:
                continue
            orders = checkout_orders(db, order_id)
            handled.update(order.id for order in orders)
            if all(order.status == 'unpaid' for order in orders):
                _cancel_locked(db, orders)
                changed += len(orders)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return changed


def review_deadline(db, order, days=None):
    base = order.received_at or order.update_time or order.create_time
    return base + timedelta(days=days if days is not None else settings_data(db, 'order')['review_expire_days']) if base else None
