"""报告决策 Agent（lesson-10）。

职责：根据查询分析 Agent 留下的证据，规划报告/预警/待复核，
报告和预警自动执行，商品复核单独确认，全部通过白名单执行。查询类 MCP 调用不在这里做。
"""

from typing import Any

from app.agent import nodes
from app.agent.state import AgentState

AGENT_ID = "decision"
AGENT_LABEL = "报告决策 Agent"


def _tag(result: dict[str, Any]) -> dict[str, Any]:
    """给节点返回值打上决策 Agent 标记。"""
    out = dict(result)
    out["current_agent"] = AGENT_ID
    out["agent_label"] = AGENT_LABEL
    msg = out.get("status_message") or ""
    if msg and not str(msg).startswith("["):
        out["status_message"] = f"[{AGENT_LABEL}] {msg}"
    return out


def decide_actions(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_decide_actions(state))


def confirm_gate(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_confirm_gate(state))


def execute_automatic_actions(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_execute_automatic_actions(state))


def execute_actions(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_execute_actions(state))
