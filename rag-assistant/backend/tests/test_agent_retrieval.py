import asyncio
import json
import sqlite3
from contextlib import contextmanager

from fastapi import HTTPException
from starlette.requests import Request

from app import main
from app.schemas import AgentRetrieveRequest


def test_agent_retrieval_only_reads_selected_knowledge_base(monkeypatch):
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE knowledge_bases (id TEXT, name TEXT)")
    db.executemany("INSERT INTO knowledge_bases VALUES (?, ?)", [
        ("selected", "指定资料"), ("other", "其他资料"),
    ])

    @contextmanager
    def fake_connect():
        yield db

    calls = []

    def fake_retrieve(query, ids, names):
        calls.append((query, ids, names))
        return [{
            "content": "文档内容", "filename": "资料.md", "page": 2,
            "knowledge_base_id": "selected", "knowledge_base_name": "指定资料", "score": 0.8,
        }]

    monkeypatch.setattr(main, "connect", fake_connect)
    monkeypatch.setattr(main, "retrieve_contexts", fake_retrieve)
    request = Request({"type": "http", "client": ("127.0.0.1", 12345)})
    response = asyncio.run(main.retrieve_for_agent(
        AgentRetrieveRequest(query="问题", knowledge_base_ids=["selected"]), request
    ))
    assert calls == [("问题", ["selected"], {"selected": "指定资料"})]
    assert json.loads(response.body)["matches"][0]["filename"] == "资料.md"
    assert response.headers["Cache-Control"] == "no-store"
    db.close()


def test_agent_retrieval_rejects_nonlocal_client():
    request = Request({"type": "http", "client": ("198.51.100.7", 12345)})
    try:
        asyncio.run(main.retrieve_for_agent(
            AgentRetrieveRequest(query="问题", knowledge_base_ids=["selected"]), request
        ))
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("远程客户端不应读取本机知识库")
