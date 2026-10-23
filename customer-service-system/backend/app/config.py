from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # 后端项目的根路径


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_EXPIRE_HOURS: int = 24
    JWT_ALGORITHM: str = "HS256"
    # 大模型（OpenAI 兼容：DeepSeek / Qwen / 硅基流动等）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com/v1"
    LLM_MODEL: str = "deepseek-chat"
    LLM_TIMEOUT: float = 60.0
    # 大模型失败重试次数：SDK 默认 2，配合 60s 超时最坏会等待 180s；
    # 交互式对话场景取 1，避免异常/越权问题让用户等太久
    LLM_MAX_RETRIES: int = 1

    # 向量模型（OpenAI 兼容 embeddings；课程默认百炼 qwen3.7-text-embedding-flash，
    # 与 LLM 共用同一个百炼 Key，EMBEDDING_API_KEY 留空即回退用 LLM_API_KEY）
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    EMBEDDING_MODEL: str = "qwen3.7-text-embedding-flash"
    EMBEDDING_TIMEOUT: float = 60.0

    # 独立 RAG 知识库（语义检索和电商数据同步都由该服务处理）
    RAG_BASE_URL: str = "http://127.0.0.1:8000"
    RAG_ECOM_KNOWLEDGE_BASE_ID: str = "ecommerce-analysis-platform"
    RAG_SYNC_TOKEN: str = ""
    RAG_SEARCH_TIMEOUT_SECONDS: float = 30.0
    RAG_SYNC_TIMEOUT_SECONDS: float = 600.0

    # Chroma 本地持久化目录（相对 backend 根目录）
    CHROMA_PERSIST_DIR: str = "data/chroma"
    CHROMA_COLLECTION: str = "ecom_docs"

    # 语义检索“相关度兜底”阈值：证据里最小的距离仍大于它就认为与业务数据无关。
    # Chroma 返回的距离 = 1 - 余弦相似度（越小越相关）。
    # 当前向量模型（百炼 qwen3.7-text-embedding-flash）实测：业务问题 ≤0.43，
    # 无关问题 ≥0.54，取 0.50 分界；换向量模型后需要重新标定。
    SEMANTIC_RELEVANCE_MAX_DISTANCE: float = 0.50

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8"
    )


settings = Settings()

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100M


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
}

# Chroma 数据目录：绝对路径，方便 PersistentClient 使用
CHROMA_DIR = BASE_DIR / settings.CHROMA_PERSIST_DIR
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
