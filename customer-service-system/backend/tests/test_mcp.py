"""MCP 工具与客户端测试。"""

import json

import pytest

from app.mcp_server import tools_chroma, tools_logs, tools_mysql
from app.mcp_server.server import mcp


def test_mcp_server_registers_three_tools():
    """FastMCP 上应注册三个查询工具。"""
    tools = mcp._tool_manager.list_tools()
    names = {t.name for t in tools}
    assert names == {
        "query_mysql_tool",
        "query_chroma_tool",
        "query_logs_tool",
    }


def test_tools_logs_returns_json():
    raw = tools_logs.query_logs(keyword="", limit=2)
    data = json.loads(raw)
    assert data["ok"] is True
    assert data["via"] == "mcp:query_logs"
    assert "runs" in data


def test_tools_chroma_returns_json():
    raw = tools_chroma.query_chroma("尺码", top_k=2)
    data = json.loads(raw)
    # 向量库可能未建，允许 ok=False，但必须是合法 JSON 结构
    assert "via" in data
    assert data["via"] == "mcp:query_chroma"
    assert "ok" in data


def test_tools_mysql_empty_question():
    raw = tools_mysql.query_mysql("")
    data = json.loads(raw)
    assert data["ok"] is False


def test_mcp_client_query_logs_via_stdio():
    """真正走 stdio 子进程调用 query_logs_tool（不依赖大模型）。

    客户端现在复用常驻会话（子进程只拉起一次），所以用同步封装 call_tool；
    不能再自行 asyncio.run（那会切到另一个事件循环，和常驻会话不匹配）。
    """
    from app.mcp_client.client import TOOL_LOGS, call_tool

    data = call_tool(TOOL_LOGS, {"keyword": "", "limit": 2})
    assert data.get("ok") is True
    assert data.get("via") == "mcp:query_logs"
