from yugan_agent.models import Message, ToolCall
from yugan_agent.providers import anthropic_messages, chat_messages, responses_input


def test_openai_tool_exchange_shape():
    messages = [
        Message(role="user", content="hello"),
        Message(role="assistant", tool_calls=[ToolCall(id="call_1", name="tool1", arguments="{}")]),
        Message(role="tool", tool_call_id="call_1", content='{"ok":true}'),
    ]
    chat = chat_messages(messages)
    assert chat[1]["tool_calls"][0]["id"] == "call_1"
    assert chat[2]["tool_call_id"] == "call_1"
    responses = responses_input(messages)
    assert responses[1]["type"] == "function_call"
    assert responses[2]["type"] == "function_call_output"


def test_anthropic_tool_result_immediately_follows_assistant():
    messages = [
        Message(role="system", content="中文回答"),
        Message(role="user", content="天气"),
        Message(
            role="assistant",
            tool_calls=[
                ToolCall(
                    id="toolu_1",
                    name="weather",
                    arguments='{"city":"桂林"}',
                )
            ],
        ),
        Message(role="tool", tool_call_id="toolu_1", content="27°C"),
    ]
    system, converted = anthropic_messages(messages)
    assert system == "中文回答"
    assert [item["role"] for item in converted] == ["user", "assistant", "user"]
    assert converted[2]["content"][0]["tool_use_id"] == "toolu_1"


def test_switching_compatible_provider_drops_old_reasoning_metadata():
    messages = [
        Message(
            role="assistant",
            tool_calls=[ToolCall(id="call_1", name="tool1", arguments="{}")],
            provider="deepseek",
            provider_data=[{"reasoning_content": "deepseek-only"}],
        )
    ]
    assert chat_messages(messages, provider="deepseek")[0]["reasoning_content"] == "deepseek-only"
    switched = chat_messages(messages, provider="kimi")[0]
    assert switched["content"] is None
    assert "reasoning_content" not in switched
