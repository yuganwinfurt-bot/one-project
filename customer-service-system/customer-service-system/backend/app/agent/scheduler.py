"""调度节点（lesson-10）：在两个 Agent 之间分派任务。

教学重点：不引入 AutoGen/CrewAI，只在同一个 LangGraph 里用两个薄包装 Agent
+ 调度节点切换「当前是谁在干活」。
"""

from typing import Any

from app.agent.state import AgentState

AGENT_ID = "scheduler"
AGENT_LABEL = "调度"


def node_scheduler_start(state: AgentState) -> dict[str, Any]:
    """图入口：先把任务交给查询分析 Agent。"""
    question = (state.get("question") or "").strip()
    preview = question[:40] + ("…" if len(question) > 40 else "")
    return {
        "current_agent": AGENT_ID,
        "agent_label": AGENT_LABEL,
        "next_agent": "analysis",
        "status_message": (
            f"[{AGENT_LABEL}] 收到问题「{preview}」，交由查询分析 Agent 处理"
        ),
    }


def node_scheduler_handoff(state: AgentState) -> dict[str, Any]:
    """查询分析完成后：把证据交给报告决策 Agent。"""
    evidence_count = len(state.get("evidence") or [])
    source = state.get("evidence_source") or "unknown"
    return {
        "current_agent": AGENT_ID,
        "agent_label": AGENT_LABEL,
        "next_agent": "decision",
        "status_message": (
            f"[{AGENT_LABEL}] 查询分析完成（证据 {evidence_count} 条，来源 {source}），"
            "交由报告决策 Agent"
        ),
    }
