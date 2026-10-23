"""真实调用购物 API，验证同批付款/超时取消不会重复扣库存或丢失优惠券。"""
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api import customer_store as api
from app.common.exceptions import BusinessException
from app.database import Base
from app.models import User, Product, Order, CustomerAddress, StaffInboxEvent
from app.models.mall import MallContent, CouponClaim, OrderPromotion
from app.services.mall_service import expire_shipped_orders
from app.services.order_lifecycle_service import expire_unpaid_orders, pay_checkout, cancel_checkout
from app.services.overview_service import get_overview
from app.schemas.ecommerce import ProductListingUpdate
from app.services.ecommerce_service import update_product_listing


@pytest.fixture()
def shop():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    with Session(engine, autoflush=False) as db:
        buyer = User(username='buyer', name='Buyer', role='customer', password='test', status=1)
        other = User(username='other', name='Other', role='customer', password='test', status=1)
        product = Product(name='Phone', category='Digital', description='', price=100, stock=8, shelf_status='on_sale', review_status='normal', variant_name='Capacity', variants=[
            {'key': '256', 'name': '256GB', 'price': 100, 'stock': 5},
            {'key': '512', 'name': '512GB', 'price': 150, 'stock': 3},
        ])
        db.add_all([buyer, other, product]); db.flush()
        address = CustomerAddress(user_id=buyer.id, receiver_name='Buyer', phone='13456789010', province='A', city='B', district='C', detail='D')
        coupon = MallContent(kind='coupons', name='满100减20', enabled=True, sort_order=0, data={
            'discount': 20, 'min_amount': 100, 'quantity': 100,
            'starts_at': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
        })
        db.add_all([address, coupon]); db.flush()
        claim = CouponClaim(user_id=buyer.id, coupon_id=coupon.id)
        db.add(claim); db.commit()
        yield SimpleNamespace(db=db, buyer=buyer, other=other, product=product, address=address, coupon=coupon, claim=claim)
    engine.dispose()


def buy(shop, key='512', quantity=1, coupon=True):
    response = api.buy_now(api.BuyNowRequest(product_id=shop.product.id, variant_key=key, quantity=quantity,
        address_id=shop.address.id, coupon_claim_id=shop.claim.id if coupon else None), shop.buyer, shop.db)
    return shop.db.get(Order, response.data['order']['id'])


def grouped(shop):
    for key in ('256', '512'):
        api.add_cart_item(api.CartItemCreate(product_id=shop.product.id, variant_key=key), shop.buyer, shop.db)
    ids = [item['id'] for item in api.get_cart(shop.buyer, shop.db).data['list']]
    data = api.checkout(api.CheckoutRequest(address_id=shop.address.id, item_ids=ids, coupon_claim_id=shop.claim.id), shop.buyer, shop.db).data
    return [shop.db.get(Order, row['id']) for row in data['list']]


def test_buy_now_waits_for_payment_and_reserves_selected_sku(shop):
    order = buy(shop, quantity=2)
    assert order.status == 'unpaid' and order.variant_key == '512'
    assert float(order.amount) == 280
    assert order.payment_deadline_at > datetime.now() + timedelta(minutes=29)
    assert shop.product.variants[1]['stock'] == 1 and shop.product.stock == 6
    assert shop.db.query(StaffInboxEvent).count() == 0
    assert get_overview(shop.db).cards.total_amount == 0


def test_grouped_payment_is_atomic_and_idempotent(shop):
    orders = grouped(shop)
    stock = shop.product.stock
    assert len({order.checkout_id for order in orders}) == 1
    assert sum(float(order.amount) for order in orders) == 230
    pay_checkout(shop.db, orders[0].id, shop.buyer.id)
    assert all(order.status == 'paid' and order.paid_at for order in orders)
    notices = shop.db.query(StaffInboxEvent).count()
    pay_checkout(shop.db, orders[1].id, shop.buyer.id)
    assert shop.db.query(StaffInboxEvent).count() == notices
    assert shop.product.stock == stock
    assert get_overview(shop.db).cards.total_amount == 230
    with pytest.raises(BusinessException):
        cancel_checkout(shop.db, orders[0].id, shop.buyer.id)


def test_expiry_restores_all_skus_and_coupon_exactly_once(shop):
    orders = grouped(shop)
    assert shop.claim.reserved_checkout_id and shop.claim.used_at is None
    future = datetime.now() + timedelta(hours=1)
    assert expire_unpaid_orders(shop.db, future) == 2
    assert all(order.status == 'cancelled' for order in orders)
    assert shop.product.stock == 8 and [v['stock'] for v in shop.product.variants] == [5, 3]
    assert shop.claim.used_at is None
    assert expire_unpaid_orders(shop.db, future) == 0
    assert shop.product.stock == 8
    assert buy(shop).status == 'unpaid'  # 原券已释放，可以再次用于结算。


