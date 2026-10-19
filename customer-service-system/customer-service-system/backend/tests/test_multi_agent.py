"""lesson-10：多智能体包装与 agent_step SSE 组装。"""

from app.agent import analysis_agent, decision_agent, scheduler
from app.services.chat_service import _emit_for_node


def test_scheduler_start_tags_next_analysis():
    out = scheduler.node_scheduler_start({"question": "最近有没有尺码相关投诉"})
    assert out["current_agent"] == "scheduler"
    assert out["next_agent"] == "analysis"
    assert "查询分析" in out["status_message"]


def test_scheduler_handoff_to_decision():
    out = scheduler.node_scheduler_handoff(
        {"evidence": [{"id": 1}, {"id": 2}], "evidence_source": "semantic"}
    )
    assert out["current_agent"] == "scheduler"
    assert out["next_agent"] == "decision"
    assert "报告决策" in out["status_message"]
    assert "2 条" in out["status_message"]


def test_analysis_agent_tags_route(monkeypatch):
    monkeypatch.setattr(
        "app.agent.nodes.node_route",
        lambda state: {
            "route": "semantic",
            "route_reason": "主题模糊",
            "status_message": "已判定走语义检索",
        },
    )
    out = analysis_agent.route_question({"question": "有没有物流吐槽"})
    assert out["current_agent"] == "analysis"
    assert out["agent_label"] == "查询分析 Agent"
    assert out["status_message"].startswith("[查询分析 Agent]")


def test_decision_agent_tags_decide(monkeypatch):
    monkeypatch.setattr(
        "app.agent.nodes.node_decide_actions",
        lambda state: {
            "pending_actions": [{"type": "create_report"}],
            "risk_level": "high",
            "status_message": "建议生成报告",
        },
    )
    out = decision_agent.decide_actions({"evidence": []})
    assert out["current_agent"] == "decision"
    assert "[报告决策 Agent]" in out["status_message"]


def test_emit_agent_step_before_status():
    events = _emit_for_node(
        "scheduler_start",
        {
            "current_agent": "scheduler",
            "agent_label": "调度",
            "next_agent": "analysis",
            "status_message": "[调度] 交给查询分析 Agent",
        },
    )
    assert events[0][0] == "agent_step"
    assert events[0][1]["agent"] == "scheduler"
    assert events[0][1]["next_agent"] == "analysis"
    assert events[1][0] == "status"


def test_emit_route_still_includes_agent_meta():
    events = _emit_for_node(
        "route_question",
        {
            "current_agent": "analysis",
            "agent_label": "查询分析 Agent",
            "route": "structured",
            "route_reason": "明确商品",
            "status_message": "[查询分析 Agent] 已判定",
        },
    )
    names = [e[0] for e in events]
    assert names == ["agent_step", "status", "route"]
    assert events[2][1]["agent"] == "analysis"
