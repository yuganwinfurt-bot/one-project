"""LangGraph 各节点函数。

每个节点：输入 AgentState 片段 → 返回要合并进状态的字典。
节点内部自己开关数据库 Session，不把连接放进 state（不好序列化）。
"""

import json
from typing import Any

from langgraph.config import get_stream_writer

from app.agent.router import (
    ROUTE_CONVERSATION,
    ROUTE_SEMANTIC,
    ROUTE_STRUCTURED,
    ROUTE_MANAGEMENT,
    decide_query_route,
    parse_query_plan,
    query_plan_messages,
)
from app.agent.state import AgentState
from app.common.exceptions import BusinessException
from app.config import settings
from app.database import SessionLocal
from app.mcp_client import query_chroma, query_mysql_sql
from app.models.product import Product


def _emit_progress(stage: str, message: str) -> None:
    """进入耗时节点前，先往 SSE 流推一条进度事件。

    节点产生的状态要等节点跑完才会以 updates 形式下发，像“生成 SQL / 检索向量”
    这类要调用大模型的节点会静默十几秒，前端看起来像卡死。
    这里提前推一条进度，过程区即可显示“正在生成 SQL 查询…”。
    仅在图以 custom 模式流式输出时生效，其他调用场景静默忽略。
    """
    try:
        writer = get_stream_writer()
        writer({"progress": stage, "message": message})
    except Exception:
        return


def _review_key(item: dict[str, Any]) -> str | None:
    """只识别评价身份，不把统计行、商品 ID、订单 ID 当作评价。"""
    if item.get("after_sale_id") is not None:
        return None
    review_id = item.get("review_id")
    if review_id is not None:
        return f"review:{review_id}"
    doc_id = str(item.get("id") or "")
    if doc_id.startswith("review:"):
        return doc_id
    # 兼容前几节直接 SELECT reviews.id, reviews.content 的写法。
    if doc_id and "content" in item and "doc_type" not in item:
        return f"review:{doc_id}"
    return None


def node_route(state: AgentState) -> dict[str, Any]:
    """节点 1：查询路由判断。"""
    _emit_progress("planning_query", "正在由模型理解问题并规划查询范围…")
    names = state.get("product_names") or []
    history = state.get("conversation_history") or []
    if state.get("use_agent_model"):
        from app.services.model_requests import request_model
        decision = request_model(
            state.get("run_id"), "理解问题并生成查询计划",
            query_plan_messages(state["question"], names, history),
            lambda raw: parse_query_plan(raw, names),
        )
        decision.signals["planner"] = "agent_model"
    else:
        decision = decide_query_route(state["question"], names, history)
    return {
        "route": decision.route,
        "route_reason": decision.reason,
        "route_signals": decision.signals,
        "status_message": (
            f"路由结果：{decision.route} — {decision.reason}"
            + (f"；语境理解：{decision.signals['context_reason']}" if decision.signals.get("context_reason") else "")
        ),
    }


def node_structured_query(state: AgentState) -> dict[str, Any]:
    """节点 2a：结构化查询 — 经 MCP 工具 query_mysql_tool，不直接调 service。

    SQL 生成/校验/执行失败时不让整轮报错：标记 structured_failed，
    条件边会改走语义检索兜底（见 select_after_structured）。
    """
    # 这一步要先让大模型把问题转成 SQL，最耗时，先推进度避免前端静默
    _emit_progress("executing_query", "正在执行已通过只读校验的数据库查询…")
    try:
        signals = state.get("route_signals") or {}
        sql = signals.get("sql")
        if not sql:
            raise BusinessException(message="查询规划未提供可执行的只读 SQL")
        try:
            result = query_mysql_sql(sql)
        except BusinessException as exc:
            if not state.get("use_agent_model"):
                raise
            from app.services.model_requests import request_model
            from app.services.nl2sql.prompt import SCHEMA_PROMPT
            from app.services.nl2sql.validate import validate_sql
            repaired = request_model(state.get("run_id"), "修正数据库查询", [
                {"role": "system", "content": SCHEMA_PROMPT},
                {"role": "user", "content": f"原问题：{state['question']}\n查询规划：{json.dumps(signals, ensure_ascii=False)}\n失败 SQL：{sql}\n错误：{exc.message}\n请修正，只输出一条 SELECT。"},
            ], validate_sql)
            result = query_mysql_sql(repaired)
    except Exception as exc:
        message = exc.message if isinstance(exc, BusinessException) else str(exc)
        return {
            "structured_failed": True,
            "structured_fail_reason": message,
            "structured_rows": [],
            "status_message": f"结构化查询失败（{message}），改用语义检索兜底",
        }
    return {
        "sql": result.get("sql"),
        "structured_rows": result.get("rows") or [],
        "structured_row_count": int(result.get("row_count") or 0),
        "structured_truncated": bool(result.get("truncated")),
        "structured_failed": False,
        "status_message": (
            f"经 MCP 查 MySQL 完成，返回 {result.get('row_count', 0)} 条"
        ),
    }


