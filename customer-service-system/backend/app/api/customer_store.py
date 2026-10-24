"""普通用户的购物车、收藏、收货地址与个人订单接口。"""

import secrets
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import func
from sqlalchemy.orm import object_session
from app.services.mall_service import price_orders, promotion_data, settings_data
from app.services.order_lifecycle_service import (
    cancel_checkout, expire_unpaid_orders, pay_checkout, payment_deadline, review_deadline,
)
from pydantic import BaseModel, Field, field_validator
from app.common.exceptions import BusinessException
from app.common.response import Response
from app.dependencies.auth import CurrentUser, DbSession
from app.models.alert_notification import AlertNotification
from app.models.order import Order
from app.models.after_sale import AfterSaleMessage, AfterSaleRequest
from app.models.staff_inbox import StaffInboxEvent
from app.models.product import Product
from app.models.review import Review
from app.models.review_reply import CustomerReviewReply
from app.models.shopping import (
    CartItem,
    CartVariantItem,
    CustomerAddress,
    CustomerMessage,
    CustomerShipmentMessage,
    FavoriteProduct,
)
from app.models.user import User
from app.schemas.after_sale import (
    AfterSaleMessageCreate,
    AfterSaleReturnShipmentUpdate,
    CustomerAfterSaleServiceRating,
    CustomerAfterSaleCreate,
)
from app.services.after_sale_service import CLOSED_STATUSES, after_sale_flow_data, after_sale_options
from app.services.after_sale_risk_service import sync_product_after_sale_risk
from app.services.inventory_service import sync_product_inventory
from app.services.product_variant_service import (
    adjust_product_stock,
    ensure_product_available,
    selected_variant_data,
    variant_snapshot,
)
from app.services.staff_inbox_service import notify_order_paid, resolve_order_paid_notice
from app.models.inventory import CustomerRestockMessage
from app.models.community import DirectMessage, DirectConversation, ReviewComment, ReviewReplyNotification
from app.services.community_service import add_review_comment, comment_data, direct_inbox, notification_data, review_owner_id

router = APIRouter(prefix="/customer", tags=["用户购物"])


class CartItemCreate(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(default=1, ge=1, le=99)
    variant_key: str | None = Field(default=None, max_length=80)


class CartQuantityUpdate(BaseModel):
    quantity: int = Field(ge=1, le=99)


class CartVariantUpdate(BaseModel):
    variant_key: str = Field(min_length=1, max_length=80)


class AddressPayload(BaseModel):
    receiver_name: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=6, max_length=30)
    province: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)
    district: str = Field(min_length=1, max_length=50)
    detail: str = Field(min_length=1, max_length=200)
    is_default: bool = False

    @field_validator("receiver_name", "phone", "province", "city", "district", "detail")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("此项不能为空")
        return value


class CheckoutRequest(BaseModel):
    address_id: int = Field(ge=1)
    item_ids: list[int | str] = Field(min_length=1, max_length=100)
    coupon_claim_id: int | None = Field(default=None, ge=1)


class BuyNowRequest(BaseModel):
    coupon_claim_id: int | None = Field(default=None, ge=1)
    product_id: int = Field(ge=1)
    variant_key: str | None = Field(default=None, max_length=80)
    quantity: int = Field(default=1, ge=1, le=99)
    address_id: int = Field(ge=1)


class CustomerReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("评价内容不能为空")
        return value


class CustomerReviewReplyPayload(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("回复内容不能为空")
        return value


def _require_customer(user):
    if user.role != "customer":
        raise BusinessException(message="仅注册用户可以使用购物功能", code=403)
    return user


def _product_data(product: Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "description": product.description,
        "image_url": product.image_url,
        "price": float(product.price),
        "original_price": float(product.original_price) if product.original_price is not None else None,
        "variant_name": product.variant_name,
        "variants": product.variants or [],
        "stock": product.stock,
        "shelf_status": product.shelf_status,
        "review_status": product.review_status,
    }


def _address_data(address: CustomerAddress) -> dict:
    return {
        "id": address.id,
        "receiver_name": address.receiver_name,
        "phone": address.phone,
        "province": address.province,
        "city": address.city,
        "district": address.district,
        "detail": address.detail,
        "is_default": address.is_default,
    }


def _order_data(order: Order, product: Product | None = None) -> dict:
    return {
        **promotion_data(object_session(order), order.id),
        "id": order.id,
        "order_no": order.order_no,
        "product_id": order.product_id,
        "variant_key": order.variant_key or "",
        "variant_name": order.variant_name,
        "product_name": product.name if product else None,
        "image_url": product.image_url if product else None,
        "buyer_name": order.buyer_name,
        "quantity": order.quantity,
        "amount": float(order.amount),
        "status": order.status,
        "checkout_id": order.checkout_id,
        "payment_deadline_at": order.payment_deadline_at.strftime("%Y-%m-%d %H:%M:%S") if order.payment_deadline_at else None,
        "paid_at": order.paid_at.strftime("%Y-%m-%d %H:%M:%S") if order.paid_at else None,
        "shipping_address": order.shipping_address,
        "tracking_no": order.tracking_no,
        "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S") if order.create_time else None,
        "after_sale": None,
    }


def _after_sale_data(record: AfterSaleRequest) -> dict:
    return {
        **after_sale_flow_data(record),
        "id": record.id,
        "order_id": record.order_id,
        "order_no": record.order_no,
        "product_id": record.product_id,
        "product_name": record.product_name,
        "service_type": record.service_type,
        "reason": record.reason,
        "description": record.description,
        "return_shipped": record.return_shipped,
        "return_tracking_no": record.return_tracking_no,
        "exchange_shipping_address": record.exchange_shipping_address,
        "exchange_tracking_no": record.exchange_tracking_no,
        "status": record.status,
        "admin_note": record.admin_note,
        "service_rating": record.service_rating,
        "service_feedback": record.service_feedback,
        "create_time": record.create_time.strftime("%Y-%m-%d %H:%M:%S") if record.create_time else None,
        "processed_at": record.processed_at.strftime("%Y-%m-%d %H:%M:%S") if record.processed_at else None,
    }


