import asyncio
import csv
import hashlib
import io
import json
import logging
import os
import re
import secrets
from contextlib import asynccontextmanager
from contextvars import ContextVar
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import FastAPI, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from .config import (
    MAX_UPLOAD_MB,
    OLLAMA_BASE_URL,
    OLLAMA_CLIENT_KWARGS,
    OLLAMA_EMBED_MODEL,
    UPLOAD_DIR,
)
from .database import connect, initialize_database, new_id, now_iso, parse_json
from .auth import AuthManager
from .model_settings import AnswerModelSettings, load_settings, save_settings, validate_settings
from .rag.graph import create_rag_graph
from .rag.pipeline import (
    ALLOWED_EXTENSIONS,
    delete_knowledge_base_collection,
    get_vector_store,
    index_file,
    read_document_chunks,
    remove_document_vectors,
    retrieve_contexts,
)
from .schemas import (
    AgentRetrieveRequest,
    ChatCreate,
    ChatUpdate,
    EcommerceSyncRequest,
    KnowledgeBaseCreate,
    MessageCreate,
    ProjectCreate,
    ProjectUpdate,
)

MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ECOMMERCE_KB_ID = "ecommerce-analysis-platform"
ECOMMERCE_KB_NAME = "电商分析平台"
ECOMMERCE_PROJECT_ID = "ecommerce-platform"
ECOMMERCE_EXPORT_FILENAME = "电商分析平台_后台业务快照.csv"
_private_access = ContextVar("rag_private_access", default=False)
_ecommerce_sync_lock = asyncio.Lock()
logger = logging.getLogger(__name__)

auth_manager = AuthManager(
    os.getenv("YUGAN_ADMIN_USERNAME", ""),
    os.getenv("YUGAN_ADMIN_PASSWORD_HASH", ""),
    os.getenv("YUGAN_AUTH_SIGNING_SECRET", ""),
)
WEB_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "RAG_WEB_ORIGINS",
        "http://localhost:4173,http://127.0.0.1:4173,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    try:
        _app.state.answer_model_settings = load_settings()
    except (OSError, ValueError):
        logger.exception("读取 RAG 模型设置失败，改用默认 Ollama 模型")
        _app.state.answer_model_settings = AnswerModelSettings()
    _app.state.rag_graph = create_rag_graph(_app.state.answer_model_settings)
    # Creating an AsyncClient loads TLS certificates synchronously on Windows.
    # Reuse it so a status poll cannot stall unrelated page requests.
    async with httpx.AsyncClient(timeout=1.5, **OLLAMA_CLIENT_KWARGS) as client:
        _app.state.ollama_status_client = client
        yield


app = FastAPI(title="本地 RAG 知识库助手", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(WEB_ORIGINS),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def authenticate_and_limit_guests(request: Request, call_next):
    if request.method == "OPTIONS" or not request.url.path.startswith("/api/"):
        return await call_next(request)
    if request.url.path in {"/api/auth/status", "/api/auth/login", "/api/auth/logout"}:
        return await call_next(request)

    role = auth_manager.role(request)
    request.state.role = role
    request.state.subject = auth_manager.subject(request)
    _private_access.set(role == "admin")
    origin = request.headers.get("origin")
    if origin and origin != str(request.base_url).rstrip("/"):
        if origin.rstrip("/") not in WEB_ORIGINS:
            return JSONResponse({"detail": "不接受跨源请求"}, status_code=403)

    if role != "admin" and request.method not in {"GET", "HEAD"}:
        path = request.url.path
        guest_chat_create = request.method == "POST" and re.fullmatch(
            r"/api/projects/[^/]+/chats", path
        )
        guest_chat_update = request.method == "PATCH" and re.fullmatch(
            r"/api/chats/[^/]+", path
        )
        guest_chat_retrieve = request.method == "POST" and re.fullmatch(
            r"/api/chats/[^/]+/retrieve", path
        )
        guest_chat_stream = request.method == "POST" and re.fullmatch(
            r"/api/chats/[^/]+/messages/stream", path
        )
        guest_chat_answer = request.method == "POST" and re.fullmatch(
            r"/api/chats/[^/]+/answer", path
        )
        guest_chat_delete = request.method == "DELETE" and re.fullmatch(
            r"/api/chats/[^/]+", path
        )
        local_agent_retrieve = (
            request.method == "POST"
            and path == "/api/integrations/agent/retrieve"
            and request.client is not None
            and request.client.host in {"127.0.0.1", "::1"}
        )
        local_ecommerce_sync = (
            request.method == "POST"
            and path == "/api/integrations/agent/sync-ecommerce"
            and request.client is not None
            and request.client.host in {"127.0.0.1", "::1"}
        )
        if not (
            guest_chat_create or guest_chat_update or guest_chat_delete
            or guest_chat_retrieve or guest_chat_answer or guest_chat_stream
            or local_agent_retrieve or local_ecommerce_sync
        ):
            return JSONResponse({"detail": "游客不能修改知识库、项目或模型设置"}, status_code=403)
    return await call_next(request)


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=512)


@app.get("/api/auth/status")
def auth_status(request: Request):
    role = auth_manager.role(request)
    subject = auth_manager.subject(request)
    if subject == "anonymous":
        guest_token, subject = auth_manager.issue_guest_session()
        response = JSONResponse({
            "role": "guest", "subject": subject, "login_configured": auth_manager.configured,
        })
        auth_manager.set_cookie(response, request, guest_token)
        return response
    response = JSONResponse({
        "role": role,
        "subject": "admin" if role == "admin" else subject,
        "login_configured": auth_manager.configured,
    })
    return response