def _query_semantic(state: AgentState) -> dict[str, Any]:
    """按本次规划检索资料；失败时保留已取得的 SQL 证据供模型回答。"""
    signals = state.get("route_signals") or {}
    names = signals.get("products") or []
    product_ids: list[int] = []
    if names:
        with SessionLocal() as db:
            product_ids = [row[0] for row in db.query(Product.id).filter(Product.name.in_(names)).all()]
        if not product_ids:
            return {
                "semantic_hits": [], "semantic_row_count": 0, "target_product_ids": [],
                "status_message": "指定商品不存在，未扩大到其他商品检索",
            }
    try:
        result = query_chroma(
            signals.get("semantic_query") or state["question"],
            top_k=20, product_ids=product_ids or None, doc_types=signals.get("doc_types") or None,
        )
    except Exception as exc:
        message = exc.message if isinstance(exc, BusinessException) else "资料检索暂不可用"
        return {
            "semantic_hits": [], "semantic_row_count": 0, "semantic_failed": True,
            "target_product_ids": product_ids,
            "status_message": f"{message}；将根据已取得的数据说明结果及限制",
        }
    hits = result.get("hits") or []
    return {
        "semantic_hits": hits, "semantic_row_count": len(hits), "semantic_failed": False,
        "target_product_ids": product_ids,
        "status_message": f"经 MCP 检索到 {len(hits)} 条资料候选，不能据此当作完整统计",
    }


def node_semantic_query(state: AgentState) -> dict[str, Any]:
    """语义查询只能补充资料，不能伪造 SQL 失败后的完整统计。"""
    signals = state.get("route_signals") or {}
    _emit_progress("searching_vectors", "正在按当前问题检索相关资料…")
    result = _query_semantic(state)
    result.update({
        "need_deepen": False,
        "statistics_unavailable": bool(
            state.get("structured_failed") and signals.get("requires_complete_data")
        ),
    })
    return result


def node_judge_deepen(state: AgentState) -> dict[str, Any]:
    """是否结合资料取决于模型的当前查询规划，而不是固定低分触发词。"""
    needed = bool((state.get("route_signals") or {}).get("needs_semantic"))
    reason = "按本次问题的查询规划补充相关资料" if needed else "本次查询规划无需补充资料"
    return {"need_deepen": needed, "deepen_reason": reason, "status_message": reason}


def node_deepen_semantic(state: AgentState) -> dict[str, Any]:
    _emit_progress("deepening", "正在按本次规划补充资料证据…")
    return _query_semantic(state)


def _hit_to_evidence(hit: dict[str, Any]) -> dict[str, Any]:
    meta = hit.get("metadata") or {}
    content = hit.get("text") or ""
    # 图片描述独立保留，合并同一评价时不会丢掉，也不会重复计算差评数量。
    image_caption = str(content).partition("【晒图内容】")[2].strip()
    return {
        "id": hit.get("id"),
        "record_id": meta.get("record_id"),
        "doc_type": meta.get("doc_type"),
        "source_table": meta.get("source_table"),
        "source_id": meta.get("source_id"),
        "create_time": meta.get("create_time"),
        "product_id": meta.get("product_id"),
        "review_id": meta.get("review_id"),
        "rating": meta.get("rating"),
        "content": content,
        "image_caption": image_caption,
        "distance": hit.get("distance"),
        "source": "semantic",  # 放最后，避免被其他字段覆盖
    }


