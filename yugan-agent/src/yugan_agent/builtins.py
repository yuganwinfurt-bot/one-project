"""默认只读工具；文件访问限定在 workspace，HTTP 限定到配置好的端点。"""

import ast
import csv
import math
import operator
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Annotated
from urllib.parse import urlsplit

import httpx
from pydantic import Field

from .tools import ToolRegistry, tool

CREATABLE_TEXT_SUFFIXES = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".py",
    ".pyi",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".xml",
    ".sql",
    ".toml",
    ".yaml",
    ".yml",
    ".sh",
    ".ps1",
    ".bat",
    ".ini",
    ".cfg",
    ".log",
}


def safe_path(root: Path, path: str) -> Path:
    base = root.resolve()
    relative = Path(path)
    if relative.is_absolute() or relative.drive or ":" in path:
        raise PermissionError("请使用 workspace 内的相对路径")
    target = (base / relative).resolve()
    if not target.is_relative_to(base):
        raise PermissionError("文件路径超出 workspace")
    if any(p.startswith(".") for p in target.relative_to(base).parts):
        raise PermissionError("不允许读取隐藏文件或目录")
    return target


def read_text(root: Path, path: str) -> str:
    target = safe_path(root, path)
    if target.suffix.lower() not in {".txt", ".md", ".csv", ".json", ".py", ".c", ".h", ".log"}:
        raise PermissionError("仅支持 txt/md/csv/json/py/c/h/log 文本文件")
    # 有限读取，避免大文件耗尽内存。
    with target.open("rb") as stream:
        content = stream.read(1_000_001)
    if len(content) > 1_000_000:
        raise ValueError("文件超过 1 MB，请先拆分")
    return content.decode("utf-8-sig")


@tool
def calculator(expression: Annotated[str, Field(max_length=256)]) -> float:
    """计算基本四则运算，支持括号、取余和有限指数；不能执行 Python 代码。"""
    tree = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 64:
        raise ValueError("表达式过于复杂")
    binary = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.BinOp) and type(node.op) in binary:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 12:
                raise ValueError("指数绝对值不能超过 12")
            value = binary[type(node.op)](left, right)
        else:
            raise ValueError("只允许数字、括号和算术运算符")
        if not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value) > 1e12:
            raise ValueError("结果必须是绝对值不超过 1e12 的有限实数")
        return value

    return visit(tree.body)


@tool
def current_time(utc_offset: Annotated[int, Field(ge=-12, le=14)] = 8) -> str:
    """获取指定 UTC 时区的当前时间；默认 UTC+8（北京时间）。"""
    return datetime.now(timezone(timedelta(hours=utc_offset))).isoformat(timespec="seconds")


@tool
def numeric_stats(values: Annotated[list[float], Field(min_length=1, max_length=10000)]) -> dict:
    """返回一组有限数值的数量、最小值、最大值、平均值、中位数和总体标准差。"""
    if any(not math.isfinite(x) or abs(x) > 1e12 for x in values):
        raise ValueError("数值必须有限且绝对值不超过 1e12")
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "median": median(values),
        "stddev": pstdev(values),
    }


def register_builtins(registry: ToolRegistry, workspace: Path, endpoints: dict[str, str]):
    workspace.mkdir(parents=True, exist_ok=True)
    for entry in (calculator, current_time, numeric_stats):
        registry.register(entry)

    @tool
    def list_files(directory: str = ".") -> list[str]:
        """列出 workspace 指定目录的非隐藏文件和子目录（最多 100 项）。"""
        folder = safe_path(workspace, directory)
        entries = []
        for entry in folder.iterdir():
            if entry.name.startswith(".") or entry.is_symlink():
                continue
            resolved = entry.resolve()
            if not resolved.is_relative_to(workspace.resolve()):
                continue
            entries.append(entry.name + ("/" if entry.is_dir() else ""))
            if len(entries) == 100:
                break
        return sorted(entries)

    @tool
    def read_file(
        path: str,
        offset: Annotated[int, Field(ge=0)] = 0,
        limit: Annotated[int, Field(ge=1, le=6000)] = 4000,
    ) -> dict:
        """按字符读取 workspace 内文本文件，返回内容和是否还有后续内容。"""
        content = read_text(workspace, path)
        return {
            "path": path,
            "content": content[offset : offset + limit],
            "has_more": offset + limit < len(content),
        }

    @tool(side_effect=True, always_confirm=True)
    def create_text_file(
        path: Annotated[str, Field(min_length=1, max_length=240)],
        content: Annotated[str, Field(max_length=6000)],
    ) -> dict:
        """在 workspace 新建常见文本或源码文件；不覆盖已有文件，Web 会逐次询问确认。"""
        target = safe_path(workspace, path)
        if target.suffix.lower() not in CREATABLE_TEXT_SUFFIXES:
            raise PermissionError("该文件类型不在允许新建的文本/源码文件列表中")
        if target.exists():
            raise ValueError("目标文件已存在；为防覆盖，不能新建")
        if not target.parent.is_dir():
            raise FileNotFoundError("目标文件夹不存在，请先在 workspace 中准备文件夹")
        with target.open("x", encoding="utf-8", newline="") as stream:
            stream.write(content)
        return {"path": path, "characters": len(content), "created": True}

    @tool
    def csv_summary(path: str, column: str) -> dict:
        """分析 workspace 中 CSV 的一个数值列，返回统计信息；空值跳过，非数值报错。"""
        reader = csv.DictReader(StringIO(read_text(workspace, path)))
        if not reader.fieldnames or column not in reader.fieldnames:
            raise ValueError("CSV 不包含指定列")
        values, missing = [], 0
        for row in reader:
            raw = row.get(column)
            if raw is None or not raw.strip():
                missing += 1
            else:
                values.append(float(raw))
            if len(values) + missing > 10000:
                raise ValueError("CSV 最多支持 10000 行")
        if not values:
            raise ValueError("该列没有可用数值")
        return {"column": column, "missing": missing, **numeric_stats.function(values)}

    @tool
    async def http_get(endpoint: str, params: dict[str, str] | None = None) -> dict:
        """GET 调用管理员预设的固定 HTTP 端点。endpoint 必须是配置中的别名，不是 URL。"""
        if endpoint not in endpoints:
            raise PermissionError("端点未配置；请在 YUGAN_HTTP_ENDPOINTS 中添加可信固定 URL")
        url = endpoints[endpoint]
        parsed = urlsplit(url)
        if parsed.username or parsed.password or parsed.fragment:
            raise ValueError("端点 URL 不能包含凭据或片段")
        if parsed.scheme != "https" and not (
            parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        ):
            raise ValueError("端点必须使用 HTTPS；本机服务允许 HTTP")
        async with httpx.AsyncClient(timeout=8, follow_redirects=False, trust_env=False) as client:
            async with client.stream("GET", url, params=params) as response:
                if response.status_code != 200:
                    raise ValueError(f"端点返回 HTTP {response.status_code}")
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > 12000:
                        raise ValueError("HTTP 响应超过 12000 字节，请缩小查询")
                return {
                    "status": response.status_code,
                    "content": body.decode("utf-8", errors="replace"),
                }

    for entry in (list_files, read_file, create_text_file, csv_summary, http_get):
        registry.register(entry)
