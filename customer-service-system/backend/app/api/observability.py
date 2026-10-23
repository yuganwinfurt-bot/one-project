"""运行历史与反馈接口。"""

from typing import Annotated, Literal

from fastapi import APIRouter, Query

from app.common.response import Response
from app.dependencies.auth import CurrentUser, DbSession
from app.observability import service as obs_service
from app.schemas.observability import AnswerPreviewRequest, FeedbackRequest
from app.services import confirmation_service

router = APIRouter(prefix="/observability", tags=["可观测性"])


@router.get("/stats")
def get_stats(
    db: DbSession,
    current_user: CurrentUser,
    only_mine: Annotated[bool, Query(description="是否只统计自己的运行")] = True,
    trend_days: Annotated[int, Query(ge=7, le=90, description="运行量趋势天数")] = 14,
):
    """观测看板：成功率、平均耗时、路由分布、阶段耗时、运行量趋势。"""
    # 非管理员强制只看自己的，与 /runs 保持同一套可见性规则
    effective_only_mine = True if current_user.role != "admin" else only_mine
    data = obs_service.get_stats(
        db,
        user_id=current_user.id,
        only_mine=effective_only_mine,
        trend_days=trend_days,
    )
    return Response.success(data=data)


@router.get("/runs")
def list_runs(
    db: DbSession,
    current_user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 10,
    only_mine: Annotated[bool, Query(description="是否只看自己的记录")] = True,
    sort_by: Literal["status", "create_time"] | None = None,
    sort_order: Literal["asc", "desc"] = "asc",
):
    """分页查询历史运行列表。普通用户只能看自己的。"""
    # 非管理员强制只看自己的，避免误传 only_mine=false 看到他人记录
    effective_only_mine = True if current_user.role != "admin" else only_mine
    data = obs_service.list_runs(
        db,
        page=page,
        page_size=page_size,
        user_id=current_user.id,
        only_mine=effective_only_mine,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    # 运行历史写在数据库里，但确认检查点当前使用 MemorySaver；
    # 服务重启后把无法恢复的待确认行标成失效，避免页面显示成仍可操作。
    for item in data.list:
        if item.get("status") != "awaiting_confirm":
            continue
        pending = confirmation_service.get_pending_confirmation(
            item["thread_id"], current_user.id
        )
        if pending is None:
            item["status"] = "confirmation_expired"
    return Response.success(data=data)


@router.get("/runs/{run_id}")
def get_run(
    run_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """查看某次运行的步骤详情。"""
    # 管理员可看全部；普通用户只能看自己的
    check_user = None if current_user.role == "admin" else current_user.id
    data = obs_service.get_run_detail(db, run_id, user_id=check_user)
    pending_confirmation = confirmation_service.get_pending_confirmation(
        data["thread_id"], current_user.id
    )
    data["pending_confirmation"] = pending_confirmation
    data["confirmation_expired"] = (
        data["status"] == "awaiting_confirm" and pending_confirmation is None
    )
    if data["confirmation_expired"]:
        pending_step = next(
            (step for step in data["steps"] if step["step_name"] == "action_pending"),
            None,
        )
        pending_detail = (pending_step or {}).get("detail") or {}
        data["expired_actions"] = pending_detail.get("actions", [])
    return Response.success(data=data)


@router.post("/runs/{run_id}/feedback")
def post_feedback(
    run_id: int,
    body: FeedbackRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """对某次运行点赞或点踩。"""
    data = obs_service.submit_feedback(
        db,
        run_id=run_id,
        user_id=current_user.id,
        rating=body.rating,
        comment=body.comment,
        is_admin=current_user.role == "admin",
    )
    return Response.success(data=data)


@router.put("/runs/{run_id}/answer")
def put_run_answer(
    run_id: int,
    body: AnswerPreviewRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """保存浏览器侧 Agent 模型的回答摘要到本次运行记录。"""
    check_user = None if current_user.role == "admin" else current_user.id
    run = obs_service.update_run_answer_preview(
        db, run_id, answer=body.answer, user_id=check_user
    )
    return Response.success(data={"id": run.id, "answer_preview": run.answer_preview})
