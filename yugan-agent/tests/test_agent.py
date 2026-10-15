import asyncio
import json

import pytest

from yugan_agent.agent import Agent
from yugan_agent.builtins import register_builtins
from yugan_agent.config import Settings
from yugan_agent.memory import SQLiteMemory, window
from yugan_agent.models import Message, ToolCall
from yugan_agent.tools import ToolRegistry, tool


def build_agent(tmp_path, provider=None, **overrides):
    settings = Settings(
        provider="mock",
        model="demo",
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
        **overrides,
    )
    registry = ToolRegistry(timeout=settings.tool_timeout)
    register_builtins(registry, settings.workspace, {})
    if provider is None:
        from yugan_agent.providers import MockProvider

        provider = MockProvider()
    return Agent(provider, registry, SQLiteMemory(settings.database), settings)


@pytest.mark.asyncio
async def test_mock_tool_and_persisted_session(tmp_path):
    agent = build_agent(tmp_path)
    try:
        result = await agent.run("计算 (12 + 8) * 3", "math")
        assert result.status == "completed"
        assert json.loads(result.answer.split("\n", 1)[1])["data"] == 60
        assert [event.name for event in result.events if event.kind == "tool"] == ["calculator"]
        saved = agent.memory.load("math")
        assert [message.role for message in saved.messages] == [
            "user",
            "assistant",
            "tool",
            "assistant",
        ]
        assert saved.messages[2].tool_call_id == saved.messages[1].tool_calls[0].id
        assert agent.memory.load("other").messages == []
        assert agent.memory.load("math").version == 1
    finally:
        await agent.close()


class ScriptedProvider:
    def __init__(self):
        self.calls = 0

    async def complete(self, messages, tools):
        self.calls += 1
        if self.calls == 1:
            return Message(
                role="assistant",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="calculator",
                        arguments='{"expression":"1+2"}',
                    )
                ],
            )
        assert messages[-1].role == "tool"
        assert json.loads(messages[-1].content)["data"] == 3
        return Message(role="assistant", content="结果是 3")

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_model_tool_feedback_loop(tmp_path):
    provider = ScriptedProvider()
    agent = build_agent(tmp_path, provider)
    assert (await agent.run("请计算", "s")).answer == "结果是 3"
    assert provider.calls == 2
    await agent.close()


@pytest.mark.asyncio
async def test_internal_reasoning_is_not_emitted_to_progress_updates(tmp_path):
    class StreamingProvider:
        async def complete_stream(self, messages, tools, *, effort="auto", on_progress):
            await on_progress({"kind": "reasoning", "delta": "private provider reasoning"})
            await on_progress({"kind": "answer_delta", "delta": "公开回答"})
            return Message(
                role="assistant",
                content="公开回答",
                provider_data=[{"reasoning_content": "private provider reasoning"}],
            )

        async def close(self):
            pass

    agent = build_agent(tmp_path, StreamingProvider())
    updates = []

    async def collect(update):
        updates.append(update)

    try:
        result = await agent.run("回答问题", "private_reasoning", on_progress=collect)
        assert result.answer == "公开回答"
        assert any(update["kind"] == "reasoning_status" for update in updates)
        assert all(update.get("delta") != "private provider reasoning" for update in updates)
    finally:
        await agent.close()


@pytest.mark.asyncio
async def test_value_error_exposes_actionable_model_failure(tmp_path):
    class InvalidResponseProvider:
        async def complete(self, messages, tools):
            raise ValueError("模型输出不完整（结束原因：length）")

        async def close(self):
            pass

    agent = build_agent(tmp_path, InvalidResponseProvider())
    try:
        result = await agent.run("请继续", "bad_model")
        assert result.status == "error"
        assert result.answer == "模型请求失败：模型输出不完整（结束原因：length）"
        assert result.events[-1].detail == "ValueError"
    finally:
        await agent.close()


@pytest.mark.asyncio
async def test_create_python_file_in_workspace_requires_confirmation(tmp_path):
    confirmations = []

    async def approve(name, description, arguments):
        confirmations.append((name, arguments))
        return True

    registry = ToolRegistry(approval_callback=approve)
    register_builtins(registry, tmp_path, {})
    result = await registry.execute(
        "create_text_file",
        {"path": "HelloWorld.py", "content": 'print("Hello World")'},
    )

    assert result.ok is True
    assert (tmp_path / "HelloWorld.py").read_text(encoding="utf-8") == 'print("Hello World")'
    assert confirmations == [
        ("create_text_file", {"path": "HelloWorld.py", "content": 'print("Hello World")'})
    ]


class EndlessProvider:
    async def complete(self, messages, tools):
        return Message(
            role="assistant",
            tool_calls=[
                ToolCall(
                    id=f"call_{len(messages)}",
                    name="current_time",
                    arguments="{}",
                )
            ],
        )

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_tool_limit_does_not_claim_success(tmp_path):
    agent = build_agent(tmp_path, EndlessProvider(), max_tool_calls=2)
    result = await agent.run("继续", "bounded")
    assert result.status == "limited"
    assert "上限" in result.answer
    await agent.close()