@app.post("/api/auth/login")
def auth_login(request: Request, payload: LoginBody):
    origin = request.headers.get("origin")
    allowed_origins = WEB_ORIGINS | {str(request.base_url).rstrip("/")}
    if origin and origin not in allowed_origins:
        raise HTTPException(status_code=403, detail="不接受跨源登录")
    token = auth_manager.authenticate(request, payload.username, payload.password)
    response = JSONResponse({"role": "admin"})
    auth_manager.set_cookie(response, request, token)
    return response


@app.post("/api/auth/logout")
def auth_logout(request: Request):
    response = JSONResponse({"role": "guest"})
    auth_manager.set_cookie(response, request, auth_manager.issue_guest())
    return response


def ensure_knowledge_bases_exist(knowledge_base_ids: list[str], *, allow_private=False):
    ids = list(dict.fromkeys(knowledge_base_ids))
    if not ids:
        return ids
    placeholders = ",".join("?" for _ in ids)
    with connect() as db:
        rows = db.execute(
            f"SELECT id, access_level FROM knowledge_bases WHERE id IN ({placeholders})", ids
        ).fetchall()
    if len(rows) != len(ids):
        raise HTTPException(status_code=404, detail="选择的知识库不存在或已被删除")
    if not (allow_private or _private_access.get()) and any(row["access_level"] == "staff" for row in rows):
        raise HTTPException(status_code=403, detail="该知识库包含后台业务资料，请登录管理员后查看")
    return ids


def guest_chat_prefix(request: Request) -> str:
    if getattr(request.state, "role", "guest") == "admin":
        return ""
    subject = getattr(request.state, "subject", "anonymous")
    return f"guest_{hashlib.sha256(subject.encode()).hexdigest()[:12]}_"


def accessible_chat_id(chat_id: str, request: Request) -> str:
    prefix = guest_chat_prefix(request)
    if prefix and not chat_id.startswith(prefix):
        raise HTTPException(status_code=404, detail="对话不存在")
    return chat_id


def project_dict(row, db):
    kb_rows = db.execute(
        "SELECT knowledge_base_id FROM project_knowledge_bases WHERE project_id = ? ORDER BY rowid",
        (row["id"],),
    ).fetchall()
    return {**dict(row), "knowledge_base_ids": [item["knowledge_base_id"] for item in kb_rows]}


def serialize_message(row):
    return {**dict(row), "sources": parse_json(row["sources"])}


def effective_knowledge_bases(db, chat):
    """自动模式每轮读项目关联；自定义模式使用这段对话自己选择的库。"""
    if chat["scope_mode"] == "project":
        rows = db.execute(
            "SELECT knowledge_base_id FROM project_knowledge_bases WHERE project_id = ? ORDER BY rowid",
            (chat["project_id"],),
        ).fetchall()
        ids = [row["knowledge_base_id"] for row in rows]
    else:
        ids = parse_json(chat["knowledge_base_ids"])
    existing = {row["id"] for row in db.execute(
        "SELECT id FROM knowledge_bases WHERE access_level != 'staff' OR ?", (int(_private_access.get()),)
    )}
    return [value for value in ids if value in existing]


def chat_dict(db, chat):
    return {**dict(chat), "knowledge_base_ids": effective_knowledge_bases(db, chat)}


def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "本地 RAG 知识库助手"}


class PublicQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@app.post("/api/internal/public-answer", include_in_schema=False)
async def public_answer(payload: PublicQuestion, x_bridge_token: str = Header(default="")):
    """只把人工选定的公开知识库交给独立入口；现有管理 API 不经此桥接。"""
    token = os.getenv("RAG_PUBLIC_BRIDGE_TOKEN", "")
    kb_ids = [item.strip() for item in os.getenv("RAG_PUBLIC_KB_IDS", "").split(",") if item.strip()]
    if not token or not kb_ids:
        raise HTTPException(status_code=503, detail="公开知识库尚未配置")
    if not secrets.compare_digest(x_bridge_token, token):
        raise HTTPException(status_code=401, detail="桥接认证失败")
    if not payload.question.strip():
        raise HTTPException(status_code=422, detail="请输入问题")
    with connect() as db:
        placeholders = ",".join("?" for _ in kb_ids)
        rows = db.execute(
            f"SELECT id, name FROM knowledge_bases WHERE id IN ({placeholders}) AND access_level != 'staff'", kb_ids
        ).fetchall()
    names = {row["id"]: row["name"] for row in rows}
    if len(names) != len(set(kb_ids)):
        raise HTTPException(status_code=503, detail="公开知识库配置无效")
    result = await app.state.rag_graph.ainvoke({
        "question": payload.question.strip(),
        "knowledge_base_ids": list(names),
        "knowledge_base_names": names,
        "history": [],
    })
    sources = [{"page": item.get("page")} for item in result.get("contexts", [])]
    return JSONResponse(
        {"answer": result.get("answer", ""), "sources": sources},
        headers={"Cache-Control": "no-store"},
    )


