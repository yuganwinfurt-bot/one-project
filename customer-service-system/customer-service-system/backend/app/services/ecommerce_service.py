"""电商业务服务：查询商品 / 订单 / 评价，并维护商品资料与商家回复。"""

import json
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session, aliased

from app.common.exceptions import BusinessException
from app.common.response import PageResponse
from app.models.alert_notification import AlertNotification
from app.models.after_sale import AfterSaleRequest
from app.models.diagnosis_report import DiagnosisReport
from app.models.order import Order
from app.models.product import Product
from app.models.review import Review
from app.models.shopping import CustomerShipmentMessage
from app.models.user import User
from app.services.customer_message_service import notify_favorited_customers_of_price_drop
from app.services.after_sale_service import after_sale_flow_data
from app.services.community_service import notify_review_reply, review_owner_id
from app.services.after_sale_risk_service import collect_after_sale_risks
from app.services.inventory_service import sync_product_inventory
from app.schemas.ecommerce import (
    AlertItem,
    DiagnosisReportItem,
    OrderDetail,
    OrderItem,
    ProductDetail,
    ProductAiDetailUpdate,
    ProductDescriptionUpdate,
    ProductNameUpdate,
    ProductManagementUpdate,
    ProductListingCreate,
    ProductListingUpdate,
    ProductShelfStatusUpdate,
    ProductImagesUpdate,
    ProductTagsUpdate,
    ProductPricingUpdate,
    ProductStockUpdate,
    ProductItem,
    ProductAfterSaleRisk,
    ProductOrderSummary,
    ProductReviewSummary,
    RatingBucket,
    ReviewItem,
    StorefrontPage,
    StorefrontProduct,
)
from app.services.platform_log_service import build_rollback_data, record_changes


_PRODUCT_AUDIT_LABELS = {
    "name": "商品名称",
    "category": "类目",
    "description": "商品介绍",
    "image_url": "商品主图",
    "image_urls": "商品图片",
    "ai_detail": "商品详情文案",
    "price": "售价",
    "original_price": "原价",
    "discount_percent": "折扣",
    "stock": "库存",
    "shelf_status": "上下架状态",
    "tags": "商品标签",
}


def _capture_product_fields(product: Product, fields: tuple[str, ...]) -> dict[str, object]:
    return {field: getattr(product, field) for field in fields}


def _record_product_changes(
    db: Session,
    actor: User | None,
    product: Product,
    before: dict[str, object],
    fields: tuple[str, ...],
    *,
    verb: str = "修改了",
) -> None:
    if {"stock", "shelf_status", "review_status"}.intersection(fields):
        sync_product_inventory(db, product.id, actor.id if actor else None)
    rollback_fields = fields
    if verb == "新建了":
        rollback_fields = (
            "name", "category", "tags", "description", "image_url", "image_urls",
            "ai_detail", "price", "original_price", "discount_percent", "stock",
            "shelf_status", "review_status",
        )
    record_changes(
        db,
        actor,
        "商品",
        str(before.get("name") or product.name),
        [
            (_PRODUCT_AUDIT_LABELS[field], before.get(field), getattr(product, field))
            for field in fields
        ],
        verb=verb,
        rollback_data=build_rollback_data(
            "product",
            product.id,
            {
                field: (before.get(field), getattr(product, field))
                for field in rollback_fields
            },
            created=verb == "新建了",
        ),
    )