def _ensure_product_available(product: Product, quantity: int = 1, variant_key: str | None = None):
    return ensure_product_available(product, quantity, variant_key)


def _make_default(db, user_id: int, address_id: int) -> None:
    db.query(CustomerAddress).filter(CustomerAddress.user_id == user_id).update(
        {CustomerAddress.is_default: False}, synchronize_session=False
    )
    address = db.query(CustomerAddress).filter(
        CustomerAddress.id == address_id,
        CustomerAddress.user_id == user_id,
    ).first()
    if address:
        address.is_default = True


@router.get("/cart")
def get_cart(user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    rows = (
        db.query(CartItem, Product)
        .join(Product, Product.id == CartItem.product_id)
        .filter(CartItem.user_id == user.id)
        .order_by(CartItem.id.desc())
        .all()
    )
    variant_rows = (
        db.query(CartVariantItem, Product)
        .join(Product, Product.id == CartVariantItem.product_id)
        .filter(CartVariantItem.user_id == user.id)
        .order_by(CartVariantItem.id.desc())
        .all()
    )
    items = [
        {
            "id": item.id,
            "quantity": item.quantity,
            "product": {
                **_product_data(product),
                # 商品若在加入购物车后才改成多规格，需要用户重新选 SKU。
                "needs_variant_selection": bool(product.variants),
            },
        }
        for item, product in rows
    ]
    for item, product in variant_rows:
        product_data = _product_data(product)
        try:
            product_data["selected_variant"] = selected_variant_data(product, item.variant_key)
        except BusinessException:
            # 后台修改或移除了 SKU 时仍展示这条购物车记录，允许用户移除后重新选规格。
            product_data["selected_variant"] = {
                "key": item.variant_key,
                "name": "规格已失效，请重新选择",
                "variant_name": product.variant_name or "规格",
                "price": float(product.price),
                "stock": 0,
                "unavailable": True,
            }
        items.append({"id": f"sku-{item.id}", "quantity": item.quantity, "product": product_data})
    return Response.success(data={"list": items})


@router.post("/cart")
def add_cart_item(payload: CartItemCreate, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    variant = _ensure_product_available(product, payload.quantity, payload.variant_key)
    if variant:
        item = db.query(CartVariantItem).filter_by(
            user_id=user.id, product_id=product.id, variant_key=variant["key"]
        ).first()
        quantity = (item.quantity if item else 0) + payload.quantity
        _ensure_product_available(product, quantity, variant["key"])
        if item:
            item.quantity = quantity
        else:
            db.add(CartVariantItem(
                user_id=user.id, product_id=product.id,
                variant_key=variant["key"], quantity=quantity,
            ))
        db.commit()
        return Response.success(message="已加入购物车")

    item = db.query(CartItem).filter_by(user_id=user.id, product_id=product.id).first()
    quantity = (item.quantity if item else 0) + payload.quantity
    _ensure_product_available(product, quantity)
    if item:
        item.quantity = quantity
    else:
        db.add(CartItem(user_id=user.id, product_id=product.id, quantity=quantity))
    db.commit()
    return Response.success(message="已加入购物车")


@router.put("/cart/{item_id}")
def update_cart_item(item_id: str, payload: CartQuantityUpdate, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    if item_id.startswith("sku-"):
        try:
            row_id = int(item_id[4:])
        except ValueError:
            raise BusinessException(message="购物车商品编号无效")
        item = db.query(CartVariantItem).filter_by(id=row_id, user_id=user.id).first()
        variant_key = item.variant_key if item else None
    else:
        try:
            row_id = int(item_id)
        except ValueError:
            raise BusinessException(message="购物车商品编号无效")
        item = db.query(CartItem).filter_by(id=row_id, user_id=user.id).first()
        variant_key = None
    if not item:
        raise BusinessException(message="购物车商品不存在")
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    _ensure_product_available(product, payload.quantity, variant_key)
    item.quantity = payload.quantity
    db.commit()
    return Response.success(message="购物车数量已更新")


@router.delete("/cart/{item_id}")
def delete_cart_item(item_id: str, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    if item_id.startswith("sku-"):
        try:
            row_id = int(item_id[4:])
        except ValueError:
            raise BusinessException(message="购物车商品编号无效")
        item = db.query(CartVariantItem).filter_by(id=row_id, user_id=user.id).first()
    else:
        try:
            row_id = int(item_id)
        except ValueError:
            raise BusinessException(message="购物车商品编号无效")
        item = db.query(CartItem).filter_by(id=row_id, user_id=user.id).first()
    if not item:
        raise BusinessException(message="购物车商品不存在")
    db.delete(item)
    db.commit()
    return Response.success(message="已从购物车移除")


@router.put("/cart/{item_id}/variant")
def change_cart_variant(item_id: str, payload: CartVariantUpdate, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    variant_line = item_id.startswith("sku-")
    try:
        row_id = int(item_id[4:] if variant_line else item_id)
    except ValueError:
        raise BusinessException(message="购物车商品编号无效")
    model = CartVariantItem if variant_line else CartItem
    item = db.query(model).filter_by(id=row_id, user_id=user.id).with_for_update().first()
    if not item:
        raise BusinessException(message="购物车商品不存在")
    product = db.query(Product).filter_by(id=item.product_id).with_for_update().first()
    if not product:
        raise BusinessException(message="商品不存在")
    _ensure_product_available(product, item.quantity, payload.variant_key)
    target = db.query(CartVariantItem).filter_by(user_id=user.id, product_id=product.id, variant_key=payload.variant_key).with_for_update().first()
    if target and variant_line and target.id == item.id:
        return Response.success(data={"id": item_id}, message="规格未变化")
    quantity = item.quantity + (target.quantity if target else 0)
    if quantity > 99:
        raise BusinessException(message="相同规格合并后的数量不能超过 99 件")
    _ensure_product_available(product, quantity, payload.variant_key)
    if target:
        target.quantity = quantity
    else:
        target = CartVariantItem(user_id=user.id, product_id=product.id, variant_key=payload.variant_key, quantity=quantity)
        db.add(target)
    db.delete(item)
    db.commit()
    return Response.success(data={"id": f"sku-{target.id}"}, message="商品规格已更换")


@router.get("/favorites")
def get_favorites(user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    rows = (
        db.query(FavoriteProduct, Product)
        .join(Product, Product.id == FavoriteProduct.product_id)
        .filter(FavoriteProduct.user_id == user.id)
        .order_by(FavoriteProduct.id.desc())
        .all()
    )
    return Response.success(
        data={"list": [{"id": favorite.id, "restock_waiting": favorite.restock_waiting, "product": _product_data(product)} for favorite, product in rows]}
    )


@router.post("/favorites/{product_id}")
def add_favorite(product_id: int, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
    if not product:
        raise BusinessException(message="商品不存在")
    exists = db.query(FavoriteProduct).filter_by(user_id=user.id, product_id=product_id).first()
    if not exists:
        db.add(FavoriteProduct(user_id=user.id, product_id=product_id, restock_waiting=product.stock <= 0))
    elif product.stock <= 0:
        exists.restock_waiting = True
    db.commit()
    return Response.success(message="已加入收藏")


@router.delete("/favorites/{product_id}")
def delete_favorite(product_id: int, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    favorite = db.query(FavoriteProduct).filter_by(user_id=user.id, product_id=product_id).first()
    if favorite:
        db.delete(favorite)
        db.commit()
    return Response.success(message="已取消收藏")


@router.get("/messages")
def get_customer_messages(user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    price_messages = (
        db.query(CustomerMessage)
        .filter(CustomerMessage.user_id == user.id)
        .order_by(CustomerMessage.create_time.desc(), CustomerMessage.id.desc())
        .all()
    )
    shipment_messages = (
        db.query(CustomerShipmentMessage)
        .filter(CustomerShipmentMessage.user_id == user.id)
        .order_by(CustomerShipmentMessage.create_time.desc(), CustomerShipmentMessage.id.desc())
        .all()
    )
    after_sale_rows = (
        db.query(AfterSaleRequest, AfterSaleMessage)
        .outerjoin(AfterSaleMessage, AfterSaleRequest.id == AfterSaleMessage.after_sale_id)
        .filter(AfterSaleRequest.user_id == user.id)
        .order_by(func.coalesce(AfterSaleMessage.create_time, AfterSaleRequest.create_time).desc(), AfterSaleMessage.id.desc())
        .all()
    )
    unread_price_count = (
        db.query(CustomerMessage.id)
        .filter(CustomerMessage.user_id == user.id, CustomerMessage.is_read.is_(False))
        .count()
    )
    unread_shipment_count = (
        db.query(CustomerShipmentMessage.id)
        .filter(
            CustomerShipmentMessage.user_id == user.id,
            CustomerShipmentMessage.is_read.is_(False),
        )
        .count()
    )
    unread_after_sale_count = (
        db.query(AfterSaleMessage.id)
        .filter(
            AfterSaleMessage.user_id == user.id,
            AfterSaleMessage.sender_role != "customer",
            AfterSaleMessage.read_by_customer.is_(False),
        )
        .count()
    )
    messages = [
        {
            "id": f"price-{message.id}",
            "type": "price_drop",
            "product_id": message.product_id,
            "product_name": message.product_name,
            "previous_price": float(message.previous_price),
            "current_price": float(message.current_price),
            "is_read": message.is_read,
            "create_time": message.create_time.strftime("%Y-%m-%d %H:%M:%S")
            if message.create_time
            else None,
            "sort_id": message.id,
        }
        for message in price_messages
    ]
    messages.extend(
        {
            "id": f"shipment-{message.id}",
            "type": "shipment",
            "order_id": message.order_id,
            "order_no": message.order_no,
            "product_id": message.product_id,
            "product_name": message.product_name,
            "is_read": message.is_read,
            "create_time": message.create_time.strftime("%Y-%m-%d %H:%M:%S")
            if message.create_time
            else None,
            "sort_id": message.id,
        }
        for message in shipment_messages
    )
    conversations = {}
    for after_sale, message in after_sale_rows:
        conversation = conversations.setdefault(
            after_sale.id,
            {
                "id": f"after-sale-{after_sale.id}",
                "type": "after_sale_chat",
                "after_sale_id": after_sale.id,
                "order_no": after_sale.order_no,
                "product_name": after_sale.product_name,
                "service_type": after_sale.service_type,
                "status": after_sale.status,
                **after_sale_flow_data(after_sale),
                "preview": message.content if message else f"售后申请已提交：{after_sale.reason}，等待商家审核",
                "create_time": message.create_time.strftime("%Y-%m-%d %H:%M:%S")
                if message and message.create_time
                else after_sale.create_time.strftime("%Y-%m-%d %H:%M:%S") if after_sale.create_time else None,
                "unread_count": 0,
                "sort_id": message.id if message else after_sale.id,
            },
        )
        if message and message.sender_role != "customer" and not message.read_by_customer:
            conversation["unread_count"] += 1
    for conversation in conversations.values():
        conversation["is_read"] = conversation["unread_count"] == 0
        messages.append(conversation)
    private_conversations = direct_inbox(db, user)
    messages.extend(private_conversations)
    from app.models.customer_support import SupportConversation
    from app.services import customer_support_service as support
    support_unread = 0
    for conversation in db.query(SupportConversation).filter_by(user_id=user.id, after_sale_id=None).all():
        chat = support.rows(db, conversation)
        if not chat:
            continue
        unread = sum(not m.read_by_customer and m.sender_role != "customer" for m in chat)
        support_unread += unread
        messages.append({"id": f"support-{conversation.id}", "type": "support_chat", "support_conversation_id": conversation.id,
                         "title": conversation.title, "preview": chat[-1].content, "unread_count": unread, "is_read": not unread,
                         "create_time": chat[-1].create_time.strftime("%Y-%m-%d %H:%M:%S"), "sort_id": chat[-1].id})
    notifications = db.query(ReviewReplyNotification).filter_by(user_id=user.id).all()
    restock_notices = db.query(CustomerRestockMessage).filter_by(user_id=user.id).all()
    for record in restock_notices:
        messages.append({"id": f"restock-{record.id}", "type": "restock", "product_id": record.product_id,
                         "product_name": record.product_name, "stock": record.stock, "is_read": record.is_read,
                         "create_time": record.create_time.strftime("%Y-%m-%d %H:%M:%S"), "sort_id": record.id})
    for record in notifications:
        messages.append({**notification_data(record), "sort_id": record.id})
    messages.sort(
        key=lambda message: (message["create_time"] or "", message.get("sort_id", message.get("conversation_id", 0))),
        reverse=True,
    )
    for message in messages:
        message.pop("sort_id", None)
    return Response.success(
        data={
            "list": messages,
            "unread_count": unread_price_count + unread_shipment_count + unread_after_sale_count
            + sum(item["unread_count"] for item in private_conversations) + sum(not record.is_read for record in notifications)
            + sum(not record.is_read for record in restock_notices) + support_unread,
        }
    )


@router.post("/messages/read-all")
def mark_customer_messages_read(user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    updated_price = (
        db.query(CustomerMessage)
        .filter(CustomerMessage.user_id == user.id, CustomerMessage.is_read.is_(False))
        .update({CustomerMessage.is_read: True}, synchronize_session=False)
    )
    updated_shipments = (
        db.query(CustomerShipmentMessage)
        .filter(
            CustomerShipmentMessage.user_id == user.id,
            CustomerShipmentMessage.is_read.is_(False),
        )
        .update({CustomerShipmentMessage.is_read: True}, synchronize_session=False)
    )
    updated_after_sale = (
        db.query(AfterSaleMessage)
        .filter(
            AfterSaleMessage.user_id == user.id,
            AfterSaleMessage.sender_role != "customer",
            AfterSaleMessage.read_by_customer.is_(False),
        )
        .update({AfterSaleMessage.read_by_customer: True}, synchronize_session=False)
    )
    updated_private = db.query(DirectMessage).filter(
        DirectMessage.conversation_id.in_(db.query(DirectConversation.id).filter_by(customer_id=user.id)),
        DirectMessage.sender_id != user.id, DirectMessage.is_read.is_(False),
    ).update({DirectMessage.is_read: True}, synchronize_session=False)
    updated_replies = db.query(ReviewReplyNotification).filter_by(user_id=user.id, is_read=False).update(
        {ReviewReplyNotification.is_read: True}, synchronize_session=False
    )
    updated_restock = db.query(CustomerRestockMessage).filter_by(user_id=user.id, is_read=False).update(
        {CustomerRestockMessage.is_read: True}, synchronize_session=False
    )
    from app.models.customer_support import SupportConversation, SupportChatMessage
    updated_support = db.query(SupportChatMessage).filter(
        SupportChatMessage.conversation_id.in_(db.query(SupportConversation.id).filter_by(user_id=user.id)),
        SupportChatMessage.read_by_customer.is_(False),
    ).update({SupportChatMessage.read_by_customer: True}, synchronize_session=False)
    db.commit()
    return Response.success(
        message="消息已全部标为已读",
        data={"updated": updated_price + updated_shipments + updated_after_sale + updated_private + updated_replies + updated_restock + updated_support},
    )


@router.post("/messages/{message_type}/{message_id}/read")
def mark_customer_message_read(
    message_type: str, message_id: int, user: CurrentUser, db: DbSession
):
    user = _require_customer(user)
    if message_type == "price_drop":
        message = (
            db.query(CustomerMessage)
            .filter_by(id=message_id, user_id=user.id)
            .first()
        )
    elif message_type == "shipment":
        message = (
            db.query(CustomerShipmentMessage)
            .filter_by(id=message_id, user_id=user.id)
            .first()
        )
    elif message_type == "restock":
        message = db.query(CustomerRestockMessage).filter_by(id=message_id, user_id=user.id).first()
    elif message_type == "review_reply":
        message = db.query(ReviewReplyNotification).filter_by(id=message_id, user_id=user.id).first()
    else:
        raise BusinessException(message="不支持的消息类型")
    if not message:
        raise BusinessException(message="消息不存在", code=404)
    if not message.is_read:
        message.is_read = True
        db.commit()
    return Response.success(message="消息已读")


def _after_sale_message_data(message: AfterSaleMessage) -> dict:
    return {
        "id": message.id,
        "after_sale_id": message.after_sale_id,
        "sender_user_id": message.sender_user_id,
        "sender_role": message.sender_role,
        "sender_name": message.sender_name,
        "content": message.content,
        "create_time": message.create_time.strftime("%Y-%m-%d %H:%M:%S")
        if message.create_time
        else None,
    }


@router.get("/messages/after-sales/{after_sale_id}")
def get_customer_after_sale_messages(after_sale_id: int, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    after_sale = db.query(AfterSaleRequest).filter_by(id=after_sale_id, user_id=user.id).first()
    if not after_sale:
        raise BusinessException(message="售后申请不存在", code=404)
    messages = (
        db.query(AfterSaleMessage)
        .filter(AfterSaleMessage.after_sale_id == after_sale.id, AfterSaleMessage.user_id == user.id)
        .order_by(AfterSaleMessage.create_time.asc(), AfterSaleMessage.id.asc())
        .all()
    )
    unread_count = sum(
        1 for message in messages
        if message.sender_role != "customer" and not message.read_by_customer
    )
    for message in messages:
        if message.sender_role != "customer":
            message.read_by_customer = True
    if unread_count:
        db.commit()
    product = db.query(Product).filter(Product.id == after_sale.product_id).first()
    application = _after_sale_data(after_sale)
    from app.services import customer_support_service as support
    conversation = support.for_after_sale(db, after_sale) if after_sale.status not in CLOSED_STATUSES else None
    application.update(support.state(conversation))
    application["conversation_closed"] = bool(application.get("conversation_closed") or (conversation and conversation.closed))
    application.update(support.ai_state(db, conversation))
    db.commit()
    application["image_url"] = product.image_url if product else None
    return Response.success(
        data={
            "after_sale_id": after_sale.id,
            "order_no": after_sale.order_no,
            "product_name": after_sale.product_name,
            "application": application,
            "messages": [_after_sale_message_data(message) for message in messages],
            "unread_count": unread_count,
        }
    )


@router.post("/messages/after-sales/{after_sale_id}")
def create_customer_after_sale_message(
    after_sale_id: int,
    payload: AfterSaleMessageCreate,
    user: CurrentUser,
    db: DbSession,
):
    user = _require_customer(user)
    after_sale = db.query(AfterSaleRequest).filter_by(id=after_sale_id, user_id=user.id).with_for_update().first()
    if not after_sale:
        raise BusinessException(message="售后申请不存在", code=404)
    if after_sale.status in CLOSED_STATUSES:
        raise BusinessException(message="售后沟通通道已关闭")
    from app.services import customer_support_service as support
    conversation = support.for_after_sale(db, after_sale)
    conversation = support.get_conversation(db, conversation.id, user.id, lock=True)
    if conversation.closed:
        raise BusinessException(message="本次人工会话已结束，可发起新的客服咨询")
    message = AfterSaleMessage(
        after_sale_id=after_sale.id,
        user_id=user.id,
        sender_user_id=user.id,
        sender_role="customer",
        sender_name=user.name or user.username,
        content=payload.content,
        read_by_customer=True,
        read_by_staff=False,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    from app.services import customer_support_service as support
    conversation = support.for_after_sale(db, after_sale)
    ai_request = support.prepare_ai(db, conversation)
    db.commit()
    return Response.success(message="消息已发送", data={**_after_sale_message_data(message), "ai_pending": bool(ai_request)})


@router.post("/after-sales/{after_sale_id}/service-rating")
def rate_customer_after_sale_service(
    after_sale_id: int,
    payload: CustomerAfterSaleServiceRating,
    user: CurrentUser,
    db: DbSession,
):
    user = _require_customer(user)
    after_sale = db.query(AfterSaleRequest).filter_by(id=after_sale_id, user_id=user.id).with_for_update().first()
    if not after_sale:
        raise BusinessException(message="售后申请不存在", code=404)
    if after_sale.status not in CLOSED_STATUSES:
        raise BusinessException(message="售后结束后才能评价服务")
    if after_sale.service_rating is not None:
        raise BusinessException(message="售后服务已评价")

    after_sale.service_rating = payload.rating
    after_sale.service_feedback = payload.feedback
    db.commit()
    db.refresh(after_sale)
    return Response.success(
        message="感谢评价售后服务",
        data=_after_sale_data(after_sale),
    )


@router.get("/addresses")
def get_addresses(user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    addresses = (
        db.query(CustomerAddress)
        .filter_by(user_id=user.id)
        .order_by(CustomerAddress.is_default.desc(), CustomerAddress.id.desc())
        .all()
    )
    return Response.success(data={"list": [_address_data(address) for address in addresses]})


@router.post("/addresses")
def create_address(payload: AddressPayload, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    has_address = db.query(CustomerAddress.id).filter_by(user_id=user.id).first() is not None
    address = CustomerAddress(user_id=user.id, **payload.model_dump())
    if payload.is_default or not has_address:
        address.is_default = True
        db.add(address)
        db.flush()
        _make_default(db, user.id, address.id)
    else:
        db.add(address)
    db.commit()
    db.refresh(address)
    return Response.success(message="收货地址已保存", data=_address_data(address))


@router.put("/addresses/{address_id}")
def update_address(address_id: int, payload: AddressPayload, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    address = db.query(CustomerAddress).filter_by(id=address_id, user_id=user.id).first()
    if not address:
        raise BusinessException(message="收货地址不存在")
    was_default = address.is_default
    for field, value in payload.model_dump().items():
        setattr(address, field, value)
    if payload.is_default:
        _make_default(db, user.id, address.id)
    elif was_default:
        next_address = (
            db.query(CustomerAddress)
            .filter(CustomerAddress.user_id == user.id, CustomerAddress.id != address.id)
            .order_by(CustomerAddress.id.desc())
            .first()
        )
        if next_address:
            next_address.is_default = True
    db.commit()
    db.refresh(address)
    return Response.success(message="收货地址已更新", data=_address_data(address))


@router.delete("/addresses/{address_id}")
def delete_address(address_id: int, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    address = db.query(CustomerAddress).filter_by(id=address_id, user_id=user.id).first()
    if not address:
        raise BusinessException(message="收货地址不存在")
    was_default = address.is_default
    db.delete(address)
    if was_default:
        next_address = (
            db.query(CustomerAddress)
            .filter(CustomerAddress.user_id == user.id, CustomerAddress.id != address_id)
            .order_by(CustomerAddress.id.desc())
            .first()
        )
        if next_address:
            next_address.is_default = True
    db.commit()
    return Response.success(message="收货地址已删除")


@router.post("/orders")
def checkout(payload: CheckoutRequest, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    address = db.query(CustomerAddress).filter_by(id=payload.address_id, user_id=user.id).first()
    if not address:
        raise BusinessException(message="请先选择有效的收货地址")
    item_ids = [str(item_id) for item_id in payload.item_ids]
    if len(set(item_ids)) != len(item_ids):
        raise BusinessException(message="购物车商品不能重复提交")
    legacy_ids, variant_ids = [], []
    for item_id in item_ids:
        try:
            if item_id.startswith("sku-"):
                variant_ids.append(int(item_id[4:]))
            else:
                legacy_ids.append(int(item_id))
        except ValueError:
            raise BusinessException(message="购物车中有商品编号无效，请刷新后重试")
    legacy_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id, CartItem.id.in_(legacy_ids))
        .with_for_update()
        .all()
        if legacy_ids else []
    )
    variant_items = (
        db.query(CartVariantItem)
        .filter(CartVariantItem.user_id == user.id, CartVariantItem.id.in_(variant_ids))
        .with_for_update()
        .all()
        if variant_ids else []
    )
    cart_by_id = {
        str(item.id): (item, None)
        for item in legacy_items
    }
    cart_by_id.update({
        f"sku-{item.id}": (item, item.variant_key)
        for item in variant_items
    })
    if len(cart_by_id) != len(item_ids):
        raise BusinessException(message="部分购物车商品已不存在，请刷新后重试")
    cart_items = [cart_by_id[item_id] for item_id in item_ids]

    address_snapshot = f"{address.receiver_name}，{address.phone}，{address.province}{address.city}{address.district}{address.detail}"
    created_orders = []
    checkout_id = secrets.token_hex(16)
    deadline = payment_deadline(db)
    try:
        for item, variant_key in cart_items:
            product = (
                db.query(Product)
                .filter(Product.id == item.product_id)
                .with_for_update()
                .first()
            )
            if not product:
                raise BusinessException(message="购物车中有商品已不存在")
            variant = _ensure_product_available(product, item.quantity, variant_key)
            unit_price = Decimal(str(variant["price"] if variant else product.price))
            adjust_product_stock(product, -item.quantity, variant_key)
            order = Order(
                order_no=f"C{datetime.now():%y%m%d%H%M%S}{secrets.token_hex(3).upper()}",
                product_id=product.id,
                variant_key=variant_key or "",
                variant_name=variant_snapshot(product, variant),
                buyer_name=user.name or user.username,
                buyer_user_id=user.id,
                shipping_address=address_snapshot,
                quantity=item.quantity,
                amount=(unit_price * item.quantity).quantize(Decimal("0.01")),
                status="unpaid",
                checkout_id=checkout_id,
                payment_deadline_at=deadline,
            )
            db.add(order)
            db.delete(item)
            created_orders.append((order, product))
        price_orders(db, user, [order for order, _ in created_orders], payload.coupon_claim_id)
        for product_id in sorted({product.id for _, product in created_orders}):
            sync_product_after_sale_risk(db, product_id)
            sync_product_inventory(db, product_id)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return Response.success(
        message="订单已创建，请在付款截止时间前完成付款",
        data={"list": [_order_data(order, product) for order, product in created_orders]},
    )


@router.post("/orders/buy-now")
def buy_now(payload: BuyNowRequest, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    address = db.query(CustomerAddress).filter_by(
        id=payload.address_id,
        user_id=user.id,
    ).first()
    if not address:
        raise BusinessException(message="请先选择有效的收货地址")

    product = (
        db.query(Product)
        .filter(Product.id == payload.product_id)
        .with_for_update()
        .first()
    )
    if not product:
        raise BusinessException(message="商品不存在")
    variant = _ensure_product_available(product, payload.quantity, payload.variant_key)

    address_snapshot = f"{address.receiver_name}，{address.phone}，{address.province}{address.city}{address.district}{address.detail}"
    unit_price = Decimal(str(variant["price"] if variant else product.price))
    adjust_product_stock(product, -payload.quantity, payload.variant_key)
    order = Order(
        order_no=f"C{datetime.now():%y%m%d%H%M%S}{secrets.token_hex(3).upper()}",
        product_id=product.id,
        variant_key=payload.variant_key or "",
        variant_name=variant_snapshot(product, variant),
        buyer_name=user.name or user.username,
        buyer_user_id=user.id,
        shipping_address=address_snapshot,
        quantity=payload.quantity,
        amount=(unit_price * payload.quantity).quantize(Decimal("0.01")),
        status="unpaid",
        checkout_id=secrets.token_hex(16),
        payment_deadline_at=payment_deadline(db),
    )
    try:
        db.add(order)
        price_orders(db, user, [order], payload.coupon_claim_id)
        sync_product_after_sale_risk(db, product.id)
        sync_product_inventory(db, product.id)
        db.commit()
        db.refresh(order)
    except Exception:
        db.rollback()
        raise

    return Response.success(
        message="订单已创建，请在付款截止时间前完成付款",
        data={"order": _order_data(order, product)},
    )


@router.get("/orders")
def get_customer_orders(user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    expire_unpaid_orders(db, user_id=user.id)
    rows = (
        db.query(Order, Product)
        .outerjoin(Product, Product.id == Order.product_id)
        .filter(Order.buyer_user_id == user.id)
        .order_by(Order.id.desc())
        .all()
    )
    order_ids = [order.id for order, _product in rows]
    reviewed_order_ids = set()
    if order_ids:
        reviewed_order_ids = {
            row[0]
            for row in db.query(Review.order_id)
            .filter(Review.order_id.in_(order_ids))
            .all()
        }
    after_sale_by_order = {}
    latest_records = {}
    if order_ids:
        after_sales = (
            db.query(AfterSaleRequest)
            .filter(AfterSaleRequest.order_id.in_(order_ids))
            .order_by(AfterSaleRequest.id.desc())
            .all()
        )
        for record in after_sales:
            after_sale_by_order.setdefault(record.order_id, _after_sale_data(record))
            latest_records.setdefault(record.order_id, record)
    orders = []
    review_days = settings_data(db, 'order')['review_expire_days']
    now = datetime.now()
    for order, product in rows:
        order_data = _order_data(order, product)
        order_data["reviewed"] = order.id in reviewed_order_ids
        deadline = review_deadline(db, order, review_days)
        order_data["review_deadline_at"] = (
            deadline.strftime("%Y-%m-%d %H:%M:%S") if deadline else None
        )
        order_data["review_expired"] = bool(
            order.status == "completed"
            and deadline
            and now >= deadline
            and order.id not in reviewed_order_ids
        )
        order_data["after_sale"] = after_sale_by_order.get(order.id)
        order_data["after_sale_options"] = after_sale_options(order, latest_records.get(order.id), product)
        orders.append(order_data)
    return Response.success(data={"list": orders})


@router.post("/orders/{order_id}/pay")
def pay_customer_order(order_id: int, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    orders = pay_checkout(db, order_id, user.id)
    return Response.success(message="模拟付款成功，等待商家发货", data={"list": [_order_data(order, db.get(Product, order.product_id)) for order in orders]})


@router.post("/orders/{order_id}/cancel")
def cancel_customer_order(order_id: int, user: CurrentUser, db: DbSession):
    user = _require_customer(user)
    orders = cancel_checkout(db, order_id, user.id)
    return Response.success(message="订单已取消，库存和优惠券已返还", data={"list": [_order_data(order, db.get(Product, order.product_id)) for order in orders]})


@router.post("/orders/{order_id}/after-sales")
def create_customer_after_sale(
    order_id: int,
    payload: CustomerAfterSaleCreate,
    user: CurrentUser,
    db: DbSession,
):
    user = _require_customer(user)
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.buyer_user_id == user.id)
        .with_for_update()
        .first()
    )
    if not order:
        raise BusinessException(message="找不到属于你的订单", code=404)
    if order.status not in {"paid", "shipped", "completed"}:
        raise BusinessException(message="已取消的订单不能申请售后")
    if order.status == "paid" and payload.service_type != "refund":
        raise BusinessException(message="未发货订单请选择退款，无需退货或换货")

    latest = (
        db.query(AfterSaleRequest)
        .filter(AfterSaleRequest.order_id == order.id)
        .order_by(AfterSaleRequest.id.desc())
        .first()
    )
    product = db.query(Product).filter(Product.id == order.product_id).with_for_update().first()
    choice = after_sale_options(order, latest, product)[payload.service_type]
    if not choice["enabled"]:
        raise BusinessException(message=choice["reason"])
    exchange_address = None
    if payload.service_type == "exchange":
        exchange_address = db.query(CustomerAddress).filter_by(
            id=payload.exchange_address_id,
            user_id=user.id,
        ).first()
        if not exchange_address:
            raise BusinessException(message="换货申请请选择有效的收货地址")

    exchange_address_snapshot = None
    if exchange_address:
        exchange_address_snapshot = (
            f"{exchange_address.receiver_name}，{exchange_address.phone}，"
            f"{exchange_address.province}{exchange_address.city}"
            f"{exchange_address.district}{exchange_address.detail}"
        )
    record = AfterSaleRequest(
        order_id=order.id,
        user_id=user.id,
        order_no=order.order_no,
        product_id=order.product_id,
        product_name=product.name if product else f"商品 #{order.product_id}",
        service_type=payload.service_type,
        reason=payload.reason,
        description=payload.description,
        return_shipped=False,
        return_tracking_no=None,
        exchange_shipping_address=exchange_address_snapshot,
        status="pending",
    )
    db.add(record)
    db.flush()
    resolve_order_paid_notice(db, order.id)
    service_type = {"refund": "退款", "return": "退货退款", "exchange": "换货"}.get(
        record.service_type, "售后"
    )
    alert_title = f"新增{service_type}申请预警"
    alert_content = (
        f"商品【{record.product_name}】收到用户 {user.name or user.username} 的{service_type}申请。"
        f"申请原因：{record.reason}。请及时核查并处理。"
    )
    db.add(
        AlertNotification(
            title=alert_title,
            content=alert_content,
            level="critical" if record.service_type == "refund" else "warning",
            product_id=record.product_id,
            created_by=user.id,
        )
    )
    db.add(
        StaffInboxEvent(
            event_type="after_sale_request",
            target_id=record.id,
            title="新的售后申请",
            content=f"用户 {user.name or user.username} 提交了 {record.product_name} 的{service_type}申请：{record.reason}",
        )
    )
    sync_product_after_sale_risk(db, record.product_id)
    db.commit()
    db.refresh(record)
    return Response.success(message="售后申请已提交", data=_after_sale_data(record))


@router.post("/after-sales/{after_sale_id}/return-shipment")
def submit_customer_return_shipment(
    after_sale_id: int,
    payload: AfterSaleReturnShipmentUpdate,
    user: CurrentUser,
    db: DbSession,
):
    """商家同意退货或换货后，买家补填寄回物流单号。"""
    user = _require_customer(user)
    record = db.query(AfterSaleRequest).filter_by(id=after_sale_id, user_id=user.id).with_for_update().first()
    if not record:
        raise BusinessException(message="售后申请不存在", code=404)
    if record.service_type not in {"return", "exchange"}:
        raise BusinessException(message="该售后申请不需要寄回商品")
    if record.status != "approved":
        raise BusinessException(message="请等待商家同意后再填写寄回物流")
    if record.return_shipped and record.return_tracking_no:
        raise BusinessException(message="寄回物流已提交")

    record.return_shipped = True
    record.return_tracking_no = payload.return_tracking_no
    message = AfterSaleMessage(
        after_sale_id=record.id,
        user_id=user.id,
        sender_user_id=user.id,
        sender_role="customer",
        sender_name=user.name or user.username,
        content="已提交寄回物流信息，详见售后卡片。",
        read_by_customer=True,
        read_by_staff=False,
    )
    db.add(message)
    db.commit()
    db.refresh(record)
    return Response.success(message="寄回物流已提交", data=_after_sale_data(record))


@router.post("/orders/{order_id}/receive")
def confirm_order_received(order_id: int, user: CurrentUser, db: DbSession):
    """买家确认已收货后，订单进入可评价状态。"""
    user = _require_customer(user)
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.buyer_user_id == user.id)
        .with_for_update()
        .first()
    )
    if not order:
        raise BusinessException(message="找不到属于你的订单", code=404)
    if order.status != "shipped":
        raise BusinessException(message="只有已发货订单可以确认收货")

    latest_after_sale = (
        db.query(AfterSaleRequest)
        .filter(AfterSaleRequest.order_id == order.id)
        .order_by(AfterSaleRequest.id.desc())
        .with_for_update()
        .first()
    )
    exchange_after_sale = latest_after_sale if (
        latest_after_sale
        and latest_after_sale.service_type == "exchange"
        and latest_after_sale.status in {"approved", "completed"}
        and latest_after_sale.exchange_tracking_no
    ) else None
    if latest_after_sale and latest_after_sale.status != "rejected" and not exchange_after_sale:
        raise BusinessException(message="该订单正在退款或退换货，请在售后会话查看处理进度")
    order.status = "completed"
    order.received_at = datetime.now()
    message = "已确认收货，现在可以评价商品"
    if exchange_after_sale:
        db.add(
            AfterSaleMessage(
                after_sale_id=exchange_after_sale.id,
                user_id=user.id,
                sender_user_id=user.id,
                sender_role="customer",
                sender_name=user.name or user.username,
                content="已确认收到换货商品。" + (
                    "请商家确认完成售后。" if exchange_after_sale.status == "approved" else ""
                ),
                read_by_customer=True,
                read_by_staff=False,
            )
        )
        message = (
            "已确认收到换货商品，等待商家完成售后；现在可以评价商品"
            if exchange_after_sale.status == "approved" else "已确认收到换货商品，现在可以评价商品"
        )
    db.commit()
    db.refresh(order)
    return Response.success(
        message=message,
        data={"id": order.id, "status": order.status},
    )


@router.post("/orders/{order_id}/review")
def create_order_review(
    order_id: int,
    payload: CustomerReviewCreate,
    user: CurrentUser,
    db: DbSession,
):
    user = _require_customer(user)
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.buyer_user_id == user.id)
        .first()
    )
    if not order:
        raise BusinessException(message="找不到属于你的订单", code=404)
    if order.status != "completed":
        raise BusinessException(message="订单发货并确认收货后才能评价")
    if db.query(Review.id).filter(Review.order_id == order.id).first():
        raise BusinessException(message="这笔订单已经评价过了")
    deadline = review_deadline(db, order)
    if deadline and datetime.now() >= deadline:
        raise BusinessException(message="评价期限已过，无法再评价")

    review = Review(
        product_id=order.product_id,
        order_id=order.id,
        rating=payload.rating,
        content=payload.content,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return Response.success(
        message="评价已提交",
        data={"id": review.id, "order_id": order.id, "rating": review.rating},
    )


def _customer_review_reply_data(reply: CustomerReviewReply, user: User) -> dict:
    return {
        "id": f"legacy-{reply.id}",
        "review_id": reply.review_id,
        "user_id": user.id,
        "user_name": user.name or user.username,
        "user_role": user.role,
        "content": reply.content,
        "create_time": reply.create_time.strftime("%Y-%m-%d %H:%M:%S") if reply.create_time else None,
    }


@router.get("/reviews/{review_id}/replies")
def get_customer_review_replies(review_id: int, _user: CurrentUser, db: DbSession):
    """读取一条商品评价下的注册用户回复。"""
    review = db.get(Review, review_id)
    if not review:
        raise BusinessException(message="评价不存在", code=404)

    rows = (
        db.query(CustomerReviewReply, User)
        .join(User, User.id == CustomerReviewReply.user_id)
        .filter(CustomerReviewReply.review_id == review_id)
        .order_by(CustomerReviewReply.create_time.asc(), CustomerReviewReply.id.asc())
        .all()
    )
    owner_id = review_owner_id(db, review)
    comments = [_customer_review_reply_data(reply, user) for reply, user in rows]
    for item in comments:
        item["kind"] = "append" if item["user_id"] == owner_id else "reply"
    comments.extend(comment_data(db, record, owner_id) for record in db.query(ReviewComment).filter_by(review_id=review_id).all())
    comments.sort(key=lambda item: (item["create_time"] or "", item["id"]))
    return Response.success(data={"list": comments})


@router.post("/reviews/{review_id}/replies")
def create_customer_review_reply(
    review_id: int,
    payload: CustomerReviewReplyPayload,
    user: CurrentUser,
    db: DbSession,
):
    """注册用户可以回复评价；不要求该用户购买过商品。"""
    user = _require_customer(user)
    review = db.get(Review, review_id)
    if not review:
        raise BusinessException(message="评价不存在", code=404)
    reply = add_review_comment(db, review, user, payload.content)
    db.commit()
    return Response.success(
        message="评论已发布",
        data=comment_data(db, reply, review_owner_id(db, review)),
    )