@app.post("/api/integrations/agent/retrieve", include_in_schema=False)
async def retrieve_for_agent(payload: AgentRetrieveRequest, request: Request):
    """Return read-only evidence from selected local knowledge bases, without Ollama chat."""
    if not request.client or request.client.host not in {"127.0.0.1", "::1"}:
        raise HTTPException(status_code=403, detail="此检索接口仅允许本机 Agent 调用")
    token = os.getenv("ECOM_RAG_SYNC_TOKEN", "").strip()
    trusted = bool(token and secrets.compare_digest(request.headers.get("x-integration-key", ""), token))
    requested_ids = payload.knowledge_base_ids
    if payload.knowledge_base_name:
        with connect() as db:
            row = db.execute("SELECT id FROM knowledge_bases WHERE name = ? ORDER BY created_at LIMIT 1", (payload.knowledge_base_name,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="电商分析平台知识库尚未创建，请先同步后台数据")
        requested_ids = [row["id"]]
    kb_ids = ensure_knowledge_bases_exist(requested_ids, allow_private=trusted)
    with connect() as db:
        placeholders = ",".join("?" for _ in kb_ids)
        rows = db.execute(
            f"SELECT id, name FROM knowledge_bases WHERE id IN ({placeholders})", kb_ids
        ).fetchall()
    names = {row["id"]: row["name"] for row in rows}
    matches = await asyncio.to_thread(
        retrieve_contexts,
        payload.query,
        kb_ids,
        names,
        payload.top_k,
        payload.product_ids,
        payload.doc_types,
    )
    collection_size = sum(
        get_vector_store(knowledge_base_id)._collection.count()
        for knowledge_base_id in kb_ids
    )
    return JSONResponse(
        {"matches": [
            {
                "content": item.get("content", "")[:3000],
                "filename": item.get("filename", "资料")[:160],
                "page": item.get("page"),
                "knowledge_base_id": item.get("knowledge_base_id", ""),
                "knowledge_base_name": item.get("knowledge_base_name", "知识库")[:80],
                "score": round(float(item.get("score", 0)), 3),
                "chunk_id": item.get("chunk_id"),
                "metadata": {
                    key: item.get("metadata", {}).get(key)
                    for key in ("record_id", "doc_type", "source_table", "source_id", "product_id", "review_id", "rating", "name", "category", "has_image", "chunk_index")
                    if item.get("metadata", {}).get(key) is not None
                },
            }
            for item in matches[:payload.top_k]
        ], "collection_size": collection_size},
        headers={"Cache-Control": "no-store"},
    )


@app.post("/api/integrations/agent/sync-ecommerce", include_in_schema=False)
async def sync_ecommerce_knowledge(payload: EcommerceSyncRequest, request: Request):
    """Replace the managed e-commerce CSV in the local RAG library; loopback + shared token only."""
    if not request.client or request.client.host not in {"127.0.0.1", "::1"}:
        raise HTTPException(status_code=403, detail="此同步接口仅允许本机 Agent 调用")
    expected_token = os.getenv("ECOM_RAG_SYNC_TOKEN", "").strip()
    supplied_token = request.headers.get("x-integration-key", "")
    if not expected_token:
        raise HTTPException(status_code=503, detail="未配置电商 RAG 同步密钥")
    if not secrets.compare_digest(supplied_token, expected_token):
        raise HTTPException(status_code=403, detail="电商 RAG 同步密钥无效")

    async with _ecommerce_sync_lock:
        return await _sync_ecommerce_records(payload)


async def _sync_ecommerce_records(payload: EcommerceSyncRequest):
    with connect() as db:
        existing = db.execute("SELECT id FROM knowledge_bases WHERE name = ? ORDER BY created_at LIMIT 1", (ECOMMERCE_KB_NAME,)).fetchone()
        kb_id = existing["id"] if existing else ECOMMERCE_KB_ID
        if not existing and db.execute("SELECT id FROM knowledge_bases WHERE id = ?", (kb_id,)).fetchone():
            kb_id = new_id()

    ids = [record.record_id for record in payload.records]
    if len(ids) != len(set(ids)):
        raise HTTPException(status_code=422, detail="同步记录包含重复编号")

    output = io.StringIO(newline="")
    fieldnames = ["record_id", "doc_type", "source_table", "source_id", "product_id", "review_id", "rating", "name", "category", "has_image", "content"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for record in payload.records:
        writer.writerow(record.model_dump())
    content = output.getvalue().encode("utf-8")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"电商资料超过 {MAX_UPLOAD_MB} MB 限制")

    with connect() as db:
        previous = db.execute("SELECT * FROM documents WHERE knowledge_base_id = ? AND filename = ?", (kb_id, ECOMMERCE_EXPORT_FILENAME)).fetchall()
        if len(previous) == 1 and Path(previous[0]["stored_path"]).is_file() and Path(previous[0]["stored_path"]).read_bytes() == content:
            db.execute("UPDATE knowledge_bases SET access_level = 'public' WHERE id = ?", (kb_id,))
            return {"knowledge_base_id": kb_id, "knowledge_base_name": ECOMMERCE_KB_NAME,
                    "record_count": len(payload.records), "chunk_count": previous[0]["chunk_count"],
                    "collection_size": get_vector_store(kb_id)._collection.count(), "unchanged": True, "cleanup_warning": False}

    document_id = uuid4().hex
    target_dir = UPLOAD_DIR / kb_id
    target_dir.mkdir(parents=True, exist_ok=True)
    stored_path = target_dir / f"{document_id}.csv"
    stored_path.write_bytes(content)
    vector_ids: list[str] = []
    try:
        chunk_count, vector_ids = await asyncio.to_thread(
            index_file,
            kb_id,
            document_id,
            stored_path,
            ECOMMERCE_EXPORT_FILENAME,
        )
        with connect() as db:
            old_docs = db.execute(
                "SELECT id, stored_path, vector_ids FROM documents WHERE knowledge_base_id = ? AND filename = ?",
                (kb_id, ECOMMERCE_EXPORT_FILENAME),
            ).fetchall()
            stamp = now_iso()
            db.execute(
                "INSERT OR IGNORE INTO knowledge_bases (id, name, description, created_at, access_level) VALUES (?, ?, ?, ?, 'public')",
                (kb_id, ECOMMERCE_KB_NAME, "电商后台完整业务快照及功能规则，已排除凭证并脱敏个人信息", stamp),
            )
            db.execute("UPDATE knowledge_bases SET access_level = 'public' WHERE id = ?", (kb_id,))
            db.execute(
                "INSERT OR IGNORE INTO projects (id, name, created_at) VALUES (?, ?, ?)",
                (ECOMMERCE_PROJECT_ID, "电商分析平台", stamp),
            )
            db.execute(
                "INSERT OR IGNORE INTO project_knowledge_bases (project_id, knowledge_base_id) VALUES (?, ?)",
                (ECOMMERCE_PROJECT_ID, kb_id),
            )
            # 旧商品评价库保留，项目改用新的完整业务库，避免重复检索同一批商品评价。
            db.execute("DELETE FROM project_knowledge_bases WHERE project_id = ? AND knowledge_base_id IN (SELECT id FROM knowledge_bases WHERE id = 'ecommerce-platform' AND name = '电商商品与评价') AND knowledge_base_id != ?", (ECOMMERCE_PROJECT_ID, kb_id))
            db.execute(
                "INSERT INTO documents (id, knowledge_base_id, filename, stored_path, chunk_count, vector_ids, uploaded_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (document_id, kb_id, ECOMMERCE_EXPORT_FILENAME, str(stored_path), chunk_count, json.dumps(vector_ids), stamp),
            )
            for old_doc in old_docs:
                db.execute("DELETE FROM documents WHERE id = ?", (old_doc["id"],))
    except Exception as exc:
        try:
            if vector_ids:
                await asyncio.to_thread(remove_document_vectors, kb_id, vector_ids)
            stored_path.unlink(missing_ok=True)
        except Exception:
            logger.exception("清理失败的电商 RAG 同步文件时发生错误")
        if isinstance(exc, HTTPException):
            raise
        logger.exception("电商资料同步到 RAG 失败")
        raise HTTPException(status_code=503, detail="电商资料索引失败，请检查 RAG 的 bge-m3 服务") from exc

    cleanup_warning = False
    for old_doc in old_docs:
        try:
            await asyncio.to_thread(
                remove_document_vectors,
                kb_id,
                parse_json(old_doc["vector_ids"]),
            )
            Path(old_doc["stored_path"]).unlink(missing_ok=True)
        except Exception:
            cleanup_warning = True
            logger.exception("清理旧电商 RAG 分片失败：%s", old_doc["id"])

    return {
        "knowledge_base_id": kb_id,
        "knowledge_base_name": ECOMMERCE_KB_NAME,
        "project_name": "电商分析平台",
        "record_count": len(payload.records),
        "chunk_count": chunk_count,
        "collection_size": get_vector_store(kb_id)._collection.count(),
        "cleanup_warning": cleanup_warning,
    }


@app.get("/api/status")
async def status():
    settings = app.state.answer_model_settings
    chat_model = settings.local_model if settings.mode == "local" else "Agent API 模型"
    try:
        response = await app.state.ollama_status_client.get(f"{OLLAMA_BASE_URL}/api/tags")
        response.raise_for_status()
        tags = response.json().get("models", [])
        names = [model.get("name", "") for model in tags]
        return {
            "ollama_connected": True,
            "models": names,
            "chat_model": chat_model,
            "embedding_model": OLLAMA_EMBED_MODEL,
            "chat_model_ready": settings.mode == "api" or any(name == settings.local_model or name.startswith(settings.local_model + ":") for name in names),
            "embedding_model_ready": any(name == OLLAMA_EMBED_MODEL or name.startswith(OLLAMA_EMBED_MODEL + ":") for name in names),
            "answer_mode": settings.mode,
        }
    except Exception:
        return {
            "ollama_connected": False,
            "models": [],
            "chat_model": chat_model,
            "embedding_model": OLLAMA_EMBED_MODEL,
            "chat_model_ready": settings.mode == "api",
            "embedding_model_ready": False,
            "answer_mode": settings.mode,
        }


class AnswerModelUpdate(BaseModel):
    mode: str = Field(pattern="^(local|api)$")
    local_model: str = Field(min_length=1, max_length=128)
    agent_profile_id: str = Field(default="", max_length=32)


class AssistantAnswer(BaseModel):
    content: str = Field(min_length=1, max_length=60000)
    sources: list[dict] = Field(default_factory=list, max_length=16)


@app.get("/api/model-settings")
def get_answer_model_settings():
    return app.state.answer_model_settings.public()


@app.put("/api/model-settings")
async def update_answer_model_settings(payload: AnswerModelUpdate, request: Request):
    try:
        settings = validate_settings(AnswerModelSettings(
            mode=payload.mode,
            local_model=payload.local_model,
            agent_profile_id=payload.agent_profile_id,
        ))
        save_settings(settings)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    app.state.answer_model_settings = settings
    app.state.rag_graph = create_rag_graph(settings)
    return settings.public()


@app.get("/api/projects")
def list_projects():
    with connect() as db:
        rows = db.execute("SELECT * FROM projects ORDER BY created_at").fetchall()
        return [project_dict(row, db) for row in rows]


@app.post("/api/projects")
def create_project(payload: ProjectCreate):
    kb_ids = ensure_knowledge_bases_exist(payload.knowledge_base_ids)
    project_id = new_id()
    stamp = now_iso()
    with connect() as db:
        db.execute("INSERT INTO projects (id, name, created_at) VALUES (?, ?, ?)", (project_id, payload.name, stamp))
        db.executemany(
            "INSERT INTO project_knowledge_bases (project_id, knowledge_base_id) VALUES (?, ?)",
            [(project_id, kb_id) for kb_id in kb_ids],
        )
        row = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return project_dict(row, db)


@app.patch("/api/projects/{project_id}")
def update_project(project_id: str, payload: ProjectUpdate):
    with connect() as db:
        row = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="项目不存在")
        if payload.name is not None:
            name = payload.name.strip()
            if not name:
                raise HTTPException(status_code=422, detail="项目名称不能为空")
            db.execute("UPDATE projects SET name = ? WHERE id = ?", (name, project_id))
        if payload.knowledge_base_ids is not None:
            kb_ids = ensure_knowledge_bases_exist(payload.knowledge_base_ids)
            db.execute("DELETE FROM project_knowledge_bases WHERE project_id = ?", (project_id,))
            db.executemany(
                "INSERT INTO project_knowledge_bases (project_id, knowledge_base_id) VALUES (?, ?)",
                [(project_id, kb_id) for kb_id in kb_ids],
            )
        row = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return project_dict(row, db)


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    with connect() as db:
        if not db.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone():
            raise HTTPException(status_code=404, detail="项目不存在")
        db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    return {"deleted": True}


