import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from app import main
from app.model_settings import (
    AgentApiProfile,
    AnswerModelSettings,
    active_agent_api_profile_id,
    get_agent_api_profile,
    list_agent_api_profiles,
    load_settings,
    save_settings,
)
from app.rag import graph
from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage

PROFILE_ID = "a" * 32
SECRET = "test-secret"


def profile(protocol="chat_completions", endpoint="https://api.example.test/v1"):
    return AgentApiProfile(PROFILE_ID, "Agent 已存模型", endpoint, "test-model", SECRET, protocol)


class AnswerModelSettingsTests(unittest.TestCase):
    def test_status_reuses_one_ollama_client_across_page_loads(self):
        class FakeStatusClient:
            def __init__(self, **_kwargs):
                self.calls = 0

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return None

            async def get(self, _url):
                self.calls += 1
                return httpx.Response(
                    200,
                    json={"models": [
                        {"name": "qwen3.5:9b"}, {"name": "bge-m3:latest"},
                    ]},
                    request=httpx.Request("GET", "http://127.0.0.1:11434/api/tags"),
                )

        clients = []

        def make_client(**kwargs):
            client = FakeStatusClient(**kwargs)
            clients.append(client)
            return client

        with (
            patch.object(main, "initialize_database"),
            patch.object(main, "load_settings", return_value=AnswerModelSettings()),
            patch.object(main.httpx, "AsyncClient", side_effect=make_client),
            TestClient(main.app) as client,
        ):
            for _ in range(2):
                response = client.get("/api/status")
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["embedding_model_ready"])
            self.assertEqual(len(clients), 1)
            self.assertEqual(clients[0].calls, 2)

    def test_agent_profiles_are_reused_without_exposing_or_copying_keys(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            agent_path = root / "model_profiles.json"
            agent_path.write_text(json.dumps({
                "version": 1, "active_id": "b" * 32,
                "profiles": [
                    {"id": PROFILE_ID, "name": "Agent 已存模型", "endpoint": "https://api.example.test/v1", "model": "test-model", "api_key": SECRET},
                    {"id": "b" * 32, "name": "本地", "endpoint": "http://127.0.0.1:11434/v1", "model": "qwen3.5:9b", "api_key": "ollama"},
                ],
            }), encoding="utf-8")
            choices = list_agent_api_profiles(agent_path)
            self.assertEqual(len(choices), 1)
            self.assertEqual(active_agent_api_profile_id(agent_path), "")
            self.assertEqual(get_agent_api_profile(PROFILE_ID, agent_path).model, "test-model")
            self.assertNotIn(SECRET, str(choices[0].public()))

            rag_path = root / "answer_model.json"
            save_settings(AnswerModelSettings(mode="api", agent_profile_id=PROFILE_ID), rag_path)
            self.assertEqual(load_settings(rag_path).agent_profile_id, PROFILE_ID)
            self.assertNotIn(SECRET, rag_path.read_text(encoding="utf-8"))
            agent_data = json.loads(agent_path.read_text(encoding="utf-8"))
            agent_data["active_id"] = PROFILE_ID
            agent_path.write_text(json.dumps(agent_data), encoding="utf-8")
            self.assertEqual(active_agent_api_profile_id(agent_path), PROFILE_ID)
            self.assertEqual(get_agent_api_profile(PROFILE_ID, agent_path).id, PROFILE_ID)

    def test_legacy_api_setting_matches_existing_agent_profile(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            agent_path = root / "models.json"
            agent_path.write_text(json.dumps({"version": 1, "profiles": [{
                "id": PROFILE_ID, "name": "Agent 已存模型",
                "endpoint": "https://api.example.test/v1", "model": "test-model", "api_key": SECRET,
            }]}), encoding="utf-8")
            rag_path = root / "rag.json"
            rag_path.write_text(json.dumps({
                "version": 1, "mode": "api", "local_model": "qwen3.5:9b",
                "api_base_url": "https://api.example.test/v1", "api_model": "test-model",
                "api_key": "old-rag-key",
            }), encoding="utf-8")
            migrated = load_settings(rag_path, agent_path)
            self.assertEqual(migrated.agent_profile_id, PROFILE_ID)
            save_settings(migrated, rag_path)
            self.assertNotIn("old-rag-key", rag_path.read_text(encoding="utf-8"))

    def test_model_endpoint_rejects_foreign_origin(self):
        initial = AnswerModelSettings()
        chosen = profile()
        with (
            patch.object(main, "initialize_database"),
            patch.object(main, "load_settings", return_value=initial),
            patch.object(main, "save_settings"),
            patch.object(main, "list_agent_api_profiles", return_value=[chosen]),
            patch.object(main, "get_agent_api_profile", return_value=chosen),
            patch.object(main, "active_agent_api_profile_id", return_value=PROFILE_ID),
            TestClient(
                main.app,
                base_url="http://127.0.0.1:8000",
                client=("127.0.0.1", 50000),
            ) as client,
        ):
            body = {"mode": "api", "local_model": "qwen3.5:9b", "agent_profile_id": PROFILE_ID}
            self.assertEqual(client.put("/api/model-settings", json=body).status_code, 403)
            response = client.put(
                "/api/model-settings",
                json=body,
                headers={"Origin": "http://127.0.0.1:4173"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["selected_agent_model"]["name"], chosen.name)
            self.assertNotIn(SECRET, response.text)


class AnswerModelGraphTests(unittest.IsolatedAsyncioTestCase):
    async def test_api_stream_dispatches_tokens(self):
        settings = AnswerModelSettings(mode="api", agent_profile_id=PROFILE_ID)

        async def fake_tokens(_profile, _messages):
            yield "第一段"
            yield "第二段"

        context = {
            "content": "已知资料", "filename": "manual.txt", "page": None,
            "knowledge_base_name": "测试库",
        }
        with (
            patch.object(graph, "retrieve_contexts", return_value=[context]),
            patch.object(graph, "get_agent_api_profile", return_value=profile()),
            patch.object(graph, "api_answer_tokens", fake_tokens),
        ):
            events = [
                event async for event in graph.create_rag_graph(settings).astream_events(
                    {
                        "question": "问题", "knowledge_base_ids": ["kb"],
                        "knowledge_base_names": {"kb": "测试库"}, "history": [],
                    },
                    version="v2",
                )
            ]
        tokens = [
            event["data"]["content"] for event in events
            if event.get("event") == "on_custom_event"
            and event.get("name") == "rag_answer_token"
        ]
        self.assertEqual(tokens, ["第一段", "第二段"])

    async def test_api_request_uses_agent_profile_endpoint_and_key(self):
        requests = []

        def respond(request):
            requests.append(request)
            return httpx.Response(200, json={"choices": [{"message": {"content": "已回答"}}]})

        original_client = httpx.AsyncClient
        with patch.object(
            graph.httpx,
            "AsyncClient",
            side_effect=lambda **kwargs: original_client(
                transport=httpx.MockTransport(respond), **kwargs
            ),
        ):
            answer = await graph.api_complete(profile(), [HumanMessage(content="你好")], 128)
        self.assertEqual(answer, "已回答")
        self.assertEqual(requests[0].url.path, "/v1/chat/completions")
        self.assertEqual(requests[0].headers["authorization"], f"Bearer {SECRET}")
        self.assertEqual(json.loads(requests[0].content)["messages"][0]["role"], "user")

    async def test_api_stream_parses_chat_completion_chunks(self):
        payload = (
            'data: {"choices":[{"delta":{"content":"第一段"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"第二段"}}]}\n\n'
            'data: [DONE]\n\n'
        )
        original_client = httpx.AsyncClient
        with patch.object(
            graph.httpx,
            "AsyncClient",
            side_effect=lambda **kwargs: original_client(
                transport=httpx.MockTransport(
                    lambda _request: httpx.Response(200, text=payload)
                ),
                **kwargs,
            ),
        ):
            tokens = [token async for token in graph.api_answer_tokens(
                profile(), [HumanMessage(content="你好")],
            )]
        self.assertEqual(tokens, ["第一段", "第二段"])

    async def test_agent_openai_and_anthropic_profiles_can_answer(self):
        def respond(request):
            if request.url.path.endswith("/responses"):
                return httpx.Response(200, json={"output": [{"content": [{"type": "output_text", "text": "OpenAI 回答"}]}]})
            return httpx.Response(200, json={"content": [{"type": "text", "text": "Claude 回答"}]})

        original_client = httpx.AsyncClient
        with patch.object(
            graph.httpx, "AsyncClient",
            side_effect=lambda **kwargs: original_client(transport=httpx.MockTransport(respond), **kwargs),
        ):
            openai_answer = await graph.api_complete(
                profile("responses", "https://api.openai.com/v1"),
                [HumanMessage(content="你好")], 128,
            )
            claude_answer = await graph.api_complete(
                profile("anthropic", "https://api.anthropic.com"),
                [HumanMessage(content="你好")], 128,
            )
        self.assertEqual(openai_answer, "OpenAI 回答")
        self.assertEqual(claude_answer, "Claude 回答")
