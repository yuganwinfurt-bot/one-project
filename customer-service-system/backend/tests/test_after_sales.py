"""退款、退货和换货完整流程回归；全部使用临时内存库。"""
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api import customer_store as customer, ecommerce as staff_api
from app.common.exceptions import BusinessException
from app.database import Base
from app.models import (
    AfterSaleMessage, AfterSaleRequest, AlertNotification, CustomerAddress,
    Order, Product, StaffInboxEvent, User,
)
from app.schemas.after_sale import (
    AfterSaleExchangeShipmentUpdate, AfterSaleMessageCreate, AfterSaleProcess,
    AfterSaleReturnShipmentUpdate, CustomerAfterSaleCreate, CustomerAfterSaleServiceRating,
)
from app.services import ecommerce_service
from app.services.after_sale_service import completion_blocked_reason


@pytest.fixture()
def shop():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        buyer = User(username="buyer", name="买家", password="test", role="customer")
        other = User(username="other", name="其他买家", password="test", role="customer")
        staff = User(username="staff", name="客服", password="test", role="user")
        product = Product(name="回归商品", category="类目", description="商品", price=59, stock=10)
        db.add_all([buyer, other, staff, product])
        db.flush()
        order = Order(order_no="RETURN-TEST", buyer_user_id=buyer.id, buyer_name=buyer.name,
                      product_id=product.id, quantity=1, amount=59, status="shipped", tracking_no="ORIGINAL-001")
        address = CustomerAddress(user_id=buyer.id, receiver_name="收货人", phone="13456789010",
                                  province="广西", city="桂林", district="临桂", detail="测试地址")
        db.add_all([order, address])
        db.commit()
        yield SimpleNamespace(db=db, buyer=buyer, other=other, staff=staff, product=product, order=order, address=address)
    engine.dispose()


def apply(shop, kind="refund"):
    result = customer.create_customer_after_sale(shop.order.id, CustomerAfterSaleCreate(
        service_type=kind, reason="产品问题", description="说明",
        exchange_address_id=shop.address.id if kind == "exchange" else None,
    ), shop.buyer, shop.db)
    return shop.db.get(AfterSaleRequest, result.data["id"])


def process(shop, record, action, note=None):
    return staff_api.process_after_sale(record.id, AfterSaleProcess(action=action, admin_note=note), shop.staff, shop.db)


def return_item(shop, record):
    return customer.submit_customer_return_shipment(record.id, AfterSaleReturnShipmentUpdate(
        return_tracking_no="RETURN-002"), shop.buyer, shop.db)


def exchange_item(shop, record):
    return staff_api.submit_after_sale_exchange_shipment(record.id, AfterSaleExchangeShipmentUpdate(
        exchange_tracking_no="EXCHANGE-003"), shop.staff, shop.db)


@pytest.mark.parametrize("kind,level", [("refund", "critical"), ("return", "warning"), ("exchange", "warning")])
def test_new_application_visible_before_first_reply_and_notifies_staff(shop, kind, level):
    record = apply(shop, kind)
    inbox = customer.get_customer_messages(shop.buyer, shop.db).data
    assert inbox["list"][0]["after_sale_id"] == record.id
    assert inbox["list"][0]["status"] == "pending"
    assert inbox["unread_count"] == 0
    assert shop.db.query(AlertNotification).one().level == level
    assert shop.db.query(StaffInboxEvent).one().target_id == record.id
    with pytest.raises(BusinessException, match="已有售后"):
        apply(shop, kind)
    assert shop.db.query(AlertNotification).count() == 1


