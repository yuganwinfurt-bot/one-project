"""查询分析 Agent（lesson-10）。

职责：判断查询路由、经 MCP 查数据、汇总证据、给出初步诊断材料。
底层仍复用 nodes.py 里的具体节点，这里只做「角色包装」，方便图与 SSE 区分 Agent。
"""

from typing import Any

from app.agent import nodes
from app.agent.state import AgentState

# 给前端 / 日志看的固定身份
AGENT_ID = "analysis"
AGENT_LABEL = "查询分析 Agent"


def _tag(result: dict[str, Any]) -> dict[str, Any]:
    """给节点返回值打上当前 Agent 标记，并在状态文案前加角色名。"""
    out = dict(result)
    out["current_agent"] = AGENT_ID
    out["agent_label"] = AGENT_LABEL
    msg = out.get("status_message") or ""
    if msg and not str(msg).startswith("["):
        out["status_message"] = f"[{AGENT_LABEL}] {msg}"
    return out


def route_question(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_route(state))


def structured_query(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_structured_query(state))


def semantic_query(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_semantic_query(state))


def judge_deepen(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_judge_deepen(state))


def deepen_semantic(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_deepen_semantic(state))


def prepare_evidence(state: AgentState) -> dict[str, Any]:
    return _tag(nodes.node_prepare_evidence(state))


# 条件边仍用 nodes 里的纯函数（不改行为）
select_query_branch = nodes.select_query_branch
select_after_structured = nodes.select_after_structured
select_after_judge = nodes.select_after_judge
