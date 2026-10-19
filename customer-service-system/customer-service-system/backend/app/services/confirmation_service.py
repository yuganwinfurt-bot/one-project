"""人工确认：待确认任务的查询、恢复执行与并发保护。

检查状态与恢复图必须在同一个临界区，避免重复确认把动作执行两次。
"""

import logging
from threading import Lock
from typing import Any

from langgraph.types import Command

from app.agent.graph import get_analysis_graph
from app.common.exceptions import BusinessException
from app.database import SessionLocal
from app.observability import service as obs_service
from app.observability.models import AgentRun

logger = logging.getLogger(__name__)

# 教学部署使用单进程：确认请求串行处理，避免两次请求同时恢复同一任务。
# 多进程部署应改用共享任务状态与数据库幂等约束。
_confirmation_lock = Lock()


def resume_actions(
    thread_id: str, approved: bool, user_id: int | None = None
) -> dict[str, Any]:
    """检查状态与恢复图必须处于同一个临界区，第二次确认会重新检查状态。"""
    with _confirmation_lock:
        return _resume_actions(thread_id, approved, user_id)


def get_pending_confirmation(thread_id: str, user_id: int) -> dict[str, Any] | None:
    """历史页恢复确认入口；MemorySaver 丢失后返回 None，不展示失效按钮。"""
    snap = get_analysis_graph().get_state({"configurable": {"thread_id": thread_id}})
    if not snap or snap.next != ("confirm_gate",):
        return None
    values = snap.values or {}
    if values.get("user_id") != user_id:
        return None
    return {
        "thread_id": thread_id,
        "message": "报告和预警已自动生成。以下商品复核操作会影响买家首页展示，请单独确认。",
        "risk_level": values.get("risk_level"),
        "reason": values.get("decide_reason"),
        "actions": values.get("pending_actions") or [],
    }


def _resume_actions(
    thread_id: str, approved: bool, user_id: int | None = None
) -> dict[str, Any]:
    """人工确认后执行商品复核；报告和预警已经在暂停前生成。"""
    if not thread_id:
        raise BusinessException(message="thread_id 不能为空")

    graph = get_analysis_graph()
    config = {"configurable": {"thread_id": thread_id}}
    snap = graph.get_state(config)
    if not snap or snap.next != ("confirm_gate",):
        raise BusinessException(
            message="没有待确认的任务，或会话已失效（服务重启会清空内存检查点）"
        )

    # 校验线程归属，防止他人用 thread_id 代为确认
    owner_id = (snap.values or {}).get("user_id")
    if user_id is not None and owner_id != user_id:
        raise BusinessException(message="无权确认该任务", code=403)

    for _ in graph.stream(
        Command(resume={"approved": approved}),
        config=config,
        stream_mode="updates",
    ):
        pass

    final = graph.get_state(config).values or {}
    status_message = final.get("status_message")
    executed = final.get("actions_executed") or []

    # 把确认结果补记到观测表
    db = SessionLocal()
    try:
        run = (
            db.query(AgentRun)
            .filter(AgentRun.thread_id == thread_id)
            .order_by(AgentRun.id.desc())
            .first()
        )
        if run:
            obs_service.add_step(
                db,
                run.id,
                step_name="executing" if approved else "cancelled",
                summary=status_message
                or (
                    f"已确认并执行 {len(executed)} 个动作"
                    if approved
                    else "用户取消，未执行动作"
                ),
                detail={"actions_executed": executed, "approved": approved},
            )
            obs_service.finish_run(
                db,
                run.id,
                status="success" if approved or executed else "cancelled",
            )
    except Exception:
        logger.exception("确认后更新观测记录失败 thread_id=%s", thread_id)
    finally:
        db.close()

    return {
        "thread_id": thread_id,
        "approved": approved,
        "actions_executed": executed,
        "human_approved": final.get("human_approved"),
        "status_message": status_message,
    }