def test_refund_completes_without_shipping_and_closes_both_channels(shop):
    record = apply(shop)
    process(shop, record, "approve")
    assert completion_blocked_reason(record) == ""
    process(shop, record, "complete")
    assert record.status == "completed"
    assert record.order.status == "shipped"  # 售后完成不等于买家收货
    assert customer.get_customer_orders(shop.buyer, shop.db).data["list"][0]["after_sale"]["conversation_closed"]
    with pytest.raises(BusinessException, match="关闭"):
        customer.create_customer_after_sale_message(record.id, AfterSaleMessageCreate(content="test"), shop.buyer, shop.db)
    with pytest.raises(BusinessException, match="关闭"):
        staff_api.create_after_sale_message(record.id, AfterSaleMessageCreate(content="test"), shop.staff, shop.db)
    customer.rate_customer_after_sale_service(record.id, CustomerAfterSaleServiceRating(rating=4), shop.buyer, shop.db)
    with pytest.raises(BusinessException, match="已评价"):
        customer.rate_customer_after_sale_service(record.id, CustomerAfterSaleServiceRating(rating=1), shop.buyer, shop.db)
    with pytest.raises(BusinessException):
        customer.confirm_order_received(shop.order.id, shop.buyer, shop.db)
    assert ecommerce_service.get_order_detail(shop.db, shop.order.id).order.after_sale_status == "completed"


def test_return_requires_approval_and_buyer_tracking_then_merchant_finishes(shop):
    record = apply(shop, "return")
    with pytest.raises(BusinessException, match="同意"):
        return_item(shop, record)
    with pytest.raises(BusinessException, match="同意"):
        process(shop, record, "complete")
    process(shop, record, "approve")
    with pytest.raises(BusinessException, match="寄回"):
        process(shop, record, "complete")
    return_item(shop, record)
    with pytest.raises(BusinessException, match="已提交"):
        return_item(shop, record)
    listing = ecommerce_service.list_orders(shop.db, 1, 10).list[0]
    assert listing.after_sale["return_shipped"] is True
    assert listing.return_tracking_no == "RETURN-002"
    assert listing.after_sale_service_type == "return"
    with pytest.raises(BusinessException, match="换货申请"):
        exchange_item(shop, record)
    process(shop, record, "complete")
    assert record.status == "completed"
    assert record.return_tracking_no == "RETURN-002"
    assert record.exchange_tracking_no is None
    with pytest.raises(BusinessException):
        process(shop, record, "complete")


def test_exchange_requires_both_tracking_numbers_and_buyer_receipt_before_closing(shop):
    record = apply(shop, "exchange")
    assert "测试地址" in record.exchange_shipping_address
    process(shop, record, "approve")
    with pytest.raises(BusinessException, match="寄回"):
        exchange_item(shop, record)
    return_item(shop, record)
    exchange_item(shop, record)
    assert shop.order.tracking_no == "ORIGINAL-001"
    assert shop.order.status == "shipped"
    with pytest.raises(BusinessException, match="确认收到"):
        process(shop, record, "complete")
    with pytest.raises(BusinessException, match="已有售后"):
        ecommerce_service.ship_order(shop.db, shop.order.id, "WRONG")
    customer.confirm_order_received(shop.order.id, shop.buyer, shop.db)
    assert record.status == "approved"  # 买家收货后由商家右键完成售后
    assert shop.order.status == "completed"
    application = customer.get_customer_after_sale_messages(record.id, shop.buyer, shop.db).data["application"]
    assert application["completion_blocked_reason"] == ""
    assert not application["can_confirm_exchange_received"]
    process(shop, record, "complete")
    detail = ecommerce_service.get_order_detail(shop.db, shop.order.id).order
    assert detail.exchange_tracking_no == "EXCHANGE-003"
    assert detail.return_tracking_no == "RETURN-002"
    assert detail.after_sale["status"] == "completed"
    assert detail.after_sale["order_status"] == "completed"
    assert any("评分" in msg.content for msg in shop.db.query(AfterSaleMessage).all())


def test_rejection_preserves_result_closes_channel_and_allows_new_application(shop):
    record = apply(shop)
    with pytest.raises(BusinessException, match="拒绝原因"):
        process(shop, record, "reject")
    process(shop, record, "reject", "不符合条件")
    assert record.status == "rejected"
    with pytest.raises(BusinessException, match="关闭"):
        customer.create_customer_after_sale_message(record.id, AfterSaleMessageCreate(content="test"), shop.buyer, shop.db)
    with pytest.raises(BusinessException, match="关闭"):
        staff_api.create_after_sale_message(record.id, AfterSaleMessageCreate(content="test"), shop.staff, shop.db)
    customer.rate_customer_after_sale_service(record.id, CustomerAfterSaleServiceRating(rating=2), shop.buyer, shop.db)
    second = apply(shop, "return")
    assert second.id != record.id
    detail = ecommerce_service.get_order_detail(shop.db, shop.order.id).order
    assert detail.after_sale["id"] == second.id
    assert detail.after_sale_service_type == "return"
    assert record.status == "rejected"


