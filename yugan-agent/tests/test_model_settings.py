import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from yugan_agent.api import create_app
from yugan_agent.config import Settings
from yugan_agent.models import Message
from yugan_agent.providers import OpenAIProvider
from yugan_agent.settings_store import new_profile, resolve_target


def test_provider_is_inferred_from_base_url_not_key():
    deepseek = resolve_target("", "")
    assert (deepseek.vendor, deepseek.provider, deepseek.model, deepseek.thinking) == (
        "DeepSeek",
        "compatible",
        "deepseek-flash",
        "disabled",
    )
    assert resolve_target("https://api.openai.com/v1", "gpt-4.1-mini").provider == "openai"
    assert resolve_target("https://api.anthropic.com", "claude-haiku-4-5").provider == "anthropic"
    assert resolve_target("https://dashscope.aliyuncs.com", "").model == "qwen-plus"
    assert resolve_target("https://open.bigmodel.cn/api/paas/v4", "glm-4").vendor == "智谱 GLM"
    kimi = resolve_target("https://api.moonshot.cn/v1", "kimi-k3")
    assert (kimi.vendor, kimi.provider, kimi.model) == ("Kimi", "compatible", "kimi-k3")
    assert new_profile("Kimi K3", "test-key", kimi).public()["effort_supported"] is True
    assert (
        new_profile(
            "Kimi K2.6", "test-key", resolve_target("https://api.moonshot.cn/v1", "kimi-k2.6")
        ).public()["effort_supported"]
        is False
    )
    local = resolve_target("http://127.0.0.1:11434/v1", "qwen3.5:9b")
    assert (local.vendor, local.provider, local.base_url) == (
        "Ollama", "compatible", "http://127.0.0.1:11434/v1"
    )
    assert new_profile("本地", "", local).public()["mode"] == "local"
    with pytest.raises(ValueError):
        resolve_target("http://example.com/v1", "model")
    with pytest.raises(ValueError):
        resolve_target("https://api.openai.com/v1", "")
    with pytest.raises(ValueError):
        resolve_target("https://api.moonshot.cn/v1/chat/completions", "kimi-k3")


