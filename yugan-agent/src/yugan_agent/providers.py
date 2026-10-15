"""模型适配层。核心 Agent 不依赖任何供应商消息格式。"""

import asyncio
import json
import re
from typing import Protocol
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from .config import Settings
from .models import Message, ToolCall


class ModelProvider(Protocol):
    async def complete(
        self, messages: list[Message], tools: list[dict], *, effort: str = "auto"
    ) -> Message: ...
    async def close(self) -> None: ...


def chat_messages(messages: list[Message], *, provider: str | None = None) -> list[dict]:
    result = []
    for m in messages:
        item = {"role": m.role, "content": m.content}
        if m.tool_calls and not m.content:
            item["content"] = None
        if m.provider == provider and provider in {"deepseek", "kimi"} and m.provider_data:
            reasoning = m.provider_data[0].get("reasoning_content")
            if reasoning:
                item["reasoning_content"] = reasoning
        if m.tool_calls:
            item["tool_calls"] = [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {
                        "name": c.name,
                        "arguments": c.arguments,
                    },
                }
                for c in m.tool_calls
            ]
        if m.tool_call_id:
            item["tool_call_id"] = m.tool_call_id
        result.append(item)
    return result


def responses_input(messages: list[Message]) -> list[dict]:
    result = []
    for m in messages:
        if m.role == "tool":
            result.append(
                {"type": "function_call_output", "call_id": m.tool_call_id, "output": m.content}
            )
        elif m.provider == "openai" and m.provider_data:
            result.extend(m.provider_data)
        else:
            if m.content:
                result.append({"role": m.role, "content": m.content})
            for c in m.tool_calls:
                result.append(
                    {
                        "type": "function_call",
                        "call_id": c.id,
                        "name": c.name,
                        "arguments": c.arguments,
                    }
                )
    return result


