"""LangGraph 图结构与深挖判断的单元测试（深挖逻辑不依赖外网）。"""

from app.agent.graph import build_analysis_graph, tag_node_failure
from app.agent.nodes import (
    LOW_RATING_DEEPEN_THRESHOLD,
    _build_deepen_query,
    node_judge_deepen,
    node_prepare_evidence,
    select_after_judge,
    select_query_branch,
)
from app.agent.router import ROUTE_SEMANTIC, ROUTE_STRUCTURED


def test_select_query_branch():
    assert select_query_branch({"route": ROUTE_STRUCTURED}) == "structured"
    assert select_query_branch({"route": ROUTE_SEMANTIC}) == "semantic"


def test_judge_deepen_when_enough_low_ratings():
    rows = [
        {"rating": 1, "content": "差"},
        {"rating": 2, "content": "也不好"},
        {"rating": 5, "content": "好"},
    ]
    out = node_judge_deepen({"structured_rows": rows, "question": "差评"})
    assert out["need_deepen"] is True
    assert select_after_judge(out) == "deepen"


def test_judge_deepen_accepts_score_alias():
    rows = [{"score": 1, "content": "a"}, {"score": 2, "content": "b"}]
    out = node_judge_deepen({"structured_rows": rows, "question": "评价"})
    assert out["need_deepen"] is True


def test_judge_deepen_fallback_without_rating_column():
    rows = [{"content": "鞋底开胶"}, {"content": "尺码不对"}]
    out = node_judge_deepen(
        {
            "structured_rows": rows,
            "question": "轻云运动跑鞋的差评有哪些",
        }
    )
    assert out["need_deepen"] is True


def test_judge_deepen_skip_when_few_low_ratings():
    rows = [{"rating": 2, "content": "一条差评"}, {"rating": 5, "content": "好评"}]
    assert LOW_RATING_DEEPEN_THRESHOLD == 2
    out = node_judge_deepen({"structured_rows": rows, "question": "评价"})
    assert out["need_deepen"] is False
    assert select_after_judge(out) == "prepare"


def test_prepare_evidence_dedupes_and_keeps_source(monkeypatch):
    # 本测只验证去重，不真正拉起 MCP 查日志
    monkeypatch.setattr(
        "app.agent.nodes.query_logs",
        lambda keyword="", limit=3: {"ok": True, "runs": []},
    )
    state = {
        "structured_rows": [
            {"id": 12, "content": "尺码偏大", "source": "should_not_win"},
        ],
        "semantic_hits": [
            {
                "id": "review:12",
                "text": "尺码偏大",
                "metadata": {"review_id": 12, "rating": 2},
            },
            {
                "id": "review:99",
                "text": "包装破损",
                "metadata": {"review_id": 99, "rating": 1},
            },
        ],
    }
    out = node_prepare_evidence(state)
    assert out["evidence_source"] == "mixed"
    assert len(out["evidence"]) == 2
    assert out["evidence"][0]["source"] == "structured"
    assert out["evidence"][1]["id"] == "review:99"


def test_build_deepen_query_includes_product():
    q = _build_deepen_query(
        {
            "question": "评分小于等于2分的评价",
            "route_signals": {"products": ["轻云运动跑鞋"]},
        }
    )
    assert "轻云运动跑鞋" in q
    assert "差评" in q


def test_graph_compiles_and_has_expected_nodes():
    graph = build_analysis_graph()
    node_names = set(graph.get_graph().nodes)
    for name in (
        "scheduler_start",
        "scheduler_handoff",
        "route_question",
        "structured_query",
        "semantic_query",
        "judge_deepen",
        "deepen_semantic",
        "prepare_evidence",
        "decide_actions",
        "confirm_gate",
        "execute_actions",
    ):
        assert name in node_names


def test_prepare_evidence_preserves_aggregate_rows(monkeypatch):
    monkeypatch.setattr("app.agent.nodes.query_logs", lambda **kwargs: {"runs": []})
    rows = [
        {"product_name": "shoe", "sales": 100},
        {"product_name": "shirt", "sales": 200},
        {"product_name": "cup", "sales": 300},
    ]
    out = node_prepare_evidence({"structured_rows": rows})
    assert [e["sales"] for e in out["evidence"]] == [100, 200, 300]


def test_prepare_evidence_merges_image_without_counting_review_twice(monkeypatch):
    from app.services.action_decision import decide_actions

    monkeypatch.setattr("app.agent.nodes.query_logs", lambda **kwargs: {"runs": []})
    out = node_prepare_evidence({
        "structured_rows": [{"review_id": 7, "product_id": 1, "rating": 1, "content": "质量不好"}],
        "semantic_hits": [{
            "id": "review:7", "text": "质量不好\n【晒图内容】鞋底开胶",
            "metadata": {"doc_type": "review", "review_id": 7, "product_id": 1, "rating": 1},
        }],
    })
    assert len(out["evidence"]) == 1
    assert out["evidence"][0]["image_caption"] == "鞋底开胶"
    assert out["evidence_source"] == "mixed"
    assert decide_actions(out)["low_rating_count"] == 1


def test_order_id_does_not_hide_review_with_same_id(monkeypatch):
    monkeypatch.setattr("app.agent.nodes.query_logs", lambda **kwargs: {"runs": []})
    out = node_prepare_evidence({
        "structured_rows": [{"id": 7, "order_no": "EO1", "amount": 100}],
        "semantic_hits": [{"id": "review:7", "text": "质量不好", "metadata": {"review_id": 7, "rating": 1}}],
    })
    assert len(out["evidence"]) == 2


def test_tag_node_failure_marks_exception():
    """节点包装：异常透出前挂上真实节点名，供 failed_node 定位。"""

    def _boom(state):
        raise ValueError("炸")

    wrapped = tag_node_failure("structured_query", _boom)
    try:
        wrapped({"question": "x"})
        raise AssertionError("应当抛出异常")
    except ValueError as exc:
        assert getattr(exc, "_failed_node", None) == "structured_query"


def test_tag_node_failure_passthrough_on_success():
    def _ok(state):
        return {"need_deepen": False}

    assert tag_node_failure("judge_deepen", _ok)({}) == {"need_deepen": False}
