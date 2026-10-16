"""Limit files created by guest tool calls to a shared workspace directory."""

import hashlib
import os
import sqlite3
from contextlib import closing, contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from pydantic import Field

from .builtins import CREATABLE_TEXT_SUFFIXES, safe_path
from .tools import ToolRegistry, tool

GUEST_FILE_LIMIT = 10
GUEST_FOLDER = "guest-files"
GUEST_TOOLS = {
    "calculator",
    "current_time",
    "numeric_stats",
    "list_files",
    "read_file",
    "csv_summary",
    "search_workspace",
    "git_status",
    "git_diff",
    "git_log",
    "list_skills",
    "read_skill",
    "create_text_file",
}


class GuestFileStore:
    """All guest sessions share the same ten files in the first workspace."""

    def __init__(self, lock_path: Path) -> None:
        self._lock_path = lock_path
        self._session: ContextVar[tuple[str, int] | None] = ContextVar(
            "generated_file_session", default=None
        )

    @contextmanager
    def session_scope(self, session_id: str, turn_index: int):
        token = self._session.set((session_id, turn_index))
        try:
            yield
        finally:
            self._session.reset(token)

    @staticmethod
    def _ensure_schema(connection: sqlite3.Connection) -> None:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS owned_guest_folders (workspace TEXT PRIMARY KEY)"
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS generated_files (
                id TEXT PRIMARY KEY, session_id TEXT NOT NULL, turn_index INTEGER NOT NULL,
                workspace TEXT NOT NULL, path TEXT NOT NULL, created_at TEXT NOT NULL,
                size INTEGER NOT NULL, sha256 TEXT NOT NULL, device INTEGER NOT NULL,
                inode INTEGER NOT NULL, mtime_ns INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active'
            )"""
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS generated_files_session ON generated_files(session_id, turn_index)"
        )

    @staticmethod
    def _file_bytes(target: Path) -> tuple[bytes, object]:
        if target.is_symlink() or not target.is_file():
            raise FileNotFoundError("生成文件已不存在")
        with target.open("rb") as stream:
            stat = os.fstat(stream.fileno())
            data = stream.read(100_001)
        if len(data) > 100_000:
            raise ValueError("生成文件已变更或过大，不能再操作")
        return data, stat

    def _insert_record(
        self, connection: sqlite3.Connection, workspace: Path, path: str,
        session_id: str, turn_index: int,
    ) -> str:
        target = safe_path(workspace, path)
        data, stat = self._file_bytes(target)
        file_id = uuid4().hex
        connection.execute(
            "UPDATE generated_files SET status = 'replaced' WHERE workspace = ? AND path = ? AND status = 'active'",
            (str(workspace.resolve()), path),
        )
        connection.execute(
            """INSERT INTO generated_files
               (id, session_id, turn_index, workspace, path, created_at,
                size, sha256, device, inode, mtime_ns, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
            (file_id, session_id, turn_index, str(workspace.resolve()), path,
             datetime.now(timezone.utc).isoformat(timespec="seconds"), len(data),
             hashlib.sha256(data).hexdigest(), stat.st_dev, stat.st_ino, stat.st_mtime_ns),
        )
        return file_id

    def record_admin_file(
        self, workspace: Path, path: str, session_id: str, turn_index: int
    ) -> str:
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self._lock_path, timeout=30)) as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._ensure_schema(connection)
            file_id = self._insert_record(connection, workspace, path, session_id, turn_index)
            connection.commit()
            return file_id

    @staticmethod
    def _status(row: sqlite3.Row) -> str:
        if row["status"] != "active":
            return row["status"]
        try:
            target = safe_path(Path(row["workspace"]), row["path"])
            data, stat = GuestFileStore._file_bytes(target)
        except (OSError, ValueError, PermissionError):
            return "missing"
        if (
            len(data) != row["size"]
            or hashlib.sha256(data).hexdigest() != row["sha256"]
            or stat.st_dev != row["device"]
            or stat.st_ino != row["inode"]
            or stat.st_mtime_ns != row["mtime_ns"]
        ):
            return "changed"
        return "active"

    @staticmethod
    def _public(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "path": row["path"],
            "turn_index": row["turn_index"],
            "created_at": row["created_at"],
            "size": row["size"],
            "status": GuestFileStore._status(row),
        }

    def list_for_session(self, session_id: str) -> list[dict]:
        if not self._lock_path.is_file():
            return []
        with closing(sqlite3.connect(self._lock_path, timeout=30)) as connection:
            connection.row_factory = sqlite3.Row
            self._ensure_schema(connection)
            rows = connection.execute(
                "SELECT * FROM generated_files WHERE session_id = ? ORDER BY rowid",
                (session_id,),
            ).fetchall()
        return [self._public(row) for row in rows]

    def read(self, session_id: str, file_id: str) -> tuple[dict, bytes]:
        with closing(sqlite3.connect(self._lock_path, timeout=30)) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("BEGIN IMMEDIATE")
            self._ensure_schema(connection)
            row = connection.execute(
                "SELECT * FROM generated_files WHERE id = ? AND session_id = ?",
                (file_id, session_id),
            ).fetchone()
            if row is None:
                raise FileNotFoundError("这次对话没有该生成文件")
            status = self._status(row)
            if status != "active":
                raise ValueError("文件已撤销、被替换或发生变更，无法查看或下载")
            target = safe_path(Path(row["workspace"]), row["path"])
            return self._public(row), self._file_bytes(target)[0]

    def revoke(self, session_id: str, file_id: str) -> dict:
        with closing(sqlite3.connect(self._lock_path, timeout=30)) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("BEGIN IMMEDIATE")
            self._ensure_schema(connection)
            row = connection.execute(
                "SELECT * FROM generated_files WHERE id = ? AND session_id = ?",
                (file_id, session_id),
            ).fetchone()
            if row is None:
                raise FileNotFoundError("这次对话没有该生成文件")
            if self._status(row) != "active":
                raise ValueError("文件已撤销、被替换或发生变更，不能撤销")
            target = safe_path(Path(row["workspace"]), row["path"])
            target.unlink()
            connection.execute(
                "UPDATE generated_files SET status = 'revoked' WHERE id = ?", (file_id,)
            )
            connection.commit()
            return {"id": file_id, "status": "revoked"}

    def restrict_registry(self, registry: ToolRegistry, workspace: Path) -> ToolRegistry:
        for schema in registry.schemas():
            if schema["name"] not in GUEST_TOOLS:
                registry.unregister(schema["name"])
        registry.unregister("create_text_file")

        @tool(name="create_text_file", side_effect=True, always_confirm=True)
        def create_guest_text_file(
            path: Annotated[str, Field(min_length=1, max_length=240)],
            content: Annotated[str, Field(max_length=6000)],
        ) -> dict:
            """在 guest-files 目录新建文本文件；所有游客共用最多 10 个，超出时删除最早创建的文件。path 只填文件名。"""
            return self.create(workspace, path, content)

        registry.register(create_guest_text_file)
        return registry

    def create(self, workspace: Path, filename: str, content: str) -> dict:
        owner = self._session.get()
        if owner is None:
            raise PermissionError("游客生成文件需要所属对话")
        if filename in {".", ".."} or Path(filename).name != filename or "\\" in filename:
            raise ValueError("游客只能填写文件名，不能包含目录")
        target = safe_path(workspace, f"{GUEST_FOLDER}/{filename}")
        if target.suffix.lower() not in CREATABLE_TEXT_SUFFIXES:
            raise PermissionError("该文件类型不在允许新建的文本/源码文件列表中")
        folder = workspace.resolve() / GUEST_FOLDER
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        # SQLite's write lock serializes guest creations across server workers.
        with closing(sqlite3.connect(self._lock_path, timeout=30)) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                self._ensure_schema(connection)
                result = self._create_locked(
                    connection, workspace.resolve(), folder, target, filename, content, owner
                )
                connection.commit()
                return result
            except Exception:
                connection.rollback()
                raise

    def _create_locked(
        self,
        connection: sqlite3.Connection,
        workspace: Path,
        folder: Path,
        target: Path,
        filename: str,
        content: str,
        owner: tuple[str, int],
    ) -> dict:
        if folder.is_symlink():
            raise PermissionError("游客文件目录不能是链接")
        if folder.exists() and not folder.is_dir():
            raise PermissionError("游客文件目录不是文件夹")
        owned = connection.execute(
            "SELECT 1 FROM owned_guest_folders WHERE workspace = ?", (str(workspace),)
        ).fetchone()
        if not owned and folder.exists() and any(folder.iterdir()):
            raise PermissionError("guest-files 中已有文件，不能自动接管或覆盖")
        folder.mkdir(exist_ok=True)
        if not owned:
            connection.execute(
                "INSERT INTO owned_guest_folders (workspace) VALUES (?)", (str(workspace),)
            )

        files = []
        for item in folder.iterdir():
            if item.is_symlink() or not item.is_file():
                raise PermissionError("guest-files 中存在非普通文件，不能自动清理")
            files.append(item)
        if target.exists() or target.is_symlink():
            raise ValueError("目标文件已存在；请换一个文件名")

        removed = []
        created = False
        try:
            with target.open("x", encoding="utf-8", newline="") as stream:
                created = True
                stream.write(content)
            relative = f"{GUEST_FOLDER}/{filename}"
            file_id = self._insert_record(connection, workspace, relative, *owner)
            while len(files) >= GUEST_FILE_LIMIT:
                oldest = min(files, key=lambda item: (item.stat().st_mtime_ns, item.name))
                connection.execute(
                    "UPDATE generated_files SET status = 'replaced' "
                    "WHERE workspace = ? AND path = ? AND status = 'active'",
                    (str(workspace), f"{GUEST_FOLDER}/{oldest.name}"),
                )
                oldest.unlink()
                files.remove(oldest)
                removed.append(oldest.name)
        except Exception:
            if created:
                target.unlink(missing_ok=True)
            raise
        return {
            "path": f"{GUEST_FOLDER}/{filename}",
            "file_id": file_id,
            "characters": len(content),
            "created": True,
            "removed_oldest": removed,
            "total_guest_files": len(files) + 1,
        }