class OpenAIProvider:
    def __init__(self, settings: Settings, client=None):
        self.settings = settings
        self.client = client
        self._client_lock = asyncio.Lock()

    async def _client(self):
        if self.client is None:
            async with self._client_lock:
                if self.client is None:
                    host = urlsplit(self.settings.base_url or "").hostname
                    local_client = (
                        httpx.AsyncClient(trust_env=False)
                        if host in {"127.0.0.1", "localhost", "::1"}
                        else None
                    )
                    self.client = await asyncio.to_thread(
                        AsyncOpenAI,
                        api_key=self.settings.api_key.get_secret_value(),
                        base_url=self.settings.base_url,
                        timeout=self.settings.model_timeout,
                        max_retries=2,
                        **({"http_client": local_client} if local_client else {}),
                    )
        return self.client

    def _compatible_kwargs(self, messages, tools, effort):
        host = urlsplit(self.settings.base_url or "").hostname
        is_deepseek = host == "api.deepseek.com"
        is_kimi_k3 = host == "api.moonshot.cn" and self.settings.model == "kimi-k3"
        kwargs = {
            "model": self.settings.model,
            "messages": chat_messages(
                messages,
                provider="deepseek"
                if is_deepseek
                else "kimi"
                if host == "api.moonshot.cn"
                else None,
            ),
        }
        # The DeepSeek thinking budget includes reasoning and visible output.
        deepseek_thinking = is_deepseek and (
            effort != "auto" or self.settings.thinking != "disabled"
        )
        if not deepseek_thinking:
            kwargs["max_tokens"] = self.settings.max_output_tokens
        if tools:
            kwargs["tools"] = [{"type": "function", "function": t} for t in tools]
        if is_kimi_k3:
            kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
        if effort != "auto" and not (is_deepseek or is_kimi_k3):
            raise ValueError("当前兼容接口没有统一的模型强度参数，请选择默认强度")
        if (is_deepseek or is_kimi_k3) and effort != "auto":
            kwargs["reasoning_effort"] = {
                "low": "low",
                "medium": "high",
                "high": "high",
                "max": "max",
            }[effort]
            if is_deepseek:
                kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
        elif self.settings.thinking != "auto" and not is_kimi_k3:
            kwargs["extra_body"] = {"thinking": {"type": self.settings.thinking}}
        return kwargs

    async def complete_stream(self, messages, tools, *, effort="auto", on_progress):
        """Stream DeepSeek's reasoning while reconstructing its complete tool reply."""
        if (
            self.settings.provider != "compatible"
            or urlsplit(self.settings.base_url or "").hostname != "api.deepseek.com"
        ):
            reply = await self.complete(messages, tools, effort=effort)
            for block in reply.provider_data:
                if isinstance(block.get("reasoning_content"), str):
                    await on_progress({"kind": "reasoning", "delta": block["reasoning_content"]})
            return reply
        client = await self._client()
        kwargs = self._compatible_kwargs(messages, tools, effort)
        stream = await client.chat.completions.create(**kwargs, stream=True)
        reasoning_parts, content_parts = [], []
        tool_parts = {}
        finish_reason = None
        async for chunk in stream:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                reasoning_parts.append(reasoning)
                await on_progress({"kind": "reasoning", "delta": reasoning})
            if delta.content:
                content_parts.append(delta.content)
                await on_progress({"kind": "answer_delta", "delta": delta.content})
            for call in delta.tool_calls or []:
                part = tool_parts.setdefault(call.index, {"id": "", "name": "", "arguments": ""})
                if call.id:
                    part["id"] += call.id
                if call.function:
                    part["name"] += call.function.name or ""
                    part["arguments"] += call.function.arguments or ""
            if choice.finish_reason:
                finish_reason = choice.finish_reason
        if finish_reason not in ("stop", "tool_calls"):
            raise ValueError(f"模型输出不完整或被过滤（结束原因：{finish_reason or '未知'}）")
        return Message(
            role="assistant",
            content="".join(content_parts),
            tool_calls=[
                ToolCall(id=part["id"], name=part["name"], arguments=part["arguments"])
                for _, part in sorted(tool_parts.items())
            ],
            provider="deepseek",
            provider_data=(
                [{"reasoning_content": "".join(reasoning_parts)}] if reasoning_parts else []
            ),
        )

    async def complete(self, messages, tools, *, effort: str = "auto") -> Message:
        client = await self._client()
        if self.settings.provider == "compatible":
            host = urlsplit(self.settings.base_url or "").hostname
            is_deepseek = host == "api.deepseek.com"
            is_kimi = host == "api.moonshot.cn"
            kwargs = self._compatible_kwargs(messages, tools, effort)
            response = await client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            if choice.finish_reason not in ("stop", "tool_calls"):
                reason = choice.finish_reason or "未知"
                output_budget = kwargs.get(
                    "max_tokens", kwargs.get("max_completion_tokens", "API 默认值")
                )
                raise ValueError(
                    f"模型输出不完整或被过滤（结束原因：{reason}，"
                    f"max_tokens={output_budget}），"
                    "请检查输出长度和模型配置"
                )
            m = choice.message
            reasoning_content = getattr(m, "reasoning_content", None)
            return Message(
                role="assistant",
                content=m.content or getattr(m, "refusal", None) or "",
                tool_calls=[
                    ToolCall(id=c.id, name=c.function.name, arguments=c.function.arguments)
                    for c in (m.tool_calls or [])
                    if c.type == "function"
                ],
                provider="deepseek" if is_deepseek else "kimi" if is_kimi else None,
                provider_data=(
                    [{"reasoning_content": reasoning_content}]
                    if (is_deepseek or is_kimi) and reasoning_content
                    else []
                ),
            )
        kwargs = {
            "model": self.settings.model,
            "input": responses_input(messages),
            "tools": [{"type": "function", **t, "strict": False} for t in tools],
            "max_output_tokens": self.settings.max_output_tokens,
            "store": False,
            "include": ["reasoning.encrypted_content"],
        }
        if effort != "auto":
            if not self.settings.model.startswith(("gpt-5", "o1", "o3", "o4")):
                raise ValueError("这个 OpenAI 模型不支持可调思考强度，请选择默认")
            kwargs["reasoning"] = {"effort": "xhigh" if effort == "max" else effort}
        response = await client.responses.create(**kwargs)
        if response.status != "completed":
            raise ValueError("模型输出未完成，请提高输出预算或缩短任务")
        return Message(
            role="assistant",
            content=response.output_text,
            tool_calls=[
                ToolCall(id=c.call_id, name=c.name, arguments=c.arguments)
                for c in response.output
                if c.type == "function_call"
            ],
            provider="openai",
            provider_data=[c.model_dump(mode="json", exclude_none=True) for c in response.output],
        )

    async def close(self):
        if self.client is not None:
            await self.client.close()


