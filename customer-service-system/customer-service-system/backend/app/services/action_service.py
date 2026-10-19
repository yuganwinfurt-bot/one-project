"""Agent 允许的三种动作：报告和预警自动生成，商品复核确认后执行。

严格禁止：改订单状态、库存、价格、上下架（本模块故意不提供对应函数）。
"""

import json
import hashlib
from typing import Any

from sqlalchemy.orm import Session

from app.common.exceptions import BusinessException
from app.models.alert_notification import AlertNotification
from app.models.diagnosis_report import DiagnosisReport
from app.models.product import Product
from app.models.staff_inbox import StaffInboxEvent
from app.models.review import Review

# 白名单：只有这些动作名可以被执行
ALLOWED_ACTION_TYPES = {
    "write_report",
    "send_alert",
    "mark_pending_review",
}

# 与 ChatRequest / 表字段对齐，入库前截断防止超长报错
QUESTION_MAX_LEN = 1000


def execute_action(db: Session, action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """执行单条动作，返回执行结果摘要。"""
    action_type = action.get("type")
    if action_type not in ALLOWED_ACTION_TYPES:
        raise BusinessException(message=f"不允许的动作类型：{action_type}")

    if action_type == "write_report":
        return _write_report(db, action, context)
    if action_type == "send_alert":
        return _send_alert(db, action, context)
    if action_type == "mark_pending_review":
        return _mark_pending_review(db, action, context)

    raise BusinessException(message=f"未实现的动作：{action_type}")


def execute_actions(
    db: Session, actions: list[dict[str, Any]], context: dict[str, Any]
) -> list[dict[str, Any]]:
    """按顺序执行多条动作（同一事务）；失败时显式回滚。"""
    results: list[dict[str, Any]] = []
    try:
        for action in actions:
            result = execute_action(db, action, context)
            results.append(result)
            if result.get("report_id"):
                context["report_id"] = result["report_id"]
        db.commit()
        return results
    except Exception:
        db.rollback()
        raise


def _write_report(
    db: Session, action: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    question = str(context.get("question") or "")[:QUESTION_MAX_LEN]
    run_id = context.get("run_id")
    if run_id is not None:
        existing = db.query(DiagnosisReport).filter(DiagnosisReport.source_run_id == run_id).first()
        if existing:
            return {"type": "write_report", "ok": True, "report_id": existing.id, "reused": True}
    report = DiagnosisReport(
        source_run_id=run_id,
        question=question,
        summary=action.get("summary")
        or context.get("summary")
        or "根据查询证据生成的诊断报告",
        route=context.get("route"),
        risk_level=context.get("risk_level") or "low",
        evidence_count=int(context.get("evidence_count") or 0),
        evidence=json.loads(
            json.dumps(context.get("evidence") or [], ensure_ascii=False, default=str)
        ),
        product_id=action.get("product_id") or context.get("product_id"),
        created_by=context.get("user_id"),
    )
    db.add(report)
    db.flush()
    # 报告是可查看的业务产物；由真正的预警发一条消息，避免一事双推送。
    return {"type": "write_report", "ok": True, "report_id": report.id}


def _send_alert(
    db: Session, action: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """仅对新的低分证据快照发送一次提醒，不按检索片段数量反复升降级。"""
    product_id = action.get("product_id") or context.get("product_id")
    if not product_id:
        raise BusinessException(message="口碑预警需要明确商品")
    product = db.query(Product).filter(Product.id == int(product_id)).with_for_update().first()
    if not product:
        raise BusinessException(message="商品不存在")
    reviews = db.query(Review.id, Review.create_time).filter(
        Review.product_id == product.id, Review.rating.in_((1, 2)),
    ).order_by(Review.id).all()
    if len(reviews) < 2:
        return {"type": "send_alert", "ok": True, "skipped": True, "reason": "当前低分记录未达到提醒阈值"}
    level = "critical" if len(reviews) >= 3 else "warning"
    snapshot = f"review-risk:{product.id}:{level}:" + ",".join(str(row.id) for row in reviews)
    dedupe_key = hashlib.sha256(snapshot.encode()).hexdigest()
    previous = db.query(AlertNotification).filter(AlertNotification.dedupe_key == dedupe_key).first()
    if previous is None:
        # 已有老预警若覆盖当前全部低分记录，直接衔接，避免上线新规则时再通知一遍。
        legacy = db.query(AlertNotification).filter(
            AlertNotification.product_id == product.id,
            AlertNotification.title.in_(("触发预警通知", "商品低分口碑预警")),
        ).order_by(AlertNotification.id.desc()).first()
        newest_review = max(row.create_time for row in reviews)
        if legacy and legacy.level == level and newest_review <= legacy.create_time:
            previous = legacy
            previous.dedupe_key = dedupe_key
    if previous:
        if previous.report_id is None and context.get("report_id"):
            previous.report_id = context["report_id"]
        return {"type": "send_alert", "ok": True, "alert_id": previous.id, "reused": True}

    title = "商品低分口碑预警"
    content = f"商品「{product.name}」累计有 {len(reviews)} 条1～2星评价，请查看具体反馈核实口碑风险。"
    alert = AlertNotification(
        title=title, content=content, level=level, product_id=product.id,
        report_id=context.get("report_id"), dedupe_key=dedupe_key, created_by=context.get("user_id"),
    )
    db.add(alert)
    db.flush()
    db.add(StaffInboxEvent(event_type="alert", target_id=alert.id, title=title, content=content))
    return {"type": "send_alert", "ok": True, "alert_id": alert.id, "reused": False}


def _mark_pending_review(
    db: Session, action: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """仅修改 review_status，绝不改 shelf_status / price / stock。"""
    product_id = action.get("product_id") or context.get("product_id")
    if not product_id:
        raise BusinessException(message="标记待复核需要指定商品 ID")

    product = db.query(Product).filter(Product.id == int(product_id)).first()
    if not product:
        raise BusinessException(message=f"商品不存在：{product_id}")

    count = db.query(Review).filter(Review.product_id == product.id, Review.rating.in_((1, 2))).count()
    if count < 3:
        return {"type": "mark_pending_review", "ok": True, "skipped": True, "reason": "实时低分记录未达到复核阈值"}
    product.review_status = "pending_review"
    db.flush()
    return {
        "type": "mark_pending_review",
        "ok": True,
        "product_id": product.id,
        "review_status": product.review_status,
    }
