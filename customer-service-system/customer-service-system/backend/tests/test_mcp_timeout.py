"""MCP 超时取消、清理及后续调用恢复，不启动实际子进程。"""
import asyncio
import threading
from types import SimpleNamespace

import pytest

from app.common.exceptions import BusinessException
from app.mcp_client import client


def test_timeout_cancels_call_and_cleans_up_before_next_request(monkeypatch):
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    events = []
    count = 0

    class FakeSession:
        async def call_tool(self, name, arguments):
            nonlocal count
            count += 1
            if count == 1:
                try:
                    await asyncio.Event().wait()
                finally:
                    events.append("cancelled")
            events.append("next_call")
            return SimpleNamespace(structuredContent={"ok": True}, isError=False)

    async def get_session():
        return FakeSession()

    async def drop_session():
        await asyncio.sleep(0.01)
        events.append("cleaned")

    monkeypatch.setattr(client, "_ensure_loop", lambda: loop)
    monkeypatch.setattr(client, "_get_session", get_session)
    monkeypatch.setattr(client, "_drop_session", drop_session)
    monkeypatch.setattr(client, "CALL_TIMEOUT_SECONDS", 0.02)
    try:
        with pytest.raises(BusinessException, match="超时"):
            client.call_tool("slow")
        assert events == ["cancelled", "cleaned"]
        assert client.call_tool("next") == {"ok": True}
        assert events == ["cancelled", "cleaned", "next_call"]
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=2)
        loop.close()
