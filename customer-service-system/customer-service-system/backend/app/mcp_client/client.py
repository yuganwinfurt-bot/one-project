"""主程序侧的 MCP 客户端：通过 stdio 子进程调用三个查询工具。

调用链（教学重点）：
    LangGraph 节点 → mcp_client.call_tool(...) → stdio 子进程 FastMCP Server → 工具函数

不要在节点里直接 import tools_mysql / tools_chroma（那会绕过 MCP）。
"""

import asyncio
import atexit
import json
import logging
import os
import sys
import threading
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.common.exceptions import BusinessException

logger = logging.getLogger(__name__)

# backend 根目录（保证子进程能 import app.*）
BACKEND_ROOT = Path(__file__).resolve().parents[2]

# 工具名必须与 mcp_server/server.py 里注册的一致
TOOL_MYSQL = "query_mysql_tool"
TOOL_MYSQL_SQL = "execute_mysql_select_tool"
TOOL_CHROMA = "query_chroma_tool"
TOOL_LOGS = "query_logs_tool"


def _server_params() -> StdioServerParameters:
    """构造 stdio 子进程参数：用当前解释器跑 MCP Server 模块。"""
    env = os.environ.copy()
    # 确保子进程能找到 backend 包
    pythonpath = env.get("PYTHONPATH", "")
    root = str(BACKEND_ROOT)
    if root not in pythonpath.split(os.pathsep):
        env["PYTHONPATH"] = root + (os.pathsep + pythonpath if pythonpath else "")

    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server.server"],
        env=env,
        cwd=root,
    )


def _parse_tool_result(result: Any) -> dict[str, Any]:
    """把 MCP CallToolResult 解成业务 dict。

    FastMCP 默认会把返回值包一层 {"result": ...}，若 result 仍是 JSON 字符串再 loads 一次。
    """
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict) and "result" in structured:
        inner = structured["result"]
        if isinstance(inner, dict):
            data = inner
        elif isinstance(inner, str):
            data = json.loads(inner)
        else:
            raise BusinessException(message="MCP 工具 structuredContent 格式异常")
        if not isinstance(data, dict):
            raise BusinessException(message="MCP 工具返回格式异常")
        return data

    if isinstance(structured, dict) and structured:
        return structured

    texts: list[str] = []
    for block in getattr(result, "content", None) or []:
        text = getattr(block, "text", None)
        if text:
            texts.append(text)
    joined = "\n".join(texts).strip()
    if not joined:
        raise BusinessException(message="MCP 工具返回空结果")

    try:
        data = json.loads(joined)
    except json.JSONDecodeError as exc:
        raise BusinessException(message="MCP 工具返回的不是合法 JSON") from exc

    # 兼容再包一层 {"result": "{...}"}
    if isinstance(data, dict) and set(data.keys()) == {"result"} and isinstance(
        data["result"], str
    ):
        data = json.loads(data["result"])

    if not isinstance(data, dict):
        raise BusinessException(message="MCP 工具返回格式异常")
    return data


# ---------------------------------------------------------------- 常驻会话
#
# 早期实现是每次调用都 `async with stdio_client(...)`，等于每次重新拉起一个
# Python 子进程：实测 query_logs 3.5s、query_chroma 5.1s，而一次问答要调 2~3 次，
# 光“起进程”就占 10 秒左右。现在改成进程内常驻会话：
#   - 后台线程跑一个事件循环，stdio 子进程只拉起一次；
#   - 同步节点通过 run_coroutine_threadsafe 提交调用；
#   - 子进程异常退出时丢弃会话，下一次调用自动重建。

_loop: asyncio.AbstractEventLoop | None = None
_loop_thread: threading.Thread | None = None
_boot_lock = threading.Lock()
_call_lock = threading.Lock()  # stdio 会话串行使用，避免多请求交叉
_session: "ClientSession | None" = None
_session_cms: list[Any] = []
CALL_TIMEOUT_SECONDS = 120.0


