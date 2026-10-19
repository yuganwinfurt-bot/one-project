"""电商业务表的出入参模型：商品 / 订单 / 评价。"""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_serializer, field_validator

from app.schemas.base import RowItem
from app.schemas.report import AlertItem, DiagnosisReportItem


class ProductAfterSaleRisk(BaseModel):
    window_days: int
    order_count: int
    after_sale_order_count: int
    refund_count: int
    return_count: int
    exchange_count: int
    after_sale_rate: float
    level: str
    needs_review: bool
    rule_text: str
    scope_text: str


class ProductItem(RowItem):
    id: int
    name: str
    category: str
    tags: list[str] | None = None
    description: str
    image_url: str | None = None
    image_urls: list[str] | None = None
    ai_detail: str | None = None
    price: Decimal
    original_price: Decimal | None = None
    discount_percent: Decimal = Decimal("0")
    stock: int
    shelf_status: str
    review_status: str
    after_sale_risk: ProductAfterSaleRisk | None = None
    create_time: datetime | None = None

    @field_serializer("price")
    def _price(self, v: Decimal) -> float:
        return float(v)

    @field_serializer("original_price")
    def _original_price(self, v: Decimal | None) -> float | None:
        return float(v) if v is not None else None

    @field_serializer("discount_percent")
    def _discount_percent(self, v: Decimal) -> float:
        return float(v)

    @field_serializer("create_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


class StorefrontProduct(BaseModel):
    """商品首页卡片需要展示的商品与销售/评价汇总。"""

    id: int
    name: str
    category: str
    tags: list[str] | None = None
    description: str
    image_url: str | None = None
    image_urls: list[str] | None = None
    ai_detail: str | None = None
    price: Decimal
    original_price: Decimal | None = None
    discount_percent: Decimal = Decimal("0")
    stock: int
    sold_quantity: int = 0
    review_count: int = 0
    avg_rating: float = 0

    @field_serializer("price")
    def _price(self, value: Decimal) -> float:
        return float(value)

    @field_serializer("original_price")
    def _original_price(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None

    @field_serializer("discount_percent")
    def _discount_percent(self, value: Decimal) -> float:
        return float(value)


class StorefrontPage(BaseModel):
    list: list[StorefrontProduct]
    total: int
    categories: list[str]


class ProductAiDetailUpdate(BaseModel):
    ai_detail: str = Field(min_length=2, max_length=12000)


class ProductDescriptionUpdate(BaseModel):
    description: str = Field(min_length=1, max_length=10000)

    @field_validator("description")
    @classmethod
    def _strip_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("商品介绍不能为空")
        return value


class ProductNameUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("商品名称不能为空")
        return value


class ProductTagsUpdate(BaseModel):
    tags: list[str] = Field(min_length=1)

    @field_validator("tags")
    @classmethod
    def _clean_tags(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("标签不能为空")
        if any(len(value) > 50 for value in cleaned):
            raise ValueError("每个标签不能超过 50 个字符")
        return list(dict.fromkeys(cleaned))


class ProductPricingUpdate(BaseModel):
    original_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    discount_percent: Decimal = Field(
        ge=0, le=Decimal("99.99"), max_digits=5, decimal_places=2
    )


class ProductStockUpdate(BaseModel):
    stock: int = Field(ge=0, le=2147483647)


class ProductManagementUpdate(BaseModel):
    """商品数据页集中维护名称、类目、折后售价、库存与优惠幅度。"""

    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    discount_percent: Decimal = Field(
        ge=0, le=Decimal("99.99"), max_digits=5, decimal_places=2
    )

    @field_validator("name", "category")
    @classmethod
    def _strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("商品名称和类目不能为空")
        return value


class ProductListingFields(BaseModel):
    """新建或编辑并上架商品所需的完整资料。"""

    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    description: str = Field(default="", max_length=10000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    discount_percent: Decimal = Field(
        ge=0, le=Decimal("99.99"), max_digits=5, decimal_places=2
    )
    image_urls: list[str] = Field(default_factory=list, max_length=3)

    @field_validator("name", "category")
    @classmethod
    def _strip_listing_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("商品名称和类目不能为空")
        return value

    @field_validator("description")
    @classmethod
    def _strip_listing_description(cls, value: str) -> str:
        return value.strip()

    @field_validator("image_urls")
    @classmethod
    def _clean_listing_images(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("商品图片地址不能为空")
        if any(len(value) > 500 for value in cleaned):
            raise ValueError("商品图片地址不能超过 500 个字符")
        return list(dict.fromkeys(cleaned))


class ProductListingCreate(ProductListingFields):
    pass


class ProductListingUpdate(ProductListingFields):
    pass


class ProductShelfStatusUpdate(BaseModel):
    shelf_status: Literal["on_sale", "off_shelf"]


class OrderItem(RowItem):
    id: int
    order_no: str
    product_id: int
    product_name: str | None = None
    buyer_name: str
    buyer_user_id: int | None = None
    quantity: int
    amount: Decimal
    status: str
    tracking_no: str | None = None
    exchange_tracking_no: str | None = None
    after_sale_service_type: str | None = None
    after_sale_status: str | None = None
    return_tracking_no: str | None = None
    after_sale: dict | None = None
    create_time: datetime | None = None


    @field_serializer("amount")
    def _amount(self, v: Decimal) -> float:
        return float(v)

    @field_serializer("create_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


class OrderShipmentUpdate(BaseModel):
    tracking_no: str = Field(min_length=1, max_length=100)

    @field_validator("tracking_no")
    @classmethod
    def _strip_tracking_no(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("请填写物流单号")
        return value


class ReviewItem(RowItem):
    id: int
    product_id: int
    product_name: str | None = None
    order_id: int | None = None
    buyer_name: str | None = None
    buyer_user_id: int | None = None
    rating: int
    content: str
    img: str | None = None
    merchant_reply: str | None = None
    create_time: datetime | None = None


    @field_serializer("create_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


class ProductImageUpdate(BaseModel):
    image_url: str | None = Field(max_length=500)


class ProductImagesUpdate(BaseModel):
    image_urls: list[str]

    @field_validator("image_urls")
    @classmethod
    def _clean_image_urls(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("图片地址不能为空")
        if any(len(value) > 500 for value in cleaned):
            raise ValueError("图片地址不能超过 500 个字符")
        return list(dict.fromkeys(cleaned))


class ReviewReplyUpdate(BaseModel):
    merchant_reply: str = Field(min_length=1, max_length=2000)

    @field_validator("merchant_reply")
    @classmethod
    def _strip_reply(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("回复内容不能为空")
        return value


class RatingBucket(BaseModel):
    """评分分布中的某一档（1~5 星）。"""

    rating: int
    count: int


class ProductReviewSummary(BaseModel):
    """单个商品的评价汇总。"""

    review_count: int
    avg_rating: float
    bad_count: int
    rating_distribution: list[RatingBucket]


class ProductOrderSummary(BaseModel):
    """单个商品的订单汇总。"""

    order_count: int
    sold_quantity: int
    total_amount: float
    last_order_time: datetime | None = None

    @field_serializer("last_order_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


class ProductDetail(BaseModel):
    """商品详情：基础信息 + 评价/订单汇总 + 最近记录 + 该商品的 Agent 产物。"""

    product: ProductItem
    review_images: list[str]
    review_summary: ProductReviewSummary
    recent_reviews: list[ReviewItem]
    order_summary: ProductOrderSummary
    recent_orders: list[OrderItem]
    reports: list[DiagnosisReportItem]
    alerts: list[AlertItem]
    after_sale_risk: ProductAfterSaleRisk | None = None


class OrderDetail(BaseModel):
    """订单详情：订单本身 + 这笔订单对应的评价（可能没有）。"""

    order: OrderItem
    review: ReviewItem | None = None
