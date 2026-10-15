"""Persist named workspaces and conversation assignments on this computer."""

import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4


def load_workspace(path: Path, fallback: Path) -> Path:
    """Read the single-workspace setting written by older versions."""
    default = fallback.expanduser().resolve()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))["workspace"]
        selected = Path(value).expanduser().resolve(strict=True)
        return selected if selected.is_dir() else default
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return default


def load_workspaces(path: Path, legacy_path: Path, fallback: Path):
    legacy = load_workspace(legacy_path, fallback)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        workspaces = []
        for item in data.get("workspaces", []):
            workspace_path = Path(item["path"]).expanduser().resolve(strict=True)
            workspace_id = str(item["id"])
            name = str(item["name"]).strip()
            if workspace_path.is_dir() and name and workspace_id:
                workspaces.append(
                    {"id": workspace_id, "name": name[:80], "path": str(workspace_path)}
                )
        sessions = {
            str(session_id): str(workspace_id)
            for session_id, workspace_id in data.get("sessions", {}).items()
            if isinstance(session_id, str) and isinstance(workspace_id, str)
        }
        active_id = str(data.get("active_workspace_id", ""))
        if workspaces:
            if not any(item["id"] == active_id for item in workspaces):
                active_id = workspaces[0]["id"]
            valid_ids = {item["id"] for item in workspaces}
            sessions = {key: value for key, value in sessions.items() if value in valid_ids}
            return workspaces, active_id, sessions
    except (AttributeError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        pass

    legacy.mkdir(parents=True, exist_ok=True)
    workspace = {"id": uuid4().hex, "name": legacy.name or "默认工作区", "path": str(legacy)}
    return [workspace], workspace["id"], {}


def save_workspaces(
    path: Path, workspaces: list[dict], active_id: str, sessions: dict[str, str]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="workspaces.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(
                {
                    "workspaces": workspaces,
                    "active_workspace_id": active_id,
                    "sessions": sessions,
                },
                stream,
                ensure_ascii=False,
                indent=2,
            )
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
