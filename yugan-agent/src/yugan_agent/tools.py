"""函数 -> Pydantic 校验 -> JSON Schema -> 可执行工具。"""

import asyncio
import inspect
import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, get_type_hints

from pydantic import BaseModel, ConfigDict, ValidationError, create_model

from .models import ToolResult


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    function: Callable
    parameters: type[BaseModel]
    side_effect: bool = False
    always_confirm: bool = False
    timeout: float | None = None

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters.model_json_schema(),
        }


def tool(
    function=None,
    *,
    name: str | None = None,
    side_effect: bool = False,
    always_confirm: bool = False,
    timeout: float | None = None,
):
    """给带类型标注和说明的函数加上 @tool，即可注册。"""

    def decorate(fn):
        tool_name = name or fn.__name__
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]{0,63}", tool_name):
            raise ValueError("工具名只能包含字母、数字和下划线，最长 64 字符")
        if timeout is not None and timeout <= 0:
            raise ValueError("工具超时必须大于 0")
        hints = get_type_hints(fn, include_extras=True)
        fields = {}
        for key, param in inspect.signature(fn).parameters.items():
            if param.kind not in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                raise TypeError("工具参数不支持 *args、**kwargs 或仅位置参数")
            if key not in hints:
                raise TypeError(f"工具参数 {key} 缺少类型标注")
            default = ... if param.default is inspect.Parameter.empty else param.default
            fields[key] = (hints[key], default)
        schema = create_model(
            f"{tool_name}Arguments", __config__=ConfigDict(extra="forbid"), **fields
        )
        return Tool(
            tool_name,
            inspect.getdoc(fn) or tool_name,
            fn,
            schema,
            side_effect,
            always_confirm,
            timeout,
        )

    return decorate(function) if function else decorate


ApprovalCallback = Callable[[str, str, dict[str, Any]], Awaitable[bool]]


class ToolRegistry:
    def __init__(
        self,
        *,
        timeout: float = 10,
        allowed_effects=(),
        approval_callback: ApprovalCallback | None = None,
    ):
        self._tools: dict[str, Tool] = {}
        self.timeout = timeout
        self.allowed_effects = set(allowed_effects)
        self.approval_callback = approval_callback

    def register(self, entry: Tool) -> Tool:
        if entry.name in self._tools:
            raise ValueError(f"工具已注册: {entry.name}")
        self._tools[entry.name] = entry
        return entry

    def unregister(self, name: str) -> Tool | None:
        """移除工具；工具管理配置更新时使用。"""
        return self._tools.pop(name, None)

    def schemas(self) -> list[dict]:
        return [entry.schema() for entry in self._tools.values()]

    async def execute(self, name: str, arguments: str | dict[str, Any]) -> ToolResult:
        entry = self._tools.get(name)
        if entry is None:
            return ToolResult(ok=False, error=f"未知工具: {name}")
        try:
            if isinstance(arguments, str):
                if len(arguments) > 32000:
                    raise ValueError("工具参数过长")
                arguments = json.loads(arguments)
            params = entry.parameters.model_validate(arguments)
            # 保留嵌套 Pydantic 对象的实际类型，避免 model_dump 改变函数参数类型。
            kwargs = {key: getattr(params, key) for key in type(params).model_fields}
            if entry.side_effect and (entry.always_confirm or name not in self.allowed_effects):
                if entry.always_confirm and self.approval_callback is None:
                    return ToolResult(ok=False, error=f"工具 {name} 需要在本地网页确认")
                if name not in self.allowed_effects and self.approval_callback is None:
                    return ToolResult(
                        ok=False, error=f"工具 {name} 有副作用，尚未列入 allowed_effects"
                    )
                if self.approval_callback is None:
                    return ToolResult(ok=False, error=f"工具 {name} 需要在本地网页确认")
                approved = await self.approval_callback(
                    name,
                    entry.description,
                    params.model_dump(mode="json"),
                )
                if not approved:
                    return ToolResult(ok=False, error="用户拒绝或未及时确认这次电脑操作")
            async with asyncio.timeout(entry.timeout or self.timeout):
                if inspect.iscoroutinefunction(entry.function):
                    value = await entry.function(**kwargs)
                else:
                    value = await asyncio.to_thread(entry.function, **kwargs)
            encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
            if len(encoded) > 16000:
                return ToolResult(ok=False, error="工具结果超过 16000 字符，请缩小查询范围")
            return ToolResult(ok=True, data=value)
        except ValidationError as exc:
            errors = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()]
            return ToolResult(ok=False, error="参数校验失败: " + "; ".join(errors))
        except TimeoutError:
            return ToolResult(ok=False, error="工具执行超时；有副作用的操作请核查是否已执行")
        except (ValueError, ArithmeticError, PermissionError, FileNotFoundError) as exc:
            return ToolResult(ok=False, error=str(exc)[:500])
        except Exception as exc:
            # 不向模型泄露第三方异常中的 URL、鉴权头和完整响应体。
            return ToolResult(ok=False, error=f"工具执行失败 ({type(exc).__name__})")
