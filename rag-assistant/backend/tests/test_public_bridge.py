import asyncio
import json
import sqlite3
from contextlib import contextmanager

import pytest
from fastapi import HTTPException

from app import main


def test_public_bridge_requires_token_and_uses_only_configured_kb(monkeypatch):
    monkeypatch.setenv("RAG_PUBLIC_BRIDGE_TOKEN", "test-bridge-token")
    monkeypatch.setenv("RAG_PUBLIC_KB_IDS", "public-id")
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE knowledge_bases (id TEXT, name TEXT)")
    db.execute("INSERT INTO knowledge_bases VALUES ('public-id', '公开资料')")
    db.execute("INSERT INTO knowledge_bases VALUES ('private-id', '私有资料')")

    @contextmanager
    def fake_connect():
        yield db

    class FakeGraph:
        async def ainvoke(self, state):
            assert state["knowledge_base_ids"] == ["public-id"]
            assert state["knowledge_base_names"] == {"public-id": "公开资料"}
            return {"answer": "来自公开资料", "contexts": [{"page": 2, "filename": "不返回文件名"}]}

    monkeypatch.setattr(main, "connect", fake_connect)
    main.app.state.rag_graph = FakeGraph()
    with pytest.raises(HTTPException) as error:
        asyncio.run(main.public_answer(main.PublicQuestion(question="问题"), x_bridge_token=""))
    assert error.value.status_code == 401
    response = asyncio.run(main.public_answer(main.PublicQuestion(question="问题"), x_bridge_token="test-bridge-token"))
    assert json.loads(response.body) == {"answer": "来自公开资料", "sources": [{"page": 2}]}
    assert response.headers["Cache-Control"] == "no-store"
    db.close()
