"""行动决策与执行的单元测试。"""

import pytest

from app.common.exceptions import BusinessException
from app.services.action_decision import decide_actions
from app.services.action_service import ALLOWED_ACTION_TYPES, execute_action


def test_decide_actions_high_risk_when_many_low_ratings():
    evidence = [
        {"rating": 1, "product_id": 1, "content": "a"},
        {"rating": 2, "product_id": 1, "content": "b"},
        {"rating": 1, "product_id": 1, "content": "c"},
    ]
    out = decide_actions({"question": "差评", "evidence": evidence})
    assert out["risk_level"] == "high"
    assert out["need_human_confirm"] is True
    types = [a["type"] for a in out["pending_actions"]]
    assert "write_report" in types
    assert "send_alert" in types
    assert "mark_pending_review" in types


def test_decide_actions_low_risk_with_little_evidence():
    evidence = [{"rating": 5, "product_id": 1, "content": "好评"}]
    out = decide_actions({"question": "怎么样", "evidence": evidence})
    assert out["need_human_confirm"] is False
    assert out["pending_actions"][0]["type"] == "write_report"


def test_many_evidence_without_bad_ratings_stays_low_risk():
    """仅证据条数多、无差评/预警动作时，不应强制人工确认。"""
    evidence = [{"rating": 5, "product_id": 1, "content": f"好评{i}"} for i in range(6)]
    out = decide_actions({"question": "怎么样", "evidence": evidence})
    assert out["need_human_confirm"] is False
    assert out["risk_level"] == "low"


def test_guess_product_id_requires_unique():
    evidence = [
        {"rating": 1, "product_id": 1, "content": "a"},
        {"rating": 1, "product_id": 2, "content": "b"},
        {"rating": 1, "product_id": 1, "content": "c"},
    ]
    out = decide_actions({"question": "差评", "evidence": evidence})
    assert out["product_id"] is None
    types = [a["type"] for a in out["pending_actions"]]
    assert "mark_pending_review" not in types
    assert "send_alert" in types


def test_forbidden_action_type_rejected(monkeypatch):
    class DummyDB:
        pass

    with pytest.raises(BusinessException):
        execute_action(
            DummyDB(),
            {"type": "update_price", "product_id": 1},
            {"question": "x"},
        )


def test_allowed_action_whitelist():
    assert ALLOWED_ACTION_TYPES == {
        "write_report",
        "send_alert",
        "mark_pending_review",
    }
    assert "update_stock" not in ALLOWED_ACTION_TYPES
    assert "change_shelf_status" not in ALLOWED_ACTION_TYPES


@pytest.mark.parametrize("flag", ["low_relevance", "statistics_unavailable"])
def test_insufficient_evidence_never_plans_writes(flag):
    out = decide_actions({flag: True, "evidence": [
        {"product_id": 1, "rating": 1} for _ in range(3)
    ]})
    assert out["pending_actions"] == []
    assert out["need_human_confirm"] is False


def test_low_ratings_are_not_combined_across_products():
    out = decide_actions({"evidence": [
        {"product_id": 1, "rating": 1}, {"product_id": 2, "rating": 1}
    ]})
    assert [a["type"] for a in out["pending_actions"]] == ["write_report"]


def test_review_actions_are_scoped_to_each_product():
    out = decide_actions({"evidence": [
        *[{"product_id": 1, "rating": 1} for _ in range(3)],
        {"product_id": 2, "rating": 1},
    ]})
    writes = [a for a in out["pending_actions"] if a["type"] != "write_report"]
    assert {(a["type"], a["product_id"]) for a in writes} == {
        ("send_alert", 1), ("mark_pending_review", 1)
    }


def test_unrelated_semantic_hits_do_not_trigger_writes_with_structured_evidence():
    out = decide_actions({"evidence": [
        {"source": "structured", "product_id": 1, "rating": 5},
        *[{"source": "semantic", "product_id": 1, "rating": 1, "distance": 0.9}
          for _ in range(3)],
    ]})
    assert [a["type"] for a in out["pending_actions"]] == ["write_report"]
