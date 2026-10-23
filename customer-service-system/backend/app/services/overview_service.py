"""首页数据概览的统计查询（看板用）。"""

from datetime import date, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.alert_notification import AlertNotification
from app.models.diagnosis_report import DiagnosisReport
from app.models.order import Order
from app.models.product import Product
from app.models.review import Review
from app.schemas.ecommerce import RatingBucket
from app.schemas.overview import (
    OrderTrendPoint,
    OverviewCards,
    OverviewStats,
    ProductRatingStat,
)
from app.schemas.report import AlertItem


def get_overview(db: Session, trend_days: int = 30) -> OverviewStats:
    """首页数据概览：规模、趋势、口碑榜单与最近预警。

    趋势按「今天往前 trend_days 天」的真实日历聚合，不按数据里的最大日期对齐，
    这样图表横轴始终是真正的日期，不会被误读。
    """
    cards = OverviewCards(
        product_count=_count(db, Product.id),
        order_count=_count(db, Order.id),
        review_count=_count(db, Review.id),
        avg_rating=round(float(db.query(func.avg(Review.rating)).scalar() or 0), 2),
        # 成交额排除已取消订单：种子数据里有状态演示用的 cancelled 单，不该计入
        total_amount=round(
            float(
                db.query(func.coalesce(func.sum(Order.amount), 0))
                .filter(Order.status.in_(("paid", "shipped", "completed")))
                .scalar()
                or 0
            ),
            2,
        ),
        high_risk_reports=_count(
            db, DiagnosisReport.id, DiagnosisReport.risk_level == "high"
        ),
        pending_review_products=_count(
            db, Product.id, Product.review_status == "pending_review"
        ),
        unread_alerts=_count(db, AlertNotification.id, AlertNotification.is_read == 0),
    )

    return OverviewStats(
        cards=cards,
        order_trend=_order_trend(db, trend_days),
        trend_days=trend_days,
        rating_distribution=_rating_distribution(db),
        worst_products=_worst_products(db),
        recent_alerts=_recent_alerts(db),
    )


def _count(db: Session, column, *filters) -> int:
    """统计行数，filters 为空时统计全表。"""
    query = db.query(func.count(column))
    if filters:
        query = query.filter(*filters)
    return int(query.scalar() or 0)


def _order_trend(db: Session, days: int) -> list[OrderTrendPoint]:
    """近 N 天每日订单量与成交额；没有订单的日期补 0，保证折线连续。"""
    today = date.today()
    start = today - timedelta(days=days - 1)
    day_col = func.date(Order.create_time)
    rows = (
        db.query(
            day_col.label("day"),
            func.count(Order.id),
            func.coalesce(func.sum(case((Order.status.in_(("paid", "shipped", "completed")), Order.amount), else_=0)), 0),
        )
        .filter(day_col >= start, day_col <= today)
        .group_by(day_col)
        .all()
    )
    by_day = {_as_date(day): (int(count), float(amount)) for day, count, amount in rows}
    trend: list[OrderTrendPoint] = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        count, amount = by_day.get(day, (0, 0.0))
        trend.append(
            OrderTrendPoint(date=day.isoformat(), count=count, amount=round(amount, 2))
        )
    return trend


def _rating_distribution(db: Session) -> list[RatingBucket]:
    """1~5 星各有多少条评价，缺档补 0。"""
    rows = db.query(Review.rating, func.count(Review.id)).group_by(Review.rating).all()
    counts = {int(rating): int(count) for rating, count in rows}
    return [RatingBucket(rating=star, count=counts.get(star, 0)) for star in range(1, 6)]


def _worst_products(db: Session, limit: int = 5) -> list[ProductRatingStat]:
    """口碑最差的商品：先看差评（<=2 星）条数，再看平均分。"""
    bad_count = func.sum(case((Review.rating <= 2, 1), else_=0))
    rows = (
        db.query(
            Product.name,
            func.count(Review.id).label("review_count"),
            func.avg(Review.rating).label("avg_rating"),
            bad_count.label("bad_count"),
        )
        .join(Review, Review.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(bad_count.desc(), func.avg(Review.rating).asc())
        .limit(limit)
        .all()
    )
    return [
        ProductRatingStat(
            product_name=name,
            review_count=int(review_count),
            avg_rating=round(float(avg_rating or 0), 2),
            bad_count=int(bad_count_value or 0),
        )
        for name, review_count, avg_rating, bad_count_value in rows
    ]


def _recent_alerts(db: Session, limit: int = 5) -> list[AlertItem]:
    """最近触发的预警，首页只展示最新几条。"""
    rows = (
        db.query(AlertNotification, Product.name.label("product_name"))
        .outerjoin(Product, AlertNotification.product_id == Product.id)
        .order_by(AlertNotification.id.desc())
        .limit(limit)
        .all()
    )
    items: list[AlertItem] = []
    for alert, product_name in rows:
        items.append(
            AlertItem.from_row(alert, product_name=product_name)
        )
    return items


def _as_date(value) -> date:
    """不同驱动返回的日期可能是 date 也可能是字符串，统一成 date。"""
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
