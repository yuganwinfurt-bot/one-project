"""对话相关请求模型。"""

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    """一轮历史消息（前端把最近几条带上来，用于多轮指代消解）。"""

    role: str = Field(pattern="^(user|assistant)$", description="user / assistant")
    content: str = Field(max_length=2000, description="该轮文本")


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000, description="用户问题")
    # 最多带最近 10 条；不带也能用（单轮问答行为不变）
    history: list[ChatTurn] = Field(default_factory=list, max_length=10, description="最近对话")
    # 由浏览器使用 Agent 当前模型生成最终回答；密钥不发送到电商后端。
    use_agent_model: bool = Field(default=False, description="是否使用浏览器侧 Agent 模型生成最终回答")
    model_protocol: int = Field(default=1, ge=1, le=2)


class ActionConfirmRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=64, description="中断时的会话 ID")
    approved: bool = Field(description="是否确认执行动作")


class ModelResultRequest(BaseModel):
    content: str = Field(default="", max_length=60000)
    error: str | None = Field(default=None, max_length=500)
    cancelled: bool = False
