"""首页数据概览的出参模型（看板统计）。"""

from pydantic import BaseModel

from app.schemas.ecommerce import RatingBucket
from app.schemas.report import AlertItem


class OverviewCards(BaseModel):
    """首页概览卡片：一眼看清数据规模与风险面。"""

    product_count: int
    order_count: int
    review_count: int
    avg_rating: float
    total_amount: float
    high_risk_reports: int
    pending_review_products: int
    unread_alerts: int


class OrderTrendPoint(BaseModel):
    """订单趋势上的某一天。"""

    date: str
    count: int
    amount: float


class ProductRatingStat(BaseModel):
    """按商品聚合的评分情况，用于找出口碑最差的商品。"""

    product_name: str
    review_count: int
    avg_rating: float
    bad_count: int


class OverviewStats(BaseModel):
    """首页数据概览：卡片 + 图表 + 榜单 + 最近预警。"""

    cards: OverviewCards
    order_trend: list[OrderTrendPoint]
    trend_days: int
    rating_distribution: list[RatingBucket]
    worst_products: list[ProductRatingStat]
    recent_alerts: list[AlertItem]