def test_browser_saves_key_locally_and_activates_provider(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("YUGAN_WORKSPACE=./workspace\nYUGAN_PROVIDER=mock\n", encoding="utf-8")
    settings = Settings(
        provider="compatible",
        model="deepseek-flash",
        api_key=SecretStr(""),
        base_url="https://api.deepseek.com",
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    origin = "http://127.0.0.1:8020"
    with TestClient(
        create_app(settings, env_path=env_path),
        base_url=origin,
        client=("127.0.0.1", 50000),
    ) as client:
        assert client.get("/api/status").json()["configured"] is False
        assert (
            client.post("/api/chat", json={"prompt": "你好", "session_id": "a"}).status_code == 503
        )
        body = {"api_key": "test-secret-1234", "endpoint": "", "model": ""}
        assert client.post("/api/settings/model", json=body).status_code == 403
        assert (
            client.post(
                "/api/settings/model", json=body, headers={"Origin": "https://evil.test"}
            ).status_code
            == 403
        )
        response = client.post("/api/settings/model", json=body, headers={"Origin": origin})
        assert response.status_code == 200
        assert response.json()["vendor"] == "DeepSeek"
        assert "test-secret-1234" not in response.text
        assert client.get("/api/status").json()["configured"] is True
        assert client.get("/api/tools").status_code == 200
        switched = client.post(
            "/api/settings/model",
            json={
                "api_key": "another-test-key-5678",
                "endpoint": "https://api.openai.com/v1",
                "model": "gpt-4.1-mini",
            },
            headers={"Origin": origin},
        )
        assert switched.status_code == 200
        assert client.get("/api/status").json()["vendor"] == "OpenAI"
        assert "another-test-key-5678" not in client.get("/api/status").text
    content = env_path.read_text(encoding="utf-8")
    assert "YUGAN_WORKSPACE=./workspace" in content
    assert 'YUGAN_API_KEY="another-test-key-5678"' in content
    assert content.count("YUGAN_PROVIDER=") == 1


def test_local_ollama_profile_needs_no_api_key(tmp_path):
    origin = "http://127.0.0.1:8020"
    settings = Settings(
        provider="mock",
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    with TestClient(
        create_app(settings, env_path=tmp_path / ".env"),
        base_url=origin,
        client=("127.0.0.1", 50000),
    ) as client:
        response = client.post(
            "/api/settings/models",
            headers={"Origin": origin},
            json={
                "name": "本地测试",
                "endpoint": "http://127.0.0.1:11434/v1",
                "model": "qwen3.5:9b",
                "api_key": "",
            },
        )
        assert response.status_code == 200
        assert response.json()["mode"] == "local"
        assert client.get("/api/status").json()["vendor"] == "Ollama"
        assert client.get("/api/settings/models").json()["models"][0]["mode"] == "local"


def test_local_model_picker_only_lists_tool_capable_models(tmp_path, monkeypatch):
    original_client = httpx.AsyncClient

    def respond(request):
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [
                {"name": "qwen3.5:9b"}, {"name": "bge-m3:latest"},
            ]})
        name = request.read().decode("utf-8")
        return httpx.Response(200, json={
            "capabilities": ["completion", "tools"] if "qwen3.5:9b" in name else ["embedding"]
        })

    class MockOllamaClient(original_client):
        def __init__(self, **kwargs):
            super().__init__(transport=httpx.MockTransport(respond), **kwargs)

    monkeypatch.setattr("yugan_agent.api.httpx.AsyncClient", MockOllamaClient)
    settings = Settings(
        provider="mock", workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db", log_file=tmp_path / "events.jsonl",
    )
    with TestClient(
        create_app(settings, env_path=tmp_path / ".env"),
        base_url="http://127.0.0.1:8020", client=("127.0.0.1", 50000),
    ) as client:
        response = client.get("/api/settings/local-models")
        assert response.status_code == 200
        assert response.json() == {"connected": True, "models": ["qwen3.5:9b"]}


@pytest.mark.asyncio
async def test_local_ollama_request_bypasses_environment_proxy(monkeypatch):
    requests = []
    clients = []
    original_client = httpx.AsyncClient

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={
            "id": "chatcmpl-test", "object": "chat.completion", "created": 1,
            "model": "qwen3.5:9b", "choices": [{
                "index": 0, "finish_reason": "stop",
                "message": {"role": "assistant", "content": "本地回答"},
            }],
        })

    class MockLocalClient(original_client):
        def __init__(self, **kwargs):
            clients.append(kwargs)
            super().__init__(transport=httpx.MockTransport(respond), **kwargs)

    monkeypatch.setattr("yugan_agent.providers.httpx.AsyncClient", MockLocalClient)
    provider = OpenAIProvider(Settings(
        provider="compatible", model="qwen3.5:9b",
        base_url="http://127.0.0.1:11434/v1", api_key=SecretStr("ollama"),
    ))
    try:
        result = await provider.complete([Message(role="user", content="你好")], [])
    finally:
        await provider.close()
    assert result.content == "本地回答"
    assert clients[0]["trust_env"] is False
    assert requests[0].url.path == "/v1/chat/completions"


def test_remote_client_cannot_save_model_key(tmp_path):
    env_path = tmp_path / ".env"
    with TestClient(
        create_app(
            Settings(
                provider="mock",
                workspace=tmp_path / "workspace",
                database=tmp_path / "memory.db",
                log_file=tmp_path / "events.jsonl",
            ),
            env_path=env_path,
        ),
        base_url="http://127.0.0.1:8020",
        client=("192.0.2.10", 50000),
    ) as client:
        response = client.post(
            "/api/settings/model",
            json={"api_key": "test-secret-1234"},
            headers={"Origin": "http://127.0.0.1:8020"},
        )
        assert response.status_code == 403
    assert not env_path.exists()


