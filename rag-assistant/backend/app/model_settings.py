"""RAG chooses an Agent API profile without copying its credentials."""

import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .config import DATA_DIR, OLLAMA_CHAT_MODEL

SETTINGS_PATH = DATA_DIR / "answer_model.json"
AGENT_PROFILES_PATH = Path(os.getenv(
    "AGENT_MODEL_PROFILES_PATH",
    str(Path(__file__).resolve().parents[3] / "yugan-agent" / ".yugan" / "model_profiles.json"),
))
MODEL_PATTERN = re.compile(r"^[A-Za-z0-9._:/-]{1,128}$")
PROFILE_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")


@dataclass(frozen=True)
class AgentApiProfile:
    id: str
    name: str
    endpoint: str
    model: str
    api_key: str
    protocol: str

    def public(self) -> dict:
        return {"id": self.id, "name": self.name, "model": self.model, "protocol": self.protocol}


@dataclass(frozen=True)
class AnswerModelSettings:
    mode: str = "local"
    local_model: str = OLLAMA_CHAT_MODEL
    agent_profile_id: str = ""

    def public(self) -> dict:
        return {
            "mode": self.mode,
            "local_model": self.local_model,
            "agent_profile_id": self.agent_profile_id,
        }


def list_agent_api_profiles(path: Path = AGENT_PROFILES_PATH) -> list[AgentApiProfile]:
    if not path.exists():
        return []
    try:
        if path.stat().st_size > 2_000_000:
            raise ValueError("Agent 模型配置文件过大")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("version") != 1 or not isinstance(data.get("profiles"), list):
            raise ValueError("Agent 模型配置格式无效")
    except (OSError, ValueError) as exc:
        raise ValueError("Agent 模型配置无法读取") from exc

    profiles = []
    for item in data["profiles"]:
        if not isinstance(item, dict):
            continue
        profile_id = item.get("id")
        endpoint = item.get("endpoint")
        model = item.get("model")
        key = item.get("api_key")
        if not all(isinstance(value, str) for value in (profile_id, endpoint, model, key)):
            continue
        parsed = urlsplit(endpoint)
        if (
            not PROFILE_ID_PATTERN.fullmatch(profile_id)
            or not MODEL_PATTERN.fullmatch(model)
            or not key
            or parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
        ):
            continue
        host = parsed.hostname.lower()
        protocol = "anthropic" if host == "api.anthropic.com" else (
            "responses" if host == "api.openai.com" else "chat_completions"
        )
        name = item.get("name")
        profiles.append(AgentApiProfile(
            id=profile_id,
            name=name[:80] if isinstance(name, str) and name else model,
            endpoint=endpoint.rstrip("/"),
            model=model,
            api_key=key,
            protocol=protocol,
        ))
    return profiles


def get_agent_api_profile(profile_id: str, path: Path = AGENT_PROFILES_PATH) -> AgentApiProfile:
    for profile in list_agent_api_profiles(path):
        if profile.id == profile_id:
            return profile
    raise ValueError("选用的 Agent API 模型已不存在；请在 RAG 左下角重新选择")


def active_agent_api_profile_id(path: Path = AGENT_PROFILES_PATH) -> str:
    if not path.exists():
        return ""
    try:
        active_id = json.loads(path.read_text(encoding="utf-8")).get("active_id")
    except (OSError, ValueError):
        return ""
    return active_id if any(profile.id == active_id for profile in list_agent_api_profiles(path)) else ""


def validate_settings(settings: AnswerModelSettings) -> AnswerModelSettings:
    if settings.mode not in {"local", "api"}:
        raise ValueError("模型来源必须是本地 Ollama 或 Agent API")
    if not MODEL_PATTERN.fullmatch(settings.local_model):
        raise ValueError("请输入有效的本地模型 ID")
    if settings.mode == "api" and not PROFILE_ID_PATTERN.fullmatch(settings.agent_profile_id):
        raise ValueError("请选择 Agent 中已保存的 API 模型")
    return settings


def load_settings(
    path: Path = SETTINGS_PATH,
    profiles_path: Path = AGENT_PROFILES_PATH,
) -> AnswerModelSettings:
    if not path.exists():
        return AnswerModelSettings()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") == 2:
        return validate_settings(AnswerModelSettings(**{
            key: data.get(key, getattr(AnswerModelSettings(), key))
            for key in AnswerModelSettings.__dataclass_fields__
        }))
    if data.get("version") != 1:
        raise ValueError("RAG 模型配置文件版本无效")
    selected_id = ""
    if data.get("mode") == "api":
        legacy_endpoint = str(data.get("api_base_url", "")).rstrip("/")
        for profile in list_agent_api_profiles(profiles_path):
            matches_endpoint = profile.endpoint == legacy_endpoint or (
                profile.endpoint == "https://api.deepseek.com"
                and legacy_endpoint == "https://api.deepseek.com/v1"
            )
            if profile.model == data.get("api_model") and matches_endpoint:
                selected_id = profile.id
                break
    return validate_settings(AnswerModelSettings(
        mode="api" if selected_id else "local",
        local_model=data.get("local_model", OLLAMA_CHAT_MODEL),
        agent_profile_id=selected_id,
    ))


def save_settings(settings: AnswerModelSettings, path: Path = SETTINGS_PATH) -> None:
    validate_settings(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="answer-model.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump({"version": 2, **settings.public()}, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