@app.get("/api/knowledge-bases")
def list_knowledge_bases():
    with connect() as db:
        rows = db.execute(
            """
            SELECT kb.*, COUNT(d.id) AS document_count
            FROM knowledge_bases kb LEFT JOIN documents d ON d.knowledge_base_id = kb.id
            WHERE kb.access_level != 'staff' OR ?
            GROUP BY kb.id ORDER BY kb.created_at
            """, (int(_private_access.get()),)
        ).fetchall()
        return [dict(row) for row in rows]


@app.post("/api/knowledge-bases")
def create_knowledge_base(payload: KnowledgeBaseCreate):
    kb_id = new_id()
    stamp = now_iso()
    with connect() as db:
        db.execute(
            "INSERT INTO knowledge_bases (id, name, description, created_at) VALUES (?, ?, ?, ?)",
            (kb_id, payload.name, payload.description.strip(), stamp),
        )
        return dict(db.execute("SELECT * FROM knowledge_bases WHERE id = ?", (kb_id,)).fetchone())


@app.delete("/api/knowledge-bases/{knowledge_base_id}")
def delete_knowledge_base(knowledge_base_id: str):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        kb = db.execute("SELECT id FROM knowledge_bases WHERE id = ?", (knowledge_base_id,)).fetchone()
        documents = db.execute(
            "SELECT stored_path FROM documents WHERE knowledge_base_id = ?", (knowledge_base_id,)
        ).fetchall()
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        try:
            delete_knowledge_base_collection(knowledge_base_id)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="删除向量集合失败，知识库记录已保留，请重试") from exc
        chat_rows = db.execute("SELECT id, knowledge_base_ids FROM chats").fetchall()
        for chat in chat_rows:
            ids = parse_json(chat["knowledge_base_ids"])
            if knowledge_base_id in ids:
                ids.remove(knowledge_base_id)
                db.execute("UPDATE chats SET knowledge_base_ids = ? WHERE id = ?", (json.dumps(ids), chat["id"]))
        db.execute("DELETE FROM knowledge_bases WHERE id = ?", (knowledge_base_id,))
    for document in documents:
        Path(document["stored_path"]).unlink(missing_ok=True)
    return {"deleted": True}


