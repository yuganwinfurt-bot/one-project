"""In-memory selected-model relay for the local commerce customer service."""
import ipaddress
import secrets
from urllib.parse import urlsplit
import httpx
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel, Field, SecretStr


class ActiveSupportModel(BaseModel):
    model: str = Field(default="", max_length=200)
    name: str = Field(default="", max_length=200)
    endpoint: str = Field(default="", max_length=1000)
    mode: str = Field(default="api", max_length=30)
    provider: str = Field(default="compatible", max_length=40)
    vendor: str = Field(default="", max_length=60)
    api_key: SecretStr = SecretStr("")


class SupportCompletion(BaseModel):
    messages: list[dict] = Field(min_length=1, max_length=40)
    max_tokens: int = Field(default=1500, ge=100, le=4000)


def _local(request):
    try:
        return ipaddress.ip_address(request.client.host).is_loopback and not request.headers.get("x-forwarded-for") and not request.headers.get("x-real-ip")
    except (ValueError, AttributeError):
        return False


def install_support_model_routes(app, settings, auth_manager, authorize):
    app.state.support_model = None

    @app.post("/api/support-model/active", dependencies=[Depends(authorize)])
    async def select_support_model(body: ActiveSupportModel, request: Request):
        if request.headers.get("origin") not in {None, str(request.base_url).rstrip("/")}:
            raise HTTPException(403, "请在Agent控制台选择共享客服模型")
        if not _local(request) and auth_manager.role(request) != "admin":
            raise HTTPException(403, "仅本机或管理员可设置客服模型")
        if not body.model:
            app.state.support_model = None
            return {"available": False}
        if body.mode != "server":
            url = urlsplit(body.endpoint)
            if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
                raise HTTPException(422, "模型接口地址无效")
        # No profile or credential is written to disk or returned to buyers.
        app.state.support_model = {"model": body.model, "name": body.name or body.model, "endpoint": body.endpoint,
                                   "mode": body.mode, "provider": body.provider, "vendor": body.vendor,
                                   "api_key": body.api_key.get_secret_value()}
        return {"available": True, "name": body.name or body.model, "model": body.model}

    @app.get("/api/support-model/status")
    async def support_model_status():
        profile = app.state.support_model
        return {"available": bool(profile), "name": profile["name"] if profile else None}

    @app.post("/api/support-model/completions")
    async def complete_support_message(body: SupportCompletion, request: Request):
        token = settings.support_service_token.get_secret_value()
        if not _local(request) or not token or not secrets.compare_digest(token, request.headers.get("x-support-token", "")):
            raise HTTPException(403, "未授权的客服模型请求")
        profile = app.state.support_model
        if not profile:
            raise HTTPException(503, "请在Agent控制台打开并选择客服使用的模型")
        if any(m.get("role") not in {"system", "user", "assistant"} or not isinstance(m.get("content"), str) for m in body.messages):
            raise HTTPException(422, "模型消息格式无效")
        anthropic = profile["provider"] == "anthropic" or profile["vendor"] == "Claude"
        endpoint = (settings.server_ollama_url.rstrip('/') + '/v1') if profile["mode"] == "server" else profile["endpoint"].rstrip('/')
        headers = {"Content-Type": "application/json"}
        if anthropic:
            address = (endpoint if endpoint.endswith('/v1') else endpoint + '/v1') + '/messages'
            headers.update({"x-api-key": profile["api_key"], "anthropic-version": "2023-06-01"})
            payload = {"model": profile["model"], "max_tokens": body.max_tokens,
                       "system": '\n\n'.join(m['content'] for m in body.messages if m['role'] == 'system'),
                       "messages": [m for m in body.messages if m['role'] != 'system']}
        else:
            address = endpoint + '/chat/completions'
            if profile["mode"] not in {"local", "server"}:
                headers["Authorization"] = "Bearer " + profile["api_key"]
            payload = {"model": profile["model"], "messages": body.messages, "max_tokens": body.max_tokens, "stream": False}
        try:
            async with httpx.AsyncClient(timeout=110, trust_env=False) as client:
                response = await client.post(address, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = ''.join(part.get('text', '') for part in data.get('content', []) if part.get('type') == 'text') if anthropic else data['choices'][0]['message']['content']
            if not isinstance(content, str) or not content.strip():
                raise ValueError('empty reply')
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
            raise HTTPException(502, "当前Agent模型暂时无法回复，请检查控制台配置") from None
        return {"content": content.strip(), "model_name": profile["name"]}
