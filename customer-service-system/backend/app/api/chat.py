"""流式对话与人工确认接口。"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.common.response import Response
from app.common.exceptions import BusinessException
from app.dependencies.auth import CurrentProductEditor, DbSession
from app.observability.models import AgentRun
from app.schemas.chat import ActionConfirmRequest, ChatRequest, ModelResultRequest
from app.services import chat_service, confirmation_service
from app.services import model_requests

router = APIRouter(prefix="/chat", tags=["对话"])


@router.post("/runs/{run_id}/model-requests/{request_id}")
def receive_model_result(
    run_id: int, request_id: str, body: ModelResultRequest,
    db: DbSession, current_user: CurrentProductEditor,
):
    run = db.get(AgentRun, run_id)
    if not run or run.user_id != current_user.id:
        raise BusinessException(message="运行记录不存在或无权读取", code=404)
    result = model_requests.submit_model_result(run_id, request_id, body.content, body.error)
    if result.get("accepted") and body.error and run.status == "running":
        run.status = "cancelled" if body.cancelled else "error"
        run.error_message = body.error
        db.commit()
    return Response.success(data=result)


@router.get("/runs/{run_id}/answer-context")
def get_answer_context(run_id: int, db: DbSession, current_user: CurrentProductEditor):
    """恢复已经完成的分析与回答；此接口只读取，不重新生成报告或修改商品。"""
    run = db.get(AgentRun, run_id)
    if not run or run.user_id != current_user.id:
        raise BusinessException(message="运行记录不存在或无权读取", code=404)
    pending = confirmation_service.get_pending_confirmation(run.thread_id, current_user.id)
    return Response.success(data={
        "run_id": run.id, "question": run.question, "status": run.status,
        "route": run.route, "elapsed_ms": run.elapsed_ms,
        "answer": run.answer_text or "", "messages": run.answer_context or [],
        "pending_action": pending,
    })


@router.post("/runs/{run_id}/report")
def save_answer_report(run_id: int, db: DbSession, current_user: CurrentProductEditor):
    from app.services.saved_reports import save_run_report
    return Response.success(data=save_run_report(db, run_id, current_user.id))


@router.post("/stream")
def chat_stream(
    body: ChatRequest,
    current_user: CurrentProductEditor,
):
    """SSE 流式对话：LangGraph 分析 + 大模型总结。

    事件类型：
    - status / route / token / done / error
    - action_pending：商品复核或后台配置修改待确认

    若收到 action_pending，请调用 POST /api/chat/actions/confirm。
    """
    if body.use_agent_model and body.model_protocol < 2:
        return StreamingResponse(iter([chat_service._sse("error", {
            "message": "问答组件已更新，请刷新页面后重新提问。"
        })]), media_type="text/event-stream")
    return StreamingResponse(
        chat_service.stream_chat(
            body.question,
            user_id=current_user.id,
            history=[turn.model_dump() for turn in body.history],
            use_agent_model=body.use_agent_model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/actions/confirm")
def confirm_actions(
    body: ActionConfirmRequest,
    current_user: CurrentProductEditor,
):
    """确认或取消高风险动作，恢复被 interrupt 暂停的图。"""
    result = confirmation_service.resume_actions(
        body.thread_id, body.approved, user_id=current_user.id
    )
    return Response.success(data=result)
