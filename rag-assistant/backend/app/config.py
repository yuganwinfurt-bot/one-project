import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
load_dotenv(BACKEND_DIR / ".env")

DATA_DIR = Path(os.getenv("RAG_DATA_DIR", str(BACKEND_DIR / "storage"))).expanduser().resolve()
UPLOAD_DIR = DATA_DIR / "uploads"
VECTOR_DIR = DATA_DIR / "vectors"
DB_PATH = DATA_DIR / "assistant.sqlite3"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_CLIENT_KWARGS = (
    {"trust_env": False}
    if urlparse(OLLAMA_BASE_URL).hostname in {"127.0.0.1", "localhost", "::1"}
    else {}
)
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen3.5:9b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "bge-m3")
RAG_TOP_K = max(1, min(int(os.getenv("RAG_TOP_K", "4")), 12))
RAG_MIN_RELEVANCE = max(0.0, min(float(os.getenv("RAG_MIN_RELEVANCE", "0.25")), 1.0))
MAX_UPLOAD_MB = max(1, int(os.getenv("MAX_UPLOAD_MB", "30")))

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)
