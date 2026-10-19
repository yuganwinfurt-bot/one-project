"""集中配置；环境变量覆盖项目目录的 .env。"""

from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="YUGAN_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    provider: Literal["mock", "openai", "compatible", "anthropic"] = "mock"
    model: str = "demo"
    api_key: SecretStr = SecretStr("")
    base_url: str | None = None
    server_ollama_url: str = Field(default="http://127.0.0.1:11434", max_length=500)
    rag_web_origin: str = Field(default="http://127.0.0.1:4173", max_length=500)
    ecommerce_web_origin: str = Field(default="http://127.0.0.1:5173", max_length=500)
    thinking: Literal["auto", "enabled", "disabled"] = "auto"
    workspace: Path = Path("workspace")
    database: Path = Path(".yugan/memory.db")
    log_file: Path = Path(".yugan/events.jsonl")
    max_steps: int = Field(default=8, ge=1, le=50)
    max_tool_calls: int = Field(default=24, ge=1, le=100)
    context_chars: int = Field(default=32000, ge=2048, le=500000)
    tool_timeout: float = Field(default=10, gt=0, le=300)
    model_timeout: float = Field(default=60, gt=0, le=600)
    max_output_tokens: int = Field(default=2048, ge=128, le=32768)
    allowed_effects: list[str] = Field(default_factory=list)
    http_endpoints: dict[str, str] = Field(default_factory=dict)
    api_token: SecretStr = SecretStr("")
    admin_username: str = ""
    admin_password_hash: SecretStr = SecretStr("")
    auth_signing_secret: SecretStr = SecretStr("")

    @model_validator(mode="after")
    def check_provider(self):
        ollama_url = urlsplit(self.server_ollama_url)
        if (
            ollama_url.scheme not in {"http", "https"}
            or not ollama_url.hostname
            or ollama_url.username
            or ollama_url.password
            or ollama_url.query
            or ollama_url.fragment
        ):
            raise ValueError("YUGAN_SERVER_OLLAMA_URL 必须是有效的 HTTP(S) 服务地址")
        rag_origin = urlsplit(self.rag_web_origin)
        if (
            rag_origin.scheme not in {"http", "https"}
            or not rag_origin.hostname
            or rag_origin.username
            or rag_origin.password
            or rag_origin.path not in {"", "/"}
            or rag_origin.query
            or rag_origin.fragment
        ):
            raise ValueError("YUGAN_RAG_WEB_ORIGIN 必须是有效的网页源地址")
        ecommerce_origin = urlsplit(self.ecommerce_web_origin)
        if (
            ecommerce_origin.scheme not in {"http", "https"}
            or not ecommerce_origin.hostname
            or ecommerce_origin.username
            or ecommerce_origin.password
            or ecommerce_origin.path not in {"", "/"}
            or ecommerce_origin.query
            or ecommerce_origin.fragment
        ):
            raise ValueError("YUGAN_ECOMMERCE_WEB_ORIGIN 必须是有效的网页源地址")
        if self.provider != "mock":
            if not self.model.strip() or self.model == "demo":
                raise ValueError("请把 YUGAN_MODEL 设置为供应商实际支持的模型 ID")
        if self.provider == "compatible" and not self.base_url:
            raise ValueError("compatible 模式需要配置 YUGAN_BASE_URL")
        return self
