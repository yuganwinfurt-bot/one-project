"""各模型供应商共用的数据结构。"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_call_id: str | None = None
    is_error: bool = False
    # 保留供应商要求回传的原始块供模型多轮调用；不会通过网页会话 API 展示。
    provider: str | None = None
    provider_data: list[dict[str, Any]] = Field(default_factory=list)


class ToolResult(BaseModel):
    ok: bool
    data: Any = None
    error: str | None = None


class Event(BaseModel):
    kind: str
    step: int = 0
    name: str = ""
    ok: bool = True
    duration_ms: int = 0
    detail: str = ""


class RunResult(BaseModel):
    session_id: str
    run_id: str
    status: Literal["completed", "limited", "error"]
    answer: str
    events: list[Event]


class ExecutionEntry(BaseModel):
    """可核验的运行事件；不保存模型内部推理、提示词、工具参数或返回正文。"""

    kind: Literal["model", "rag", "tool", "run"]
    step: int = Field(default=0, ge=0, le=100)
    name: str = Field(default="", max_length=128)
    status: Literal["info", "ok", "error", "skipped"] = "info"
    duration_ms: int = Field(default=0, ge=0, le=600_000)
    detail: str = Field(default="", max_length=240)


class ExecutionTrace(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    created_at: str = Field(min_length=1, max_length=40)
    turn_index: int | None = Field(default=None, ge=0)
    model: str = Field(default="", max_length=128)
    entries: list[ExecutionEntry] = Field(default_factory=list, max_length=100)


class Snapshot(BaseModel):
    messages: list[Message] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)
    execution_traces: list[ExecutionTrace] = Field(default_factory=list)
    version: int = 0