@app.get("/api/knowledge-bases/{knowledge_base_id}/documents")
def list_documents(knowledge_base_id: str):
    ensure_knowledge_bases_exist([knowledge_base_id])
    with connect() as db:
        kb = db.execute("SELECT id FROM knowledge_bases WHERE id = ?", (knowledge_base_id,)).fetchone()
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        rows = db.execute(
            "SELECT id, knowledge_base_id, filename, chunk_count, uploaded_at FROM documents WHERE knowledge_base_id = ? ORDER BY uploaded_at DESC",
            (knowledge_base_id,),
        ).fetchall()
        return [dict(row) for row in rows]


@app.post("/api/knowledge-bases/{knowledge_base_id}/documents")
async def upload_documents(knowledge_base_id: str, files: list[UploadFile] = File(...)):
    with connect() as db:
        kb = db.execute("SELECT id FROM knowledge_bases WHERE id = ?", (knowledge_base_id,)).fetchone()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not files:
        raise HTTPException(status_code=422, detail="请选择文件")

    results = []
    for uploaded in files:
        original_name = Path(uploaded.filename or "资料").name
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=415, detail=f"{original_name} 格式不支持，请上传 PDF、DOCX、TXT、MD 或 CSV")
        content = await uploaded.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"{original_name} 超过 {MAX_UPLOAD_MB} MB 限制")

        document_id = uuid4().hex
        target_dir = UPLOAD_DIR / knowledge_base_id
        target_dir.mkdir(parents=True, exist_ok=True)
        stored_path = target_dir / f"{document_id}{suffix}"
        stored_path.write_bytes(content)
        vector_ids = []
        try:
            chunk_count, vector_ids = await asyncio.to_thread(
                index_file, knowledge_base_id, document_id, stored_path, original_name
            )
            with connect() as db:
                db.execute(
                    "INSERT INTO documents (id, knowledge_base_id, filename, stored_path, chunk_count, vector_ids, uploaded_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (document_id, knowledge_base_id, original_name, str(stored_path), chunk_count, json.dumps(vector_ids), now_iso()),
                )
        except Exception as exc:
            logger.exception("资料导入失败：%s", original_name)
            try:
                if vector_ids:
                    await asyncio.to_thread(remove_document_vectors, knowledge_base_id, vector_ids)
                stored_path.unlink(missing_ok=True)
            except Exception:
                logger.exception("清理导入失败的资料时发生错误：%s", document_id)
            message = str(exc) or "建立向量索引失败"
            if "status code: 502" in message or "status code: 503" in message:
                message = "Ollama 向量服务暂时不可用（上游 502/503），已自动重试仍失败，请稍后重试"
            raise HTTPException(status_code=503, detail=f"{original_name} 导入失败：{message}") from exc

        results.append({"id": document_id, "filename": original_name, "chunk_count": chunk_count})
    return {"uploaded": results}


