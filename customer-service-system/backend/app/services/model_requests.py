"""把规划及 SQL 修正交给浏览器当前模型；后端只接收结果，不接收 API Key。

与现有 LangGraph MemorySaver 一样用于单个应用进程；请求结束或超时即清理。
"""

from dataclasses import dataclass, field
from threading import Event, Lock
from time import monotonic
from typing import Any, Callable
from uuid import uuid4

from langgraph.config import get_stream_writer

from app.common.exceptions import BusinessException


@dataclass
class PendingModelRequest:
    run_id: int
    validate: Callable[[str], Any]
    ready: Event = field(default_factory=Event)
    value: Any = None
    error: str | None = None


_pending: dict[str, PendingModelRequest] = {}
_lock = Lock()
MODEL_REQUEST_TIMEOUT = 120.0


def request_model(run_id: int | None, purpose: str, messages: list[dict], validate: Callable[[str], Any]) -> Any:
    if run_id is None:
        raise BusinessException(message="未能创建运行记录，无法连接当前模型")
    request_id = uuid4().hex
    pending = PendingModelRequest(run_id=run_id, validate=validate)
    with _lock:
        _pending[request_id] = pending
    try:
        writer = get_stream_writer()
        writer({"model_request": {
            "request_id": request_id, "run_id": run_id, "purpose": purpose,
            "messages": messages, "timeout_ms": int(MODEL_REQUEST_TIMEOUT * 1000),
        }})
        started = monotonic()
        last_update = started
        while not pending.ready.wait(0.5):
            now = monotonic()
            if now - started >= MODEL_REQUEST_TIMEOUT:
                raise BusinessException(message="当前所选模型响应超时，未切换到其他模型")
            if now - last_update >= 10:
                writer({"progress": "model_wait", "message": f"当前模型正在{purpose}（{int(now - started)}秒）…"})
                last_update = now
        if pending.error:
            raise BusinessException(message=pending.error)
        return pending.value
    finally:
        with _lock:
            _pending.pop(request_id, None)


def submit_model_result(run_id: int, request_id: str, content: str, error: str | None = None) -> dict:
    with _lock:
        pending = _pending.get(request_id)
    if pending is None or pending.run_id != run_id or pending.ready.is_set():
        return {"accepted": False, "expired": True, "error": "模型请求已结束或失效"}
    if error:
        pending.error = error[:500]
        pending.ready.set()
        return {"accepted": True}
    try:
        value = pending.validate(content)
    except (BusinessException, ValueError, TypeError, KeyError) as exc:
        return {"accepted": False, "error": (getattr(exc, "message", None) or str(exc))[:1000]}
    pending.value = value
    pending.ready.set()
    return {"accepted": True}


def cancel_model_requests(run_id: int | None) -> None:
    with _lock:
        for pending in _pending.values():
            if pending.run_id == run_id and not pending.ready.is_set():
                pending.error = "本次模型请求已取消"
                pending.ready.set()