def test_context_window_keeps_tool_call_and_result_together():
    messages = [
        Message(role="user", content="old"),
        Message(role="assistant", content="old answer"),
        Message(role="user", content="new"),
        Message(role="assistant", tool_calls=[ToolCall(id="c", name="calculator", arguments="{}")]),
        Message(role="tool", tool_call_id="c", content="3"),
        Message(role="assistant", content="3"),
    ]
    latest_cost = sum(len(m.model_dump_json()) for m in messages[2:])
    kept, dropped = window(messages, latest_cost)
    assert dropped == 1
    assert kept == messages[2:]


@pytest.mark.asyncio
async def test_tool_validation_and_side_effect_gate():
    registry = ToolRegistry()

    @tool(side_effect=True)
    def change_state(value: int) -> int:
        """改变某个状态。"""
        return value

    registry.register(change_state)
    assert not (await registry.execute("change_state", '{"value":1}')).ok
    registry.allowed_effects.add("change_state")
    assert (await registry.execute("change_state", '{"value":1}')).data == 1
    assert not (await registry.execute("change_state", '{"value":1,"extra":2}')).ok
    assert not (await registry.execute("not_registered", "{}")).ok


@pytest.mark.asyncio
async def test_tool_timeout_and_rejects_code_execution():
    registry = ToolRegistry(timeout=0.01)

    @tool
    async def slow() -> str:
        """模拟耗时调用。"""
        await asyncio.sleep(0.1)
        return "finished"

    registry.register(slow)
    assert "超时" in (await registry.execute("slow", "{}")).error

    from yugan_agent.builtins import calculator

    registry.register(calculator)
    assert not (await registry.execute("calculator", '{"expression":"__import__(1)"}')).ok


@pytest.mark.asyncio
async def test_same_session_concurrent_calls_are_serialized(tmp_path):
    agent = build_agent(tmp_path)
    try:
        results = await asyncio.gather(agent.run("计算 1+1", "same"), agent.run("计算 2+2", "same"))
        assert all(result.status == "completed" for result in results)
        assert [m.role for m in agent.memory.load("same").messages].count("user") == 2
        assert agent.memory.load("same").version == 2
    finally:
        await agent.close()


@pytest.mark.asyncio
async def test_current_turn_over_budget_is_limited(tmp_path):
    agent = build_agent(tmp_path, context_chars=2048)
    try:
        result = await agent.run("X" * 3000, "too_long")
        assert result.status == "limited"
        assert "上下文" in result.answer
    finally:
        await agent.close()


@pytest.mark.asyncio
async def test_deepseek_reasoning_survives_tool_feedback_over_history_budget(tmp_path):
    class LongReasoningProvider:
        def __init__(self):
            self.calls = 0

        async def complete(self, messages, tools, *, effort="auto"):
            self.calls += 1
            if self.calls == 1:
                return Message(
                    role="assistant",
                    provider="deepseek",
                    provider_data=[{"reasoning_content": "推理" * 20_000}],
                    tool_calls=[ToolCall(id="call_1", name="echo", arguments='{"value":3}')],
                )
            assert messages[-2].provider_data[0]["reasoning_content"] == "推理" * 20_000
            assert messages[-1].role == "tool"
            return Message(role="assistant", content="完成")

        async def close(self):
            pass

    settings = Settings(
        provider="compatible",
        model="deepseek-flash",
        base_url="https://api.deepseek.com",
        workspace=tmp_path,
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
        context_chars=32_000,
    )
    registry = ToolRegistry(timeout=settings.tool_timeout)

    @tool
    async def echo(value: int) -> int:
        return value

    registry.register(echo)
    provider = LongReasoningProvider()
    agent = Agent(provider, registry, SQLiteMemory(settings.database), settings)
    try:
        result = await agent.run("计算 1+2", "deepseek_long_reasoning", effort="max")
        assert result.status == "completed"
        assert result.answer == "完成"
        assert provider.calls == 2
    finally:
        await agent.close()


@pytest.mark.asyncio
async def test_deepseek_reasoning_language_hint_does_not_change_saved_user_message(tmp_path):
    class CapturingProvider:
        async def complete(self, messages, tools, *, effort="auto"):
            self.sent = messages
            return Message(role="assistant", content="好的")

        async def close(self):
            pass

    settings = Settings(
        provider="compatible",
        model="deepseek-flash",
        base_url="https://api.deepseek.com",
        workspace=tmp_path,
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    provider = CapturingProvider()
    agent = Agent(provider, ToolRegistry(), SQLiteMemory(settings.database), settings)
    try:
        result = await agent.run("解释 1+1", "chinese_reasoning", effort="low")
        assert result.status == "completed"
        assert provider.sent[-1].content.startswith("请从思考过程的第一个词开始全程使用简体中文")
        assert provider.sent[-1].content.endswith("解释 1+1")
        assert agent.memory.load("chinese_reasoning").messages[0].content == "解释 1+1"
    finally:
        await agent.close()