@app.get("/api/knowledge-bases/{knowledge_base_id}/documents/{document_id}/chunks")
def list_chunks(knowledge_base_id: str, document_id: str,
                offset: int = Query(default=0, ge=0),
                limit: int = Query(default=20, ge=1, le=100)):
    ensure_knowledge_bases_exist([knowledge_base_id])
    with connect() as db:
        document = db.execute(
            "SELECT * FROM documents WHERE id = ? AND knowledge_base_id = ?",
            (document_id, knowledge_base_id),
        ).fetchone()
    if not document:
        raise HTTPException(status_code=404, detail="资料不属于这个知识库，或已经删除")
    vector_ids = parse_json(document["vector_ids"])
    try:
        items = read_document_chunks(
            knowledge_base_id, document_id, document["filename"], vector_ids, offset, limit
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="暂时无法读取分片，请重试") from exc
    return {"items": items, "total": len(vector_ids), "offset": offset, "limit": limit}


@app.delete("/api/knowledge-bases/{knowledge_base_id}/documents/{document_id}/chunks/{chunk_id}")
def delete_chunk(knowledge_base_id: str, document_id: str, chunk_id: str):
    with connect() as db:
        # 串行更新同一份文档的有序 ID 列表，避免并发删除造成计数丢失。
        db.execute("BEGIN IMMEDIATE")
        document = db.execute(
            "SELECT * FROM documents WHERE id = ? AND knowledge_base_id = ?",
            (document_id, knowledge_base_id),
        ).fetchone()
        if not document:
            raise HTTPException(status_code=404, detail="资料不属于这个知识库，或已经删除")
        vector_ids = parse_json(document["vector_ids"])
        if chunk_id not in vector_ids:
            raise HTTPException(status_code=404, detail="分片不属于这份文档，或已经删除")
        try:
            # Chroma 删除已缺失的 ID 也是安全的，便于中断后重试并修复计数。
            remove_document_vectors(knowledge_base_id, [chunk_id])
        except Exception as exc:
            raise HTTPException(status_code=503, detail="分片删除失败，记录已保留，请重试") from exc
        remaining = [value for value in vector_ids if value != chunk_id]
        db.execute(
            "UPDATE documents SET vector_ids = ?, chunk_count = ? WHERE id = ?",
            (json.dumps(remaining), len(remaining), document_id),
        )
    return {"deleted": True, "remaining_chunks": len(remaining)}


@app.delete("/api/knowledge-bases/{knowledge_base_id}/documents/{document_id}")
def delete_document(knowledge_base_id: str, document_id: str):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT * FROM documents WHERE id = ? AND knowledge_base_id = ?",
            (document_id, knowledge_base_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="资料不存在")
        vector_ids = parse_json(row["vector_ids"])
        stored_path = row["stored_path"]
        try:
            remove_document_vectors(knowledge_base_id, vector_ids)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="删除文档分片失败，记录已保留，请重试") from exc
        db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    Path(stored_path).unlink(missing_ok=True)
    return {"deleted": True}


@app.get("/api/projects/{project_id}/chats")
def list_chats(project_id: str, request: Request):
    with connect() as db:
        if not db.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone():
            raise HTTPException(status_code=404, detail="项目不存在")
        rows = db.execute(
            "SELECT * FROM chats WHERE project_id = ? ORDER BY updated_at DESC",
            (project_id,),
        ).fetchall()
        prefix = guest_chat_prefix(request)
        if prefix:
            rows = [row for row in rows if row["id"].startswith(prefix)]
        return [chat_dict(db, row) for row in rows]


@app.post("/api/projects/{project_id}/chats")
def create_chat(project_id: str, payload: ChatCreate, request: Request):
    with connect() as db:
        if not db.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone():
            raise HTTPException(status_code=404, detail="项目不存在")
        scope_mode = payload.scope_mode
        if payload.knowledge_base_ids is not None and "scope_mode" not in payload.model_fields_set:
            scope_mode = "custom"  # 兼容旧版明确提交资料范围的客户端。
        if scope_mode == "project":
            rows = db.execute(
                "SELECT knowledge_base_id FROM project_knowledge_bases WHERE project_id = ? ORDER BY rowid",
                (project_id,),
            ).fetchall()
            kb_ids = [row["knowledge_base_id"] for row in rows]
        else:
            kb_ids = ensure_knowledge_bases_exist(payload.knowledge_base_ids or [])
        chat_id = guest_chat_prefix(request) + new_id()
        stamp = now_iso()
        db.execute(
            "INSERT INTO chats (id, project_id, title, knowledge_base_ids, scope_mode, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (chat_id, project_id, "新对话", json.dumps(kb_ids), scope_mode, stamp, stamp),
        )
        return {"id": chat_id, "project_id": project_id, "title": "新对话", "knowledge_base_ids": kb_ids, "scope_mode": scope_mode, "created_at": stamp, "updated_at": stamp}


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str, request: Request):
    chat_id = accessible_chat_id(chat_id, request)
    with connect() as db:
        chat = db.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
        if not chat:
            raise HTTPException(status_code=404, detail="对话不存在")
        messages = db.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY id", (chat_id,)).fetchall()
        return {
            **chat_dict(db, chat),
            "messages": [serialize_message(row) for row in messages],
        }


