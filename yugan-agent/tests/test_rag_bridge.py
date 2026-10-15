import asyncio

import httpx
from fastapi.testclient import TestClient

from yugan_agent import api, rag_bridge
from yugan_agent.agent import Agent
from yugan_agent.config import Settings
from yugan_agent.memory import SQLiteMemory
from yugan_agent.models import Message
from yugan_agent.tools import ToolRegistry


def test_selected_rag_project_retrieves_only_its_knowledge_bases(monkeypatch):
    async def fake_catalog():
        return {
            "projects": [
                {"id": "project-1", "name": "机械臂", "knowledge_base_ids": ["kb-1"]},
                {"id": "project-2", "name": "其他", "knowledge_base_ids": ["kb-2"]},
            ],
            "knowledge_bases": [
                {"id": "kb-1", "name": "机械臂资料"},
                {"id": "kb-2", "name": "其他资料"},
            ],
        }

    sent = []

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, path, json):
            sent.append((path, json))
            return httpx.Response(
                200,
                json={"matches": [{
                    "filename": "手册.pdf", "page": 3, "knowledge_base_name": "机械臂资料",
                    "content": "机械臂参数", "score": 0.9,
                }]},
                request=httpx.Request("POST", "http://127.0.0.1:8000" + path),
            )

    monkeypatch.setattr(rag_bridge, "catalog", fake_catalog)
    monkeypatch.setattr(rag_bridge.httpx, "AsyncClient", FakeClient)
    result = asyncio.run(rag_bridge.retrieve(
        "参数是什么", rag_bridge.RagSelection(mode="project", project_id="project-1")
    ))
    assert sent[0][1]["knowledge_base_ids"] == ["kb-1"]
    assert "手册.pdf，第 3 页" in result["context"]
    assert "机械臂参数" in result["context"]
    assert "其他资料" not in result["context"]


def test_agent_receives_rag_evidence_without_storing_snippets(tmp_path):
    class CaptureProvider:
        def __init__(self):
            self.messages = []

        async def complete(self, messages, tools, *, effort="auto"):
            self.messages = messages
            return Message(role="assistant", content="根据 [资料 1]，参数是 10。")

        async def close(self):
            pass

    settings = Settings(
        provider="mock", model="demo", workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db", log_file=tmp_path / "events.jsonl",
    )
    provider = CaptureProvider()
    agent = Agent(provider, ToolRegistry(), SQLiteMemory(settings.database), settings)
    selection = {"mode": "custom", "project_id": "", "knowledge_base_ids": ["kb-1"]}

    async def run():
        try:
            return await agent.run(
                "参数是什么", "rag-session", rag_context="[资料 1] 参数是 10。",
                rag_selection=selection,
            )
        finally:
            await agent.close()

    result = asyncio.run(run())
    assert result.status == "completed"
    assert any("[资料 1] 参数是 10。" in item.content for item in provider.messages)
    snapshot = agent.memory.load("rag-session")
    assert snapshot.state["rag_selection"] == selection
    assert all("[资料 1] 参数是 10。" not in item.content for item in snapshot.messages)


def test_chat_stream_uses_saved_rag_selection(monkeypatch, tmp_path):
    async def fake_retrieve(question, selection):
        assert question == "参数是什么"
        assert selection.knowledge_base_ids == ["kb-1"]
        return {
            "context": "[资料 1] 参数是 10。", "matches": [{"content": "参数是 10。"}],
            "knowledge_base_names": ["机械臂资料"],
        }

    monkeypatch.setattr(api, "rag_retrieve", fake_retrieve)
    settings = Settings(
        provider="mock", model="demo", workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db", log_file=tmp_path / "events.jsonl",
    )
    with TestClient(api.create_app(settings, env_path=tmp_path / ".env")) as client:
        response = client.post("/api/chat/stream", json={
            "prompt": "参数是什么", "session_id": "rag-session",
            "rag": {"mode": "custom", "knowledge_base_ids": ["kb-1"]},
        })
        assert response.status_code == 200
        assert '"kind": "rag_retrieving"' in response.text
        assert '"kind": "rag_result"' in response.text
        state = client.get("/api/sessions/rag-session").json()["state"]
        assert state["rag_selection"]["knowledge_base_ids"] == ["kb-1"]
