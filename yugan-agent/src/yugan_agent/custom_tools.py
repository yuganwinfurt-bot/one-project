"""用户自定义的固定 HTTP 工具；不执行用户提供的 Python 代码。"""

import json
from typing import Literal
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr, create_model, model_validator

from .tools import Tool, ToolRegistry


class ToolParameter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(pattern=r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$", max_length=64)
    kind: Literal["string", "number", "integer", "boolean"] = "string"
    description: str = Field(default="", max_length=300)
    required: bool = True


class CustomToolDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(pattern=r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$", max_length=64)
    description: str = Field(min_length=1, max_length=500)
    endpoint: str = Field(min_length=8, max_length=2048)
    method: Literal["GET", "POST"] = "GET"
    api_key: SecretStr = SecretStr("")
    parameters: list[ToolParameter] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def validate_endpoint_and_parameters(self):
        parsed = urlsplit(self.endpoint)
        if (
            not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("接口地址需要是固定 URL，不能包含账号、密码、查询参数或片段")
        if parsed.scheme != "https" and not (
            parsed.scheme == "http" and parsed.hostname.lower() in {"127.0.0.1", "localhost", "::1"}
        ):
            raise ValueError("自定义工具接口必须使用 HTTPS；本机服务允许 HTTP")
        if len({item.name for item in self.parameters}) != len(self.parameters):
            raise ValueError("参数名称不能重复")
        if any(char in self.api_key.get_secret_value() for char in "\r\n"):
            raise ValueError("API Key 格式无效")
        if len(self.api_key.get_secret_value()) > 4096:
            raise ValueError("API Key 不能超过 4096 个字符")
        return self

    def for_storage(self) -> dict:
        return self.model_dump(exclude={"api_key"}) | {"api_key": self.api_key.get_secret_value()}

    def public(self) -> dict:
        return self.model_dump(exclude={"api_key"}) | {
            "has_api_key": bool(self.api_key.get_secret_value())
        }


def build_custom_tool(definition: CustomToolDefinition) -> Tool:
    python_types = {"string": str, "number": float, "integer": int, "boolean": bool}
    fields = {}
    for item in definition.parameters:
        annotation = python_types[item.kind]
        field = Field(description=item.description or None)
        if item.required:
            fields[item.name] = (annotation, field)
        else:
            optional_field = Field(default=None, description=item.description or None)
            fields[item.name] = (annotation | None, optional_field)
    schema = create_model(
        f"{definition.name}Arguments", __config__=ConfigDict(extra="forbid"), **fields
    )
    endpoint = definition.endpoint
    method = definition.method
    api_key = definition.api_key.get_secret_value()

    async def invoke(**arguments):
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        async with httpx.AsyncClient(timeout=8, follow_redirects=False, trust_env=False) as client:
            async with client.stream(
                method,
                endpoint,
                params=arguments if method == "GET" else None,
                json=arguments if method == "POST" else None,
                headers=headers,
            ) as response:
                if not 200 <= response.status_code < 300:
                    raise ValueError(f"自定义接口返回 HTTP {response.status_code}")
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > 12000:
                        raise ValueError("接口响应超过 12000 字节")
                content = body.decode("utf-8", errors="replace")
                try:
                    content = json.loads(content)
                except (json.JSONDecodeError, ValueError):
                    pass
                return {"status": response.status_code, "content": content}

    return Tool(definition.name, definition.description, invoke, schema)


def register_custom_tools(registry: ToolRegistry, definitions: list[CustomToolDefinition]) -> None:
    for definition in definitions:
        registry.register(build_custom_tool(definition))