@app.patch("/api/chats/{chat_id}")
def rename_chat(chat_id: str, payload: ChatUpdate, request: Request):
    chat_id = accessible_chat_id(chat_id, request)
    with connect() as db:
        if not db.execute("SELECT id FROM chats WHERE id = ?", (chat_id,)).fetchone():
            raise HTTPException(status_code=404, detail="对话不存在")
        updates = []
        values = []
        if payload.title is not None:
            title = payload.title.strip()
            if not title:
                raise HTTPException(status_code=422, detail="对话名称不能为空")
            updates.append("title = ?")
            values.append(title)
        if payload.knowledge_base_ids is not None:
            kb_ids = ensure_knowledge_bases_exist(payload.knowledge_base_ids)
            updates.append("knowledge_base_ids = ?")
            values.append(json.dumps(kb_ids))
        mode = payload.scope_mode
        if mode is None and payload.knowledge_base_ids is not None:
            mode = "custom"
        if mode is not None:
            updates.append("scope_mode = ?")
            values.append(mode)
        if not updates:
            raise HTTPException(status_code=422, detail="没有要更新的内容")
        updates.append("updated_at = ?")
        values.extend([now_iso(), chat_id])
        db.execute(f"UPDATE chats SET {', '.join(updates)} WHERE id = ?", values)
        row = db.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
        return chat_dict(db, row)


@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: str, request: Request):
    chat_id = accessible_chat_id(chat_id, request)
    with connect() as db:
        if not db.execute("SELECT id FROM chats WHERE id = ?", (chat_id,)).fetchone():
            raise HTTPException(status_code=404, detail="对话不存在")
        db.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    return {"deleted": True}


@app.post("/api/chats/{chat_id}/retrieve")
async def retrieve_for_browser_model(chat_id: str, payload: MessageCreate, request: Request):
    """保存用户问题并只返回检索资料；回答模型由浏览器直接调用。"""
    chat_id = accessible_chat_id(chat_id, request)
    question = payload.content.strip()
    with connect() as db:
        chat = db.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
        if not chat:
            raise HTTPException(status_code=404, detail="对话不存在")
        if payload.knowledge_base_ids is not None:
            kb_ids = ensure_knowledge_bases_exist(payload.knowledge_base_ids)
            db.execute(
                "UPDATE chats SET knowledge_base_ids = ?, scope_mode = 'custom' WHERE id = ?",
                (json.dumps(kb_ids), chat_id),
            )
            chat = db.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
        kb_ids = effective_knowledge_bases(db, chat)
        history_rows = db.execute(
            "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT 12",
            (chat_id,),
        ).fetchall()
        history = [dict(row) for row in reversed(history_rows)]
        if not db.execute("SELECT id FROM projects WHERE id = ?", (chat["project_id"],)).fetchone():
            raise HTTPException(status_code=404, detail="项目不存在")
        names_by_id = {}
        if kb_ids:
            placeholders = ",".join("?" for _ in kb_ids)
            rows = db.execute(
                f"SELECT id, name FROM knowledge_bases WHERE id IN ({placeholders})", kb_ids
            ).fetchall()
            names_by_id = {row["id"]: row["name"] for row in rows}
        stamp = now_iso()
        db.execute(
            "UPDATE chats SET knowledge_base_ids = ?, updated_at = ? WHERE id = ?",
            (json.dumps(kb_ids), stamp, chat_id),
        )
        db.execute(
            "INSERT INTO messages (chat_id, role, content, sources, created_at) VALUES (?, 'user', ?, '[]', ?)",
            (chat_id, question, stamp),
        )
        if chat["title"] == "新对话":
            title = re.sub(r"\s+", " ", question)[:28].strip() or "新对话"
            db.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))

    try:
        contexts = await asyncio.to_thread(retrieve_contexts, question, kb_ids, names_by_id)
    except Exception as exc:
        logger.exception("知识库检索失败")
        raise HTTPException(status_code=503, detail="知识库检索失败，请检查向量服务") from exc
    sources = [
        {
            "filename": item.get("filename", "资料"),
            "page": item.get("page"),
            "knowledge_base_name": item.get("knowledge_base_name", "知识库"),
            "chunk_id": item.get("chunk_id"),
            "chunk_index": item.get("chunk_index"),
            "score": round(float(item.get("score", 0)), 3),
            "preview": item.get("content", "")[:220],
        }
        for item in contexts
    ]
    return JSONResponse(
        {
            "history": history,
            "contexts": contexts,
            "sources": sources,
            "knowledge_bases": [{"id": item, "name": names_by_id[item]} for item in kb_ids],
        },
        headers={"Cache-Control": "no-store"},
    )


@app.post("/api/chats/{chat_id}/answer")
def save_browser_generated_answer(chat_id: str, payload: AssistantAnswer, request: Request):
    chat_id = accessible_chat_id(chat_id, request)
    with connect() as db:
        if not db.execute("SELECT id FROM chats WHERE id = ?", (chat_id,)).fetchone():
            raise HTTPException(status_code=404, detail="对话不存在")
        stamp = now_iso()
        db.execute(
            "INSERT INTO messages (chat_id, role, content, sources, created_at) VALUES (?, 'assistant', ?, ?, ?)",
            (chat_id, payload.content, json.dumps(payload.sources, ensure_ascii=False), stamp),
        )
        db.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (stamp, chat_id))
    return {"saved": True}