def _attach_product_names(evidence: list[dict[str, Any]]) -> None:
    """给证据补上商品名（就地修改）。

    向量文档的 metadata 里只有 product_id，评价正文也不含商品名，
    纯语义证据送进大模型后会被写成「商品6」这种编号——用户不该看到编号。
    SQL 只返回 id 没返回名称时，同样的补齐也生效。
    """
    product_ids = {
        item.get("product_id")
        for item in evidence
        if item.get("product_id") is not None
    }
    if not product_ids:
        return

    db = SessionLocal()
    try:
        rows = (
            db.query(Product.id, Product.name, Product.category)
            .filter(Product.id.in_(product_ids))
            .all()
        )
    finally:
        db.close()

    names = {pid: (name, category) for pid, name, category in rows}
    for item in evidence:
        info = names.get(item.get("product_id"))
        if not info:
            continue
        if not item.get("product_name"):
            item["product_name"] = info[0]
        if not item.get("category"):
            item["category"] = info[1]


def node_prepare_evidence(state: AgentState) -> dict[str, Any]:
    """节点 5：合并证据；并经 MCP 查日志，附上最近相关运行摘要。"""
    if state.get("route") == ROUTE_CONVERSATION:
        return {
            "evidence": [], "evidence_source": ROUTE_CONVERSATION,
            "recent_logs": [], "low_relevance": True,
            "status_message": "本次无需查询业务数据，交给模型生成回复",
        }
    _emit_progress("preparing_evidence", "正在汇总证据…")
    evidence: list[dict[str, Any]] = []
    reviews: dict[str, dict[str, Any]] = {}
    seen_semantic: set[str] = set()

    for row in state.get("structured_rows") or []:
        # 来源字段由流程设置，防止 SQL 中的同名列覆盖证据来源。
        item = {**row, "source": "structured", "sources": ["structured"]}
        # SQL 已经决定返回哪些行，统计结果可能没有 ID / 正文，全部保留。
        key = _review_key(item)
        if key is not None:
            if key in reviews:
                continue
            reviews.setdefault(key, item)
        evidence.append(item)

    targets = state.get("target_product_ids") or []
    for hit in state.get("semantic_hits") or []:
        item = _hit_to_evidence(hit)
        if targets and item.get("product_id") not in targets:
            continue
        key = _review_key(item)
        if key is not None and key in reviews:
            existing = reviews[key]
            if item.get("image_caption"):
                existing["image_caption"] = item["image_caption"]
            # 早期 SQL 未返回评分/商品 ID 时，由同一评价的 metadata 补齐。
            for field in ("rating", "product_id", "review_id"):
                if existing.get(field) is None and item.get(field) is not None:
                    existing[field] = item[field]
            existing["sources"] = list(dict.fromkeys([existing["source"], "semantic"]))
            continue
        doc_id = str(item.get("id") or "")
        if doc_id and doc_id in seen_semantic:
            continue
        if doc_id:
            seen_semantic.add(doc_id)
        evidence.append(item)
        if key is not None:
            reviews[key] = item

    has_structured = any(e.get("source") == "structured" for e in evidence)
    has_semantic = any(
        e.get("source") == "semantic" or "semantic" in e.get("sources", [])
        for e in evidence
    )
    if has_structured and has_semantic:
        source = "mixed"
    elif has_structured:
        source = ROUTE_STRUCTURED
    else:
        source = ROUTE_SEMANTIC

    # 相关度兜底：语义路线下，证据里的最小向量距离仍大于阈值（或压根没命中），
    # 说明这些候选证据不足以支持业务动作或可靠回答。
    distances = [
        float(e["distance"])
        for e in evidence
        if isinstance(e.get("distance"), (int, float))
    ]
    best_distance = min(distances) if distances else None
    low_relevance = (
        not has_structured
        and (state.get("route") == ROUTE_SEMANTIC or state.get("structured_failed"))
        and (
            best_distance is None
            or best_distance > settings.SEMANTIC_RELEVANCE_MAX_DISTANCE
        )
    )

    # 送大模型之前补齐商品名，避免回答里出现「商品6」这种编号
    _attach_product_names(evidence)

    return {
        "evidence": evidence,
        "evidence_source": source,
        "recent_logs": [],
        "best_distance": best_distance,
        "low_relevance": low_relevance,
        "status_message": (
            f"证据汇总完成，共 {len(evidence)} 条（来源：{source}）"
            + ("；与问题相关性不足" if low_relevance else "")
        ),
    }


