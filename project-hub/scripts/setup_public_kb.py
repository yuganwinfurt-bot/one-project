"""Run with rag-assistant/backend's Python to index the reviewed public Markdown."""

import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAG_BACKEND = ROOT.parent / "rag-assistant" / "backend"
sys.path.insert(0, str(RAG_BACKEND))

from app.config import UPLOAD_DIR
from app.database import connect, initialize_database, new_id, now_iso
from app.rag.pipeline import index_file

SOURCE = ROOT / "content" / "public-projects.md"
KB_NAME = "项目实验室公开资料"
DOC_NAME = "项目说明.md"


def check_public_text(text: str) -> None:
    blocked = [
        r"C:\\Users\\", r"[A-Za-z]:\\", r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        r"(?<!\d)1[3-9]\d{9}(?!\d)", r"(?<!\d)\d{17}[\dXx](?!\d)",
    ]
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in blocked):
        raise SystemExit("公开资料存在可能的个人信息或本机路径，请先检查并修改")
    custom_terms = [item.strip() for item in os.getenv("PUBLIC_FORBIDDEN_TERMS", "").split(",") if item.strip()]
    if any(item in text for item in custom_terms):
        raise SystemExit("公开资料包含私有禁止词，请先检查并修改")


def main() -> None:
    check_public_text(SOURCE.read_text(encoding="utf-8"))
    initialize_database()
    with connect() as db:
        existing = db.execute("SELECT id FROM knowledge_bases WHERE name=?", (KB_NAME,)).fetchone()
        kb_id = existing["id"] if existing else new_id()
        if not existing:
            db.execute(
                "INSERT INTO knowledge_bases (id,name,description,created_at) VALUES (?,?,?,?)",
                (kb_id, KB_NAME, "仅供公开项目问答的审核资料", now_iso()),
            )
        document = db.execute(
            "SELECT id FROM documents WHERE knowledge_base_id=? AND filename=?",
            (kb_id, DOC_NAME),
        ).fetchone()
        if document:
            print(f"公开知识库已存在。RAG_PUBLIC_KB_IDS={kb_id}")
            return
    document_id = new_id()
    target_dir = UPLOAD_DIR / kb_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{document_id}.md"
    shutil.copyfile(SOURCE, target)
    try:
        count, vector_ids = index_file(kb_id, document_id, target, DOC_NAME)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    with connect() as db:
        db.execute(
            "INSERT INTO documents (id,knowledge_base_id,filename,stored_path,chunk_count,vector_ids,uploaded_at) VALUES (?,?,?,?,?,?,?)",
            (document_id, kb_id, DOC_NAME, str(target), count, json.dumps(vector_ids), now_iso()),
        )
    print(f"公开知识库已建立。RAG_PUBLIC_KB_IDS={kb_id}")


if __name__ == "__main__":
    main()