@app.post("/api/chats/{chat_id}/messages/stream")
async def stream_message(chat_id: str, payload: MessageCreate):
    question = payload.content.strip()
    with connect() as db:
        chat = db.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
        if not chat:
            raise HTTPException(status_code=404, detail="对话不存在")
        if payload.knowledge_base_ids is not None:
            kb_ids = ensure_knowledge_bases_exist(payload.knowledge_base_ids)
            db.execute(
                "UPDATE chats SET knowledge_base_ids = ?, scope_mode = 'custom' WHERE id = ?",
                (json.dumps(kb_ids), chat_id),
            )
            chat = db.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
        kb_ids = effective_knowledge_bases(db, chat)
        scope_mode = chat["scope_mode"]
        db.execute(
            "UPDATE chats SET knowledge_base_ids = ?, updated_at = ? WHERE id = ?",
            (json.dumps(kb_ids), now_iso(), chat_id),
        )
        db.execute(
            "INSERT INTO messages (chat_id, role, content, sources, created_at) VALUES (?, 'user', ?, '[]', ?)",
            (chat_id, question, now_iso()),
        )
        if chat["title"] == "新对话":
            title = re.sub(r"\s+", " ", question)[:28].strip() or "新对话"
            db.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
        history_rows = db.execute(
            "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT 12", (chat_id,)
        ).fetchall()
        history = [dict(row) for row in reversed(history_rows)][:-1]
        if not db.execute("SELECT id FROM projects WHERE id = ?", (chat["project_id"],)).fetchone():
            raise HTTPException(status_code=404, detail="项目不存在")
        if kb_ids:
            placeholders = ",".join("?" for _ in kb_ids)
            rows = db.execute(
                f"SELECT id, name FROM knowledge_bases WHERE id IN ({placeholders})", kb_ids
            ).fetchall()
            names_by_id = {row["id"]: row["name"] for row in rows}
        else:
            names_by_id = {}

    async def generate_events():
        answer_parts = []
        retrieved_contexts = []
        final_answer = ""
        try:
            yield sse({
                "type": "status", "stage": "retrieving", "scope_mode": scope_mode,
                "knowledge_bases": [{"id": kb_id, "name": names_by_id[kb_id]} for kb_id in kb_ids],
            })
            graph = app.state.rag_graph
            async for event in graph.astream_events(
                {
                    "question": question,
                    "knowledge_base_ids": kb_ids,
                    "knowledge_base_names": names_by_id,
                    "history": history,
                },
                version="v2",
            ):
                if event.get("event") == "on_custom_event" and event.get("name") == "rag_answer_token":
                    token = event.get("data", {}).get("content", "")
                    if token:
                        answer_parts.append(token)
                        yield sse({"type": "token", "content": token})
                if event.get("event") == "on_chat_model_stream" and "rag_answer" in event.get("tags", []):
                    chunk = event.get("data", {}).get("chunk")
                    content = getattr(chunk, "content", "")
                    if isinstance(content, str) and content:
                        answer_parts.append(content)
                        yield sse({"type": "token", "content": content})
                    elif isinstance(content, list):
                        for block in content:
                            token = block.get("text", "") if isinstance(block, dict) else ""
                            if token:
                                answer_parts.append(token)
                                yield sse({"type": "token", "content": token})

                output = event.get("data", {}).get("output")
                if isinstance(output, dict) and isinstance(output.get("contexts"), list):
                    retrieved_contexts = output["contexts"]
                if isinstance(output, dict) and isinstance(output.get("answer"), str):
                    final_answer = output["answer"]

            answer = (final_answer or "".join(answer_parts)).strip()
            if not answer:
                answer = "回答生成失败，请检查当前模型服务和配置后重试。"
            if not answer_parts:
                # 空库等直接返回的节点没有模型 token，也要即时显示答案。
                yield sse({"type": "token", "content": answer})

            sources = [
                {
                    "filename": item.get("filename", "资料"),
                    "page": item.get("page"),
                    "knowledge_base_name": item.get("knowledge_base_name", "知识库"),
                    "chunk_id": item.get("chunk_id"),
                    "chunk_index": item.get("chunk_index"),
                    "score": round(float(item.get("score", 0)), 3),
                    "preview": item.get("content", "")[:220],
                }
                for item in retrieved_contexts
            ]
            with connect() as db:
                db.execute(
                    "INSERT INTO messages (chat_id, role, content, sources, created_at) VALUES (?, 'assistant', ?, ?, ?)",
                    (chat_id, answer, json.dumps(sources, ensure_ascii=False), now_iso()),
                )
                db.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now_iso(), chat_id))
            yield sse({"type": "sources", "sources": sources})
            yield sse({"type": "done", "answer": answer, "sources": sources})
        except Exception as exc:
            message = str(exc) or "未知错误"
            if isinstance(exc, (httpx.ConnectError, ConnectionError)) or "connection" in message.lower():
                if app.state.answer_model_settings.mode == "api":
                    message = "连接不到所选 API 模型。请检查接口地址、网络和 API Key。"
                else:
                    message = f"连接不到 Ollama（{OLLAMA_BASE_URL}）。请先启动 Ollama，并确认已下载聊天模型和 bge-m3。"
            yield sse({"type": "error", "message": message})

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