def node_mall_configuration(state: AgentState) -> dict[str, Any]:
    from app.services.mall_agent_service import MANAGEMENT_PROMPT, management_context, parse_management_plan, build_management_actions
    _emit_progress("planning_configuration", "正在读取商品与后台业务资料，生成操作方案…")
    with SessionLocal() as db:
        catalog = management_context(db, state.get("user_id"), state["question"], state.get("conversation_history"))
    messages = [
        {"role": "system", "content": MANAGEMENT_PROMPT},
        {"role": "user", "content": json.dumps({"question": state["question"], "history": state.get("conversation_history") or [], "catalog": catalog}, ensure_ascii=False)},
    ]
    if state.get("use_agent_model"):
        from app.services.model_requests import request_model
        plan = request_model(state.get("run_id"), "规划后台业务操作", messages, parse_management_plan)
    else:
        from app.utils.llm import chat_once
        plan = parse_management_plan(chat_once(messages[0]["content"], messages[1]["content"]))
    with SessionLocal() as db:
        actions = build_management_actions(db, state.get("user_id"), plan)
    return {
        "pending_actions": actions, "need_human_confirm": bool(actions),
        "decide_reason": plan["message"][:2000],
        "evidence": [{"source": "management", "current_configuration": {
                          "settings": catalog.get("settings", []), "coupons": catalog.get("coupons", []),
                          "allowed_operations": {key: value["operations"] for key, value in catalog.get("allowed_operations", {}).items()},
                          "forbidden": catalog.get("forbidden"),
                          "source_counts": {key: value["total"] for key, value in catalog.items() if isinstance(value, dict) and "total" in value},
                      }, "plan_message": plan["message"],
                      "pending_changes": [{"title": a["title"], "changes": a["changes"], "notice": a.get("notice")} for a in actions], "saved": False}],
        "evidence_source": "management", "current_agent": "configuration", "agent_label": "后台业务助手",
        "status_message": f"已读取业务资料并准备 {len(actions)} 项待确认修改" if actions else "已读取业务资料；没有执行修改",
    }


def node_decide_actions(state: AgentState) -> dict[str, Any]:
    """节点 6：根据证据规划允许的动作，并判断是否需要人工确认。"""
    if state.get("route") == ROUTE_MANAGEMENT:
        actions = state.get("pending_actions") or []
        return {"pending_actions": actions, "need_human_confirm": bool(actions), "risk_level": "high" if actions else "low", "decide_reason": state.get("decide_reason") or "已读取后台配置"}
    from app.services.action_decision import decide_actions

    result = decide_actions(state)
    return result


def node_confirm_gate(state: AgentState) -> dict[str, Any]:
    """商品状态变更用 LangGraph interrupt 暂停，报告与预警已在前一节点生成。

    注意：恢复执行时本节点会从头再跑一遍，interrupt() 之前不要写库。
    """
    from langgraph.types import interrupt

    if not state.get("need_human_confirm"):
        return {
            "human_approved": None,
            "status_message": "常规分析产物自动完成，无需人工确认",
        }

    # 真正的人工介入：图在此暂停，resume 值会成为 interrupt 的返回值
    decision = interrupt(
        {
            "message": ("请核对以下后台业务操作及变更内容，确认后执行并记录操作日志。" if state.get("route") == ROUTE_MANAGEMENT else "报告和预警已自动生成。以下操作会将商品标记为待复核，并从买家商品首页隐藏，请单独确认。"),
            "risk_level": state.get("risk_level"),
            "actions": state.get("pending_actions") or [],
            "reason": state.get("decide_reason") or "",
        }
    )
    approved = bool((decision or {}).get("approved"))
    return {
        "human_approved": approved,
        "status_message": "用户已确认执行" if approved else "用户已取消执行",
    }