def test_saved_models_switch_edit_and_survive_restart(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    origin = "http://127.0.0.1:8020"
    monkeypatch.setattr(
        "yugan_agent.providers.AsyncOpenAI",
        lambda **kwargs: pytest.fail("仅切换模型不应创建 SDK 网络客户端"),
    )

    def app():
        return create_app(
            Settings(
                provider="mock",
                api_key=SecretStr(""),
                workspace=tmp_path / "workspace",
                database=tmp_path / "memory.db",
                log_file=tmp_path / "events.jsonl",
            ),
            env_path=env_path,
        )

    with TestClient(app(), base_url=origin, client=("127.0.0.1", 50000)) as client:
        headers = {"Origin": origin}
        first = client.post(
            "/api/settings/models",
            headers=headers,
            json={"name": "日常", "api_key": "first-test-key", "model": "deepseek-flash"},
        )
        assert first.status_code == 200
        first_id = first.json()["id"]
        second = client.post(
            "/api/settings/models",
            headers=headers,
            json={
                "name": "编程",
                "api_key": "second-test-key",
                "endpoint": "https://api.openai.com/v1",
                "model": "gpt-5.2-codex",
            },
        )
        assert second.status_code == 200
        second_id = second.json()["id"]
        listing = client.get("/api/settings/models").json()
        assert len(listing["models"]) == 2
        assert listing["active_model_id"] == second_id
        assert listing["models"][0]["effort_supported"] is True
        assert "first-test-key" not in str(listing)
        assert "second-test-key" not in str(listing)

        switched = client.post(f"/api/settings/models/{first_id}/activate", headers=headers)
        assert switched.status_code == 200
        assert client.get("/api/status").json()["model"] == "deepseek-flash"
        assert 'YUGAN_API_KEY="first-test-key"' in env_path.read_text(encoding="utf-8")
        edited = client.put(
            f"/api/settings/models/{first_id}",
            headers=headers,
            json={"name": "常用 DeepSeek", "api_key": "", "model": "deepseek-flash"},
        )
        assert edited.status_code == 200
        assert edited.json()["id"] == first_id
        assert 'YUGAN_API_KEY="first-test-key"' in env_path.read_text(encoding="utf-8")

    with TestClient(app(), base_url=origin, client=("127.0.0.1", 50000)) as client:
        listing = client.get("/api/settings/models").json()
        assert listing["active_model_id"] == first_id
        assert [item["name"] for item in listing["models"]] == ["常用 DeepSeek", "编程"]
        removed_second = client.delete(f"/api/settings/models/{second_id}", headers=headers)
        assert removed_second.status_code == 200
        removed_first = client.delete(f"/api/settings/models/{first_id}", headers=headers)
        assert removed_first.status_code == 200
        assert client.get("/api/settings/models").json()["models"] == []
        assert client.get("/api/status").json()["configured"] is False
        assert 'YUGAN_API_KEY=""' in env_path.read_text(encoding="utf-8")


def test_switch_model_while_chat_is_running_keeps_old_run_alive(tmp_path, monkeypatch):
    origin = "http://127.0.0.1:8020"
    started = threading.Event()
    continue_run = threading.Event()
    agents = []

    class FakeAgent:
        def __init__(self, settings):
            self.model = settings.model
            self.closed = threading.Event()

        async def run(self, prompt, session_id, *, effort="auto"):
            if self.model == "deepseek-flash":
                started.set()
                await asyncio.to_thread(continue_run.wait)
            return {"status": "completed", "answer": self.model}

        async def close(self):
            self.closed.set()

    def fake_create_agent(settings, *, approval_callback=None):
        agent = FakeAgent(settings)
        agents.append(agent)
        return agent

    monkeypatch.setattr("yugan_agent.api.create_agent", fake_create_agent)
    app = create_app(
        Settings(
            provider="compatible",
            api_key=SecretStr(""),
            workspace=tmp_path / "workspace",
            database=tmp_path / "memory.db",
            log_file=tmp_path / "events.jsonl",
        ),
        env_path=tmp_path / ".env",
    )
    with TestClient(app, base_url=origin, client=("127.0.0.1", 50000)) as client:
        headers = {"Origin": origin}
        first = client.post(
            "/api/settings/models",
            headers=headers,
            json={"api_key": "first-test-key", "model": "deepseek-flash"},
        ).json()
        second = client.post(
            "/api/settings/models",
            headers=headers,
            json={
                "api_key": "second-test-key",
                "endpoint": "https://api.moonshot.cn/v1",
                "model": "kimi-k3",
            },
        ).json()
        client.post(f"/api/settings/models/{first['id']}/activate", headers=headers)
        old_agent = agents[-1]
        with ThreadPoolExecutor(max_workers=1) as pool:
            try:
                running = pool.submit(
                    client.post,
                    "/api/chat",
                    json={"prompt": "计算", "session_id": "switch-test"},
                )
                assert started.wait(5)
                switched = client.post(
                    f"/api/settings/models/{second['id']}/activate", headers=headers
                )
                assert switched.status_code == 200
                assert client.get("/api/status").json()["model"] == "kimi-k3"
                assert not old_agent.closed.is_set()
            finally:
                continue_run.set()
            assert running.result(timeout=5).json()["answer"] == "deepseek-flash"
        assert old_agent.closed.wait(5)
        assert (
            client.post("/api/chat", json={"prompt": "计算", "session_id": "switch-test"}).json()[
                "answer"
            ]
            == "kimi-k3"
        )
