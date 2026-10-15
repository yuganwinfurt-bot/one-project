from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    knowledge_base_ids: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("项目名称不能为空")
        return value


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    knowledge_base_ids: list[str] | None = None


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    description: str = Field(default="", max_length=240)

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("知识库名称不能为空")
        return value


class AgentRetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    knowledge_base_ids: list[Annotated[str, Field(min_length=1, max_length=64)]] = Field(
        min_length=1, max_length=20
    )

    @field_validator("query")
    @classmethod
    def trim_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("检索问题不能为空")
        return value


class ChatCreate(BaseModel):
    scope_mode: Literal["project", "custom"] = "project"
    knowledge_base_ids: list[str] | None = None


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=12000)
    knowledge_base_ids: list[str] | None = None

    @field_validator("content")
    @classmethod
    def trim_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("问题不能为空")
        return value


class ChatUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=80)
    scope_mode: Literal["project", "custom"] | None = None
    knowledge_base_ids: list[str] | None = None
