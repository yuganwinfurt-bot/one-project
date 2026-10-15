"""通过官方 SDK 和本地假 HTTP 响应验证三种模型协议的工具往返。"""

import json

import httpx
import pytest
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from pydantic import SecretStr

from yugan_agent.config import Settings
from yugan_agent.models import Message, ToolCall
from yugan_agent.providers import AnthropicProvider, OpenAIProvider

TOOL = {
    "name": "calculator",
    "description": "计算",
    "parameters": {
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"],
        "additionalProperties": False,
    },
}


@pytest.mark.asyncio
async def test_openai_responses_sdk_tool_roundtrip():
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        output = (
            [
                {
                    "id": "fc_1",
                    "type": "function_call",
                    "name": "calculator",
                    "call_id": "call_1",
                    "arguments": '{"expression":"2+3"}',
                    "status": "completed",
                }
            ]
            if len(requests) == 1
            else [
                {
                    "id": "msg_1",
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": "5", "annotations": []}],
                }
            ]
        )
        return httpx.Response(
            200,
            json={
                "id": f"resp_{len(requests)}",
                "object": "response",
                "created_at": 0,
                "model": "test-model",
                "status": "completed",
                "output": output,
                "parallel_tool_calls": True,
                "tools": [],
            },
        )

    client = AsyncOpenAI(
        api_key="test",
        base_url="https://api.test/v1",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        max_retries=0,
    )
    provider = OpenAIProvider(
        Settings(provider="openai", model="gpt-5.2-codex", api_key=SecretStr("test")), client=client
    )
    messages = [Message(role="user", content="计算 2+3")]
    try:
        first = await provider.complete(messages, [TOOL], effort="max")
        assert first.tool_calls[0].id == "call_1"
        messages.extend([first, Message(role="tool", tool_call_id="call_1", content="5")])
        second = await provider.complete(messages, [TOOL], effort="max")
        assert second.content == "5"
        assert requests[0]["store"] is False
        assert requests[0]["reasoning"] == {"effort": "xhigh"}
        assert any(item.get("type") == "function_call_output" for item in requests[1]["input"])
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_deepseek_compatible_sdk_tool_roundtrip():
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        message = (
            {
                "role": "assistant",
                "content": None,
                "reasoning_content": "thinking",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "calculator", "arguments": '{"expression":"2+3"}'},
                    }
                ],
            }
            if len(requests) == 1
            else {"role": "assistant", "content": "5"}
        )
        return httpx.Response(
            200,
            json={
                "id": "chat_1",
                "object": "chat.completion",
                "created": 0,
                "model": "deepseek-flash",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "tool_calls" if len(requests) == 1 else "stop",
                        "message": message,
                    }
                ],
            },
        )

    client = AsyncOpenAI(
        api_key="test",
        base_url="https://api.deepseek.com",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        max_retries=0,
    )
    provider = OpenAIProvider(
        Settings(
            provider="compatible",
            model="deepseek-flash",
            api_key=SecretStr("test"),
            base_url="https://api.deepseek.com",
            thinking="disabled",
        ),
        client=client,
    )
    messages = [Message(role="user", content="计算 2+3")]
    try:
        first = await provider.complete(messages, [TOOL], effort="max")
        messages.extend([first, Message(role="tool", tool_call_id="call_1", content="5")])
        second = await provider.complete(messages, [TOOL], effort="max")
        assert second.content == "5"
        await provider.complete([Message(role="user", content="普通回复")], [], effort="auto")
        assert all(requests[index]["thinking"] == {"type": "enabled"} for index in (0, 1))
        assert all(requests[index]["reasoning_effort"] == "max" for index in (0, 1))
        # DeepSeek's token budget includes reasoning; omit the small fixed cap so
        # the API can choose its larger mode-aware default for thinking requests.
        assert all("max_tokens" not in requests[index] for index in (0, 1))
        # Explicitly disabled thinking still honors the configured output limit.
        assert requests[2]["max_tokens"] == 2048
        assert requests[2]["thinking"] == {"type": "disabled"}
        assert requests[1]["messages"][1]["reasoning_content"] == "thinking"
        assert requests[1]["messages"][-1]["tool_call_id"] == "call_1"
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_deepseek_stream_shows_reasoning_and_reassembles_tool_call():
    request_bodies = []

    async def handler(request):
        request_bodies.append(json.loads(request.content))
        deltas = [
            {"reasoning_content": "先计算"},
            {"reasoning_content": "表达式。"},
            {
                "tool_calls": [
                    {
                        "index": 0,
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "calculator", "arguments": '{"expression":'},
                    }
                ]
            },
            {"tool_calls": [{"index": 0, "function": {"arguments": '"2+3"}'}}]},
        ]
        events = [
            {
                "id": "chat_1",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "deepseek-flash",
                "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
            }
            for delta in deltas
        ]
        events.append(
            {
                "id": "chat_1",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "deepseek-flash",
                "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}],
            }
        )
        body = "".join(f"data: {json.dumps(event)}\n\n" for event in events) + "data: [DONE]\n\n"
        return httpx.Response(200, content=body, headers={"content-type": "text/event-stream"})

    client = AsyncOpenAI(
        api_key="test",
        base_url="https://api.deepseek.com",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        max_retries=0,
    )
    provider = OpenAIProvider(
        Settings(
            provider="compatible",
            model="deepseek-flash",
            api_key=SecretStr("test"),
            base_url="https://api.deepseek.com",
            thinking="disabled",
        ),
        client=client,
    )
    updates = []

    async def on_progress(update):
        updates.append(update)

    try:
        reply = await provider.complete_stream(
            [Message(role="user", content="计算 2+3")],
            [TOOL],
            effort="max",
            on_progress=on_progress,
        )
        assert request_bodies[0]["stream"] is True
        assert [item["delta"] for item in updates] == ["先计算", "表达式。"]
        assert reply.provider_data == [{"reasoning_content": "先计算表达式。"}]
        assert reply.tool_calls == [
            ToolCall(id="call_1", name="calculator", arguments='{"expression":"2+3"}')
        ]
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_kimi_k3_sdk_tool_roundtrip_preserves_reasoning():
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        message = (
            {
                "role": "assistant",
                "content": None,
                "reasoning_content": "plan",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "calculator", "arguments": '{"expression":"2+3"}'},
                    }
                ],
            }
            if len(requests) == 1
            else {"role": "assistant", "content": "5"}
        )
        return httpx.Response(
            200,
            json={
                "id": "chat_1",
                "object": "chat.completion",
                "created": 0,
                "model": "kimi-k3",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "tool_calls" if len(requests) == 1 else "stop",
                        "message": message,
                    }
                ],
            },
        )

    client = AsyncOpenAI(
        api_key="test",
        base_url="https://api.moonshot.cn/v1",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        max_retries=0,
    )
    provider = OpenAIProvider(
        Settings(
            provider="compatible",
            model="kimi-k3",
            api_key=SecretStr("test"),
            base_url="https://api.moonshot.cn/v1",
        ),
        client=client,
    )
    messages = [Message(role="user", content="计算 2+3")]
    try:
        first = await provider.complete(messages, [TOOL], effort="max")
        assert first.tool_calls[0].id == "call_1"
        messages.extend([first, Message(role="tool", tool_call_id="call_1", content="5")])
        second = await provider.complete(messages, [TOOL], effort="max")
        assert second.content == "5"
        assert all(body["reasoning_effort"] == "max" for body in requests)
        assert all("thinking" not in body for body in requests)
        assert all(body["max_completion_tokens"] == 2048 for body in requests)
        assert all("max_tokens" not in body for body in requests)
        assert requests[1]["messages"][1]["content"] is None
        assert requests[1]["messages"][1]["reasoning_content"] == "plan"
        assert requests[1]["messages"][1]["tool_calls"][0]["id"] == "call_1"
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_anthropic_sdk_tool_roundtrip():
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        content = (
            [
                {
                    "type": "tool_use",
                    "id": "toolu_1",
                    "name": "calculator",
                    "input": {"expression": "2+3"},
                }
            ]
            if len(requests) == 1
            else [{"type": "text", "text": "5"}]
        )
        return httpx.Response(
            200,
            json={
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "content": content,
                "model": "test-model",
                "stop_reason": "tool_use" if len(requests) == 1 else "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 4},
            },
        )

    client = AsyncAnthropic(
        api_key="test",
        base_url="https://api.test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        max_retries=0,
    )
    provider = AnthropicProvider(
        Settings(provider="anthropic", model="test-model", api_key=SecretStr("test")), client=client
    )
    messages = [Message(role="user", content="计算 2+3")]
    try:
        first = await provider.complete(messages, [TOOL])
        messages.extend([first, Message(role="tool", tool_call_id="toolu_1", content="5")])
        second = await provider.complete(messages, [TOOL])
        assert second.content == "5"
        assert requests[1]["messages"][-1]["content"][0]["type"] == "tool_result"
    finally:
        await provider.close()
