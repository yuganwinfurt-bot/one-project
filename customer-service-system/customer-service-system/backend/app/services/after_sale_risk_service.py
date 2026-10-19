"""商品售后集中异常：数据库统计、分级预警和商家确认复核。

分母、分子使用同一批近30天下单的有效订单；按订单的最新申请去重。
申请数量并不代表质量问题已经成立，因此“待复核”必须由商家确认。
"""
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import aliased

from app.common.exceptions import BusinessException
from app.models.after_sale import AfterSaleRequest
from app.models.after_sale_risk import ProductAfterSaleRiskState
from app.models.alert_notification import AlertNotification
from app.models.order import Order
from app.models.product import Product
from app.models.staff_inbox import StaffInboxEvent
from app.services.platform_log_service import record_changes

WINDOW_DAYS = 30
WARNING_COUNT, WARNING_RATE = 2, 20
CRITICAL_COUNT, CRITICAL_RATE = 3, 30
RULE_TEXT = "近30天下单的有效订单：至少2笔售后且占比≥20%提醒；至少3笔且占比≥30%严重预警，建议人工复核。"
SCOPE_TEXT = "按订单最新售后申请去重，排除已拒绝申请和已取消订单；包含待审核、已同意及已完成申请。"
LEVEL_RANK = {"normal": 0, "warning": 1, "critical": 2}


def risk_level(count, order_count):
    # 整数交叉相乘，避免边界比例的浮点误差。
    if order_count and count >= CRITICAL_COUNT and count * 100 >= order_count * CRITICAL_RATE:
        return "critical"
    if order_count and count >= WARNING_COUNT and count * 100 >= order_count * WARNING_RATE:
        return "warning"
    return "normal"


def collect_after_sale_risks(db, product_ids, now=None):
    """只读，两次聚合查询返回整页商品的统计，不在列表读取时发通知。"""
    ids = list(dict.fromkeys(product_ids))
    if not ids:
        return {}
    now = now or datetime.now()
    start = now - timedelta(days=WINDOW_DAYS)
    scope = (
        Order.product_id.in_(ids), Order.status != "cancelled",
        Order.create_time >= start, Order.create_time <= now,
    )
    orders = dict(db.query(Order.product_id, func.count(Order.id)).filter(*scope).group_by(Order.product_id).all())
    latest_ids = db.query(
        AfterSaleRequest.order_id, func.max(AfterSaleRequest.id).label("request_id")
    ).filter(AfterSaleRequest.create_time <= now).group_by(AfterSaleRequest.order_id).subquery()
    application = aliased(AfterSaleRequest)
    rows = db.query(Order.product_id, application.service_type, func.count(Order.id)).select_from(Order).join(
        latest_ids, latest_ids.c.order_id == Order.id
    ).join(application, application.id == latest_ids.c.request_id).filter(
        *scope, application.product_id == Order.product_id,
        application.status.in_(["pending", "approved", "completed"]),
        application.service_type.in_(["refund", "return", "exchange"]),
    ).group_by(Order.product_id, application.service_type).all()
    types = {pid: {"refund": 0, "return": 0, "exchange": 0} for pid in ids}
    for pid, kind, count in rows:
        types[pid][kind] = int(count)
    result = {}
    for pid in ids:
        count = sum(types[pid].values())
        total = int(orders.get(pid, 0))
        level = risk_level(count, total)
        result[pid] = {
            "window_days": WINDOW_DAYS, "order_count": total, "after_sale_order_count": count,
            "refund_count": types[pid]["refund"], "return_count": types[pid]["return"],
            "exchange_count": types[pid]["exchange"],
            "after_sale_rate": round(count * 100 / total, 2) if total else 0,
            "level": level, "needs_review": level == "critical",
            "rule_text": RULE_TEXT, "scope_text": SCOPE_TEXT,
        }
    return result


def sync_product_after_sale_risk(db, product_id, actor_id=None, now=None):
    """与售后业务共用事务；商品行锁串行化同商品的风险状态和首次通知。"""
    product = db.query(Product).filter_by(id=product_id).with_for_update().first()
    if not product:
        return None
    db.flush()  # Session 关闭了 autoflush，必须让刚创建/审核的申请进入统计。
    summary = collect_after_sale_risks(db, [product_id], now)[product_id]
    state = db.query(ProductAfterSaleRiskState).filter_by(product_id=product_id).first()
    previous = state.level if state else "normal"
    if not state:
        state = ProductAfterSaleRiskState(product_id=product_id, level="normal")
        db.add(state)
    level = summary["level"]
    # 过期风险重新出现时应能再次提醒。
    if state.update_time and state.update_time < (now or datetime.now()) - timedelta(days=WINDOW_DAYS):
        previous = "normal"
    created = LEVEL_RANK[level] > LEVEL_RANK.get(previous, 0)
    if created:
        title = "商品售后集中异常：建议复核" if level == "critical" else "商品售后集中异常提醒"
        content = (
            f"商品【{product.name}】近{WINDOW_DAYS}天下单的{summary['order_count']}笔有效订单中，"
            f"{summary['after_sale_order_count']}笔涉及售后，占比{summary['after_sale_rate']:g}%；"
            f"退款{summary['refund_count']}笔、退货退款{summary['return_count']}笔、换货{summary['exchange_count']}笔。"
            f"{SCOPE_TEXT}"
            + ("已达到严重预警阈值，请核查原因，并在商品详情中确认是否标记待复核。" if level == "critical" else "已达到提醒阈值，请关注售后原因。")
        )
        alert = AlertNotification(title=title, content=content, level=level, product_id=product_id, created_by=actor_id)
        db.add(alert)
        db.flush()
        db.add(StaffInboxEvent(event_type="alert", target_id=alert.id, title=title, content=content))
    state.level = level
    # 即使级别相同，也记录本次检查时间，表示此状态确实经过重新计算。
    state.update_time = now or datetime.now()
    return {**summary, "alert_created": created}


def sync_all_after_sale_risks(db, actor_id=None):
    """补查已有售后及旧风险状态；重复检查不会重复推送同一级别预警。"""
    ids = {pid for (pid,) in db.query(AfterSaleRequest.product_id).distinct().all()}
    ids.update(pid for (pid,) in db.query(ProductAfterSaleRiskState.product_id).all())
    results = [sync_product_after_sale_risk(db, pid, actor_id) for pid in sorted(ids)]
    return {
        "checked": sum(item is not None for item in results),
        "alerts_created": sum(bool(item and item["alert_created"]) for item in results),
        "warning_products": sum(bool(item and item["level"] == "warning") for item in results),
        "critical_products": sum(bool(item and item["level"] == "critical") for item in results),
    }


def confirm_after_sale_risk_review(db, product_id, actor):
    summary = sync_product_after_sale_risk(db, product_id, actor.id)
    if summary is None:
        raise BusinessException(message="商品不存在", code=404)
    if not summary["needs_review"]:
        raise BusinessException(message="当前售后统计未达到严重预警阈值，请刷新后查看", code=400)
    product = db.get(Product, product_id)
    if product.review_status != "pending_review":
        product.review_status = "pending_review"
        record_changes(db, actor, "商品", product.name, [("复核状态", "正常", "待复核（售后集中异常）")])
    db.flush()
    return {"product_id": product.id, "review_status": product.review_status, "after_sale_risk": summary}
