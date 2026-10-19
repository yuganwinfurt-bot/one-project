"""巡检：系统用固定问题触发一次完整运行，并复用仍未确认的结果。"""

import logging
from typing import Any

from app.database import SessionLocal
from app.observability.models import AgentRun
from app.services.chat_events import _parse_sse
from app.services.chat_service import stream_chat
from app.services.confirmation_service import get_pending_confirmation

logger = logging.getLogger(__name__)


PATROL_QUESTION = "最近哪些商品差评最多？帮我看看并处理"


def _find_reusable_patrol(user_id: int, question: str) -> dict[str, Any] | None:
    """找一次仍然待确认的同问题巡检，找到就复用它，不重复跑图。

    只认「运行记录还没结束 + 图里的待确认状态还在」的那种：进程重启后
    MemorySaver 里的状态会丢，这时复用等于让用户去点一个失效的确认按钮。
    """
    db = SessionLocal()
    try:
        run = (
            db.query(AgentRun)
            .filter(
                AgentRun.user_id == user_id,
                AgentRun.question == question[:1000],
                AgentRun.status == "awaiting_confirm",
            )
            .order_by(AgentRun.id.desc())
            .first()
        )
        if not run:
            return None
        pending = get_pending_confirmation(run.thread_id, user_id)
        if not pending:
            return None
        return {
            "question": question,
            "answer": run.answer_preview or "",
            "route": run.route,
            "run_id": run.id,
            "thread_id": run.thread_id,
            "awaiting_confirmation": True,
            "actions": pending.get("actions") or [],
            "error": None,
            "reused": True,
        }
    finally:
        db.close()


def run_patrol(
    question: str = PATROL_QUESTION,
    user_id: int | None = None,
    reuse_pending: bool = True,
) -> dict[str, Any]:
    """系统触发的巡检：用固定问题跑一遍完整链路，返回结论而不逐字推送。

    复用 stream_chat，保证巡检与用户提问走的是同一张图、同一套观测记录；
    结论里带上 run_id 与待确认动作，由前端引导用户去运行历史确认执行。
    上一次巡检还没确认时直接沿用结果，避免连点攒出一堆待确认运行。
    """
    if reuse_pending and user_id is not None:
        existing = _find_reusable_patrol(user_id, question)
        if existing:
            logger.info("巡检沿用待确认运行 run_id=%s", existing["run_id"])
            return existing

    result: dict[str, Any] = {
        "question": question,
        "answer": "",
        "route": None,
        "run_id": None,
        "thread_id": None,
        "awaiting_confirmation": False,
        "actions": [],
        "error": None,
        "reused": False,
    }
    for chunk in stream_chat(question, user_id=user_id):
        event, data = _parse_sse(chunk)
        if event == "token":
            result["answer"] += data.get("content") or ""
        elif event == "action_pending":
            result["awaiting_confirmation"] = True
            result["thread_id"] = data.get("thread_id") or result["thread_id"]
            result["run_id"] = data.get("run_id") or result["run_id"]
            result["actions"] = data.get("actions") or []
        elif event == "done":
            result["route"] = data.get("route") or result["route"]
            result["run_id"] = data.get("run_id") or result["run_id"]
            result["thread_id"] = data.get("thread_id") or result["thread_id"]
            if data.get("awaiting_confirmation"):
                result["awaiting_confirmation"] = True
        elif event == "error":
            result["error"] = data.get("message")
            result["run_id"] = data.get("run_id") or result["run_id"]
            result["thread_id"] = data.get("thread_id") or result["thread_id"]
            if data.get("awaiting_confirmation"):
                result["awaiting_confirmation"] = True
    return result
