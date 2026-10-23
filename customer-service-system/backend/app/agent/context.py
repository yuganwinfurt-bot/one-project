"""整理有限的对话历史；原始问题不做字符串替换，语义理解由模型完成。"""

from typing import Any


def prepare_history(history: list[dict[str, Any]] | None, max_turns: int = 8) -> list[dict[str, str]]:
    """只传入最近的用户/助手消息，不接收历史里的系统指令或工具角色。"""
    result: list[dict[str, str]] = []
    remaining = 6000
    for turn in reversed(list(history or [])[-max_turns:]):
        if not isinstance(turn, dict) or turn.get("role") not in {"user", "assistant"}:
            continue
        content = str(turn.get("content") or "").strip()
        if not content:
            continue
        content = content[:min(1200, remaining)]
        if not content:
            break
        result.append({"role": turn["role"], "content": content})
        remaining -= len(content)
    return list(reversed(result))