def list_products(
    db: Session,
    page: int,
    page_size: int,
    keywords: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
) -> PageResponse:
    query = db.query(Product)
    if keywords:
        like = f"%{keywords.strip()}%"
        query = query.filter(
            or_(Product.name.ilike(like), Product.category.ilike(like))
        )
    total = query.count()
    sort_columns = {
        "price": Product.price,
        "discount_percent": Product.discount_percent,
        "stock": Product.stock,
        "create_time": Product.create_time,
        "shelf_status": case(
            (Product.shelf_status == "on_sale", 0),
            (Product.shelf_status == "off_shelf", 1),
            else_=2,
        ),
        "review_status": case(
            (Product.review_status == "normal", 0),
            (Product.review_status == "pending_review", 1),
            else_=2,
        ),
    }
    if sort_by in sort_columns:
        sort_column = sort_columns[sort_by]
        primary_order = sort_column.desc() if sort_order == "desc" else sort_column.asc()
        ordering = (primary_order, Product.id.asc())
    else:
        ordering = (Product.id.asc(),)
    rows = (
        query.order_by(*ordering)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    risks = collect_after_sale_risks(db, [row.id for row in rows])
    return PageResponse(
        list=[ProductItem.from_row(row, after_sale_risk=ProductAfterSaleRisk.model_validate(risks[row.id])) for row in rows],
        total=total,
    )


def list_storefront_products(
    db: Session,
    page: int,
    page_size: int,
    keywords: str | None = None,
    category: str | None = None,
    sort_by: str = "default",
) -> StorefrontPage:
    """查询商品首页目录；不展示下架或待人工复核商品。"""
    sold = (
        db.query(
            Order.product_id.label("product_id"),
            func.coalesce(func.sum(Order.quantity), 0).label("sold_quantity"),
        )
        .filter(Order.status != "cancelled")
        .group_by(Order.product_id)
        .subquery()
    )
    review_stats = (
        db.query(
            Review.product_id.label("product_id"),
            func.count(Review.id).label("review_count"),
            func.avg(Review.rating).label("avg_rating"),
        )
        .group_by(Review.product_id)
        .subquery()
    )

    category_rows = (
        db.query(Product.category, Product.tags)
        .filter(Product.shelf_status == "on_sale", Product.review_status == "normal")
        .all()
    )
    category_set = set()
    for primary_category, tags in category_rows:
        if primary_category:
            category_set.add(primary_category)
        category_set.update(tag for tag in (tags or []) if tag)
    categories = sorted(category_set)

    query = (
        db.query(
            Product,
            func.coalesce(sold.c.sold_quantity, 0).label("sold_quantity"),
            func.coalesce(review_stats.c.review_count, 0).label("review_count"),
            func.coalesce(review_stats.c.avg_rating, 0).label("avg_rating"),
        )
        .outerjoin(sold, sold.c.product_id == Product.id)
        .outerjoin(review_stats, review_stats.c.product_id == Product.id)
        .filter(Product.shelf_status == "on_sale", Product.review_status == "normal")
    )
    if keywords and keywords.strip():
        like = f"%{keywords.strip()}%"
        query = query.filter(
            or_(
                Product.name.ilike(like),
                Product.category.ilike(like),
                Product.description.ilike(like),
            )
        )
    if category and category.strip():
        selected_tag = category.strip()
        query = query.filter(
            or_(
                Product.category == selected_tag,
                func.json_contains(Product.tags, json.dumps(selected_tag)) == 1,
            )
        )

    total = query.count()
    sold_quantity = func.coalesce(sold.c.sold_quantity, 0)
    sort_options = {
        "default": (Product.id.desc(),),
        "price_asc": (Product.price.asc(), Product.id.desc()),
        "price_desc": (Product.price.desc(), Product.id.desc()),
        "sales_asc": (sold_quantity.asc(), Product.id.desc()),
        "sales_desc": (sold_quantity.desc(), Product.id.desc()),
    }
    rows = (
        query.order_by(*sort_options.get(sort_by, sort_options["default"]))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        StorefrontProduct(
            id=product.id,
            name=product.name,
            category=product.category,
            tags=product.tags or [product.category],
            description=product.description,
            image_url=product.image_url,
            image_urls=product.image_urls or ([product.image_url] if product.image_url else []),
            ai_detail=product.ai_detail,
            price=product.price,
            original_price=product.original_price or product.price,
            discount_percent=product.discount_percent or Decimal("0"),
            stock=product.stock,
            sold_quantity=int(sold_quantity or 0),
            review_count=int(review_count or 0),
            avg_rating=round(float(avg_rating or 0), 2),
        )
        for product, sold_quantity, review_count, avg_rating in rows
    ]
    return StorefrontPage(list=items, total=total, categories=categories)


def _orders_with_after_sales(db: Session):
    latest_id = (
        db.query(func.max(AfterSaleRequest.id))
        .filter(AfterSaleRequest.order_id == Order.id)
        .correlate(Order)
        .scalar_subquery()
    )
    latest = aliased(AfterSaleRequest)
    return (
        db.query(Order, Product.name.label("product_name"), latest)
        .outerjoin(Product, Order.product_id == Product.id)
        .outerjoin(latest, (latest.order_id == Order.id) & (latest.id == latest_id))
    )


def _order_item(order: Order, product_name: str | None, after_sale=None) -> OrderItem:
    application = None
    if after_sale:
        application = {
            "id": after_sale.id,
            "service_type": after_sale.service_type,
            "status": after_sale.status,
            "return_shipped": after_sale.return_shipped,
            "return_tracking_no": after_sale.return_tracking_no,
            "exchange_tracking_no": after_sale.exchange_tracking_no,
            **after_sale_flow_data(after_sale),
        }
    return OrderItem.from_row(
        order, product_name=product_name, after_sale=application,
        exchange_tracking_no=after_sale.exchange_tracking_no if after_sale else None,
        return_tracking_no=after_sale.return_tracking_no if after_sale else None,
        after_sale_service_type=after_sale.service_type if after_sale else None,
        after_sale_status=after_sale.status if after_sale else None,
    )


def list_orders(
    db: Session,
    page: int,
    page_size: int,
    keywords: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
) -> PageResponse:
    query = _orders_with_after_sales(db)
    if keywords:
        like = f"%{keywords.strip()}%"
        query = query.filter(
            or_(
                Order.order_no.ilike(like),
                Order.buyer_name.ilike(like),
                Product.name.ilike(like),
            )
        )
    total = query.count()
    sort_columns = {
        "quantity": Order.quantity,
        "amount": Order.amount,
        "status": case(
            (Order.status == "paid", 0),
            (Order.status == "shipped", 1),
            (Order.status == "completed", 2),
            (Order.status == "cancelled", 3),
            else_=4,
        ),
        "create_time": Order.create_time,
    }
    if sort_by in sort_columns:
        column = sort_columns[sort_by]
        primary_order = column.desc() if sort_order == "desc" else column.asc()
        ordering = (primary_order, Order.id.desc())
    else:
        ordering = (Order.id.desc(),)
    rows = (
        query.order_by(*ordering)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items: list[OrderItem] = []
    for order, product_name, after_sale in rows:
        items.append(_order_item(order, product_name, after_sale))
    return PageResponse(list=items, total=total)


def ship_order(db: Session, order_id: int, tracking_no: str) -> OrderItem:
    """后台填写物流单号并将已支付订单发货；收货由买家另行确认。"""
    order = db.query(Order).filter(Order.id == order_id).with_for_update().first()
    if not order:
        raise BusinessException(message="订单不存在")
    if order.status not in {"paid", "shipped", "completed"}:
        raise BusinessException(message="当前订单状态不能发货或补录物流")
    latest = db.query(AfterSaleRequest).filter_by(order_id=order.id).order_by(AfterSaleRequest.id.desc()).first()
    if latest and latest.status != "rejected":
        raise BusinessException(message="该订单已有售后，请在售后会话处理，不能再次普通发货")
    if order.status != "paid" and order.tracking_no:
        raise BusinessException(message="该订单已录入物流单号")
    exchange_tracking_exists = (
        db.query(AfterSaleRequest.id)
        .filter(
            AfterSaleRequest.order_id == order.id,
            AfterSaleRequest.service_type == "exchange",
            AfterSaleRequest.exchange_tracking_no.isnot(None),
        )
        .first()
    )
    if exchange_tracking_exists and not order.tracking_no:
        raise BusinessException(message="换货物流单号已提交，无需再填写普通发货单号")

    product_name = db.query(Product.name).filter(Product.id == order.product_id).scalar()
    first_shipment = order.status == "paid"
    if first_shipment:
        order.status = "shipped"
    order.tracking_no = tracking_no
    if first_shipment and order.buyer_user_id is not None:
        db.add(
            CustomerShipmentMessage(
                user_id=order.buyer_user_id,
                order_id=order.id,
                order_no=order.order_no,
                product_id=order.product_id,
                product_name=product_name or f"商品 #{order.product_id}",
            )
        )
    db.commit()
    db.refresh(order)
    return OrderItem.from_row(order, product_name=product_name)


def list_reviews(
    db: Session,
    page: int,
    page_size: int,
    keywords: str | None = None,
    product_id: int | None = None,
    rating: int | None = None,
    has_reply: bool | None = None,
    focus_review_id: int | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
) -> PageResponse:
    query = (
        db.query(
            Review,
            Product.name.label("product_name"),
            Order.buyer_name.label("buyer_name"),
            Order.buyer_user_id.label("buyer_user_id"),
        )
        .outerjoin(Product, Review.product_id == Product.id)
        .outerjoin(Order, Review.order_id == Order.id)
    )
    if keywords:
        like = f"%{keywords.strip()}%"
        query = query.filter(
            or_(Review.content.ilike(like), Product.name.ilike(like))
        )
    if product_id is not None:
        query = query.filter(Review.product_id == product_id)
    if rating is not None:
        query = query.filter(Review.rating == rating)
    if has_reply is True:
        query = query.filter(Review.merchant_reply.isnot(None))
    elif has_reply is False:
        query = query.filter(Review.merchant_reply.is_(None))
    total = query.count()
    sort_columns = {"rating": Review.rating, "create_time": Review.create_time}
    if sort_by in sort_columns:
        column = sort_columns[sort_by]
        primary_order = column.desc() if sort_order == "desc" else column.asc()
        ordering = (primary_order, Review.id.desc())
    elif focus_review_id is not None:
        ordering = (case((Review.id == focus_review_id, 0), else_=1), Review.id.desc())
    else:
        ordering = (Review.id.desc(),)
    rows = (
        query.order_by(*ordering)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items: list[ReviewItem] = []
    for review, product_name, buyer_name, buyer_user_id in rows:
        items.append(
            ReviewItem.from_row(
                review, product_name=product_name, buyer_name=buyer_name, buyer_user_id=buyer_user_id
            )
        )
    return PageResponse(list=items, total=total)


def update_product_image(
    db: Session, product_id: int, image_url: str | None, actor: User | None = None
) -> ProductItem:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(product, ("name", "image_urls"))
    product.image_url = image_url
    product.image_urls = [image_url] if image_url else []
    _record_product_changes(db, actor, product, before, ("image_urls",))
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_images(
    db: Session, product_id: int, payload: ProductImagesUpdate, actor: User | None = None
) -> ProductItem:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(product, ("name", "image_urls"))
    product.image_urls = payload.image_urls
    product.image_url = payload.image_urls[0] if payload.image_urls else None
    _record_product_changes(db, actor, product, before, ("image_urls",))
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_ai_detail(
    db: Session, product_id: int, payload: ProductAiDetailUpdate, actor: User | None = None
) -> ProductItem:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(product, ("name", "ai_detail"))
    product.ai_detail = payload.ai_detail
    _record_product_changes(db, actor, product, before, ("ai_detail",))
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_description(
    db: Session, product_id: int, payload: ProductDescriptionUpdate, actor: User | None = None
) -> ProductItem:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(product, ("name", "description"))
    product.description = payload.description
    _record_product_changes(db, actor, product, before, ("description",))
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_name(
    db: Session, product_id: int, payload: ProductNameUpdate, actor: User | None = None
) -> ProductItem:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(product, ("name",))
    product.name = payload.name
    _record_product_changes(db, actor, product, before, ("name",))
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_management(
    db: Session, product_id: int, payload: ProductManagementUpdate, actor: User | None = None
) -> ProductItem:
    """商品数据页集中更新基本资料；售价为折后价，按折扣反算原价。"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")

    before = _capture_product_fields(
        product,
        ("name", "category", "tags", "price", "original_price", "discount_percent", "stock"),
    )
    previous_price = product.price
    old_category = product.category
    product.name = payload.name
    product.category = payload.category
    extra_tags = [
        tag
        for tag in (product.tags or [])
        if tag not in {old_category, payload.category}
    ]
    product.tags = list(dict.fromkeys([payload.category, *extra_tags]))

    discount_factor = Decimal("1") - payload.discount_percent / Decimal("100")
    original_price = (payload.price / discount_factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    if original_price > Decimal("99999999.99"):
        raise BusinessException(message="按该折扣换算的原价超出商品价格范围")

    product.price = payload.price
    product.original_price = original_price
    product.discount_percent = payload.discount_percent
    product.stock = payload.stock
    notify_favorited_customers_of_price_drop(db, product, previous_price)
    _record_product_changes(
        db,
        actor,
        product,
        before,
        ("name", "category", "tags", "price", "original_price", "discount_percent", "stock"),
    )
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_stock(
    db: Session, product_id: int, payload: ProductStockUpdate, actor: User | None = None
) -> ProductItem:
    """独立更新商品库存。"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(product, ("name", "stock"))
    product.stock = payload.stock
    _record_product_changes(db, actor, product, before, ("stock",))
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def _listing_prices(payload: ProductListingCreate | ProductListingUpdate) -> Decimal:
    discount_factor = Decimal("1") - payload.discount_percent / Decimal("100")
    original_price = (payload.price / discount_factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    if original_price > Decimal("99999999.99"):
        raise BusinessException(message="按该折扣换算的原价超出商品价格范围")
    return original_price


def _apply_listing_fields(
    product: Product, payload: ProductListingCreate | ProductListingUpdate
) -> None:
    old_category = product.category
    product.name = payload.name
    product.category = payload.category
    extra_tags = [
        tag
        for tag in (product.tags or [])
        if tag not in {old_category, payload.category}
    ]
    product.tags = list(dict.fromkeys([payload.category, *extra_tags]))
    product.description = payload.description
    product.price = payload.price
    product.original_price = _listing_prices(payload)
    product.discount_percent = payload.discount_percent
    product.stock = payload.stock
    product.image_urls = payload.image_urls or None
    product.image_url = payload.image_urls[0] if payload.image_urls else None
    product.shelf_status = "on_sale"


def create_product_listing(
    db: Session, payload: ProductListingCreate, actor: User | None = None
) -> ProductItem:
    """创建商品并直接上架。"""
    product = Product(
        name=payload.name,
        category=payload.category,
        tags=[payload.category],
        description=payload.description,
        price=payload.price,
        original_price=_listing_prices(payload),
        discount_percent=payload.discount_percent,
        stock=payload.stock,
        image_urls=payload.image_urls or None,
        image_url=payload.image_urls[0] if payload.image_urls else None,
        shelf_status="on_sale",
        review_status="normal",
    )
    db.add(product)
    db.flush()
    _record_product_changes(
        db,
        actor,
        product,
        {},
        (
            "name", "category", "price", "discount_percent", "stock",
            "description", "image_urls",
        ),
        verb="新建了",
    )
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_listing(
    db: Session, product_id: int, payload: ProductListingUpdate, actor: User | None = None
) -> ProductItem:
    """保存商品完整资料并恢复在售状态。"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    fields = (
        "name", "category", "tags", "description", "price", "original_price",
        "discount_percent", "stock", "image_urls", "shelf_status",
    )
    before = _capture_product_fields(product, fields)
    previous_price = product.price
    _apply_listing_fields(product, payload)
    notify_favorited_customers_of_price_drop(db, product, previous_price)
    _record_product_changes(db, actor, product, before, fields)
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_shelf_status(
    db: Session, product_id: int, payload: ProductShelfStatusUpdate, actor: User | None = None
) -> ProductItem:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(product, ("name", "shelf_status"))
    product.shelf_status = payload.shelf_status
    _record_product_changes(db, actor, product, before, ("shelf_status",))
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_tags(
    db: Session, product_id: int, payload: ProductTagsUpdate, actor: User | None = None
) -> ProductItem:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(product, ("name", "category", "tags"))
    product.tags = payload.tags
    # 保留旧 category 字段作为主标签，兼容现有列表、查询和 Agent 数据结构。
    product.category = payload.tags[0]
    _record_product_changes(db, actor, product, before, ("category", "tags"))
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_product_pricing(
    db: Session, product_id: int, payload: ProductPricingUpdate, actor: User | None = None
) -> ProductItem:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")
    before = _capture_product_fields(
        product, ("name", "price", "original_price", "discount_percent")
    )
    previous_price = product.price
    discount_factor = Decimal("1") - payload.discount_percent / Decimal("100")
    sale_price = (payload.original_price * discount_factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    if sale_price < Decimal("0.01"):
        raise BusinessException(message="折后售价不能低于 0.01 元")
    product.original_price = payload.original_price
    product.discount_percent = payload.discount_percent
    product.price = sale_price
    notify_favorited_customers_of_price_drop(db, product, previous_price)
    _record_product_changes(
        db,
        actor,
        product,
        before,
        ("price", "original_price", "discount_percent"),
    )
    db.commit()
    db.refresh(product)
    return ProductItem.model_validate(product)


def update_review_reply(
    db: Session, review_id: int, merchant_reply: str, actor: User | None = None
) -> ReviewItem:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise BusinessException(message="评价不存在")
    product_name = db.query(Product.name).filter(Product.id == review.product_id).scalar()
    before_reply = review.merchant_reply
    review.merchant_reply = merchant_reply.strip()
    if actor is not None and before_reply != review.merchant_reply:
        notify_review_reply(db, review, actor, review.merchant_reply, review_owner_id(db, review))
    record_changes(
        db,
        actor,
        "商品",
        f"{product_name or review.product_id}的评价",
        [("商家回复", before_reply, review.merchant_reply)],
        rollback_data=build_rollback_data(
            "review",
            review.id,
            {"merchant_reply": (before_reply, review.merchant_reply)},
        ),
    )
    db.commit()
    db.refresh(review)
    buyer_name = (
        db.query(Order.buyer_name).filter(Order.id == review.order_id).scalar()
        if review.order_id is not None
        else None
    )
    return ReviewItem.from_row(review, buyer_name=buyer_name)


def get_order_detail(db: Session, order_id: int) -> OrderDetail:
    """订单详情：订单本身 + 这笔订单的评价。

    reviews.order_id 允许为空，所以订单可能没有评价，这种情况下 review 返回 null。
    """
    row = _orders_with_after_sales(db).filter(Order.id == order_id).first()
    if not row:
        raise BusinessException(message="订单不存在")

    order, product_name, after_sale = row
    review = (
        db.query(Review)
        .filter(Review.order_id == order_id)
        .order_by(Review.id.desc())
        .first()
    )

    return OrderDetail(
        order=_order_item(order, product_name, after_sale),
        review=(
            ReviewItem.from_row(
                review, product_name=product_name, buyer_name=order.buyer_name
            )
            if review
            else None
        ),
    )


def get_product_detail(db: Session, product_id: int) -> ProductDetail:
    """商品详情：把该商品的评价、订单与 Agent 产物（诊断报告/预警）串在一起。"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise BusinessException(message="商品不存在")

    after_sale_risk = ProductAfterSaleRisk.model_validate(collect_after_sale_risks(db, [product_id])[product_id])

    rating_rows = (
        db.query(Review.rating, func.count(Review.id))
        .filter(Review.product_id == product_id)
        .group_by(Review.rating)
        .all()
    )
    counts = {int(rating): int(count) for rating, count in rating_rows}
    avg_rating = (
        db.query(func.avg(Review.rating))
        .filter(Review.product_id == product_id)
        .scalar()
    )

    recent_reviews = (
        db.query(Review, Order.buyer_name.label("buyer_name"))
        .outerjoin(Order, Review.order_id == Order.id)
        .filter(Review.product_id == product_id)
        .order_by(Review.create_time.desc(), Review.id.desc())
        .limit(5)
        .all()
    )
    review_images = list(
        dict.fromkeys(
            image
            for (image,) in (
                db.query(Review.img)
                .filter(Review.product_id == product_id, Review.img.isnot(None))
                .order_by(Review.create_time.desc(), Review.id.desc())
                .all()
            )
            if image
        )
    )

    order_count, total_amount, last_order_time = (
        db.query(
            func.count(Order.id),
            func.coalesce(func.sum(Order.amount), 0),
            func.max(Order.create_time),
        )
        .filter(Order.product_id == product_id)
        .one()
    )
    sold_quantity = (
        db.query(func.coalesce(func.sum(Order.quantity), 0))
        .filter(Order.product_id == product_id, Order.status != "cancelled")
        .scalar()
    )
    recent_orders = (
        db.query(Order)
        .filter(Order.product_id == product_id)
        .order_by(Order.create_time.desc(), Order.id.desc())
        .limit(3)
        .all()
    )

    reports = (
        db.query(DiagnosisReport)
        .filter(DiagnosisReport.product_id == product_id)
        .order_by(DiagnosisReport.create_time.desc(), DiagnosisReport.id.desc())
        .limit(3)
        .all()
    )
    alerts = (
        db.query(AlertNotification)
        .filter(AlertNotification.product_id == product_id)
        .order_by(AlertNotification.create_time.desc(), AlertNotification.id.desc())
        .limit(3)
        .all()
    )

    return ProductDetail(
        product=ProductItem.from_row(product, after_sale_risk=after_sale_risk),
        after_sale_risk=after_sale_risk,
        review_images=review_images,
        review_summary=ProductReviewSummary(
            review_count=sum(counts.values()),
            avg_rating=round(float(avg_rating or 0), 2),
            bad_count=sum(count for rating, count in counts.items() if rating <= 2),
            rating_distribution=[
                RatingBucket(rating=star, count=counts.get(star, 0))
                for star in range(1, 6)
            ],
        ),
        recent_reviews=[
            ReviewItem.from_row(
                review, product_name=product.name, buyer_name=buyer_name
            )
            for review, buyer_name in recent_reviews
        ],
        order_summary=ProductOrderSummary(
            order_count=int(order_count or 0),
            sold_quantity=int(sold_quantity or 0),
            total_amount=round(float(total_amount or 0), 2),
            last_order_time=last_order_time,
        ),
        recent_orders=[
            OrderItem.from_row(o, product_name=product.name)
            for o in recent_orders
        ],
        reports=[
            DiagnosisReportItem.from_row(r, product_name=product.name)
            for r in reports
        ],
        alerts=[
            AlertItem.from_row(a, product_name=product.name)
            for a in alerts
        ],
    )
