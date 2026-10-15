"""在本机保存模型配置；不记录或返回 API Key。"""

import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4


@dataclass(frozen=True)
class ModelTarget:
    vendor: str
    provider: str
    model: str
    base_url: str
    thinking: str = "auto"


@dataclass(frozen=True)
class ModelProfile:
    id: str
    name: str
    endpoint: str
    model: str
    api_key: str

    @property
    def target(self) -> ModelTarget:
        return resolve_target(self.endpoint, self.model)

    def public(self) -> dict:
        target = self.target
        return {
            "id": self.id,
            "name": self.name,
            "endpoint": target.base_url,
            "model": target.model,
            "vendor": target.vendor,
            "provider": target.provider,
            "mode": "local" if target.vendor == "Ollama" else "api",
            "effort_supported": target.vendor in {"DeepSeek", "Claude"}
            or (target.vendor == "Kimi" and target.model == "kimi-k3")
            or (
                target.provider == "openai" and target.model.startswith(("gpt-5", "o1", "o3", "o4"))
            ),
        }


def new_profile(name: str, key: str, target: ModelTarget) -> ModelProfile:
    label = name.strip() or f"{target.vendor} · {target.model}"
    if len(label) > 80 or any(char in label for char in "\r\n"):
        raise ValueError("模型配置名称不能超过 80 字，也不能换行")
    if target.vendor == "Ollama":
        key = "ollama"
    if not key.strip() or any(char in key for char in "\r\n"):
        raise ValueError("请输入有效的 API Key")
    return ModelProfile(uuid4().hex, label, target.base_url, target.model, key.strip())


def load_model_profiles(path: Path) -> tuple[str | None, list[ModelProfile]]:
    if not path.exists():
        return None, []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 1 or not isinstance(payload.get("profiles"), list):
        raise ValueError("模型配置文件格式无效")
    profiles = [ModelProfile(**item) for item in payload["profiles"]]
    if len({item.id for item in profiles}) != len(profiles):
        raise ValueError("模型配置 ID 重复")
    for item in profiles:
        if not item.id or not item.api_key or not item.name:
            raise ValueError("模型配置文件内容无效")
        resolve_target(item.endpoint, item.model)
    active_id = payload.get("active_id")
    if active_id and active_id not in {item.id for item in profiles}:
        active_id = None
    return active_id, profiles


def save_model_profiles(path: Path, active_id: str | None, profiles: list[ModelProfile]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".models.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                {
                    "version": 1,
                    "active_id": active_id,
                    "profiles": [item.__dict__ for item in profiles],
                },
                stream,
                ensure_ascii=False,
                indent=2,
            )
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def resolve_target(endpoint: str, model: str) -> ModelTarget:
    """按接口地址选择协议；仅凭 API Key 不能可靠识别供应商。"""
    endpoint = endpoint.strip() or "https://api.deepseek.com"
    parsed = urlsplit(endpoint)
    local_ollama = (
        parsed.scheme == "http"
        and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    )
    if (
        (parsed.scheme != "https" and not local_ollama)
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("API 地址必须使用 HTTPS；本地 Ollama 仅允许本机地址")
    if parsed.query or parsed.fragment:
        raise ValueError("接口地址不能包含查询参数或片段")
    host = parsed.hostname.lower()
    base_url = endpoint.rstrip("/")
    vendor, provider, default_model, thinking = "兼容接口", "compatible", "", "auto"
    if local_ollama:
        if parsed.path.rstrip("/") not in {"", "/v1"}:
            raise ValueError("本地 Ollama 地址应以 /v1 结尾")
        vendor, default_model = "Ollama", ""
        base_url = endpoint.rstrip("/")
        if parsed.path.rstrip("/") != "/v1":
            base_url += "/v1"
    elif host == "api.deepseek.com":
        vendor, default_model, thinking = "DeepSeek", "deepseek-flash", "disabled"
        if parsed.path.rstrip("/") not in {"", "/v1"}:
            raise ValueError("DeepSeek 接口地址请填写 https://api.deepseek.com")
        base_url = "https://api.deepseek.com"
    elif host == "api.openai.com":
        vendor, provider = "OpenAI", "openai"
        if parsed.path.rstrip("/") not in {"", "/v1"}:
            raise ValueError("OpenAI 接口地址请填写 https://api.openai.com/v1")
        base_url = "https://api.openai.com/v1"
    elif host == "api.anthropic.com":
        vendor, provider = "Claude", "anthropic"
        if parsed.path.rstrip("/") not in {"", "/v1"}:
            raise ValueError("Claude 接口地址请填写 https://api.anthropic.com")
        base_url = "https://api.anthropic.com"
    elif host == "api.moonshot.cn":
        vendor = "Kimi"
        if parsed.path.rstrip("/") not in {"", "/v1"}:
            raise ValueError("Kimi 接口地址请填写 https://api.moonshot.cn/v1")
        base_url = "https://api.moonshot.cn/v1"
    elif host == "open.bigmodel.cn":
        vendor = "智谱 GLM"
        if parsed.path.rstrip("/") not in {"", "/api/paas/v4"}:
            raise ValueError("智谱接口地址请填写 https://open.bigmodel.cn/api/paas/v4")
        base_url = "https://open.bigmodel.cn/api/paas/v4"
    elif host.endswith(".maas.aliyuncs.com") or host in {
        "dashscope.aliyuncs.com",
        "dashscope-intl.aliyuncs.com",
        "dashscope-us.aliyuncs.com",
        "cn-hongkong.dashscope.aliyuncs.com",
    }:
        vendor, default_model = "阿里百炼", "qwen-plus"
        if parsed.path.rstrip("/") not in {"", "/compatible-mode/v1"}:
            raise ValueError("百炼接口地址应以 /compatible-mode/v1 结尾")
        base_url = endpoint.rstrip("/")
        if not parsed.path.strip("/"):
            base_url += "/compatible-mode/v1"
    chosen_model = model.strip() or default_model
    if not re.fullmatch(r"[A-Za-z0-9._:/-]{1,128}", chosen_model):
        raise ValueError("该接口请填写有效的模型 ID")
    return ModelTarget(vendor, provider, chosen_model, base_url, thinking)


def save_model_config(path: Path, key: str, target: ModelTarget) -> None:
    """只更新模型相关项，保留 .env 中的其他设置。"""
    if (not key and target.provider != "mock") or "\n" in key or "\r" in key:
        raise ValueError("请输入有效的 API Key")
    values = {
        "YUGAN_PROVIDER": target.provider,
        "YUGAN_MODEL": target.model,
        "YUGAN_BASE_URL": target.base_url,
        "YUGAN_THINKING": target.thinking,
        "YUGAN_API_KEY": json.dumps(key),
    }
    original = path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
    output: list[str] = []
    seen: set[str] = set()
    for line in original:
        match = re.match(r"^\s*(YUGAN_[A-Z_]+)\s*=", line)
        name = match.group(1) if match else ""
        if name in values:
            if name not in seen:
                output.append(f"{name}={values[name]}")
                seen.add(name)
        else:
            output.append(line)
    for name, value in values.items():
        if name not in seen:
            output.append(f"{name}={value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".env.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write("\n".join(output) + "\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
