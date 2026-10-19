"""电商数据接口：业务查询、商品主图维护、商家评价回复与预警处理。"""

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import aliased

from app.common.exceptions import BusinessException
from app.common.response import Response
from app.dependencies.auth import CurrentAdmin, CurrentProductEditor, CurrentUser, DbSession
from app.models.after_sale import AfterSaleMessage, AfterSaleRequest
from app.models.order import Order
from app.models.product import Product
from app.models.staff_inbox import StaffInboxEvent
from app.models.user import User
from app.schemas.ecommerce import (
    ProductAiDetailUpdate,
    ProductDescriptionUpdate,
    ProductImageUpdate,
    ProductNameUpdate,
    ProductManagementUpdate,
    ProductListingCreate,
    ProductListingUpdate,
    ProductImagesUpdate,
    ProductTagsUpdate,
    ProductPricingUpdate,
    ProductShelfStatusUpdate,
    ProductStockUpdate,
    ReviewReplyUpdate,
    OrderShipmentUpdate,
)
from app.schemas.after_sale import AfterSaleExchangeShipmentUpdate, AfterSaleMessageCreate, AfterSaleProcess
from app.services import diagnosis_service, ecommerce_service, overview_service
from app.services.after_sale_service import CLOSED_STATUSES, after_sale_flow_data, completion_blocked_reason
from app.models.community import ReviewReplyNotification
from app.services.community_service import direct_inbox, notification_data
from app.services.after_sale_risk_service import sync_product_after_sale_risk, sync_all_after_sale_risks, confirm_after_sale_risk_review
from app.services.inventory_service import sync_product_inventory

router = APIRouter(prefix="/ecommerce", tags=["电商业务数据与维护"])


@router.get("/overview")
def get_overview(
    _user: CurrentUser,
    db: DbSession,
    trend_days: Annotated[int, Query(ge=7, le=90, description="订单趋势天数")] = 30,
):
    """首页数据概览：规模卡片、订单趋势、评分分布、口碑榜单、最近预警（只读）。"""
    return Response.success(data=overview_service.get_overview(db, trend_days))


@router.get("/products")
def get_products(
    _user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
    sort_by: Literal[
        "price",
        "discount_percent",
        "stock",
        "create_time",
        "shelf_status",
        "review_status",
    ] | None = None,
    sort_order: Literal["asc", "desc"] = "asc",
):
    """分页查询商品（支持售价、折扣、库存和创建时间排序）。"""
    return Response.success(
        data=ecommerce_service.list_products(
            db, page, page_size, keywords, sort_by, sort_order
        )
    )


@router.get("/storefront/products")
def get_storefront_products(
    _user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=60)] = 12,
    keywords: str | None = None,
    category: str | None = None,
    sort_by: Literal[
        "default", "price_asc", "price_desc", "sales_asc", "sales_desc"
    ] = "default",
):
    """商品首页目录：只展示在售且已通过复核的商品。"""
    return Response.success(
        data=ecommerce_service.list_storefront_products(
            db, page, page_size, keywords, category, sort_by
        )
    )


