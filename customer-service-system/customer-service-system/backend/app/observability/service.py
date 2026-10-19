"""观测服务：创建运行、追加步骤、结束运行、查历史、提交反馈、统计看板。"""

import json
from datetime import date, timedelta
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessException
from app.common.response import PageResponse
from app.observability.models import AgentFeedback, AgentRun, AgentRunStep
from app.schemas.observability import (
    MetricsBucket,
    MetricsCards,
    MetricsDayPoint,
    MetricsStats,
    MetricsStepStat,
)

ANSWER_PREVIEW_MAX = 500
SUMMARY_MAX = 500


def create_run(
    db: Session,
    *,
    thread_id: str,
    question: str,
    user_id: int | None,
) -> AgentRun:
    """开始一次新的运行记录。"""
    run = AgentRun(
        thread_id=thread_id,
        question=question[:1000],
        user_id=user_id,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def add_step(
    db: Session,
    run_id: int,
    *,
    step_name: str,
    summary: str,
    success: bool = True,
    elapsed_ms: int | None = None,
    detail: dict[str, Any] | None = None,
) -> AgentRunStep:
    """追加一步；序号按当前已有步骤自动递增。"""
    count = (
        db.query(AgentRunStep).filter(AgentRunStep.run_id == run_id).count()
    )
    step = AgentRunStep(
        run_id=run_id,
        step_order=count + 1,
        step_name=step_name[:50],
        summary=(summary or "")[:SUMMARY_MAX],
        success=1 if success else 0,
        elapsed_ms=elapsed_ms,
        detail=json.dumps(detail, ensure_ascii=False) if detail else None,
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def finish_run(
    db: Session,
    run_id: int,
    *,
    status: str,
    elapsed_ms: int | None = None,
    route: str | None = None,
    evidence_source: str | None = None,
    error_message: str | None = None,
    answer_preview: str | None = None,
) -> AgentRun:
    """结束运行并回填总览字段。"""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).with_for_update().first()
    if not run:
        raise BusinessException(message="运行记录不存在")
    # 浏览器侧模型尚未交回回答时，不能提前记成成功。
    run.status = "answering" if status == "success" and run.answer_context and not (run.answer_text or answer_preview) else status
    if elapsed_ms is not None:
        run.elapsed_ms = elapsed_ms
    if route is not None:
        run.route = route
    if evidence_source is not None:
        run.evidence_source = evidence_source
    if error_message is not None:
        run.error_message = error_message[:500]
    if answer_preview:
        run.answer_preview = answer_preview[:ANSWER_PREVIEW_MAX]
        run.answer_text = answer_preview
        from app.services.saved_reports import update_report_answer
        update_report_answer(db, run_id, answer_preview)
    db.commit()
    db.refresh(run)
    return run


def update_run_answer_preview(
    db: Session, run_id: int, *, answer: str, user_id: int | None = None
) -> AgentRun:
    """保存浏览器侧 Agent 模型生成的最终回答；普通用户只能更新自己的运行。"""
    query = db.query(AgentRun).filter(AgentRun.id == run_id)
    if user_id is not None:
        query = query.filter(AgentRun.user_id == user_id)
    run = query.with_for_update().first()
    if not run:
        raise BusinessException(message="运行记录不存在")
    run.answer_preview = answer[:ANSWER_PREVIEW_MAX]
    run.answer_text = answer
    from app.services.saved_reports import update_report_answer
    update_report_answer(db, run_id, answer)
    if run.status == "answering":
        run.status = "success"
    db.commit()
    db.refresh(run)
    return run


def save_run_answer_context(db: Session, run_id: int, messages: list[dict[str, str]]) -> None:
    """先持久化分析结果，再交给浏览器生成回答；断线重连无需重跑业务动作。"""
    run = db.get(AgentRun, run_id)
    if run:
        run.answer_context = messages
        db.commit()


def list_runs(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    user_id: int | None = None,
    only_mine: bool = False,
    sort_by: str | None = None,
    sort_order: str = "asc",
) -> PageResponse:
    """分页查运行列表；only_mine 时只看当前用户。"""
    page = max(page, 1)
    page_size = min(max(page_size, 1), 50)
    query = db.query(AgentRun)
    if only_mine and user_id is not None:
        query = query.filter(AgentRun.user_id == user_id)
    total = query.count()
    sort_columns = {
        "status": case(
            (AgentRun.status.in_(("running", "answering")), 0),
            (AgentRun.status == "awaiting_confirm", 1),
            (AgentRun.status == "success", 2),
            (AgentRun.status == "error", 3),
            (AgentRun.status == "cancelled", 4),
            else_=5,
        ),
        "create_time": AgentRun.create_time,
    }
    if sort_by in sort_columns:
        column = sort_columns[sort_by]
        primary_order = column.desc() if sort_order == "desc" else column.asc()
        ordering = (primary_order, AgentRun.id.desc())
    else:
        ordering = (AgentRun.id.desc(),)
    rows = (
        query.order_by(*ordering)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [_run_brief(r) for r in rows]
    return PageResponse(list=items, total=total)


def get_run_detail(db: Session, run_id: int, user_id: int | None = None) -> dict:
    """查看某次运行详情（含步骤）；可选校验归属。"""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise BusinessException(message="运行记录不存在")
    # 非管理员场景：若传入 user_id，仅允许看自己的（教学简化：有 user_id 就校验）
    if user_id is not None and run.user_id is not None and run.user_id != user_id:
        raise BusinessException(message="无权查看该运行记录", code=403)

    steps = (
        db.query(AgentRunStep)
        .filter(AgentRunStep.run_id == run_id)
        .order_by(AgentRunStep.step_order.asc())
        .all()
    )
    feedback = (
        db.query(AgentFeedback)
        .filter(AgentFeedback.run_id == run_id)
        .order_by(AgentFeedback.id.desc())
        .first()
    )
    return {
        **_run_brief(run),
        "answer_preview": run.answer_preview,
        "error_message": run.error_message,
        "steps": [_step_dict(s) for s in steps],
        "feedback": _feedback_dict(feedback) if feedback else None,
    }


def submit_feedback(
    db: Session,
    *,
    run_id: int,
    user_id: int,
    rating: int,
    comment: str | None = None,
    is_admin: bool = False,
) -> dict:
    """提交或更新点赞/点踩（同一用户对同一运行只保留最新一条）。"""
    if rating not in (1, -1):
        raise BusinessException(message="rating 只能是 1（赞）或 -1（踩）")

    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise BusinessException(message="运行记录不存在")

    if not is_admin and run.user_id != user_id:
        raise BusinessException(message="无权评价该运行记录", code=403)

    existing = (
        db.query(AgentFeedback)
        .filter(AgentFeedback.run_id == run_id, AgentFeedback.user_id == user_id)
        .first()
    )
    if existing:
        existing.rating = rating
        existing.comment = (comment or None)
        if existing.comment and len(existing.comment) > 500:
            existing.comment = existing.comment[:500]
        db.commit()
        db.refresh(existing)
        return _feedback_dict(existing)

    row = AgentFeedback(
        run_id=run_id,
        user_id=user_id,
        rating=rating,
        comment=(comment[:500] if comment else None),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _feedback_dict(row)


def get_stats(
    db: Session,
    *,
    user_id: int | None = None,
    only_mine: bool = False,
    trend_days: int = 14,
) -> MetricsStats:
    """观测看板统计：运行质量、路由分布、阶段耗时、运行量趋势。

    与 list_runs 同一套可见性规则：only_mine 为真时只统计当前用户自己的运行。
    """
    scope = only_mine and user_id is not None

    def scoped(query):
        return query.filter(AgentRun.user_id == user_id) if scope else query

    status_rows = (
        scoped(db.query(AgentRun.status, func.count(AgentRun.id)))
        .group_by(AgentRun.status)
        .all()
    )
    by_status = {status: int(count) for status, count in status_rows}
    total = sum(by_status.values())
    success = by_status.get("success", 0)
    failed = by_status.get("error", 0)
    cancelled = by_status.get("cancelled", 0)
    # running / awaiting_confirm 都属于「还没结束」，不计入成功率分母
    unfinished = sum(by_status.get(status, 0) for status in ("running", "answering", "awaiting_confirm"))
    closed = success + failed + cancelled

    avg_elapsed = (
        scoped(db.query(func.avg(AgentRun.elapsed_ms)))
        .filter(AgentRun.status == "success", AgentRun.elapsed_ms.isnot(None))
        .scalar()
    )

    feedback_query = db.query(
        AgentFeedback.rating, func.count(AgentFeedback.id)
    ).join(AgentRun, AgentFeedback.run_id == AgentRun.id)
    if scope:
        feedback_query = feedback_query.filter(AgentRun.user_id == user_id)
    feedback_rows = feedback_query.group_by(AgentFeedback.rating).all()
    by_rating = {int(rating): int(count) for rating, count in feedback_rows}
    up_count = by_rating.get(1, 0)
    down_count = by_rating.get(-1, 0)
    rated = up_count + down_count

    cards = MetricsCards(
        total_runs=total,
        success_runs=success,
        failed_runs=failed,
        cancelled_runs=cancelled,
        unfinished_runs=unfinished,
        success_rate=round(success / closed * 100, 1) if closed else 0.0,
        avg_elapsed_ms=int(avg_elapsed or 0),
        up_count=up_count,
        down_count=down_count,
        up_rate=round(up_count / rated * 100, 1) if rated else 0.0,
    )

    return MetricsStats(
        cards=cards,
        route_distribution=_route_distribution(db, scope, user_id),
        step_stats=_step_stats(db, scope, user_id),
        run_trend=_run_trend(db, scope, user_id, trend_days),
        trend_days=trend_days,
    )


def _route_distribution(
    db: Session, scope: bool, user_id: int | None
) -> list[MetricsBucket]:
    """各类查询与模型对话的运行分布。"""
    query = db.query(AgentRun.route, func.count(AgentRun.id))
    if scope:
        query = query.filter(AgentRun.user_id == user_id)
    rows = query.group_by(AgentRun.route).all()
    labels = {"structured": "结构化", "semantic": "语义检索", "conversation": "模型对话"}
    buckets = [
        MetricsBucket(name=labels.get(route, "未判定"), count=int(count))
        for route, count in rows
    ]
    return sorted(buckets, key=lambda b: b.count, reverse=True)


def _step_stats(db: Session, scope: bool, user_id: int | None) -> list[MetricsStepStat]:
    """各阶段平均耗时，倒序取前 8，用来定位慢在哪一步。

    历史数据里同一阶段有 route / routing 两种名字，统计时合并成一个。
    """
    step_label = case(
        (AgentRunStep.step_name == "route", "routing"), else_=AgentRunStep.step_name
    )
    query = (
        db.query(
            step_label.label("step_name"),
            func.count(AgentRunStep.id),
            func.avg(AgentRunStep.elapsed_ms),
            func.max(AgentRunStep.elapsed_ms),
        )
        .join(AgentRun, AgentRunStep.run_id == AgentRun.id)
        .filter(AgentRunStep.elapsed_ms.isnot(None))
    )
    if scope:
        query = query.filter(AgentRun.user_id == user_id)
    rows = (
        query.group_by(step_label)
        .order_by(func.avg(AgentRunStep.elapsed_ms).desc())
        .limit(8)
        .all()
    )
    return [
        MetricsStepStat(
            step_name=step_name,
            count=int(count),
            avg_ms=int(avg_ms or 0),
            max_ms=int(max_ms or 0),
        )
        for step_name, count, avg_ms, max_ms in rows
    ]


def _run_trend(
    db: Session, scope: bool, user_id: int | None, days: int
) -> list[MetricsDayPoint]:
    """近 N 天每天的运行量，没运行的日子补 0。"""
    today = date.today()
    start = today - timedelta(days=days - 1)
    day_col = func.date(AgentRun.create_time)
    query = db.query(day_col.label("day"), func.count(AgentRun.id)).filter(
        day_col >= start, day_col <= today
    )
    if scope:
        query = query.filter(AgentRun.user_id == user_id)
    rows = query.group_by(day_col).all()
    by_day = {_as_date(day): int(count) for day, count in rows}
    return [
        MetricsDayPoint(
            date=(start + timedelta(days=offset)).isoformat(),
            count=by_day.get(start + timedelta(days=offset), 0),
        )
        for offset in range(days)
    ]


def _as_date(value) -> date:
    """不同驱动返回的日期可能是 date 也可能是字符串，统一成 date。"""
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _run_brief(run: AgentRun) -> dict:
    return {
        "id": run.id,
        "thread_id": run.thread_id,
        "question": run.question,
        "user_id": run.user_id,
        "route": run.route,
        "evidence_source": run.evidence_source,
        "status": run.status,
        "elapsed_ms": run.elapsed_ms,
        "create_time": run.create_time.isoformat(sep=" ", timespec="seconds")
        if run.create_time
        else None,
    }


def _step_dict(step: AgentRunStep) -> dict:
    detail = None
    if step.detail:
        try:
            detail = json.loads(step.detail)
        except json.JSONDecodeError:
            detail = step.detail
    return {
        "id": step.id,
        "step_order": step.step_order,
        "step_name": step.step_name,
        "summary": step.summary,
        "success": bool(step.success),
        "elapsed_ms": step.elapsed_ms,
        "detail": detail,
    }


def _feedback_dict(fb: AgentFeedback) -> dict:
    return {
        "id": fb.id,
        "run_id": fb.run_id,
        "user_id": fb.user_id,
        "rating": fb.rating,
        "comment": fb.comment,
    }
