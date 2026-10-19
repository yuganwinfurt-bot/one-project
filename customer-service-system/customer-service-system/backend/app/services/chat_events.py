"""对话事件协议：事件名映射、SSE 格式化与拆分、进度事件构造。

协议约定：一条事件 = `event: 名称` + `data: JSON` + 一个空行。
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generator


_NODE_STAGE = {
    "scheduler_start": "scheduling",
    "scheduler_handoff": "scheduling",
    "route_question": "routing",
    "structured_query": "querying",
    "semantic_query": "querying",
    "judge_deepen": "judging",
    "deepen_semantic": "deepening",
    "prepare_evidence": "preparing",
    "decide_actions": "deciding",
    "execute_automatic_actions": "executing",
    "confirm_gate": "confirming",
    "execute_actions": "executing",
}


_NODE_AGENT = {
    "scheduler_start": ("scheduler", "调度"),
    "scheduler_handoff": ("scheduler", "调度"),
    "route_question": ("analysis", "查询分析 Agent"),
    "structured_query": ("analysis", "查询分析 Agent"),
    "semantic_query": ("analysis", "查询分析 Agent"),
    "judge_deepen": ("analysis", "查询分析 Agent"),
    "deepen_semantic": ("analysis", "查询分析 Agent"),
    "prepare_evidence": ("analysis", "查询分析 Agent"),
    "decide_actions": ("decision", "报告决策 Agent"),
    "execute_automatic_actions": ("decision", "报告决策 Agent"),
    "confirm_gate": ("decision", "报告决策 Agent"),
    "execute_actions": ("decision", "报告决策 Agent"),
}


def _json_default(obj: Any) -> Any:
    """JSON 序列化兜底：Decimal / 日期时间。"""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat(sep=" ", timespec="seconds")
    if isinstance(obj, date):
        return obj.isoformat()
    return str(obj)


def _sse(event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False, default=_json_default)
    return f"event: {event}\ndata: {payload}\n\n"


def _parse_sse(chunk: str) -> tuple[str, dict[str, Any]]:
    """把一条 SSE 文本拆回 (event, data)，供非流式调用方复用同一条链路。"""
    event = ""
    payload = ""
    for line in chunk.strip().splitlines():
        if line.startswith("event: "):
            event = line[len("event: ") :].strip()
        elif line.startswith("data: "):
            payload = line[len("data: ") :]
    if not payload:
        return event, {}
    try:
        return event, json.loads(payload)
    except json.JSONDecodeError:
        return event, {}


def _reply_chunks(text: str, size: int = 8) -> Generator[str, None, None]:
    """把固定回复切成小块逐段下发，保持前端的打字机效果。"""
    for i in range(0, len(text), size):
        yield text[i : i + size]


def _agent_meta(node_name: str, delta: dict[str, Any]) -> tuple[str, str]:
    """从节点返回值或节点名解析当前 Agent 身份。"""
    agent = delta.get("current_agent")
    label = delta.get("agent_label")
    if agent and label:
        return str(agent), str(label)
    fallback = _NODE_AGENT.get(node_name)
    if fallback:
        return fallback
    return "unknown", node_name


def _emit_for_node(node_name: str, delta: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """根据刚跑完的节点，组装要推给前端的 SSE 事件（event, data）。"""
    if node_name == "__interrupt__":
        return []

    events: list[tuple[str, dict[str, Any]]] = []
    stage = _NODE_STAGE.get(node_name, node_name)
    status_message = delta.get("status_message") or f"完成节点：{node_name}"
    agent, agent_label = _agent_meta(node_name, delta)

    # lesson-10：先推 agent_step，过程区可区分是哪个 Agent
    agent_payload: dict[str, Any] = {
        "agent": agent,
        "agent_label": agent_label,
        "node": node_name,
        "stage": stage,
        "message": status_message,
    }
    if delta.get("next_agent"):
        agent_payload["next_agent"] = delta.get("next_agent")
    # 结构化查询这一步把当次 SQL 一起推给前端，过程区可以直接看着 SQL 讲
    if delta.get("sql"):
        agent_payload["sql"] = delta["sql"]
    events.append(("agent_step", agent_payload))

    if node_name == "route_question":
        events.append(
            (
                "status",
                {
                    "stage": stage,
                    "message": "正在判断该走结构化查询还是语义检索…",
                    "agent": agent,
                    "agent_label": agent_label,
                },
            )
        )
        events.append(
            (
                "route",
                {
                    "route": delta.get("route"),
                    "reason": delta.get("route_reason"),
                    "signals": delta.get("route_signals") or {},
                    "agent": agent,
                    "agent_label": agent_label,
                },
            )
        )
        return events

    extra: dict[str, Any] = {
        "stage": stage,
        "message": status_message,
        "agent": agent,
        "agent_label": agent_label,
    }
    if "sql" in delta:
        extra["sql"] = delta.get("sql")
    if "structured_row_count" in delta:
        extra["row_count"] = delta.get("structured_row_count")
        extra["truncated"] = delta.get("structured_truncated", False)
    if "semantic_row_count" in delta:
        extra["row_count"] = delta.get("semantic_row_count")
    if "need_deepen" in delta:
        extra["need_deepen"] = delta.get("need_deepen")
    if "evidence" in delta:
        extra["row_count"] = len(delta.get("evidence") or [])
        extra["evidence_source"] = delta.get("evidence_source")
    if "pending_actions" in delta:
        extra["action_count"] = len(delta.get("pending_actions") or [])
        extra["risk_level"] = delta.get("risk_level")
        extra["need_human_confirm"] = delta.get("need_human_confirm")
    if "actions_executed" in delta:
        extra["executed_count"] = len(delta.get("actions_executed") or [])

    events.append(("status", extra))
    return events
