"""行动决策与执行的单元测试。"""

import pytest

from app.common.exceptions import BusinessException
from app.services.action_decision import decide_actions
from app.services.action_service import ALLOWED_ACTION_TYPES, execute_action


def diagnose(state):
    """动作规划用例显式授权业务诊断；普通查询单独测试不写入。"""
    return decide_actions({**state, 'route_signals': {'request_diagnostics': True, 'analyze_business_records': True}})


def test_decide_actions_high_risk_when_many_low_ratings():
    evidence = [
        {"rating": 1, "product_id": 1, "content": "a"},
        {"rating": 2, "product_id": 1, "content": "b"},
        {"rating": 1, "product_id": 1, "content": "c"},
    ]
    out = diagnose({"question": "差评", "evidence": evidence})
    assert out["risk_level"] == "high"
    assert out["need_human_confirm"] is True
    types = [a["type"] for a in out["pending_actions"]]
    assert "write_report" in types
    assert "send_alert" in types
    assert "mark_pending_review" in types


def test_decide_actions_low_risk_with_little_evidence():
    evidence = [{"rating": 5, "product_id": 1, "content": "好评"}]
    out = diagnose({"question": "怎么样", "evidence": evidence})
    assert out["need_human_confirm"] is False
    assert out["pending_actions"][0]["type"] == "write_report"


def test_many_evidence_without_bad_ratings_stays_low_risk():
    """仅证据条数多、无差评/预警动作时，不应强制人工确认。"""
    evidence = [{"rating": 5, "product_id": 1, "content": f"好评{i}"} for i in range(6)]
    out = diagnose({"question": "怎么样", "evidence": evidence})
    assert out["need_human_confirm"] is False
    assert out["risk_level"] == "low"


def test_guess_product_id_requires_unique():
    evidence = [
        {"rating": 1, "product_id": 1, "content": "a"},
        {"rating": 1, "product_id": 2, "content": "b"},
        {"rating": 1, "product_id": 1, "content": "c"},
    ]
    out = diagnose({"question": "差评", "evidence": evidence})
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
        "update_mall_setting",
        "update_coupon",
    }
    assert "update_stock" not in ALLOWED_ACTION_TYPES
    assert "change_shelf_status" not in ALLOWED_ACTION_TYPES


@pytest.mark.parametrize("flag", ["low_relevance", "statistics_unavailable"])
def test_insufficient_evidence_never_plans_writes(flag):
    out = diagnose({flag: True, "evidence": [
        {"product_id": 1, "rating": 1} for _ in range(3)
    ]})
    assert out["pending_actions"] == []
    assert out["need_human_confirm"] is False


def test_low_ratings_are_not_combined_across_products():
    out = diagnose({"evidence": [
        {"product_id": 1, "rating": 1}, {"product_id": 2, "rating": 1}
    ]})
    assert [a["type"] for a in out["pending_actions"]] == ["write_report"]


def test_review_actions_are_scoped_to_each_product():
    out = diagnose({"evidence": [
        *[{"product_id": 1, "rating": 1} for _ in range(3)],
        {"product_id": 2, "rating": 1},
    ]})
    writes = [a for a in out["pending_actions"] if a["type"] != "write_report"]
    assert {(a["type"], a["product_id"]) for a in writes} == {
        ("send_alert", 1), ("mark_pending_review", 1)
    }


def test_unrelated_semantic_hits_do_not_trigger_writes_with_structured_evidence():
    out = diagnose({"evidence": [
        {"source": "structured", "product_id": 1, "rating": 5},
        *[{"source": "semantic", "product_id": 1, "rating": 1, "distance": 0.9}
          for _ in range(3)],
    ]})
    assert [a["type"] for a in out["pending_actions"]] == ["write_report"]


def test_plain_query_does_not_plan_writes_without_diagnostic_request():
    out = decide_actions({'question': '看看差评', 'evidence': [{'product_id': 1, 'rating': 1}] * 5})
    assert out['pending_actions'] == [] and not out['need_human_confirm']