def _loop_forever(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


def _ensure_loop() -> asyncio.AbstractEventLoop:
    global _loop, _loop_thread
    with _boot_lock:
        if _loop is None or _loop.is_closed():
            _loop = asyncio.new_event_loop()
        if _loop_thread is None or not _loop_thread.is_alive():
            _loop_thread = threading.Thread(
                target=_loop_forever, args=(_loop,), name="mcp-loop", daemon=True
            )
            _loop_thread.start()
    return _loop


async def _get_session() -> ClientSession:
    """取常驻会话；没有就建立（进程启动成本只在首次调用时付一次）。"""
    global _session
    if _session is not None:
        return _session
    stdio_cm = stdio_client(_server_params())
    read, write = await stdio_cm.__aenter__()
    _session_cms[:] = [stdio_cm]
    session_cm = ClientSession(read, write)
    session = await session_cm.__aenter__()
    _session_cms.insert(0, session_cm)
    await session.initialize()
    _session = session
    logger.info("MCP 常驻会话已建立")
    return _session


async def _drop_session() -> None:
    """丢弃会话（子进程可能已退出），下一次调用会自动重建。"""
    global _session
    _session = None
    while _session_cms:
        cm = _session_cms.pop(0)
        try:
            await cm.__aexit__(None, None, None)
        except Exception:
            logger.debug("关闭 MCP 会话失败", exc_info=True)


async def _call_tool_async(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """异步调用工具（复用常驻会话）。"""
    logger.info("MCP 调用工具 %s args=%s", tool_name, list(arguments.keys()))
    try:
        async with asyncio.timeout(15.0 if tool_name == TOOL_MYSQL_SQL else CALL_TIMEOUT_SECONDS):
            session = await _get_session()
            result = await session.call_tool(tool_name, arguments=arguments)
    except (Exception, asyncio.CancelledError):
        # 会话可能已坏：丢掉，让下一次调用重建
        await _drop_session()
        raise
    if getattr(result, "isError", False):
        raise BusinessException(message=f"MCP 工具执行失败：{tool_name}")
    data = _parse_tool_result(result)
    if data.get("ok") is False:
        raise BusinessException(
            message=data.get("error") or f"MCP 工具业务失败：{tool_name}"
        )
    return data


def call_tool(tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """同步封装：复用常驻 MCP 子进程（供 LangGraph 同步节点使用）。"""
    loop = _ensure_loop()
    with _call_lock:
        future = asyncio.run_coroutine_threadsafe(
            _call_tool_async(tool_name, arguments or {}), loop
        )
        # 超时在协程内部触发；清理结束前保持同步锁，避免下次请求复用坏会话。
        try:
            return future.result()
        except TimeoutError as exc:
            raise BusinessException(message="MCP 工具调用超时，请稍后重试") from exc


def _shutdown() -> None:
    """进程退出时收尾：关闭会话与后台事件循环。"""
    if _loop is None:
        return
    try:
        asyncio.run_coroutine_threadsafe(_drop_session(), _loop).result(timeout=5)
    except Exception:
        pass
    try:
        _loop.call_soon_threadsafe(_loop.stop)
    except Exception:
        pass


atexit.register(_shutdown)


def query_mysql(question: str) -> dict[str, Any]:
    """经 MCP 查 MySQL。"""
    return call_tool(TOOL_MYSQL, {"question": question})


def query_mysql_sql(sql: str) -> dict[str, Any]:
    """当前模型已生成 SQL；MCP 只校验与执行，不再次调用另一模型。"""
    return call_tool(TOOL_MYSQL_SQL, {"sql": sql})


def query_chroma(
    query: str, top_k: int = 8, product_ids: list[int] | None = None,
    doc_types: list[str] | None = None,
) -> dict[str, Any]:
    """经 MCP 查 Chroma。"""
    arguments: dict[str, Any] = {"query": query, "top_k": top_k}
    if product_ids:
        arguments["product_ids"] = product_ids
    if doc_types:
        arguments["doc_types"] = doc_types
    return call_tool(TOOL_CHROMA, arguments)


def query_logs(keyword: str = "", limit: int = 5) -> dict[str, Any]:
    """经 MCP 查观测日志。"""
    return call_tool(TOOL_LOGS, {"keyword": keyword, "limit": limit})