def _execute_planned_actions(state: AgentState, actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """独立事务执行指定动作，供自动执行与确认后执行节点共用。"""
    from app.services import action_service

    db = SessionLocal()
    try:
        context = {
            "question": state.get("question"),
            "route": state.get("route"),
            "risk_level": state.get("risk_level"),
            "evidence_count": len(state.get("evidence") or []),
            "evidence": state.get("evidence") or [],
            "product_id": state.get("product_id"),
            "user_id": state.get("user_id"),
            "run_id": state.get("run_id"),
            "summary": (state.get("decide_reason") or "数据分析诊断"),
        }
        return action_service.execute_actions(db, actions, context)
    finally:
        db.close()


def node_execute_automatic_actions(state: AgentState) -> dict[str, Any]:
    """在独立检查点节点生成报告/预警，恢复确认时不会重复运行此节点。"""
    from app.services.action_decision import AUTOMATIC_ACTION_TYPES

    if state.get("route") == ROUTE_MANAGEMENT:
        actions = state.get("pending_actions") or []
        return {"pending_actions": actions, "need_human_confirm": bool(actions), "status_message": f"已准备 {len(actions)} 项后台操作，等待核对确认" if actions else "已读取后台配置，未提出修改"}

    actions = state.get("pending_actions") or []
    automatic = [action for action in actions if action.get("type") in AUTOMATIC_ACTION_TYPES]
    pending = [action for action in actions if action.get("type") not in AUTOMATIC_ACTION_TYPES]
    pending_count = len(pending)
    review_ids = {action["product_id"] for action in pending if action.get("type") == "mark_pending_review" and action.get("product_id")}
    if review_ids:
        with SessionLocal() as db:
            already_pending = {
                row.id for row in db.query(Product.id)
                .filter(Product.id.in_(review_ids), Product.review_status == "pending_review")
                .all()
            }
        pending = [
            action for action in pending
            if action.get("type") != "mark_pending_review" or action.get("product_id") not in already_pending
        ]
    skipped = pending_count - len(pending)
    results = _execute_planned_actions(state, automatic) if automatic else []
    return {
        "pending_actions": pending,
        "need_human_confirm": bool(pending),
        "actions_executed": [*(state.get("actions_executed") or []), *results],
        "status_message": (
            f"已自动完成 {len(results)} 项报告/预警"
            + (f"；{skipped} 件商品已处于待复核状态，无需重复确认" if skipped else "")
            + (f"；另有 {len(pending)} 项商品复核操作待确认" if pending else "")
        ),
    }


def node_execute_actions(state: AgentState) -> dict[str, Any]:
    """保留自动生成的产物，仅对剩余商品状态变更执行确认结果。"""
    actions = state.get("pending_actions") or []
    executed = state.get("actions_executed") or []
    if state.get("route") == ROUTE_MANAGEMENT:
        if not actions:
            return {"actions_executed": executed, "status_message": "后台业务查询完成"}
        if not state.get("human_approved"):
            return {"actions_executed": executed, "status_message": "已取消本次后台操作"}
        results = _execute_planned_actions(state, actions)
        return {"actions_executed": [*executed, *results], "status_message": "后台操作已执行：" + "；".join(result["summary"] for result in results)}
    if not actions:
        return {
            "actions_executed": executed,
            "status_message": f"分析处理完成，已自动执行 {len(executed)} 项报告/预警",
        }
    if not state.get("human_approved"):
        return {
            "actions_executed": executed,
            "status_message": "已取消商品复核操作，自动生成的报告和预警已保留",
        }
    results = _execute_planned_actions(state, actions)
    return {
        "actions_executed": [*executed, *results],
        "status_message": f"已确认并执行 {len(results)} 项商品复核操作，报告和预警已保留",
    }


# ---------- 条件边用的小函数 ----------

def select_query_branch(state: AgentState) -> str:
    """按模型规划选择数据工具；无需数据时仍由模型生成回答。"""
    if state.get("route") == ROUTE_MANAGEMENT:
        return "management"
    if state.get("route") == ROUTE_CONVERSATION:
        return "conversation"
    if state.get("route") == ROUTE_STRUCTURED:
        return "structured"
    return "semantic"


def select_after_structured(state: AgentState) -> str:
    """结构化查询之后：失败就改走语义检索兜底，避免整轮报错。"""
    if state.get("structured_failed"):
        return "fallback"
    return "continue"


def select_after_judge(state: AgentState) -> str:
    """判断深挖之后：要不要再查语义。"""
    if state.get("need_deepen"):
        return "deepen"
    return "prepare"
