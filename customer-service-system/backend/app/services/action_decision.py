"""行动决策与风险判断（lesson-07）。

根据证据条数/差评数量决定：
- 要执行哪些允许的动作
- 诊断风险与操作确认分别判断，报告和预警自动完成
"""

from typing import Any

from app.config import settings

# 可配置阈值（教学示例，写死在常量里便于讲解）
LOW_RATING_ALERT_THRESHOLD = 2  # ≥2 条差评 → 发预警
LOW_RATING_REVIEW_THRESHOLD = 3  # ≥3 条差评 → 标记待复核 + 高风险
AUTOMATIC_ACTION_TYPES = frozenset({"write_report", "send_alert"})


def _count_low_ratings(evidence: list[dict[str, Any]]) -> int:
    """统计有效证据中 1～2 星评价的条数。"""
    count = 0
    for item in evidence:
        rating = item.get("rating")
        if rating is None:
            continue
        try:
            if 1 <= int(rating) <= 2:
                count += 1
        except (TypeError, ValueError):
            continue
    return count


def _guess_product_id(state: dict[str, Any]) -> int | None:
    """推断商品 ID：仅当证据里只出现一个商品时返回，避免多商品误标。"""
    ids: list[int] = []
    for item in state.get("evidence") or []:
        pid = item.get("product_id")
        if pid is None:
            continue
        try:
            ids.append(int(pid))
        except (TypeError, ValueError):
            continue
    unique = list(dict.fromkeys(ids))
    if len(unique) == 1:
        return unique[0]
    return None


def decide_actions(state: dict[str, Any]) -> dict[str, Any]:
    """根据当前状态规划待执行动作列表与风险等级。"""
    evidence = state.get("evidence") or []
    question = state.get("question") or ""
    product_id = _guess_product_id(state)

    actions: list[dict[str, Any]] = []

    if not (state.get("route_signals") or {}).get("request_diagnostics"):
        return {
            "pending_actions": [], "risk_level": "low", "need_human_confirm": False,
            "product_id": None, "low_rating_count": 0,
            "decide_reason": "普通查询只记录运行历史；可在回答后按需保存诊断报告",
            "status_message": "本轮为查询问答，不自动生成报告或预警",
        }

    if not (state.get("route_signals") or {}).get("analyze_business_records"):
        return {
            "pending_actions": [], "risk_level": "low", "need_human_confirm": False,
            "product_id": None, "low_rating_count": 0,
            "decide_reason": "本轮不是业务记录诊断，不规划报告、预警或商品状态操作",
            "status_message": "本轮仅生成问答回复",
        }

    if (
        state.get("low_relevance") or state.get("statistics_unavailable")
        or (state.get("route_signals") or {}).get("planning_failed")
    ):
        return {
            "pending_actions": [],
            "risk_level": "low",
            "need_human_confirm": False,
            "product_id": None,
            "low_rating_count": 0,
            "decide_reason": "证据不足，不规划业务动作",
            "status_message": "证据不足，不规划业务动作",
        }

    # 写动作只使用相关、归属明确的评价，按商品分别计数。
    grouped: dict[int, list[dict[str, Any]]] = {}
    for item in evidence:
        if item.get("source") == "semantic":
            distance = item.get("distance")
            if (
                not isinstance(distance, (int, float))
                or not 0 <= distance <= settings.SEMANTIC_RELEVANCE_MAX_DISTANCE
            ):
                continue
        try:
            pid = int(item["product_id"])
        except (KeyError, TypeError, ValueError):
            continue
        if pid > 0:
            grouped.setdefault(pid, []).append(item)

    low_count = sum(_count_low_ratings(items) for items in grouped.values())

    # 1) 有证据就写一份诊断报告（低风险时也可直接执行）。
    if evidence:
        actions.append(
            {
                "type": "write_report",
                "title": "生成诊断报告",
                "summary": f"针对问题「{question[:80]}」的分析报告，证据 {len(evidence)} 条，差评信号 {low_count} 条。",
                "product_id": product_id,
            }
        )

    # 2) 各商品分别达到阈值才预警，不能跨商品累加。
    for pid, items in grouped.items():
        product_low_count = _count_low_ratings(items)
        if product_low_count < LOW_RATING_ALERT_THRESHOLD:
            continue
        actions.append(
            {
                "type": "send_alert",
                "title": "触发预警通知",
                "content": f"该商品检测到 {product_low_count} 条低分评价相关证据，请关注商品口碑。",
                "product_id": pid,
                "level": "critical" if product_low_count >= LOW_RATING_REVIEW_THRESHOLD else "warning",
            }
        )

        # 3) 达到复核阈值时，仅标记该组对应的商品。
        if product_low_count >= LOW_RATING_REVIEW_THRESHOLD:
            product_name = next((str(item["product_name"]) for item in items if item.get("product_name")), f"商品 {pid}")
            actions.append(
                {
                    "type": "mark_pending_review",
                    "title": f"将「{product_name}」标记为待复核",
                    "product_id": pid,
                }
            )

    # 诊断风险用于提示商品问题；只有改变商品状态的操作才暂停确认。
    risk_level = (
        "high" if any(a["type"] in ("send_alert", "mark_pending_review") for a in actions)
        else "low"
    )
    confirmation_count = sum(a["type"] not in AUTOMATIC_ACTION_TYPES for a in actions)
    need_human = confirmation_count > 0

    reason = (
        f"低分评价信号 {low_count} 条，规划动作 {len(actions)} 个；报告和预警自动生成"
        + (f"，另有 {confirmation_count} 项商品复核操作需要确认" if need_human else "，无需人工确认")
    )
    return {
        "pending_actions": actions,
        "risk_level": risk_level,
        "need_human_confirm": need_human,
        "product_id": product_id,
        "low_rating_count": low_count,
        "decide_reason": reason,
        "status_message": reason,
    }
