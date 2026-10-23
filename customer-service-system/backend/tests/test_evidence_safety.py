"""证据范围与统计回退回归测试，隔离数据库和外部模型。"""
import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.agent import nodes
from app.agent.graph import build_analysis_graph
from app.database import Base
from app.models import Product
from app.services import chat_service


@pytest.fixture
def product_db(monkeypatch):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine, tables=[Product.__table__])
    with Session(engine) as db:
        db.add(Product(id=1, name="跑鞋", category="鞋", description="跑鞋", price=1, stock=1))
        db.add(Product(id=2, name="键盘", category="数码", description="键盘", price=1, stock=1))
        db.commit()
    monkeypatch.setattr(nodes, "SessionLocal", lambda: Session(engine))
    monkeypatch.setattr(nodes, "query_logs", lambda **kwargs: {"runs": []})
    yield
    engine.dispose()


def test_deepening_limits_products_and_merge_rejects_other_hits(product_db, monkeypatch):
    calls = []

    def search(query, **kwargs):
        calls.append(kwargs)
        # 即使工具返回了范围外的结果，汇总也需要再次检查归属。
        return {"hits": [
            {"id": "review:1", "text": "开胶", "distance": 0.2,
             "metadata": {"review_id": 1, "product_id": 1, "rating": 1}},
            {"id": "review:2", "text": "失灵", "distance": 0.2,
             "metadata": {"review_id": 2, "product_id": 2, "rating": 1}},
        ]}

    monkeypatch.setattr(nodes, "query_chroma", search)
    state = {"question": "跑鞋差评", "route_signals": {"products": ["跑鞋"]}}
    state.update(nodes.node_deepen_semantic(state))
    prepared = nodes.node_prepare_evidence(state)
    assert calls == [{"top_k": 5, "product_ids": [1]}]
    assert [e["product_id"] for e in prepared["evidence"]] == [1]


def test_failed_statistics_graph_does_not_query_vectors_or_plan_actions(monkeypatch):
    def fail_sql(question):
        raise RuntimeError("SQL failed")

    monkeypatch.setattr(nodes, "query_mysql", fail_sql)
    monkeypatch.setattr(nodes, "query_chroma", lambda *a, **kw: pytest.fail("不能以语义结果代替统计"))
    monkeypatch.setattr(nodes, "query_logs", lambda **kwargs: {"runs": []})
    graph = build_analysis_graph()
    state = graph.invoke({"question": "订单量多少", "product_names": []},
                         config={"configurable": {"thread_id": "failed-statistics"}})
    assert state["statistics_unavailable"] is True
    assert state["pending_actions"] == []
    monkeypatch.setattr(chat_service, "chat_stream", lambda *a: pytest.fail("无需模型猜测统计"))
    chunks = list(chat_service._stream_answer("订单量多少", state))
    answer = "".join(json.loads(c.split("data: ")[1])["content"] for c in chunks)
    assert "统计查询失败" in answer


def test_failed_non_statistical_query_still_uses_semantic_fallback(monkeypatch):
    monkeypatch.setattr(nodes, "query_chroma", lambda *a, **kw: {"hits": []})
    out = nodes.node_semantic_query({"question": "跑鞋有哪些评价", "structured_failed": True,
                                    "route_signals": {"has_aggregate_intent": False}})
    assert not out.get("statistics_unavailable")


def test_failed_structured_fallback_is_checked_for_relevance(monkeypatch):
    monkeypatch.setattr(nodes, "query_logs", lambda **kwargs: {"runs": []})
    out = nodes.node_prepare_evidence({"route": "structured", "structured_failed": True,
        "semantic_hits": [{"id": "review:1", "text": "irrelevant", "distance": 0.9,
                           "metadata": {"rating": 1}}]})
    assert out["low_relevance"] is True


def test_low_relevance_suppresses_writes_but_still_answers(monkeypatch):
    """相关性闸门只拦业务写入，不拦回答。

    阈值与正常业务问题存在重叠（实测「最近的投诉集中在哪些方面」距离 0.611），
    拿它拒答会误伤，所以回答仍交给模型基于现有证据生成。
    """
    from app.services.action_decision import decide_actions

    prepared = nodes.node_prepare_evidence(
        {
            "route": "structured",
            "structured_failed": True,
            "semantic_hits": [
                {
                    "id": "review:1",
                    "text": "irrelevant",
                    "distance": 0.9,
                    "metadata": {"rating": 1, "product_id": 1},
                }
            ],
        }
    )
    assert prepared["low_relevance"] is True

    # 动作层面被拦住：不规划任何业务写入
    decided = decide_actions(prepared)
    assert decided["pending_actions"] == []

    # 回答层面不被拦住：模型仍会被调用（这里注入假流，不联网）
    monkeypatch.setattr(chat_service, "chat_stream", lambda *a, **kw: iter(["仍然回答"]))
    chunks = list(chat_service._stream_answer("最近的投诉集中在哪些方面", prepared))
    tokens = [
        json.loads(chunk.split("data: ")[1])["content"]
        for chunk in chunks
        if chunk.startswith("event: token")
    ]
    assert "".join(tokens) == "仍然回答"


def test_duplicate_sql_reviews_do_not_inflate_alert_threshold(product_db):
    row = {"review_id": 1, "product_id": 1, "rating": 1, "content": "开胶"}
    prepared = nodes.node_prepare_evidence({"structured_rows": [row, dict(row)]})
    from app.services.action_decision import decide_actions

    out = decide_actions(prepared)
    assert out["low_rating_count"] == 1
    assert [a["type"] for a in out["pending_actions"]] == ["write_report"]
