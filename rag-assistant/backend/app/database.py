import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

from .config import DB_PATH


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def new_id():
    return uuid4().hex


@contextmanager
def connect():
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS knowledge_bases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS project_knowledge_bases (
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                knowledge_base_id TEXT NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
                PRIMARY KEY (project_id, knowledge_base_id)
            );
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL DEFAULT '新对话',
                knowledge_base_ids TEXT NOT NULL DEFAULT '[]',
                scope_mode TEXT NOT NULL DEFAULT 'project',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources TEXT NOT NULL DEFAULT '[]',
                execution_steps TEXT NOT NULL DEFAULT '[]',
                execution_elapsed_ms INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                knowledge_base_id TEXT NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                vector_ids TEXT NOT NULL DEFAULT '[]',
                uploaded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ecommerce_sync_jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                stage TEXT NOT NULL,
                record_count INTEGER NOT NULL,
                processed_chunks INTEGER NOT NULL DEFAULT 0,
                total_chunks INTEGER NOT NULL DEFAULT 0,
                result TEXT NOT NULL DEFAULT '{}',
                error TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS embedding_cache (
                model_key TEXT NOT NULL,
                text_hash TEXT NOT NULL,
                dimensions INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (model_key, text_hash)
            );
            CREATE INDEX IF NOT EXISTS idx_chats_project_updated ON chats(project_id, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id, id);
            CREATE INDEX IF NOT EXISTS idx_documents_knowledge_base ON documents(knowledge_base_id, uploaded_at DESC);
            """
        )
        message_columns = {row["name"] for row in db.execute("PRAGMA table_info(messages)")}
        if "execution_steps" not in message_columns:
            db.execute("ALTER TABLE messages ADD COLUMN execution_steps TEXT NOT NULL DEFAULT '[]'")
        if "execution_elapsed_ms" not in message_columns:
            db.execute("ALTER TABLE messages ADD COLUMN execution_elapsed_ms INTEGER NOT NULL DEFAULT 0")
        document_columns = {row["name"] for row in db.execute("PRAGMA table_info(documents)")}
        if "embedding_profile" not in document_columns:
            db.execute("ALTER TABLE documents ADD COLUMN embedding_profile TEXT NOT NULL DEFAULT ''")
        job_columns = {row["name"] for row in db.execute("PRAGMA table_info(ecommerce_sync_jobs)")}
        for column in ("reused_chunks", "embedded_chunks"):
            if column not in job_columns:
                db.execute(f"ALTER TABLE ecommerce_sync_jobs ADD COLUMN {column} INTEGER NOT NULL DEFAULT 0")
        # 老会话保留已选范围；新会话默认每轮跟随项目关联的知识库。
        kb_columns = {row["name"] for row in db.execute("PRAGMA table_info(knowledge_bases)")}
        if "access_level" not in kb_columns:
            db.execute("ALTER TABLE knowledge_bases ADD COLUMN access_level TEXT NOT NULL DEFAULT 'public'")
        # 电商演示库公开读取；凭证排除和个人信息脱敏由同步导出层处理。
        db.execute(
            "UPDATE knowledge_bases SET access_level = 'public' WHERE name = ?",
            ("电商分析平台",),
        )
        chat_columns = {row["name"] for row in db.execute("PRAGMA table_info(chats)")}
        if "scope_mode" not in chat_columns:
            db.execute("ALTER TABLE chats ADD COLUMN scope_mode TEXT NOT NULL DEFAULT 'custom'")
        if db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
            stamp = now_iso()
            kb_rows = []
            for name, description in [
                ("STM32F103", "STM32F103 芯片、外设、HAL 库和项目笔记"),
                ("机械臂", "机械臂结构、舵机、运动学和控制资料"),
                ("MQTT", "MQTT 协议、设备通信和农业物联网资料"),
            ]:
                kb_id = new_id()
                db.execute(
                    "INSERT INTO knowledge_bases (id, name, description, created_at) VALUES (?, ?, ?, ?)",
                    (kb_id, name, description, stamp),
                )
                kb_rows.append(kb_id)

            project_id = new_id()
            db.execute("INSERT INTO projects (id, name, created_at) VALUES (?, ?, ?)", (project_id, "嵌入式项目", stamp))
            db.executemany(
                "INSERT INTO project_knowledge_bases (project_id, knowledge_base_id) VALUES (?, ?)",
                [(project_id, kb_id) for kb_id in kb_rows],
            )
            db.execute("INSERT INTO projects (id, name, created_at) VALUES (?, ?, ?)", (new_id(), "通用工作区", stamp))


def parse_json(value):
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
