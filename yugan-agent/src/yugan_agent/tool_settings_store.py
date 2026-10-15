"""在本机保存启停状态和自定义工具定义。"""

import json
import os
import tempfile
from pathlib import Path

from .custom_tools import CustomToolDefinition


def load_tool_settings(path: Path) -> tuple[set[str], list[CustomToolDefinition]]:
    if not path.exists():
        return set(), []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 1:
        raise ValueError("工具配置文件格式无效")
    disabled = payload.get("disabled_builtins", [])
    custom_payload = payload.get("custom_tools", [])
    if not isinstance(disabled, list) or not isinstance(custom_payload, list):
        raise ValueError("工具配置文件格式无效")
    if len(custom_payload) > 30:
        raise ValueError("自定义工具最多保存 30 个")
    custom = [CustomToolDefinition.model_validate(item) for item in custom_payload]
    if len({item.name for item in custom}) != len(custom):
        raise ValueError("自定义工具名称不能重复")
    return set(disabled), custom


def save_tool_settings(
    path: Path,
    disabled_builtins: set[str],
    custom_tools: list[CustomToolDefinition],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".tools.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                {
                    "version": 1,
                    "disabled_builtins": sorted(disabled_builtins),
                    "custom_tools": [item.for_storage() for item in custom_tools],
                },
                stream,
                ensure_ascii=False,
                indent=2,
            )
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
