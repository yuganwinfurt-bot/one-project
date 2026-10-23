"""结构化查询相关的请求 / 响应模型。"""

from typing import Any

from pydantic import BaseModel, Field


class Nl2SqlRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500, description="自然语言问题")


class Nl2SqlResponse(BaseModel):
    question: str
    sql: str
    row_count: int
    truncated: bool = False
    rows: list[dict[str, Any]]
