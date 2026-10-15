import json
from functools import partial

from fastapi.testclient import TestClient
from pydantic import SecretStr

from yugan_agent.api import create_app, server_chat_model_names
from yugan_agent.config import Settings
from yugan_agent.memory import SQLiteMemory
from yugan_agent.models import Message, Snapshot


def test_local_api_chat_workflow_and_auth(tmp_path):
    settings = Settings(
        provider="mock",
        model="demo",
        api_token=SecretStr("test-token"),
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    with TestClient(create_app(settings, env_path=tmp_path / ".env")) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["name"] == "yugan-agent"
        assert client.get("/").status_code == 200
        assert client.get("/static/app.js").status_code == 200
        assert client.get("/api/tools").status_code == 401
        headers = {"Authorization": "Bearer test-token"}
        assert (
            client.get("/api/tools", headers={**headers, "Origin": "https://evil.test"}).status_code
            == 403
        )
        assert client.get("/api/status", headers=headers).json()["demo"] is True
        response = client.post(
            "/api/chat",
            headers=headers,
            json={
                "prompt": "计算 2+3",
                "session_id": "abc",
                "effort": "max",
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert client.get("/api/sessions/abc", headers=headers).json()["version"] == 1
        renamed = client.patch(
            "/api/sessions/abc/title", headers=headers, json={"title": "桌面文件任务"}
        )
        assert renamed.status_code == 200
        assert (
            next(
                item
                for item in client.get("/api/sessions", headers=headers).json()
                if item["id"] == "abc"
            )["title"]
            == "桌面文件任务"
        )
        workflow = client.get("/api/workflows/demo", headers=headers).json()["workflow"]
        result = client.post("/api/workflows/run", headers=headers, json=workflow).json()
        assert result["status"] == "completed"
        assert result["state"]["checks"] == 3
        computer_workflow = {
            "name": "顺序任务",
            "start": "first",
            "max_steps": 2,
            "nodes": [
                {
                    "id": "first",
                    "kind": "agent",
                    "prompt": "步骤一",
                    "output": "one",
                    "next": "second",
                },
                {"id": "second", "kind": "agent", "prompt": "步骤二", "output": "two"},
            ],
        }
        response = client.post(
            "/api/workflows/run?session_id=wf_test",
            headers={**headers, "X-Yugan-Run-Scope": "a" * 32},
            json=computer_workflow,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        messages = client.get("/api/sessions/wf_test", headers=headers).json()["messages"]
        assert [message["content"] for message in messages if message["role"] == "user"] == [
            "步骤一",
            "步骤二",
        ]
        assert client.delete("/api/sessions/abc", headers=headers).status_code == 200


def test_remove_workspace_keeps_files_and_moves_session_assignments(tmp_path):
    settings = Settings(
        provider="mock",
        model="demo",
        workspace=tmp_path / "original",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    headers = {"Origin": "http://127.0.0.1:8020"}
    with TestClient(
        create_app(settings, env_path=tmp_path / ".env"),
        base_url="http://127.0.0.1:8020",
        client=("127.0.0.1", 50000),
    ) as client:
        original = client.get("/api/workspaces").json()["active_workspace_id"]
        second_dir = tmp_path / "second"
        second = client.post(
            "/api/workspaces",
            headers=headers,
            json={"name": "第二工作区", "path": str(second_dir)},
        )
        assert second.status_code == 200
        second_id = second.json()["active_workspace_id"]
        assert second_id != original
        assert client.put(
            "/api/sessions/remembered/workspace",
            headers=headers,
            json={"workspace_id": second_id},
        ).status_code == 200
        assert client.delete(f"/api/workspaces/{second_id}").status_code == 403

        removed = client.delete(f"/api/workspaces/{second_id}", headers=headers)
        assert removed.status_code == 200
        assert removed.json()["active_workspace_id"] == original
        assert [item["id"] for item in removed.json()["workspaces"]] == [original]
        assert second_dir.is_dir()
        saved = json.loads((tmp_path / ".yugan" / "workspaces.json").read_text(encoding="utf-8"))
        assert saved["sessions"]["remembered"] == original
        reply = client.post(
            "/api/chat",
            json={"prompt": "删除后仍可工作", "session_id": "remembered"},
        )
        assert reply.status_code == 200
        assert client.delete(f"/api/workspaces/{original}", headers=headers).status_code == 409


def test_chat_stream_emits_progress_and_final_result(tmp_path):
    settings = Settings(
        provider="mock",
        model="demo",
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    with TestClient(create_app(settings, env_path=tmp_path / ".env")) as client:
        response = client.post(
            "/api/chat/stream",
            json={"prompt": "计算 2+3", "session_id": "stream_test"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        updates = [
            json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")
        ]
        assert updates[0] == {"kind": "model_start", "step": 1}
        assert any(
            update["kind"] == "tool" and update["name"] == "calculator" for update in updates
        )
        assert updates[-1]["kind"] == "result"
        assert updates[-1]["data"]["status"] == "completed"


def test_session_does_not_expose_provider_reasoning_or_payload(tmp_path):
    settings = Settings(
        provider="mock",
        model="demo",
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    memory = SQLiteMemory(settings.database)
    snapshot = Snapshot(
        messages=[
            Message(role="user", content="问题"),
            Message(
                role="assistant",
                content="答案",
                provider="deepseek",
                provider_data=[{"reasoning_content": "分析过程"}],
            ),
        ]
    )
    memory.save("reasoning_history", snapshot)
    app = create_app(settings, env_path=tmp_path / ".env")
    with TestClient(app) as client:
        client.cookies.set("yugan_session", app.state.auth_manager.issue())
        messages = client.get("/api/sessions/reasoning_history").json()["messages"]
    assert "reasoning_content" not in messages[1]
    assert "provider_data" not in messages[1]


def test_rag_origin_can_call_agent_server_model_endpoint(tmp_path):
    settings = Settings(
        provider="mock",
        model="demo",
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    with TestClient(create_app(settings, env_path=tmp_path / ".env")) as client:
        response = client.options(
            "/api/models/server-ollama/chat/completions",
            headers={
                "Origin": "http://127.0.0.1:4173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:4173"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_server_model_list_excludes_embedding_only_models():
    assert server_chat_model_names([
        {"name": "qwen", "capabilities": ["completion", "tools"]},
        {"name": "bge", "capabilities": ["embedding"]},
        {"name": "old-bert", "details": {"family": "bert"}},
        {"name": "old-chat", "details": {"family": "llama"}},
    ]) == ["qwen", "old-chat"]


def test_request_size_limit(tmp_path):
    settings = Settings(
        provider="mock",
        model="demo",
        workspace=tmp_path / "ws",
        database=tmp_path / "db.sqlite",
        log_file=tmp_path / "events.jsonl",
    )
    with TestClient(create_app(settings, env_path=tmp_path / ".env")) as client:
        response = client.post("/api/chat", content=b"x" * 131073)
        assert response.status_code == 413


def test_existing_sessions_have_readable_task_summaries(tmp_path):
    memory = SQLiteMemory(tmp_path / "memory.db")
    memory.save(
        "old-session-id",
        Snapshot(
            messages=[
                Message(role="user", content="1"),
                Message(role="assistant", content="请描述具体任务。"),
                Message(role="user", content="在桌面创建 HelloWorld.txt\n并写入 Hello World"),
                Message(role="assistant", content="已创建文件。\n路径：workspace/HelloWorld.txt"),
            ]
        ),
    )
    memory.save("state-only", Snapshot(state={"step": 1}))
    memory.save(
        "short-follow-up",
        Snapshot(
            messages=[
                Message(role="user", content="计算 (12 + 8) * 3"),
                Message(role="assistant", content="结果是 60。"),
                Message(role="user", content="1"),
                Message(role="assistant", content="请说明下一步。"),
            ]
        ),
    )

    sessions = {session["id"]: session for session in memory.list_sessions()}
    task = sessions["old-session-id"]
    assert task["title"] == "在桌面创建 HelloWorld.txt 并写入 Hello World"
    assert task["summary"] == "最近回复：已创建文件。 路径：workspace/HelloWorld.txt"
    assert task["turns"] == 2
    assert sessions["state-only"]["title"] == "仅保存状态"
    assert sessions["state-only"]["summary"] == "暂无任务消息"
    assert sessions["short-follow-up"]["summary"] == "最近回复：请说明下一步。"


def test_legacy_session_database_can_persist_renamed_titles(tmp_path):
    import sqlite3

    database = tmp_path / "legacy-memory.db"
    snapshot = Snapshot(messages=[Message(role="user", content="原始任务名称")])
    with sqlite3.connect(database) as db:
        db.execute("""CREATE TABLE sessions (
            id TEXT PRIMARY KEY, payload TEXT NOT NULL, version INTEGER NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        db.execute(
            "INSERT INTO sessions(id, payload, version) VALUES (?, ?, ?)",
            ("legacy", snapshot.model_dump_json(), snapshot.version),
        )

    memory = SQLiteMemory(database)
    assert memory.list_sessions()[0]["title"] == "原始任务名称"
    assert memory.rename_session("legacy", "整理后的会话")
    loaded = memory.load("legacy")
    loaded.messages.append(Message(role="assistant", content="继续对话"))
    memory.save("legacy", loaded)
    assert SQLiteMemory(database).list_sessions()[0]["title"] == "整理后的会话"


def test_session_rename_endpoint_updates_the_saved_title(tmp_path):
    settings = Settings(
        provider="mock",
        model="demo",
        api_token=SecretStr("test-token"),
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    with TestClient(create_app(settings, env_path=tmp_path / ".env")) as client:
        client.app.state.agent.memory.save(
            "rename-me", Snapshot(messages=[Message(role="user", content="自动生成的原标题")])
        )
        headers = {"Authorization": "Bearer test-token"}
        response = client.patch(
            "/api/sessions/rename-me/title", headers=headers, json={"title": "我改的名字"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "我改的名字"
        assert client.get("/api/sessions", headers=headers).json()[0]["title"] == "我改的名字"


def test_approve_all_endpoint_requires_local_page_and_active_run(tmp_path):
    settings = Settings(
        provider="mock",
        model="demo",
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
    )
    app = create_app(settings, env_path=tmp_path / ".env")
    origin = "http://127.0.0.1:8020"
    scope = "c" * 32
    with TestClient(app, base_url=origin, client=("127.0.0.1", 50000)) as client:
        broker = app.state.approval_broker
        client.portal.call(broker.begin, scope)
        future = client.portal.start_task_soon(
            partial(broker.request, "type_text", "输入文字", {}, scope=scope)
        )
        assert len(client.get(f"/api/approvals/pending?scope={scope}").json()["pending"]) == 1
        url = f"/api/approval-scopes/{scope}/approve-all"
        assert client.post(url).status_code == 403
        assert client.post(url, headers={"Origin": origin}).status_code == 200
        assert future.result(timeout=2) is True
        client.portal.call(broker.end, scope)
        assert client.post(url, headers={"Origin": origin}).status_code == 404