@router.post("/products")
def create_product_listing(
    payload: ProductListingCreate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """创建商品并上架；仅运营与管理员可操作。"""
    return Response.success(data=ecommerce_service.create_product_listing(db, payload, editor))


@router.get("/alerts/summary")
def get_alert_summary(
    _user: CurrentUser,
    db: DbSession,
):
    """预警概览：总数与未读数（页签角标用，不受分页影响）。"""
    return Response.success(data=diagnosis_service.get_alert_summary(db))


@router.post("/alerts/read-all")
def mark_all_alerts_read(
    _user: CurrentUser,
    db: DbSession,
):
    """把所有预警标记为已读（只改通知状态，不动业务数据）。"""
    return Response.success(data={"updated": diagnosis_service.mark_all_alerts_read(db)})


@router.post("/alerts/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    _user: CurrentUser,
    db: DbSession,
):
    """把一条预警标记为已读。"""
    return Response.success(data=diagnosis_service.mark_alert_read(db, alert_id))


@router.get("/products/{product_id}/detail")
def get_product_detail(
    product_id: int,
    _user: CurrentUser,
    db: DbSession,
):
    """商品详情：基础信息 + 评价/订单汇总 + 最近记录 + 该商品相关的报告与预警（只读）。"""
    return Response.success(data=ecommerce_service.get_product_detail(db, product_id))


@router.post("/after-sale-risks/scan")
def scan_after_sale_risks(editor: CurrentProductEditor, db: DbSession):
    result = sync_all_after_sale_risks(db, editor.id)
    db.commit()
    return Response.success(data=result)


@router.post("/products/{product_id}/after-sale-risk/review")
def review_after_sale_risk(product_id: int, editor: CurrentProductEditor, db: DbSession):
    result = confirm_after_sale_risk_review(db, product_id, editor)
    db.commit()
    return Response.success(data=result, message="商品已标记待人工复核")


@router.put("/products/{product_id}")
def update_product_management(
    product_id: int,
    payload: ProductManagementUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """商品数据页更新名称、类目、折后售价、库存与折扣；运营与管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_product_management(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/listing")
def update_product_listing(
    product_id: int,
    payload: ProductListingUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """更新商品完整资料并上架；仅运营与管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_product_listing(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/stock")
def update_product_stock(
    product_id: int,
    payload: ProductStockUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """更新单个商品的库存；仅运营与管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_product_stock(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/shelf-status")
def update_product_shelf_status(
    product_id: int,
    payload: ProductShelfStatusUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """更新商品上下架状态；运营与管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_product_shelf_status(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/image")
def update_product_image(
    product_id: int,
    payload: ProductImageUpdate,
    _admin: CurrentAdmin,
    db: DbSession,
):
    """设置或清除商品主图；仅管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_product_image(
            db, product_id, payload.image_url, _admin
        )
    )


@router.put("/products/{product_id}/images")
def update_product_images(
    product_id: int,
    payload: ProductImagesUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """更新商品图片列表，第一张作为商品主图；商家可按需添加图片。"""
    return Response.success(
        data=ecommerce_service.update_product_images(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/ai-detail")
def update_product_ai_detail(
    product_id: int,
    payload: ProductAiDetailUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """保存 AI 商品文案；运营与管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_product_ai_detail(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/description")
def update_product_description(
    product_id: int,
    payload: ProductDescriptionUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """更新商品介绍；运营与管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_product_description(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/name")
def update_product_name(
    product_id: int,
    payload: ProductNameUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """更新商品名称；运营与管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_product_name(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/tags")
def update_product_tags(
    product_id: int,
    payload: ProductTagsUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """更新商品标签，可设置多个标签。"""
    return Response.success(
        data=ecommerce_service.update_product_tags(db, product_id, payload, editor)
    )


@router.put("/products/{product_id}/pricing")
def update_product_pricing(
    product_id: int,
    payload: ProductPricingUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    """更新商品原价与优惠百分比，并自动计算售价。"""
    return Response.success(
        data=ecommerce_service.update_product_pricing(db, product_id, payload, editor)
    )


@router.get("/orders")
def get_orders(
    _user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
    sort_by: Literal[
        "quantity", "amount", "status", "create_time"
    ] | None = None,
    sort_order: Literal["asc", "desc"] = "asc",
):
    """分页查询订单（只读）。"""
    return Response.success(
        data=ecommerce_service.list_orders(
            db, page, page_size, keywords, sort_by, sort_order
        )
    )


@router.get("/orders/{order_id}/detail")
def get_order_detail(
    order_id: int,
    _user: CurrentUser,
    db: DbSession,
):
    """订单详情：订单本身 + 这笔订单的评价（可能没有）（只读）。"""
    return Response.success(data=ecommerce_service.get_order_detail(db, order_id))


@router.post("/orders/{order_id}/ship")
def ship_order(
    order_id: int,
    payload: OrderShipmentUpdate,
    _editor: CurrentProductEditor,
    db: DbSession,
):
    """运营或管理员填写物流单号并为已支付订单发货。"""
    return Response.success(
        message="订单已发货",
        data=ecommerce_service.ship_order(db, order_id, payload.tracking_no),
    )


def _after_sale_data(record: AfterSaleRequest, username: str, user_name: str) -> dict:
    return {
        **after_sale_flow_data(record),
        "id": record.id,
        "order_id": record.order_id,
        "order_no": record.order_no,
        "product_id": record.product_id,
        "product_name": record.product_name,
        "user_id": record.user_id,
        "username": username,
        "user_name": user_name,
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


@router.get("/after-sales")
def list_after_sales(
    _editor: CurrentProductEditor,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    status: Literal["pending", "approved", "rejected", "completed"] | None = None,
    keywords: str | None = None,
    product_id: Annotated[int | None, Query(ge=1)] = None,
):
    query = db.query(AfterSaleRequest, User.username, User.name).join(
        User, User.id == AfterSaleRequest.user_id
    )

    if status:
        query = query.filter(AfterSaleRequest.status == status)
    if product_id is not None:
        query = query.filter(AfterSaleRequest.product_id == product_id)
    if keywords and keywords.strip():
        pattern = f"%{keywords.strip()}%"
        query = query.filter(
            or_(
                AfterSaleRequest.order_no.ilike(pattern),
                AfterSaleRequest.product_name.ilike(pattern),
                AfterSaleRequest.reason.ilike(pattern),
                User.username.ilike(pattern),
                User.name.ilike(pattern),
            )
        )
    total = query.order_by(None).count()
    rows = (
        query.order_by(AfterSaleRequest.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    after_sale_ids = [record.id for record, _, _ in rows]
    unread_message_counts = {}
    if after_sale_ids:
        unread_message_counts = dict(
            db.query(AfterSaleMessage.after_sale_id, func.count(AfterSaleMessage.id))
            .filter(
                AfterSaleMessage.after_sale_id.in_(after_sale_ids),
                AfterSaleMessage.sender_role == "customer",
                AfterSaleMessage.read_by_staff.is_(False),
            )
            .group_by(AfterSaleMessage.after_sale_id)
            .all()
        )
    records = []
    for record, username, user_name in rows:
        item = _after_sale_data(record, username, user_name)
        item["unread_messages_count"] = unread_message_counts.get(record.id, 0)
        records.append(item)
    return Response.success(
        data={
            "list": records,
            "total": total,
        }
    )


@router.get("/message-center")
def get_staff_message_center(_editor: CurrentProductEditor, db: DbSession):
    """后台消息中心：售后会话、新订单和业务事件通知。"""
    event_rows = (
        db.query(StaffInboxEvent)
        .order_by(StaffInboxEvent.create_time.desc(), StaffInboxEvent.id.desc())
        .limit(200)
        .all()
    )
    unread_event_count = (
        db.query(func.count(StaffInboxEvent.id))
        .filter(StaffInboxEvent.is_read.is_(False))
        .scalar()
        or 0
    )
    unread_chat_count = (
        db.query(func.count(AfterSaleMessage.id))
        .filter(
            AfterSaleMessage.sender_role == "customer",
            AfterSaleMessage.read_by_staff.is_(False),
        )
        .scalar()
        or 0
    )
    unread_by_after_sale = dict(
        db.query(AfterSaleMessage.after_sale_id, func.count(AfterSaleMessage.id))
        .filter(
            AfterSaleMessage.sender_role == "customer",
            AfterSaleMessage.read_by_staff.is_(False),
        )
        .group_by(AfterSaleMessage.after_sale_id)
        .all()
    )
    latest_message_ids = (
        db.query(
            AfterSaleMessage.after_sale_id.label("after_sale_id"),
            func.max(AfterSaleMessage.id).label("message_id"),
        )
        .group_by(AfterSaleMessage.after_sale_id)
        .subquery()
    )
    latest_message = aliased(AfterSaleMessage)
    conversation_rows = (
        db.query(AfterSaleRequest, User.username, User.name, latest_message)
        .join(User, User.id == AfterSaleRequest.user_id)
        .outerjoin(latest_message_ids, latest_message_ids.c.after_sale_id == AfterSaleRequest.id)
        .outerjoin(latest_message, latest_message.id == latest_message_ids.c.message_id)
        .order_by(
            func.coalesce(latest_message.create_time, AfterSaleRequest.create_time).desc(),
            AfterSaleRequest.id.desc(),
        )
        .limit(200)
        .all()
    )
    events = [
        {
            "id": event.id,
            "event_type": event.event_type,
            "target_id": event.target_id,
            "title": event.title,
            "content": event.content,
            "is_read": event.is_read,
            "create_time": event.create_time.strftime("%Y-%m-%d %H:%M:%S")
            if event.create_time
            else None,
        }
        for event in event_rows
    ]
    conversations = []
    for record, username, user_name, message in conversation_rows:
        conversations.append(
            {
                "after_sale_id": record.id,
                **after_sale_flow_data(record),
                "order_no": record.order_no,
                "product_name": record.product_name,
                "service_type": record.service_type,
                "status": record.status,
                "return_shipped": record.return_shipped,
                "return_tracking_no": record.return_tracking_no,
                "exchange_shipping_address": record.exchange_shipping_address,
                "exchange_tracking_no": record.exchange_tracking_no,
                "user_id": record.user_id,
                "username": username,
                "user_name": user_name,
                "preview": message.content if message else f"售后申请：{record.reason}",
                "create_time": message.create_time.strftime("%Y-%m-%d %H:%M:%S")
                if message and message.create_time
                else record.create_time.strftime("%Y-%m-%d %H:%M:%S")
                if record.create_time
                else None,
                "unread_count": int(unread_by_after_sale.get(record.id, 0)),
            }
        )
    private_conversations = direct_inbox(db, _editor)
    reply_notifications = db.query(ReviewReplyNotification).filter_by(user_id=_editor.id).all()
    for notification in reply_notifications:
        item = notification_data(notification)
        events.append({**item, "event_type": "review_reply", "title": f"{notification.actor_name}回复了你的评论"})
    events.sort(key=lambda item: item["create_time"] or "", reverse=True)
    return Response.success(
        data={
            "events": events,
            "conversations": conversations,
            "direct_conversations": private_conversations,
            "unread_count": int(unread_event_count + unread_chat_count)
            + sum(item["unread_count"] for item in private_conversations) + sum(not item.is_read for item in reply_notifications),
        }
    )


@router.post("/message-center/events/{event_id}/read")
def mark_staff_message_event_read(
    event_id: int, _editor: CurrentProductEditor, db: DbSession
):
    event = db.query(StaffInboxEvent).filter(StaffInboxEvent.id == event_id).first()
    if not event:
        raise BusinessException(message="消息不存在", code=404)
    if not event.is_read:
        event.is_read = True
        db.commit()
    return Response.success(message="消息已读")


@router.post("/message-center/events/read-all")
def mark_all_staff_message_events_read(_editor: CurrentProductEditor, db: DbSession):
    updated = (
        db.query(StaffInboxEvent)
        .filter(StaffInboxEvent.is_read.is_(False))
        .update({StaffInboxEvent.is_read: True}, synchronize_session=False)
    )
    updated += db.query(ReviewReplyNotification).filter_by(user_id=_editor.id, is_read=False).update(
        {ReviewReplyNotification.is_read: True}, synchronize_session=False
    )
    db.commit()
    return Response.success(data={"updated": int(updated or 0)})


@router.post("/after-sales/{after_sale_id}/process")
def process_after_sale(
    after_sale_id: int,
    payload: AfterSaleProcess,
    editor: CurrentProductEditor,
    db: DbSession,
):
    record = db.query(AfterSaleRequest).filter(AfterSaleRequest.id == after_sale_id).with_for_update().first()
    if not record:
        raise BusinessException(message="售后申请不存在", code=404)

    if payload.action in {"approve", "reject"}:
        if record.status != "pending":
            raise BusinessException(message="该申请已处理，无法重复审核")
        if payload.action == "reject" and not payload.admin_note:
            raise BusinessException(message="请填写拒绝原因")
        if payload.action == "approve" and record.service_type == "exchange":
            product = db.query(Product).filter_by(id=record.product_id).with_for_update().first()
            if not product or product.stock < record.order.quantity:
                raise BusinessException(message="换货库存不足，请先补货或与买家沟通改为退款/退货退款")
        record.status = "approved" if payload.action == "approve" else "rejected"
    else:
        blocked = completion_blocked_reason(record)
        if blocked:
            raise BusinessException(message=blocked)
        record.status = "completed"

    if payload.admin_note is not None:
        record.admin_note = payload.admin_note
    record.processed_by = editor.id
    record.processed_at = datetime.now()
    service_type = {"refund": "退款", "return": "退货退款", "exchange": "换货"}.get(
        record.service_type, "售后"
    )
    result_text = {
        "approve": f"你的{service_type}申请已同意，售后处理中",
        "reject": f"你的{service_type}申请审核未通过。会话已关闭，记录仍可查看；如需重新申请，请从订单的“更多”进入。你也可以评价本次售后服务",
    }.get(payload.action)
    if payload.action == "complete":
        completion_text = {
            "refund": "退款已完成",
            "return": "退货退款已完成",
            "exchange": "换货售后已完成",
        }.get(record.service_type, "售后已完成")
        result_text = f"{completion_text}。沟通通道已关闭，对话记录仍可查看，请为本次售后服务评分"
    notice = AfterSaleMessage(
        after_sale_id=record.id,
        user_id=record.user_id,
        sender_user_id=editor.id,
        sender_role="system",
        sender_name="售后保障",
        content=f"{result_text}。"
        + (f"处理说明：{record.admin_note}" if record.admin_note else ""),
        read_by_customer=False,
        read_by_staff=True,
    )
    db.add(notice)
    sync_product_after_sale_risk(db, record.product_id, editor.id)
    db.commit()
    db.refresh(record)
    customer = db.query(User).filter(User.id == record.user_id).first()
    return Response.success(
        message="售后申请已更新",
        data=_after_sale_data(record, customer.username if customer else "", customer.name if customer else ""),
    )


@router.post("/after-sales/{after_sale_id}/exchange-shipment")
def submit_after_sale_exchange_shipment(
    after_sale_id: int,
    payload: AfterSaleExchangeShipmentUpdate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    record = db.query(AfterSaleRequest).filter(AfterSaleRequest.id == after_sale_id).with_for_update().first()
    if not record:
        raise BusinessException(message="售后申请不存在", code=404)
    if record.service_type != "exchange":
        raise BusinessException(message="只有换货申请需要填写商家发货物流")
    if record.status != "approved":
        raise BusinessException(message="请先同意换货申请")
    if not (record.return_shipped and record.return_tracking_no):
        raise BusinessException(message="请等待用户寄回商品并提交物流单号")
    if record.exchange_tracking_no:
        raise BusinessException(message="换货商品物流单号已提交")

    order = db.query(Order).filter(Order.id == record.order_id).first()
    if not order:
        raise BusinessException(message="原订单不存在", code=404)
    if order.status == "cancelled":
        raise BusinessException(message="已取消的订单不能发出换货商品")

    product = db.query(Product).filter_by(id=record.product_id).with_for_update().first()
    if not product or product.stock < order.quantity:
        raise BusinessException(message="换货库存不足，请先补货；退款和退货退款不受库存限制")
    product.stock -= order.quantity
    sync_product_inventory(db, product.id, editor.id)

    record.exchange_tracking_no = payload.exchange_tracking_no
    # 换货商品寄出后，订单进入待买家确认收货状态，避免仍显示“已支付”或再次普通发货。
    order.status = "shipped"
    notice = AfterSaleMessage(
        after_sale_id=record.id,
        user_id=record.user_id,
        sender_user_id=editor.id,
        sender_role="system",
        sender_name="售后保障",
        content="商家已提交换货发货物流信息，详见售后卡片。",
        read_by_customer=False,
        read_by_staff=True,
    )
    db.add(notice)
    db.commit()
    db.refresh(record)
    customer = db.query(User).filter(User.id == record.user_id).first()
    return Response.success(
        message="换货商品物流单号已提交",
        data=_after_sale_data(record, customer.username if customer else "", customer.name if customer else ""),
    )


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


@router.get("/after-sales/{after_sale_id}/messages")
def get_after_sale_messages(after_sale_id: int, _editor: CurrentProductEditor, db: DbSession):
    record = db.query(AfterSaleRequest).filter(AfterSaleRequest.id == after_sale_id).first()
    if not record:
        raise BusinessException(message="售后申请不存在", code=404)
    unread_count = (
        db.query(AfterSaleMessage.id)
        .filter(
            AfterSaleMessage.after_sale_id == record.id,
            AfterSaleMessage.sender_role == "customer",
            AfterSaleMessage.read_by_staff.is_(False),
        )
        .count()
    )
    db.query(AfterSaleMessage).filter(
        AfterSaleMessage.after_sale_id == record.id,
        AfterSaleMessage.sender_role == "customer",
        AfterSaleMessage.read_by_staff.is_(False),
    ).update({AfterSaleMessage.read_by_staff: True}, synchronize_session=False)
    messages = (
        db.query(AfterSaleMessage)
        .filter(AfterSaleMessage.after_sale_id == record.id)
        .order_by(AfterSaleMessage.create_time.asc(), AfterSaleMessage.id.asc())
        .all()
    )
    if unread_count:
        db.commit()
    product = db.query(Product).filter(Product.id == record.product_id).first()
    user = db.query(User).filter(User.id == record.user_id).first()
    application = _after_sale_data(
        record,
        user.username if user else "",
        user.name if user else "",
    )
    application["image_url"] = product.image_url if product else None
    return Response.success(
        data={
            "after_sale_id": record.id,
            "order_no": record.order_no,
            "product_name": record.product_name,
            "application": application,
            "messages": [_after_sale_message_data(message) for message in messages],
            "unread_count": unread_count,
        }
    )


@router.post("/after-sales/{after_sale_id}/messages")
def create_after_sale_message(
    after_sale_id: int,
    payload: AfterSaleMessageCreate,
    editor: CurrentProductEditor,
    db: DbSession,
):
    record = db.query(AfterSaleRequest).filter(AfterSaleRequest.id == after_sale_id).with_for_update().first()
    if not record:
        raise BusinessException(message="售后申请不存在", code=404)
    if record.status in CLOSED_STATUSES:
        raise BusinessException(message="售后会话已关闭，不能继续发送消息")
    message = AfterSaleMessage(
        after_sale_id=record.id,
        user_id=record.user_id,
        sender_user_id=editor.id,
        sender_role=editor.role,
        sender_name=editor.name or editor.username,
        content=payload.content,
        read_by_customer=False,
        read_by_staff=True,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return Response.success(message="消息已发送", data=_after_sale_message_data(message))


@router.get("/reviews")
def get_reviews(
    _user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
    product_id: Annotated[int | None, Query(ge=1)] = None,
    rating: Annotated[int | None, Query(ge=1, le=5)] = None,
    has_reply: bool | None = None,
    focus_review_id: Annotated[int | None, Query(ge=1)] = None,
    sort_by: Literal["rating", "create_time"] | None = None,
    sort_order: Literal["asc", "desc"] = "asc",
):
    """分页查询评价，可按商品、评分、回复状态筛选。"""
    return Response.success(
        data=ecommerce_service.list_reviews(
            db,
            page,
            page_size,
            keywords,
            product_id,
            rating,
            has_reply,
            focus_review_id,
            sort_by,
            sort_order,
        )
    )


@router.put("/reviews/{review_id}/reply")
def update_review_reply(
    review_id: int,
    payload: ReviewReplyUpdate,
    _admin: CurrentAdmin,
    db: DbSession,
):
    """发布或修改商家评价回复；仅管理员可操作。"""
    return Response.success(
        data=ecommerce_service.update_review_reply(
            db, review_id, payload.merchant_reply, _admin
        )
    )


@router.get("/reports")
def get_diagnosis_reports(
    _user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
):
    """分页查询诊断报告（Agent 写操作的产物，只读）。"""
    return Response.success(
        data=diagnosis_service.list_diagnosis_reports(db, page, page_size, keywords)
    )


@router.get("/reports/{report_id}")
def get_diagnosis_report_detail(
    report_id: int,
    _user: CurrentUser,
    db: DbSession,
):
    """诊断报告详情及生成时保存的证据明细。"""
    return Response.success(
        data=diagnosis_service.get_diagnosis_report(db, report_id)
    )


@router.get("/alerts")
def get_alert_notifications(
    _user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
):
    """分页查询预警通知（Agent 写操作的产物，只读）。"""
    return Response.success(
        data=diagnosis_service.list_alert_notifications(db, page, page_size, keywords)
    )