def anthropic_messages(messages: list[Message]) -> tuple[str, list[dict]]:
    system = "\n\n".join(m.content for m in messages if m.role == "system")
    result: list[dict] = []
    for m in messages:
        if m.role == "system":
            continue
        role = "user" if m.role == "tool" else m.role
        if m.role == "tool":
            blocks = [
                {
                    "type": "tool_result",
                    "tool_use_id": m.tool_call_id,
                    "content": m.content,
                    "is_error": m.is_error,
                }
            ]
        elif m.provider == "anthropic" and m.provider_data:
            blocks = m.provider_data
        else:
            blocks = [{"type": "text", "text": m.content}] if m.content else []
            blocks += [
                {"type": "tool_use", "id": c.id, "name": c.name, "input": json.loads(c.arguments)}
                for c in m.tool_calls
            ]
        if result and result[-1]["role"] == role:
            result[-1]["content"].extend(blocks)
        else:
            result.append({"role": role, "content": list(blocks)})
    return system, result


class AnthropicProvider:
    def __init__(self, settings: Settings, client=None):
        self.settings = settings
        self.client = client
        self._client_lock = asyncio.Lock()

    async def _client(self):
        if self.client is None:
            async with self._client_lock:
                if self.client is None:
                    self.client = await asyncio.to_thread(
                        AsyncAnthropic,
                        api_key=self.settings.api_key.get_secret_value(),
                        base_url=self.settings.base_url,
                        timeout=self.settings.model_timeout,
                        max_retries=2,
                    )
        return self.client

    async def complete(self, messages, tools, *, effort: str = "auto") -> Message:
        client = await self._client()
        system, converted = anthropic_messages(messages)
        kwargs = {
            "model": self.settings.model,
            "max_tokens": self.settings.max_output_tokens,
            "system": system,
            "messages": converted,
            "tools": [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "input_schema": t["parameters"],
                }
                for t in tools
            ],
        }
        if effort != "auto":
            kwargs["output_config"] = {"effort": effort}
        response = await client.messages.create(**kwargs)
        if response.stop_reason not in ("end_turn", "tool_use", "stop_sequence"):
            raise ValueError("Claude 输出未完成，请提高输出预算或缩短任务")
        return Message(
            role="assistant",
            content="\n".join(c.text for c in response.content if c.type == "text"),
            tool_calls=[
                ToolCall(id=c.id, name=c.name, arguments=json.dumps(c.input))
                for c in response.content
                if c.type == "tool_use"
            ],
            provider="anthropic",
            provider_data=[c.model_dump(mode="json", exclude_none=True) for c in response.content],
        )

    async def close(self):
        if self.client is not None:
            await self.client.close()


class MockProvider:
    """确定性的离线演示，演示真实工具链路，不冒充大语言模型。"""

    async def complete(self, messages, tools, *, effort: str = "auto") -> Message:
        if messages[-1].role == "tool":
            return Message(
                role="assistant", content="[离线演示] 工具执行结果：\n" + messages[-1].content
            )
        prompt = messages[-1].content.strip()
        call = None
        if prompt.startswith(("计算 ", "calc ")):
            call = ("calculator", {"expression": prompt.split(" ", 1)[1]})
        elif "温度" in prompt or "传感器" in prompt:
            call = ("csv_summary", {"path": "sensor_readings.csv", "column": "temperature"})
        elif prompt.startswith("读取 "):
            call = ("read_file", {"path": prompt[3:].strip()})
        elif "文件" in prompt:
            call = ("list_files", {})
        elif "时间" in prompt:
            call = ("current_time", {})
        elif prompt.startswith("统计 "):
            call = (
                "numeric_stats",
                {"values": [float(x) for x in re.split(r"[,，\s]+", prompt[3:].strip())]},
            )
        if call:
            name, arguments = call
            return Message(
                role="assistant",
                tool_calls=[
                    ToolCall(
                        id="demo_" + uuid4().hex[:12],
                        name=name,
                        arguments=json.dumps(arguments, ensure_ascii=False),
                    )
                ],
            )
        return Message(
            role="assistant",
            content=(
                "[离线演示] 当前未连接大模型。可以试试：\n"
                "计算 (12 + 8) * 3\n分析传感器温度\n列出文件\n读取 notes.md\n现在时间\n"
                "统计 24,26,30\n连接真实模型后支持自然语言规划和多轮推理。"
            ),
        )

    async def close(self):
        pass


def create_provider(settings: Settings) -> ModelProvider:
    if settings.provider == "mock":
        return MockProvider()
    if settings.provider == "anthropic":
        return AnthropicProvider(settings)
    return OpenAIProvider(settings)
