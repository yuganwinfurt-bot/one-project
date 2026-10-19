"""诊断报告与预警通知的查询与已读状态维护。

本模块是唯一会写入通知状态的地方（标记已读），其余函数均为只读查询。
"""

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessException
from app.common.response import PageResponse
from app.models.alert_notification import AlertNotification
from app.models.diagnosis_report import DiagnosisReport
from app.models.product import Product
from app.schemas.report import AlertItem, DiagnosisReportDetail, DiagnosisReportItem


def list_diagnosis_reports(
    db: Session,
    page: int,
    page_size: int,
    keywords: str | None = None,
) -> PageResponse:
    """诊断报告列表（Agent 写操作的产物，按 id 倒序）。"""
    query = db.query(DiagnosisReport, Product.name.label("product_name")).outerjoin(
        Product, DiagnosisReport.product_id == Product.id
    )
    if keywords:
        like = f"%{keywords.strip()}%"
        query = query.filter(
            or_(
                DiagnosisReport.question.ilike(like),
                DiagnosisReport.summary.ilike(like),
                Product.name.ilike(like),
            )
        )
    total = query.count()
    rows = (
        query.order_by(DiagnosisReport.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items: list[DiagnosisReportItem] = []
    for report, product_name in rows:
        items.append(
            DiagnosisReportItem.from_row(report, product_name=product_name)
        )
    return PageResponse(list=items, total=total)


def get_diagnosis_report(db: Session, report_id: int) -> DiagnosisReportDetail:
    row = (
        db.query(DiagnosisReport, Product.name.label("product_name"))
        .outerjoin(Product, DiagnosisReport.product_id == Product.id)
        .filter(DiagnosisReport.id == report_id)
        .first()
    )
    if not row:
        raise BusinessException(message="诊断报告不存在")
    report, product_name = row
    return DiagnosisReportDetail.from_row(report, product_name=product_name)


def list_alert_notifications(
    db: Session,
    page: int,
    page_size: int,
    keywords: str | None = None,
) -> PageResponse:
    """预警通知列表（Agent 写操作的产物，按 id 倒序）。"""
    query = db.query(AlertNotification, Product.name.label("product_name")).outerjoin(
        Product, AlertNotification.product_id == Product.id
    )
    if keywords:
        like = f"%{keywords.strip()}%"
        query = query.filter(
            or_(
                AlertNotification.title.ilike(like),
                AlertNotification.content.ilike(like),
                Product.name.ilike(like),
            )
        )
    total = query.count()
    rows = (
        query.order_by(AlertNotification.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items: list[AlertItem] = []
    for alert, product_name in rows:
        items.append(
            AlertItem.from_row(alert, product_name=product_name)
        )
    return PageResponse(list=items, total=total)


def get_alert_summary(db: Session) -> dict[str, int]:
    """预警概览：总条数与未读数。

    页签角标要用它，而不是当前页数据——否则未读只统计到某一页、切到别的页签还看不见。
    """
    total = db.query(func.count(AlertNotification.id)).scalar() or 0
    unread = (
        db.query(func.count(AlertNotification.id))
        .filter(AlertNotification.is_read == 0)
        .scalar()
        or 0
    )
    return {"total": int(total), "unread": int(unread)}


def mark_alert_read(db: Session, alert_id: int) -> AlertItem:
    """把一条预警标记为已读：只改通知的已读状态，不碰任何业务数据。"""
    alert = (
        db.query(AlertNotification)
        .filter(AlertNotification.id == alert_id)
        .first()
    )
    if not alert:
        raise BusinessException(message="预警通知不存在")
    if not alert.is_read:
        alert.is_read = 1
        db.commit()
        db.refresh(alert)
    return AlertItem.model_validate(alert)


def mark_all_alerts_read(db: Session) -> int:
    """把所有未读预警标记为已读，返回本次更新的条数。"""
    updated = (
        db.query(AlertNotification)
        .filter(AlertNotification.is_read == 0)
        .update({AlertNotification.is_read: 1}, synchronize_session=False)
    )
    db.commit()
    return int(updated or 0)
