from fastapi.testclient import TestClient

from yugan_agent.api import create_app
from yugan_agent.config import Settings


def test_builtin_toggle_and_custom_http_tool_crud_persist_without_exposing_key(tmp_path):
    origin = "http://127.0.0.1:8020"
    headers = {"Origin": origin}
    env_path = tmp_path / ".env"

    def app():
        return create_app(
            Settings(
                provider="mock",
                workspace=tmp_path / "workspace",
                database=tmp_path / "memory.db",
                log_file=tmp_path / "events.jsonl",
            ),
            env_path=env_path,
        )

    with TestClient(app(), base_url=origin, client=("127.0.0.1", 50000)) as client:
        management = client.get("/api/tools/management").json()
        assert any(
            item["name"] == "calculator" and item["enabled"] for item in management["builtins"]
        )

        disabled = client.patch(
            "/api/tools/builtins/calculator", headers=headers, json={"enabled": False}
        )
        assert disabled.status_code == 200
        assert "calculator" not in {item["name"] for item in client.get("/api/tools").json()}

        definition = {
            "name": "weather_query",
            "description": "查询指定城市的天气",
            "endpoint": "https://api.example.test/weather",
            "method": "GET",
            "api_key": "test-secret-tool-key",
            "parameters": [
                {"name": "city", "kind": "string", "description": "城市名称"},
                {"name": "unit", "kind": "string", "required": False},
            ],
        }
        added = client.post("/api/tools/custom", headers=headers, json=definition)
        assert added.status_code == 200, added.text
        assert added.json()["has_api_key"] is True
        assert "test-secret-tool-key" not in added.text
        assert "weather_query" in {item["name"] for item in client.get("/api/tools").json()}

    tool_file = tmp_path / ".yugan" / "tools.json"
    assert "test-secret-tool-key" in tool_file.read_text(encoding="utf-8")

    with TestClient(app(), base_url=origin, client=("127.0.0.1", 50000)) as client:
        management = client.get("/api/tools/management").json()
        calculator = next(item for item in management["builtins"] if item["name"] == "calculator")
        assert calculator["enabled"] is False
        weather = next(
            item for item in management["custom_tools"] if item["name"] == "weather_query"
        )
        assert weather["has_api_key"] is True
        assert "test-secret-tool-key" not in client.get("/api/tools/management").text

        removed = client.delete("/api/tools/custom/weather_query", headers=headers)
        assert removed.status_code == 200
        enabled = client.patch(
            "/api/tools/builtins/calculator", headers=headers, json={"enabled": True}
        )
        assert enabled.status_code == 200
        assert "calculator" in {item["name"] for item in client.get("/api/tools").json()}


def test_custom_tool_rejects_arbitrary_http_and_duplicate_parameter_names():
    from pydantic import ValidationError

    from yugan_agent.custom_tools import CustomToolDefinition

    base = {
        "name": "sample_tool",
        "description": "Sample API",
        "endpoint": "http://192.168.1.8/private",
    }
    try:
        CustomToolDefinition.model_validate(base)
    except ValidationError:
        pass
    else:
        raise AssertionError("外部 HTTP 接口应被拒绝")

    try:
        CustomToolDefinition.model_validate(
            base
            | {
                "endpoint": "https://api.example.test/tool",
                "parameters": [
                    {"name": "value"},
                    {"name": "value", "kind": "integer"},
                ],
            }
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("重复参数名应被拒绝")