@pytest.mark.parametrize("kind", ["return", "exchange"])
def test_unshipped_order_uses_refund_only(shop, kind):
    shop.order.status = "paid"
    shop.db.commit()
    with pytest.raises(BusinessException, match="未发货"):
        apply(shop, kind)
    assert shop.db.query(AfterSaleRequest).count() == 0


def test_active_after_sale_blocks_normal_shipping_and_receipt(shop):
    record = apply(shop, "return")
    with pytest.raises(BusinessException, match="售后"):
        ecommerce_service.ship_order(shop.db, shop.order.id, "OTHER")
    with pytest.raises(BusinessException, match="售后"):
        customer.confirm_order_received(shop.order.id, shop.buyer, shop.db)
    with pytest.raises(BusinessException, match="结束"):
        customer.rate_customer_after_sale_service(record.id, CustomerAfterSaleServiceRating(rating=5), shop.buyer, shop.db)


def test_legacy_shipped_flag_without_tracking_can_be_repaired(shop):
    record = apply(shop, "return")
    process(shop, record, "approve")
    record.return_shipped = True
    record.return_tracking_no = None
    shop.db.commit()
    assert completion_blocked_reason(record)
    return_item(shop, record)
    assert record.return_tracking_no == "RETURN-002"
    assert completion_blocked_reason(record) == ""


def test_legacy_prematurely_completed_exchange_can_still_confirm_receipt(shop):
    record = apply(shop, "exchange")
    record.status = "completed"
    record.return_shipped = True
    record.return_tracking_no = "OLD-RETURN"
    record.exchange_tracking_no = "OLD-EXCHANGE"
    shop.db.commit()
    application = customer.get_customer_after_sale_messages(record.id, shop.buyer, shop.db).data["application"]
    assert application["can_confirm_exchange_received"]
    customer.confirm_order_received(shop.order.id, shop.buyer, shop.db)
    assert shop.order.status == "completed"
    assert record.status == "completed"


def test_order_list_counts_orders_and_only_uses_latest_case(shop):
    rejected = apply(shop)
    process(shop, rejected, "reject", "重新申请")
    latest = apply(shop, "return")
    second = Order(order_no="SECOND-ORDER", buyer_user_id=shop.other.id, buyer_name=shop.other.name,
                   product_id=shop.product.id, quantity=1, amount=59, status="completed")
    shop.db.add(second)
    shop.db.commit()
    page = ecommerce_service.list_orders(shop.db, 1, 10)
    assert page.total == 2
    assert len(page.list) == 2
    assert next(item for item in page.list if item.id == shop.order.id).after_sale["id"] == latest.id
    assert next(item for item in page.list if item.id == second.id).after_sale is None


@pytest.mark.parametrize("operation", ["read", "send", "return", "rating", "receive"])
def test_customer_cannot_operate_another_buyers_case(shop, operation):
    record = apply(shop, "return")
    actions = {
        "read": lambda: customer.get_customer_after_sale_messages(record.id, shop.other, shop.db),
        "send": lambda: customer.create_customer_after_sale_message(record.id, AfterSaleMessageCreate(content="bad"), shop.other, shop.db),
        "return": lambda: customer.submit_customer_return_shipment(record.id, AfterSaleReturnShipmentUpdate(return_tracking_no="bad"), shop.other, shop.db),
        "rating": lambda: customer.rate_customer_after_sale_service(record.id, CustomerAfterSaleServiceRating(rating=1), shop.other, shop.db),
        "receive": lambda: customer.confirm_order_received(shop.order.id, shop.other, shop.db),
    }
    with pytest.raises(BusinessException) as exc:
        actions[operation]()
    assert exc.value.code == 404