def test_pay_at_deadline_cancels_instead_of_charging(shop):
    order = buy(shop)
    with pytest.raises(BusinessException):
        pay_checkout(shop.db, order.id, shop.buyer.id, now=order.payment_deadline_at)
    assert order.status == 'cancelled' and order.paid_at is None
    assert shop.product.stock == 8 and shop.claim.used_at is None


def test_manual_cancel_and_ownership(shop):
    order = buy(shop)
    with pytest.raises(BusinessException):
        pay_checkout(shop.db, order.id, shop.other.id)
    with pytest.raises(BusinessException):
        cancel_checkout(shop.db, order.id, shop.other.id)
    assert order.status == 'unpaid'
    cancel_checkout(shop.db, order.id, shop.buyer.id)
    cancel_checkout(shop.db, order.id, shop.buyer.id)
    assert shop.product.stock == 8 and shop.claim.used_at is None


def test_failed_checkout_rolls_back_reserved_stock(shop):
    with pytest.raises(BusinessException):
        api.buy_now(api.BuyNowRequest(product_id=shop.product.id, variant_key='512', address_id=shop.address.id,
            coupon_claim_id=9999), shop.buyer, shop.db)
    assert shop.db.query(Order).count() == 0
    assert shop.product.stock == 8 and shop.product.variants[1]['stock'] == 3


def test_cart_can_change_and_merge_sku_without_reserving_inventory(shop):
    for key in ('256', '512'):
        api.add_cart_item(api.CartItemCreate(product_id=shop.product.id, variant_key=key), shop.buyer, shop.db)
    rows = api.get_cart(shop.buyer, shop.db).data['list']
    source = next(row for row in rows if row['product']['selected_variant']['key'] == '256')
    api.change_cart_variant(source['id'], api.CartVariantUpdate(variant_key='512'), shop.buyer, shop.db)
    result = api.get_cart(shop.buyer, shop.db).data['list']
    assert len(result) == 1 and result[0]['quantity'] == 2
    assert result[0]['product']['selected_variant']['key'] == '512'
    assert shop.product.stock == 8


def test_reserved_sku_cannot_be_deleted_while_order_unpaid(shop):
    buy(shop)
    with pytest.raises(BusinessException):
        update_product_listing(shop.db, shop.product.id, ProductListingUpdate(
            name='Phone', category='Digital', price=100, stock=5, discount_percent=0,
            variant_name='Capacity', variants=[shop.product.variants[0]],
        ))


def test_auto_receive_and_review_deadline_use_actual_receipt_time(shop):
    order = buy(shop)
    pay_checkout(shop.db, order.id, shop.buyer.id)
    order.status = 'shipped'
    order.shipped_at = datetime.now() - timedelta(days=8)
    shop.db.commit()
    assert expire_shipped_orders(shop.db)
    assert order.status == 'completed' and order.received_at > datetime.now() - timedelta(minutes=1)
    order.received_at = datetime.now() - timedelta(days=8)
    order.update_time = datetime.now()  # 其他更新时间不能延长评价资格。
    shop.db.commit()
    with pytest.raises(BusinessException):
        api.create_order_review(order.id, api.CustomerReviewCreate(rating=5, content='Good'), shop.buyer, shop.db)


def test_active_after_sale_pauses_auto_receive(shop):
    from app.schemas.after_sale import CustomerAfterSaleCreate
    from app.models import AfterSaleRequest
    order = buy(shop)
    pay_checkout(shop.db, order.id, shop.buyer.id)
    order.status = 'shipped'
    order.shipped_at = datetime.now() - timedelta(days=8)
    shop.db.commit()
    response = api.create_customer_after_sale(order.id, CustomerAfterSaleCreate(service_type='refund', reason='Issue'), shop.buyer, shop.db)
    assert not expire_shipped_orders(shop.db)
    assert order.status == 'shipped' and order.received_at is None
    shop.db.get(AfterSaleRequest, response.data['id']).status = 'rejected'
    shop.db.commit()
    assert expire_shipped_orders(shop.db) and order.status == 'completed'


def test_ai_order_configuration_changes_real_payment_deadline(shop):
    from app.services.mall_agent_service import build_management_actions
    from app.services.action_service import execute_actions
    admin = User(username='admin', name='Admin', role='admin', password='test', status=1)
    shop.db.add(admin); shop.db.commit()
    actions = build_management_actions(shop.db, admin.id, {'message': '调整未付款期限', 'changes': [
        {'resource': 'settings-order', 'id': None, 'patch': {'unpaid_timeout_minutes': 5}},
    ]})
    execute_actions(shop.db, actions, {'user_id': admin.id})
    now = datetime.now()
    order = buy(shop)
    assert now + timedelta(minutes=4, seconds=59) < order.payment_deadline_at < now + timedelta(minutes=5, seconds=2)
