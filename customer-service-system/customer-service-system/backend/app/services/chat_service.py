"""对话服务：跑 LangGraph 分析图，流式下发过程事件与回答（SSE）。

本模块只保留主流程；事件协议见 chat_events.py，提示词与脱敏见 chat_prompt.py，
人工确认见 confirmation_service.py，巡检见 patrol_service.py。
"""

import json
import logging
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Generator

from app.agent.context import prepare_history
from app.agent.graph import FAILED_NODE_ATTR, get_analysis_graph
from app.agent.state import AgentState
from app.common.exceptions import BusinessException
from app.database import SessionLocal
from app.models.product import Product
from app.observability import service as obs_service
from app.observability.models import AgentRun
from app.services.chat_events import (
    _emit_for_node,
    _json_default,
    _sse,
)
from app.services.chat_prompt import SUMMARY_SYSTEM_PROMPT, _shrink_rows
from app.utils.llm import chat_stream

logger = logging.getLogger(__name__)


def _load_product_names() -> list[str]:
    """加载已知商品名，供查询模型识别实体。"""
    db = SessionLocal()
    try:
        rows = db.query(Product.name).all()
        return [r[0] for r in rows if r[0]]
    finally:
        db.close()


def _record_step(
    run_id: int | None,
    *,
    step_name: str,
    summary: str,
    success: bool = True,
    elapsed_ms: int | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    """写入观测步骤；失败只打日志，不影响主流程。"""
    if run_id is None:
        return
    db = SessionLocal()
    try:
        obs_service.add_step(
            db,
            run_id,
            step_name=step_name,
            summary=summary,
            success=success,
            elapsed_ms=elapsed_ms,
            detail=detail,
        )
    except Exception:
        logger.exception("写入运行步骤失败 run_id=%s step=%s", run_id, step_name)
    finally:
        db.close()


def _finish_run_safe(run_id: int | None, **kwargs: Any) -> None:
    """结束运行记录；失败只打日志。"""
    if run_id is None:
        return
    db = SessionLocal()
    try:
        obs_service.finish_run(db, run_id, **kwargs)
    except Exception:
        logger.exception("结束运行记录失败 run_id=%s", run_id)
    finally:
        db.close()


def _stream_answer(
    question: str, final_state: AgentState, *, use_agent_model: bool = False, run_id: int | None = None
) -> Generator[str, None, str]:
    """根据证据流式生成自然语言回答；同时收集完整文本供观测预览。"""
    evidence = final_state.get("evidence") or []
    evidence_source = final_state.get("evidence_source") or "unknown"
    truncated = bool(final_state.get("structured_truncated"))

    yield _sse(
        "status",
        {"stage": "answering", "message": "正在根据证据生成回答…"},
    )

    rows_for_llm = _shrink_rows(evidence)
    signals = final_state.get("route_signals") or {}
    context = {
        "用户原始问题": question,
        "最近对话_仅供理解追问": final_state.get("conversation_history") or [],
        "业务时间": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "查询规划": {key: signals.get(key) for key in (
            "planner", "analysis_scope", "time_scope", "retrieval_question", "context_reason",
            "doc_types", "requires_complete_data", "planning_failed",
        )},
        "实际执行的只读查询_仅供核对口径": final_state.get("sql"),
        "证据来源": evidence_source,
        "诊断风险信号": final_state.get("risk_level") or "low",
        "结构化查询失败": bool(final_state.get("structured_failed")),
        "精确统计不可用": bool(final_state.get("statistics_unavailable")),
        "资料检索失败": bool(final_state.get("semantic_failed")),
        "结构化结果可能达到行数上限": truncated,
        "取得的证据条数": len(evidence),
        "本次提供给模型的条数": len(rows_for_llm),
        "提示词证据已裁剪": len(rows_for_llm) < len(evidence),
        "证据": rows_for_llm,
    }
    user_prompt = json.dumps(context, ensure_ascii=False, default=_json_default)
    if use_agent_model:
        messages = [
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        if run_id is not None:
            with SessionLocal() as db:
                obs_service.save_run_answer_context(db, run_id, messages)
        yield _sse("agent_model_context", {
            "messages": messages,
            "run_id": run_id,
        })
        return ""
    parts: list[str] = []
    for token in chat_stream(SUMMARY_SYSTEM_PROMPT, user_prompt):
        parts.append(token)
        yield _sse("token", {"content": token})
    return "".join(parts)


def stream_chat(
    question: str,
    user_id: int | None = None,
    history: list[dict[str, Any]] | None = None,
    use_agent_model: bool = False,
) -> Generator[str, None, None]:
    """SSE：跑图；若命中人工确认则暂停并返回 thread_id；并写入观测表。

    history：最近几轮对话交给查询规划及回答模型理解，保留用户原始问题。
    """
    started = time.perf_counter()
    original_question = (question or "").strip()
    if not original_question:
        yield _sse("error", {"message": "问题不能为空"})
        return

    product_names = _load_product_names()

    question = original_question
    conversation_history = prepare_history(history)

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    current_node = ""
    run_id: int | None = None
    answer_text = ""

    # 创建运行总览
    db = SessionLocal()
    try:
        run = obs_service.create_run(
            db, thread_id=thread_id, question=original_question, user_id=user_id
        )
        run_id = run.id
    except Exception:
        logger.exception("创建运行记录失败")
        run_id = None
    finally:
        db.close()

    try:
        yield _sse(
            "status",
            {
                "stage": "starting",
                "message": "已接入 LangGraph 分析流程…",
                "run_id": run_id,
            },
        )
        _record_step(
            run_id,
            step_name="starting",
            summary="已接入 LangGraph 分析流程",
        )

        initial: AgentState = {
            "question": question,
            "conversation_history": conversation_history,
            "product_names": product_names,
            "user_id": user_id,
            "run_id": run_id,
            "use_agent_model": use_agent_model,
            "structured_rows": [],
            "semantic_hits": [],
            "evidence": [],
            "pending_actions": [],
            "actions_executed": [],
        }

        graph = get_analysis_graph()
        final_state: AgentState = dict(initial)
        interrupted_payload: dict[str, Any] | None = None
        step_started = time.perf_counter()

        # stream_mode 追加 custom：节点内可用 get_stream_writer 推送“开始处理”进度，
        # 避免生成 SQL / 检索向量期间前端长时间收不到任何事件（看起来像卡死）。
        for mode, payload in graph.stream(
            initial, config=config, stream_mode=["updates", "custom"]
        ):
            if mode == "custom":
                if isinstance(payload, dict) and payload.get("model_request"):
                    yield _sse("agent_model_request", payload["model_request"])
                    continue
                if isinstance(payload, dict) and payload.get("progress"):
                    yield _sse(
                        "status",
                        {
                            "stage": payload["progress"],
                            "message": payload.get("message") or "处理中…",
                        },
                    )
                continue

            for node_name, delta in payload.items():
                current_node = node_name
                step_elapsed = int((time.perf_counter() - step_started) * 1000)
                step_started = time.perf_counter()

                if node_name == "__interrupt__":
                    if delta and len(delta) > 0:
                        interrupted_payload = delta[0].value
                    continue
                if isinstance(delta, dict):
                    final_state.update(delta)
                    for event_name, data in _emit_for_node(node_name, delta):
                        yield _sse(event_name, data)
                        # 把过程写进观测表（agent_step 单独记一步，便于区分 Agent）
                        if event_name == "agent_step":
                            _record_step(
                                run_id,
                                step_name=f"agent:{data.get('agent') or 'unknown'}",
                                summary=str(data.get("message") or data.get("agent_label")),
                                elapsed_ms=step_elapsed,
                                detail={
                                    k: data[k]
                                    for k in (
                                        "agent",
                                        "agent_label",
                                        "node",
                                        "next_agent",
                                    )
                                    if k in data
                                }
                                or None,
                            )
                            continue
                        stage = data.get("stage") or event_name
                        summary = data.get("message") or data.get("reason") or stage
                        if event_name == "route":
                            summary = (
                                f"路由 → {data.get('route')}：{data.get('reason') or ''}"
                            )
                            stage = "route"
                        _record_step(
                            run_id,
                            step_name=str(stage),
                            summary=str(summary),
                            elapsed_ms=step_elapsed,
                            detail={
                                k: data[k]
                                for k in (
                                    "route",
                                    "sql",
                                    "row_count",
                                    "evidence_source",
                                    "risk_level",
                                    "agent",
                                )
                                if k in data
                            }
                            or None,
                        )

        snap = graph.get_state(config)
        if snap and snap.values:
            final_state.update(snap.values)

        # 流式回答，并收集预览文本
        gen = _stream_answer(
            question, final_state, use_agent_model=use_agent_model, run_id=run_id
        )
        current_node = "answering"
        try:
            answer_text = yield from gen
        except Exception as exc:
            if interrupted_payload is None:
                raise
            # 回答模型失败不等于取消待确认动作，仍继续发送 action_pending。
            logger.exception("总结失败，保留待确认任务 thread_id=%s", thread_id)
            message = exc.message if isinstance(exc, BusinessException) else "回答生成失败"
            _record_step(run_id, step_name="answering", summary=message, success=False)
            yield _sse("error", {
                "message": f"{message}，可继续确认或取消动作",
                "failed_node": "answering",
                "run_id": run_id,
                "thread_id": thread_id,
                "awaiting_confirmation": True,
            })
        else:
            _record_step(run_id, step_name="answering", summary="分析结果已保存，等待浏览器模型生成回答" if use_agent_model and not answer_text else "已根据证据生成回答")

        elapsed_ms = int((time.perf_counter() - started) * 1000)

        if interrupted_payload is not None:
            _record_step(
                run_id,
                step_name="action_pending",
                summary=interrupted_payload.get("message") or "等待人工确认动作",
                detail={"actions": interrupted_payload.get("actions") or []},
            )
            _finish_run_safe(
                run_id,
                status="awaiting_confirm",
                elapsed_ms=elapsed_ms,
                route=final_state.get("route"),
                evidence_source=final_state.get("evidence_source"),
                answer_preview=answer_text,
            )
            yield _sse(
                "action_pending",
                {
                    "thread_id": thread_id,
                    "run_id": run_id,
                    "risk_level": interrupted_payload.get("risk_level")
                    or final_state.get("risk_level"),
                    "message": interrupted_payload.get("message")
                    or "请确认是否执行动作",
                    "reason": interrupted_payload.get("reason")
                    or final_state.get("decide_reason"),
                    "actions": interrupted_payload.get("actions")
                    or final_state.get("pending_actions")
                    or [],
                },
            )
            yield _sse(
                "done",
                {
                    "elapsed_ms": elapsed_ms,
                    "row_count": len(final_state.get("evidence") or []),
                    "route": final_state.get("route"),
                    "evidence_source": final_state.get("evidence_source"),
                    "awaiting_confirmation": True,
                    "thread_id": thread_id,
                    "run_id": run_id,
                },
            )
            return

        _finish_run_safe(
            run_id,
            status="success",
            elapsed_ms=elapsed_ms,
            route=final_state.get("route"),
            evidence_source=final_state.get("evidence_source"),
            answer_preview=answer_text,
        )
        yield _sse(
            "done",
            {
                "elapsed_ms": elapsed_ms,
                "row_count": len(final_state.get("evidence") or []),
                "truncated": bool(final_state.get("structured_truncated")),
                "route": final_state.get("route"),
                "evidence_source": final_state.get("evidence_source"),
                "need_deepen": bool(final_state.get("need_deepen")),
                "awaiting_confirmation": False,
                "actions_executed": final_state.get("actions_executed") or [],
                "thread_id": thread_id,
                "run_id": run_id,
            },
        )

    except BusinessException as exc:
        # 节点抛异常时不会产出 update，current_node 会停在上一个节点；
        # 优先取节点包装函数挂在异常上的真实节点名
        failed_node = getattr(exc, FAILED_NODE_ATTR, None) or current_node or None
        executed = len(final_state.get("actions_executed") or [])
        message = exc.message
        if executed:
            # 动作在回答之前执行：这里要讲清楚"库已经改了"，避免用户以为白等了
            message = f"{message}（但已执行 {executed} 个动作，可在运行历史查看）"
        _record_step(
            run_id,
            step_name=failed_node or "error",
            summary=message,
            success=False,
        )
        _finish_run_safe(
            run_id,
            status="error",
            elapsed_ms=int((time.perf_counter() - started) * 1000),
            error_message=exc.message,
            answer_preview=answer_text or None,
        )
        yield _sse(
            "error",
            {
                "message": exc.message,
                "failed_node": failed_node,
                "run_id": run_id,
            },
        )
    except Exception as exc:
        failed_node = getattr(exc, FAILED_NODE_ATTR, None) or current_node or None
        logger.exception(
            "流式对话失败 question=%s node=%s", question, failed_node
        )
        _record_step(
            run_id,
            step_name=failed_node or "error",
            summary="对话失败",
            success=False,
        )
        _finish_run_safe(
            run_id,
            status="error",
            elapsed_ms=int((time.perf_counter() - started) * 1000),
            error_message="对话失败，请稍后重试",
            answer_preview=answer_text or None,
        )
        yield _sse(
            "error",
            {
                "message": "对话失败，请稍后重试",
                "failed_node": failed_node,
                "run_id": run_id,
            },
        )
    finally:
        from app.services.model_requests import cancel_model_requests
        cancel_model_requests(run_id)


# 巡检固定问题：措辞会影响路由，这里刻意命中「聚合 + 商品口碑」路径
PATROL_QUESTION = "最近哪些商品差评最多？帮我看看并处理"
