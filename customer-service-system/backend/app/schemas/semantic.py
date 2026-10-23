"""语义检索相关请求 / 响应模型。"""

from typing import Any

from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500, description="模糊主题 / 自然语言问题")
    top_k: int = Field(default=5, ge=1, le=20, description="返回条数")


class SemanticSearchResponse(BaseModel):
    query: str
    top_k: int
    hit_count: int
    collection_size: int
    hits: list[dict[str, Any]]
