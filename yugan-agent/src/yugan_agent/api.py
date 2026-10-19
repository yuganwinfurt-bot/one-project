"""本机 Web 控制台与 REST API。默认只监听回环地址。"""

import asyncio
import hashlib
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
from contextlib import asynccontextmanager, nullcontext
from contextvars import ContextVar
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from urllib.parse import quote, unquote
from uuid import uuid4

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, SecretStr
from starlette.middleware.cors import CORSMiddleware

from . import __version__
from .approvals import ApprovalBroker
from .attachment_extract import MAX_ATTACHMENT_BYTES, extract_attachment_text
from .auth import AuthManager
from .config import Settings
from .custom_tools import CustomToolDefinition
from .guest_files import GuestFileStore
from .memory import SessionConflict, SQLiteMemory
from .models import ExecutionEntry, ExecutionTrace, Message
from .rag_bridge import RagBridgeError, RagSelection
from .rag_bridge import catalog as rag_catalog
from .rag_bridge import retrieve as rag_retrieve
from .runtime import build_tool_registry, create_agent
from .settings_store import (
    ModelProfile,
    load_model_profiles,
    new_profile,
    resolve_target,
    save_model_config,
    save_model_profiles,
)
from .tool_settings_store import load_tool_settings, save_tool_settings
from .workflow import Workflow
from .workspace_store import load_workspaces, save_workspaces


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    session_id: str = Field(default_factory=lambda: uuid4().hex, pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    effort: str = Field(default="auto", pattern=r"^(auto|low|medium|high|max)$")
    workspace_id: str | None = Field(default=None, max_length=64)
    rag: RagSelection = Field(default_factory=RagSelection)


class StateRequest(BaseModel):
    values: dict


class ModelSettingsRequest(BaseModel):
    api_key: SecretStr = SecretStr("")
    endpoint: str = Field(default="", max_length=500)
    model: str = Field(default="", max_length=128)
    name: str = Field(default="", max_length=80)


class ServerOllamaCompletion(BaseModel):
    model: str = Field(min_length=1, max_length=128)
    messages: list[dict] = Field(min_length=1, max_length=100)
    max_tokens: int = Field(default=1024, ge=64, le=4096)
    tools: list[dict] = Field(default_factory=list, max_length=64)


def server_chat_model_names(models: object) -> list[str]:
    if not isinstance(models, list):
        return []
    names = []
    for item in models:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            continue
        capabilities = item.get("capabilities")
        details = item.get("details")
        family = details.get("family", "") if isinstance(details, dict) else ""
        if isinstance(capabilities, list):
            if not {"completion", "tools"}.intersection(capabilities):
                continue
        elif family == "bert":
            continue
        names.append(item["name"])
    return names


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    path: str = Field(min_length=1, max_length=4096)


class SessionWorkspace(BaseModel):
    workspace_id: str = Field(min_length=1, max_length=64)


class SessionRename(BaseModel):
    title: str = Field(min_length=1, max_length=80)


class ApprovalDecision(BaseModel):
    approved: bool


class BuiltinToolToggle(BaseModel):
    enabled: bool


class BrowserTurn(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    answer: str = Field(min_length=1, max_length=60000)
    model: str = Field(default="", max_length=128)
    execution: list[ExecutionEntry] = Field(default_factory=list, max_length=100)


class BrowserRagRetrieve(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    rag: RagSelection = Field(default_factory=RagSelection)


class ToolExecutionRequest(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$")
    arguments: dict = Field(default_factory=dict)
    disabled_tools: list[str] = Field(default_factory=list, max_length=100)
    session_id: str | None = Field(default=None, pattern=r"^[a-zA-Z0-9_-]{1,64}$")


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=512)


def create_app(settings: Settings | None = None, env_path: Path | None = None) -> FastAPI:
    settings = settings or Settings()
    auth_manager = AuthManager(
        settings.admin_username,
        settings.admin_password_hash.get_secret_value(),
        settings.auth_signing_secret.get_secret_value(),
    )
    env_path = env_path or Path.cwd() / ".env"
    models_path = env_path.parent / ".yugan" / "model_profiles.json"
    tool_settings_path = env_path.parent / ".yugan" / "tools.json"
    workspace_path = env_path.parent / ".yugan" / "workspaces.json"
    legacy_workspace_path = env_path.parent / ".yugan" / "workspace.json"
    approval_broker = ApprovalBroker()
    guest_files = GuestFileStore(env_path.parent / ".yugan" / "guest_files.lock.sqlite3")
    approval_scope: ContextVar[str | None] = ContextVar("approval_scope", default=None)

    async def request_computer_approval(name: str, description: str, arguments: dict) -> bool:
        return await approval_broker.request(
            name, description, arguments, scope=approval_scope.get()
        )

    @asynccontextmanager
    async def scoped_run(request: Request):
        scope = request.headers.get("x-yugan-run-scope")
        if scope is None:
            yield
            return
        if not re.fullmatch(r"[0-9a-f]{32}", scope):
            raise HTTPException(400, "无效的任务确认标识")
        if not approval_broker.begin(scope):
            raise HTTPException(409, "该任务确认标识正在使用")
        token = approval_scope.set(scope)
        try:
            yield
        finally:
            approval_scope.reset(token)
            approval_broker.end(scope)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # New model settings are browser-only. Keep any previous local model
        # file intact until an administrator explicitly imports it to a browser.
        app.state.model_profiles = []
        app.state.active_model_id = None
        current = settings.model_copy(
            update={
                "provider": "mock",
                "model": "demo",
                "api_key": SecretStr(""),
                "base_url": None,
                "thinking": "auto",
            }
        )
        workspaces, active_workspace_id, session_workspaces = load_workspaces(
            workspace_path, legacy_workspace_path, current.workspace
        )
        app.state.workspaces = workspaces
        app.state.active_workspace_id = active_workspace_id
        app.state.session_workspaces = session_workspaces
        active_workspace = next(item for item in workspaces if item["id"] == active_workspace_id)
        current = current.model_copy(update={"workspace": Path(active_workspace["path"])})
        app.state.settings = current
        disabled_tools, custom_tools = load_tool_settings(tool_settings_path)
        app.state.disabled_builtin_tools = disabled_tools
        app.state.custom_tools = custom_tools
        app.state.agent_lock = asyncio.Lock()
        app.state.agent_users = {}
        app.state.approval_broker = approval_broker
        app.state.workspace_agents = {}
        active_agent = make_agent(current)
        app.state.agent = active_agent
        if active_agent is not None:
            app.state.workspace_agents[active_workspace_id] = active_agent
        yield
        for agent in {*app.state.workspace_agents.values(), *app.state.agent_users} - {None}:
            await agent.close()

    app = FastAPI(title="yugan-agent", version=__version__, lifespan=lifespan)
    trusted_web_origins = set()
    for configured_origin in (settings.rag_web_origin, settings.ecommerce_web_origin):
        origin = configured_origin.rstrip("/")
        trusted_web_origins.add(origin)
        if origin.startswith("http://127.0.0.1:"):
            trusted_web_origins.add(origin.replace("127.0.0.1", "localhost", 1))
        elif origin.startswith("http://localhost:"):
            trusted_web_origins.add(origin.replace("localhost", "127.0.0.1", 1))
    app.state.trusted_web_origins = trusted_web_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=sorted(trusted_web_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    app.state.auth_manager = auth_manager
    @app.get("/api/auth/status")
    async def auth_status(request: Request):
        role = auth_manager.role(request)
        subject = auth_manager.subject(request)
        if subject == "anonymous":
            guest_token, subject = auth_manager.issue_guest_session()
            response = JSONResponse({
                "role": "guest", "subject": subject, "login_configured": auth_manager.configured,
                "trusted_origins": sorted(trusted_web_origins),
            })
            auth_manager.set_cookie(response, request, guest_token)
            return response
        response = JSONResponse({
            "role": role,
            "subject": "admin" if role == "admin" else subject,
            "login_configured": auth_manager.configured,
            "trusted_origins": sorted(trusted_web_origins),
        })
        return response

    @app.post("/api/auth/login")
    async def auth_login(request: Request, body: LoginBody):
        origin = request.headers.get("origin")
        if origin and origin != str(request.base_url).rstrip("/"):
            raise HTTPException(403, "不接受跨源登录")
        token = auth_manager.authenticate(request, body.username, body.password)
        response = JSONResponse({"role": "admin"})
        auth_manager.set_cookie(response, request, token)
        return response

    @app.post("/api/auth/logout")
    async def auth_logout(request: Request):
        response = JSONResponse({"role": "guest"})
        auth_manager.set_cookie(response, request, auth_manager.issue_guest())
        return response

    def require_admin(request: Request):
        if getattr(request.state, "role", "guest") != "admin":
            raise HTTPException(403, "该操作仅限管理员")

    def make_agent(target_settings: Settings):
        agent = create_agent(target_settings, approval_callback=request_computer_approval)
        if hasattr(agent, "tools"):
            agent.tools = build_tool_registry(
                target_settings,
                approval_callback=request_computer_approval,
                disabled_builtins=app.state.disabled_builtin_tools,
                custom_tools=app.state.custom_tools,
            )
        return agent

    async def update_tool_configuration(
        request: Request,
        *,
        disabled: set[str],
        custom: list[CustomToolDefinition],
    ):
        async with app.state.agent_lock:
            if app.state.agent_users:
                raise HTTPException(409, "任务运行中，完成后再修改工具配置")
            if len(custom) > 30:
                raise HTTPException(400, "自定义工具最多保存 30 个")
            prepared = []
            for workspace_id, agent in app.state.workspace_agents.items():
                try:
                    registry = build_tool_registry(
                        agent.settings,
                        approval_callback=request_computer_approval,
                        disabled_builtins=disabled,
                        custom_tools=custom,
                    )
                except ValueError as exc:
                    raise HTTPException(400, str(exc)) from None
                prepared.append((workspace_id, agent, registry))
            try:
                await asyncio.to_thread(save_tool_settings, tool_settings_path, disabled, custom)
            except OSError:
                raise HTTPException(500, "工具配置无法保存到本机") from None
            app.state.disabled_builtin_tools = disabled
            app.state.custom_tools = custom
            for workspace_id, agent, registry in prepared:
                agent.tools = registry
                app.state.workspace_agents[workspace_id] = agent
            app.state.agent = app.state.workspace_agents.get(app.state.active_workspace_id)

    def builtin_tool_catalog():
        try:
            registry = build_tool_registry(
                app.state.settings,
                approval_callback=request_computer_approval,
                custom_tools=[],
            )
        except (OSError, ValueError):
            return []
        return registry.schemas()

    async def authorize(request: Request):
        expected = settings.api_token.get_secret_value()
        if expected:
            supplied = request.headers.get("authorization", "")
            if not secrets.compare_digest(supplied, "Bearer " + expected):
                raise HTTPException(401, "需要正确的 Bearer 令牌")
        # 阻止其他网站通过浏览器向本机 API 发起跨源调用。
        origin = request.headers.get("origin")
        if origin and origin not in {str(request.base_url).rstrip("/"), *trusted_web_origins}:
            raise HTTPException(403, "不接受跨源请求")
        request.state.role = auth_manager.role(request)
        request.state.subject = auth_manager.subject(request)

    @asynccontextmanager
    async def acquire_agent(workspace_id: str):
        async with app.state.agent_lock:
            workspace = next(
                (item for item in app.state.workspaces if item["id"] == workspace_id), None
            )
            if workspace is None:
                raise HTTPException(404, "工作区不存在")
            agent = app.state.workspace_agents.get(workspace_id)
            if agent is None and (
                app.state.settings.provider == "mock"
                or app.state.settings.api_key.get_secret_value()
            ):
                agent_settings = app.state.settings.model_copy(
                    update={"workspace": Path(workspace["path"])}
                )
                try:
                    agent = make_agent(agent_settings)
                except (OSError, ValueError):
                    raise HTTPException(400, "无法在所选工作区启用文件工具") from None
                app.state.workspace_agents[workspace_id] = agent
            if agent is None:
                raise HTTPException(503, "请先在模型设置中填写 API Key")
            app.state.agent_users[agent] = app.state.agent_users.get(agent, 0) + 1
        try:
            yield agent
        finally:
            async with app.state.agent_lock:
                remaining = app.state.agent_users[agent] - 1
                if remaining:
                    app.state.agent_users[agent] = remaining
                else:
                    del app.state.agent_users[agent]
                    if agent not in app.state.workspace_agents.values():
                        await agent.close()

    async def ready_agent():
        async with acquire_agent(app.state.active_workspace_id) as agent:
            yield agent

    ready_dependency = Depends(ready_agent)

    @app.middleware("http")
    async def limit_body(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH"}:
            path = request.url.path.rstrip("/")
            if path.endswith("/api/attachments/extract"):
                max_bytes = MAX_ATTACHMENT_BYTES
                limit_label = "8 MB"
            elif path.endswith("/api/models/server-ollama/chat/completions"):
                # Base64 image data is larger than the original image files.
                max_bytes = 18 * 1024 * 1024
                limit_label = "18 MB"
            else:
                max_bytes = 128 * 1024
                limit_label = "128 KB"
            content_length = request.headers.get("content-length", "")
            if content_length.isdigit() and int(content_length) > max_bytes:
                return JSONResponse({"detail": f"请求体不能超过 {limit_label}"}, status_code=413)
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > max_bytes:
                    return JSONResponse({"detail": f"请求体不能超过 {limit_label}"}, status_code=413)
            request._body = bytes(body)
        return await call_next(request)

    @app.exception_handler(ValueError)
    async def value_error(request, exc):
        return JSONResponse({"detail": str(exc)[:500]}, status_code=400)

    @app.exception_handler(SessionConflict)
    async def session_conflict(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.get("/health")
    async def health():
        return {"name": "yugan-agent", "status": "ok", "version": __version__}

    auth = [Depends(authorize)]

    def workspace_payload():
        return {
            "active_workspace_id": app.state.active_workspace_id,
            "workspaces": [
                {**workspace, "active": workspace["id"] == app.state.active_workspace_id}
                for workspace in app.state.workspaces
            ],
        }

    async def persist_workspaces(workspaces=None, active_id=None, sessions=None):
        await asyncio.to_thread(
            save_workspaces,
            workspace_path,
            workspaces if workspaces is not None else app.state.workspaces,
            active_id if active_id is not None else app.state.active_workspace_id,
            sessions if sessions is not None else app.state.session_workspaces,
        )

    async def switch_workspace(workspace_id: str):
        async with app.state.agent_lock:
            workspace = next(
                (item for item in app.state.workspaces if item["id"] == workspace_id), None
            )
            if workspace is None:
                raise HTTPException(404, "工作区不存在")
            if workspace_id == app.state.active_workspace_id:
                return workspace_payload()
            agent = app.state.workspace_agents.get(workspace_id)
            if agent is None and (
                app.state.settings.provider == "mock"
                or app.state.settings.api_key.get_secret_value()
            ):
                target_settings = app.state.settings.model_copy(
                    update={"workspace": Path(workspace["path"])}
                )
                try:
                    agent = make_agent(target_settings)
                except (OSError, ValueError):
                    raise HTTPException(400, "无法在所选工作区启用文件工具") from None
            try:
                await persist_workspaces(active_id=workspace_id)
            except OSError:
                if agent is not None and agent not in app.state.workspace_agents.values():
                    await agent.close()
                raise HTTPException(500, "工作区设置无法保存到本机") from None
            app.state.active_workspace_id = workspace_id
            app.state.settings = app.state.settings.model_copy(
                update={"workspace": Path(workspace["path"])}
            )
            if agent is not None:
                app.state.workspace_agents[workspace_id] = agent
            app.state.agent = agent
            return workspace_payload()

    @app.get("/api/workspaces", dependencies=auth)
    async def list_workspaces(request: Request):
        if getattr(request.state, "role", "guest") != "admin":
            guest_id = app.state.workspaces[0]["id"]
            workspace = next(item for item in app.state.workspaces if item["id"] == guest_id)
            return {
                "active_workspace_id": guest_id,
                "workspaces": [{
                    "id": guest_id,
                    "name": workspace["name"],
                    "path": "",
                    "active": True,
                }],
            }
        return workspace_payload()

    @app.post("/api/workspaces/pick", dependencies=auth)
    async def pick_workspace_directory(request: Request):
        require_admin(request)
        check_local_model_request(request)
        try:
            selected = await asyncio.to_thread(
                choose_workspace_directory, app.state.settings.workspace
            )
        except Exception:
            raise HTTPException(
                503, "Windows 文件夹选择窗口无法启动；也可以直接填写路径。"
            ) from None
        return {"cancelled": not bool(selected), "path": selected or ""}

    @app.post("/api/workspaces", dependencies=auth)
    async def create_workspace(request: Request, body: WorkspaceCreate):
        require_admin(request)
        check_local_model_request(request, json_body=True)
        name = body.name.strip()
        if not name:
            raise HTTPException(400, "请输入工作区名称")
        try:
            directory = await asyncio.to_thread(create_workspace_directory, body.path)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from None
        except (OSError, RuntimeError):
            raise HTTPException(400, "无法创建这个文件夹，请检查路径和权限") from None

        async with app.state.agent_lock:
            if any(item["path"] == str(directory) for item in app.state.workspaces):
                raise HTTPException(409, "这个文件夹已经添加为工作区")
            workspace = {"id": uuid4().hex, "name": name[:80], "path": str(directory)}
            workspaces = [*app.state.workspaces, workspace]
            agent = None
            if (
                app.state.settings.provider == "mock"
                or app.state.settings.api_key.get_secret_value()
            ):
                target_settings = app.state.settings.model_copy(update={"workspace": directory})
                try:
                    agent = make_agent(target_settings)
                except (OSError, ValueError):
                    raise HTTPException(400, "无法在新工作区启用文件工具") from None
            try:
                await persist_workspaces(workspaces, workspace["id"])
            except OSError:
                if agent is not None:
                    await agent.close()
                raise HTTPException(500, "工作区设置无法保存到本机") from None
            app.state.workspaces = workspaces
            app.state.active_workspace_id = workspace["id"]
            app.state.settings = app.state.settings.model_copy(update={"workspace": directory})
            if agent is not None:
                app.state.workspace_agents[workspace["id"]] = agent
            app.state.agent = agent
            return workspace_payload()

    @app.post("/api/workspaces/{workspace_id}/activate", dependencies=auth)
    async def activate_workspace(workspace_id: str, request: Request):
        require_admin(request)
        check_local_model_request(request)
        return await switch_workspace(workspace_id)

    @app.delete("/api/workspaces/{workspace_id}", dependencies=auth)
    async def remove_workspace(workspace_id: str, request: Request):
        require_admin(request)
        check_local_model_request(request)
        async with app.state.agent_lock:
            if not any(item["id"] == workspace_id for item in app.state.workspaces):
                raise HTTPException(404, "工作区不存在")
            if len(app.state.workspaces) == 1:
                raise HTTPException(409, "至少需要保留一个工作区")
            if app.state.agent_users:
                raise HTTPException(409, "任务运行中，完成后再移除工作区")

            remaining = [item for item in app.state.workspaces if item["id"] != workspace_id]
            active_id = (
                remaining[0]["id"]
                if workspace_id == app.state.active_workspace_id
                else app.state.active_workspace_id
            )
            assignments = {
                session_id: active_id if assigned_id == workspace_id else assigned_id
                for session_id, assigned_id in app.state.session_workspaces.items()
            }
            next_workspace = next(item for item in remaining if item["id"] == active_id)
            next_agent = app.state.workspace_agents.get(active_id)
            if workspace_id == app.state.active_workspace_id and next_agent is None and (
                app.state.settings.provider == "mock"
                or app.state.settings.api_key.get_secret_value()
            ):
                next_settings = app.state.settings.model_copy(
                    update={"workspace": Path(next_workspace["path"])}
                )
                try:
                    next_agent = make_agent(next_settings)
                except (OSError, ValueError):
                    raise HTTPException(400, "无法在剩余工作区启用文件工具") from None
            try:
                await persist_workspaces(remaining, active_id, assignments)
            except OSError:
                if next_agent is not None and next_agent not in app.state.workspace_agents.values():
                    await next_agent.close()
                raise HTTPException(500, "工作区设置无法保存到本机") from None

            removed_agent = app.state.workspace_agents.pop(workspace_id, None)
            app.state.workspaces = remaining
            app.state.active_workspace_id = active_id
            app.state.session_workspaces = assignments
            if next_agent is not None:
                app.state.workspace_agents[active_id] = next_agent
            app.state.settings = app.state.settings.model_copy(
                update={"workspace": Path(next_workspace["path"])}
            )
            app.state.agent = app.state.workspace_agents.get(active_id)
            if removed_agent is not None and removed_agent is not next_agent:
                await removed_agent.close()
            return workspace_payload()

    @app.put("/api/sessions/{session_id}/workspace", dependencies=auth)
    async def assign_session_workspace(session_id: str, request: Request, body: SessionWorkspace):
        require_admin(request)
        check_local_model_request(request, json_body=True)
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", session_id):
            raise HTTPException(400, "无效的会话 ID")
        if not any(item["id"] == body.workspace_id for item in app.state.workspaces):
            raise HTTPException(404, "目标工作区不存在")
        async with app.state.agent_lock:
            assignments = {**app.state.session_workspaces, session_id: body.workspace_id}
            try:
                await persist_workspaces(sessions=assignments)
            except OSError:
                raise HTTPException(500, "会话工作区无法保存到本机") from None
            app.state.session_workspaces = assignments
        return {"session_id": session_id, "workspace_id": body.workspace_id}

    @app.get("/api/status", dependencies=auth)
    async def status(request: Request):
        current = app.state.settings
        if current.provider == "mock":
            vendor = "本机演示"
        else:
            try:
                vendor = resolve_target(current.base_url or "", current.model).vendor
            except ValueError:
                vendor = current.provider
        return {
            "name": "yugan-agent",
            "version": __version__,
            "provider": current.provider,
            "model": current.model,
            "vendor": vendor,
            "demo": current.provider == "mock",
            "configured": app.state.agent is not None,
            "token_required": bool(settings.api_token.get_secret_value()),
            "active_model_id": app.state.active_model_id,
            "role": getattr(request.state, "role", "guest"),
        }

    @app.get("/api/models/server-ollama", dependencies=auth)
    async def server_ollama_models():
        """Expose only model names from the Ollama service configured by the server operator."""
        endpoint = settings.server_ollama_url.rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
                response = await client.get(f"{endpoint}/api/tags")
            if response.status_code != 200:
                return {"available": False, "models": []}
            names = server_chat_model_names(response.json().get("models", []))
            return {"available": True, "models": names}
        except (httpx.HTTPError, ValueError, AttributeError):
            return {"available": False, "models": []}

    @app.post("/api/models/server-ollama/chat/completions", dependencies=auth)
    async def server_ollama_completion(body: ServerOllamaCompletion, request: Request):
        # This endpoint never accepts a client API key. Require the page's own origin
        # before forwarding a model request to the operator-configured Ollama service.
        origin = request.headers.get("origin")
        if origin not in {str(request.base_url).rstrip("/"), *trusted_web_origins}:
            raise HTTPException(403, "只能由当前 Agent 页面调用服务器模型")
        endpoint = settings.server_ollama_url.rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
                tags_response = await client.get(f"{endpoint}/api/tags")
            if tags_response.status_code != 200:
                raise HTTPException(503, "服务器 Ollama 暂不可用")
            available_models = server_chat_model_names(tags_response.json().get("models", []))
        except (httpx.HTTPError, ValueError, AttributeError):
            raise HTTPException(503, "服务器 Ollama 暂不可用") from None
        if body.model not in available_models:
            raise HTTPException(400, "请选择服务器已安装的对话模型")
        payload = {
            "model": body.model,
            "messages": body.messages,
            "max_tokens": body.max_tokens,
            "stream": False,
        }
        if body.tools:
            payload["tools"] = body.tools
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(300, connect=5), trust_env=False) as client:
                response = await client.post(f"{endpoint}/v1/chat/completions", json=payload)
        except httpx.HTTPError:
            raise HTTPException(503, "服务器 Ollama 暂不可用") from None
        if response.status_code != 200:
            has_image = any(
                isinstance(message.get("content"), list)
                and any(part.get("type") == "image_url" for part in message["content"] if isinstance(part, dict))
                for message in body.messages if isinstance(message, dict)
            )
            detail = "服务器模型无法处理图片，请换用支持识图的模型" if has_image else "服务器 Ollama 请求失败"
            raise HTTPException(502, detail)
        try:
            result = response.json()
        except ValueError:
            raise HTTPException(502, "服务器 Ollama 返回了无效响应") from None
        if not isinstance(result, dict) or not result.get("choices"):
            raise HTTPException(502, "服务器 Ollama 没有返回有效回答")
        return result

    def check_local_model_request(request: Request, *, json_body: bool = False):
        origin = request.headers.get("origin")
        if origin and origin != str(request.base_url).rstrip("/"):
            raise HTTPException(403, "不接受跨源请求")
        if json_body and (
            request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            != "application/json"
        ):
            raise HTTPException(415, "请使用 JSON 请求")

    def check_local_workspace_read(request: Request):
        if (
            request.client is None
            or request.client.host not in {"127.0.0.1", "::1"}
            or request.url.hostname not in {"127.0.0.1", "localhost", "::1"}
        ):
            raise HTTPException(403, "工作区只能从本机网页查看")
        origin = request.headers.get("origin")
        if origin and origin != str(request.base_url).rstrip("/"):
            raise HTTPException(403, "不接受跨源请求")

    def create_workspace_directory(path: str) -> Path:
        directory = Path(path).expanduser().resolve()
        if directory.exists() and not directory.is_dir():
            raise ValueError("路径已存在，但它不是文件夹")
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def choose_workspace_directory(initial: Path) -> str:
        if os.name == "nt":
            powershell = shutil.which("powershell.exe") or str(
                Path(os.environ.get("WINDIR", r"C:\Windows"))
                / "System32"
                / "WindowsPowerShell"
                / "v1.0"
                / "powershell.exe"
            )
            script = r"""
Add-Type -AssemblyName System.Windows.Forms
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = '选择 yugan-agent 工作区文件夹'
$dialog.ShowNewFolderButton = $true
$start = $env:YUGAN_WORKSPACE_START
if ($start -and (Test-Path -LiteralPath $start -PathType Container)) {
    $dialog.SelectedPath = $start
}
if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
    [Console]::Write($dialog.SelectedPath)
}
"""
            environment = os.environ.copy()
            environment["YUGAN_WORKSPACE_START"] = str(initial.expanduser().resolve())
            completed = subprocess.run(
                [powershell, "-NoProfile", "-STA", "-Command", script],
                capture_output=True,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                encoding="utf-8",
                errors="replace",
                env=environment,
                timeout=600,
            )
            if completed.returncode:
                raise RuntimeError("Windows 文件夹选择器未能正常退出")
            return completed.stdout.strip()

        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        try:
            return filedialog.askdirectory(
                title="选择 yugan-agent 工作区文件夹",
                initialdir=str(initial if initial.is_dir() else Path.cwd()),
                mustexist=False,
            )
        finally:
            root.destroy()

    async def activate_profile(profile: ModelProfile, profiles: list[ModelProfile]):
        target = profile.target
        old_agents = dict(app.state.workspace_agents)
        base_settings = app.state.settings.model_copy(
            update={
                "provider": target.provider,
                "model": target.model,
                "api_key": SecretStr(profile.api_key),
                "base_url": target.base_url,
                "thinking": target.thinking,
            }
        )
        new_agents = {}
        try:
            workspace_ids = set(old_agents) | {app.state.active_workspace_id}
            for workspace_id in workspace_ids:
                workspace = next(
                    item for item in app.state.workspaces if item["id"] == workspace_id
                )
                workspace_settings = base_settings.model_copy(
                    update={"workspace": Path(workspace["path"])}
                )
                new_agents[workspace_id] = make_agent(workspace_settings)
        except (OSError, ValueError):
            for agent in new_agents.values():
                await agent.close()
            raise HTTPException(400, "无法在工作区启用所选模型") from None
        try:
            save_model_config(env_path, profile.api_key, target)
            save_model_profiles(models_path, profile.id, profiles)
        except (OSError, ValueError):
            for agent in new_agents.values():
                await agent.close()
            raise HTTPException(400, "模型配置写入本机失败") from None
        active_workspace = next(
            item for item in app.state.workspaces if item["id"] == app.state.active_workspace_id
        )
        app.state.settings = base_settings.model_copy(
            update={"workspace": Path(active_workspace["path"])}
        )
        app.state.workspace_agents = new_agents
        app.state.agent = new_agents.get(app.state.active_workspace_id)
        app.state.model_profiles = profiles
        app.state.active_model_id = profile.id
        for old_agent in old_agents.values():
            if old_agent not in app.state.agent_users:
                await old_agent.close()
        return {"saved": True, "active_model_id": profile.id, **profile.public()}

    async def upsert_profile(body: ModelSettingsRequest, existing_id: str | None = None):
        target = resolve_target(body.endpoint, body.model)
        existing = next((item for item in app.state.model_profiles if item.id == existing_id), None)
        if existing_id and existing is None:
            raise HTTPException(404, "模型配置不存在")
        key = (
            "ollama" if target.vendor == "Ollama" else
            body.api_key.get_secret_value().strip() or (existing.api_key if existing else "")
        )
        profile = new_profile(body.name or (existing.name if existing else ""), key, target)
        if existing:
            profile = ModelProfile(existing.id, profile.name, profile.endpoint, profile.model, key)
            profiles = [
                profile if item.id == existing_id else item for item in app.state.model_profiles
            ]
        else:
            profiles = [*app.state.model_profiles, profile]
        return await activate_profile(profile, profiles)

    @app.get("/api/settings/models", dependencies=auth)
    async def list_models():
        return {"active_model_id": None, "models": [], "storage": "browser"}

    @app.get("/api/settings/models/legacy-export", dependencies=auth)
    async def export_legacy_models(request: Request):
        require_admin(request)
        try:
            active_id, profiles = load_model_profiles(models_path)
        except FileNotFoundError:
            return JSONResponse(
                {"active_model_id": None, "models": []},
                headers={"Cache-Control": "no-store"},
            )
        except (OSError, ValueError):
            raise HTTPException(409, "旧模型配置无法读取") from None
        return JSONResponse(
            {
                "active_model_id": active_id,
                "models": [
                    {**profile.public(), "api_key": profile.api_key}
                    for profile in profiles
                ],
            },
            headers={"Cache-Control": "no-store"},
        )

    @app.delete("/api/settings/models/legacy-export", dependencies=auth)
    async def remove_legacy_models(request: Request):
        require_admin(request)
        models_path.unlink(missing_ok=True)
        return {"deleted": True}

    @app.get("/api/settings/local-models", dependencies=auth)
    async def list_local_models(request: Request):
        raise HTTPException(410, "本地模型列表必须由浏览器直接读取")

    @app.post("/api/settings/model", dependencies=auth)
    @app.post("/api/settings/models", dependencies=auth)
    async def save_model(request: Request, body: ModelSettingsRequest):
        raise HTTPException(410, "模型配置只保存在浏览器；请更新 Agent 页面后在本地保存")

    @app.put("/api/settings/models/{profile_id}", dependencies=auth)
    async def update_model(profile_id: str, request: Request, body: ModelSettingsRequest):
        raise HTTPException(410, "模型配置只保存在浏览器；服务器不再接收 API Key")

    @app.post("/api/settings/models/{profile_id}/activate", dependencies=auth)
    async def select_model(profile_id: str, request: Request):
        raise HTTPException(410, "模型切换由浏览器本地完成")

    @app.delete("/api/settings/models/{profile_id}", dependencies=auth)
    async def delete_model(profile_id: str, request: Request):
        raise HTTPException(410, "模型配置由浏览器本地删除，服务器不保存 API Key")

    def default_workspace_for_session(session_id: str) -> str:
        return app.state.session_workspaces.get(session_id, app.state.workspaces[0]["id"])

    def scoped_session_id(session_id: str, request: Request) -> str:
        if getattr(request.state, "role", "guest") == "admin":
            return session_id
        subject = getattr(request.state, "subject", "anonymous")
        prefix = f"guest_{hashlib.sha256(subject.encode()).hexdigest()[:12]}_"
        if session_id.startswith(prefix):
            return session_id
        return prefix + session_id[:64 - len(prefix)]

    async def bind_session_workspace(
        session_id: str,
        requested_id: str | None = None,
        request: Request | None = None,
    ) -> str:
        async with app.state.agent_lock:
            current = app.state.session_workspaces.get(session_id)
            is_guest = request is not None and getattr(request.state, "role", "guest") != "admin"
            workspace_id = (
                app.state.workspaces[0]["id"]
                if is_guest
                else current or requested_id or app.state.active_workspace_id
            )
            if not any(item["id"] == workspace_id for item in app.state.workspaces):
                raise HTTPException(404, "会话所属的工作区不存在")
            if current is None:
                assignments = {**app.state.session_workspaces, session_id: workspace_id}
                try:
                    await persist_workspaces(sessions=assignments)
                except OSError:
                    raise HTTPException(500, "会话工作区无法保存到本机") from None
                app.state.session_workspaces = assignments
        return workspace_id

    @app.get("/api/rag/catalog", dependencies=auth)
    async def rag_catalog_route():
        try:
            return await rag_catalog()
        except RagBridgeError as exc:
            raise HTTPException(503, str(exc)) from exc

    @app.post("/api/rag/retrieve", dependencies=auth)
    async def browser_rag_retrieve(body: BrowserRagRetrieve):
        try:
            return await rag_retrieve(body.prompt, body.rag)
        except RagBridgeError as exc:
            raise HTTPException(503, str(exc)) from exc

    @app.post("/api/chat", dependencies=auth)
    async def chat(body: ChatRequest, request: Request):
        raise HTTPException(410, "模型调用必须由浏览器直连；请更新 Agent 页面")

    @app.post("/api/chat/stream", dependencies=auth)
    async def chat_stream(body: ChatRequest, request: Request):
        raise HTTPException(410, "模型调用必须由浏览器直连；请更新 Agent 页面")

    @app.get("/api/approvals/pending", dependencies=auth)
    async def pending_approvals(
        scope: str | None = Query(default=None, pattern=r"^[0-9a-f]{32}$"),
    ):
        return {"pending": approval_broker.list_pending(scope)}

    @app.post("/api/approval-scopes/{scope}/approve-all", dependencies=auth)
    async def approve_all_for_run(scope: str, request: Request):
        if (
            request.client is None
            or request.client.host not in {"127.0.0.1", "::1"}
            or request.headers.get("origin") != str(request.base_url).rstrip("/")
        ):
            raise HTTPException(403, "只能从本机网页批准整次任务")
        if not re.fullmatch(r"[0-9a-f]{32}", scope):
            raise HTTPException(400, "无效的任务确认标识")
        if not approval_broker.approve_all(scope):
            raise HTTPException(404, "本次任务没有等待确认的操作")
        return {"approved_for_run": True}

    @app.post("/api/approvals/{approval_id}", dependencies=auth)
    async def decide_approval(approval_id: str, body: ApprovalDecision):
        if not approval_broker.decide(approval_id, body.approved):
            raise HTTPException(404, "这项操作已处理或已超时")
        return {"accepted": True}

    @app.get("/api/tools", dependencies=auth)
    async def tools(request: Request):
        workspace = app.state.workspaces[0] if request.state.role != "admin" else next(
            item for item in app.state.workspaces if item["id"] == app.state.active_workspace_id
        )
        target = app.state.settings.model_copy(update={"workspace": Path(workspace["path"])})
        registry = build_tool_registry(
            target,
            approval_callback=request_computer_approval,
            custom_tools=app.state.custom_tools if request.state.role == "admin" else [],
        )
        if request.state.role != "admin":
            guest_files.restrict_registry(registry, target.workspace)
        return registry.schemas()

    @app.post("/api/tools/execute", dependencies=auth)
    async def execute_browser_tool(body: ToolExecutionRequest, request: Request):
        workspace = app.state.workspaces[0] if request.state.role != "admin" else next(
            item for item in app.state.workspaces if item["id"] == app.state.active_workspace_id
        )
        target = app.state.settings.model_copy(update={"workspace": Path(workspace["path"])})
        disabled = set(body.disabled_tools) if request.state.role == "admin" else set()
        custom = []
        if request.state.role == "admin":
            disabled |= app.state.disabled_builtin_tools
            custom = app.state.custom_tools
        registry = build_tool_registry(
            target,
            approval_callback=request_computer_approval,
            disabled_builtins=disabled,
            custom_tools=custom,
        )
        if request.state.role != "admin":
            guest_files.restrict_registry(registry, target.workspace)
            for name in body.disabled_tools:
                registry.unregister(name)
        if body.name not in {item["name"] for item in registry.schemas()}:
            raise HTTPException(403, "该工具已停用或当前账号不可用")
        stored_id = None
        turn_index = None
        if body.name == "create_text_file":
            if not body.session_id:
                raise HTTPException(400, "生成文件需要当前会话 ID")
            stored_id = scoped_session_id(body.session_id, request)
            snapshot = SQLiteMemory(app.state.settings.database).load(stored_id)
            turn_index = sum(message.role == "user" for message in snapshot.messages)
        session_context = (
            guest_files.session_scope(stored_id, turn_index)
            if request.state.role != "admin" and stored_id is not None
            else nullcontext()
        )
        with session_context:
            async with scoped_run(request):
                result = await registry.execute(body.name, body.arguments)
        if request.state.role == "admin" and stored_id is not None and result.ok:
            try:
                result.data["file_id"] = guest_files.record_admin_file(
                    target.workspace, result.data["path"], stored_id, turn_index
                )
            except (OSError, ValueError, PermissionError, sqlite3.Error) as exc:
                result.data["file_record_error"] = f"文件已创建，但无法显示下载卡片：{exc}"
        return result.model_dump(mode="json")

    def generated_file_session(session_id: str, request: Request) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", session_id):
            raise HTTPException(400, "无效的会话 ID")
        return scoped_session_id(session_id, request)

    @app.get("/api/sessions/{session_id}/generated-files/{file_id}", dependencies=auth)
    async def preview_generated_file(session_id: str, file_id: str, request: Request):
        stored_id = generated_file_session(session_id, request)
        if not re.fullmatch(r"[0-9a-f]{32}", file_id):
            raise HTTPException(404, "生成文件不存在")
        try:
            metadata, content = guest_files.read(stored_id, file_id)
        except FileNotFoundError:
            raise HTTPException(404, "生成文件不存在") from None
        except (ValueError, PermissionError):
            raise HTTPException(409, "文件已撤销、替换或变更") from None
        return {**metadata, "content": content.decode("utf-8-sig")}

    @app.get("/api/sessions/{session_id}/generated-files/{file_id}/download", dependencies=auth)
    async def download_generated_file(session_id: str, file_id: str, request: Request):
        stored_id = generated_file_session(session_id, request)
        if not re.fullmatch(r"[0-9a-f]{32}", file_id):
            raise HTTPException(404, "生成文件不存在")
        try:
            metadata, content = guest_files.read(stored_id, file_id)
        except FileNotFoundError:
            raise HTTPException(404, "生成文件不存在") from None
        except (ValueError, PermissionError):
            raise HTTPException(409, "文件已撤销、替换或变更") from None
        filename = Path(metadata["path"]).name
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}",
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @app.delete("/api/sessions/{session_id}/generated-files/{file_id}", dependencies=auth)
    async def revoke_generated_file(session_id: str, file_id: str, request: Request):
        stored_id = generated_file_session(session_id, request)
        if not re.fullmatch(r"[0-9a-f]{32}", file_id):
            raise HTTPException(404, "生成文件不存在")
        try:
            return guest_files.revoke(stored_id, file_id)
        except FileNotFoundError:
            raise HTTPException(404, "生成文件不存在") from None
        except (ValueError, PermissionError):
            raise HTTPException(409, "文件已撤销、替换或变更，不能删除") from None

    @app.post("/api/attachments/extract", dependencies=auth)
    async def extract_browser_attachment(request: Request):
        encoded_name = request.headers.get("x-filename", "")
        if not encoded_name or len(encoded_name) > 1024:
            raise HTTPException(400, "缺少文件名")
        if request.headers.get("content-length", "").isdigit():
            if int(request.headers["content-length"]) > MAX_ATTACHMENT_BYTES:
                raise HTTPException(413, "单个文件不能超过 8 MB")
        chunks = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_ATTACHMENT_BYTES:
                raise HTTPException(413, "单个文件不能超过 8 MB")
            chunks.append(chunk)
        return extract_attachment_text(unquote(encoded_name), b"".join(chunks))

    @app.post("/api/sessions/{session_id}/browser-turn", dependencies=auth)
    async def save_browser_turn(session_id: str, request: Request, body: BrowserTurn):
        stored_id = scoped_session_id(session_id, request)
        agent = app.state.agent
        if agent is None:
            raise HTTPException(503, "会话存储暂不可用")
        async with agent.session_lock(stored_id):
            snapshot = agent.memory.load(stored_id)
            turn_index = sum(message.role == "user" for message in snapshot.messages)
            snapshot.messages.extend([
                Message(role="user", content=body.prompt),
                Message(role="assistant", content=body.answer),
            ])
            if body.execution or body.model:
                snapshot.execution_traces.append(
                    ExecutionTrace(
                        id=uuid4().hex,
                        created_at=datetime.now(timezone.utc).isoformat(),
                        turn_index=turn_index,
                        model=body.model,
                        entries=body.execution,
                    )
                )
                snapshot.execution_traces = snapshot.execution_traces[-500:]
            agent.memory.save(stored_id, snapshot)
        return {"saved": True}

    @app.get("/api/tools/management", dependencies=auth)
    async def tool_management(request: Request):
        workspace = app.state.workspaces[0] if request.state.role != "admin" else next(
            item for item in app.state.workspaces if item["id"] == app.state.active_workspace_id
        )
        tool_settings = app.state.settings.model_copy(update={"workspace": Path(workspace["path"])})
        catalog = build_tool_registry(
            tool_settings,
            approval_callback=request_computer_approval,
            custom_tools=app.state.custom_tools if request.state.role == "admin" else [],
        )
        if request.state.role != "admin":
            guest_files.restrict_registry(catalog, tool_settings.workspace)
        catalog = catalog.schemas()
        builtin_names = {item["name"] for item in catalog}
        disabled = (
            app.state.disabled_builtin_tools if request.state.role == "admin" else set()
        ) & builtin_names
        return {
            "builtins": [
                {
                    **item,
                    "enabled": item["name"] not in disabled,
                    "parameters": list(item.get("parameters", {}).get("properties", {})),
                }
                for item in catalog
            ],
            "custom_tools": (
                [item.public() for item in app.state.custom_tools]
                if request.state.role == "admin" else []
            ),
        }

    @app.patch("/api/tools/builtins/{name}", dependencies=auth)
    async def toggle_builtin_tool(name: str, request: Request, body: BuiltinToolToggle):
        require_admin(request)
        check_local_model_request(request, json_body=True)
        names = {item["name"] for item in builtin_tool_catalog()}
        if name not in names:
            raise HTTPException(404, "内置工具不存在")
        disabled = set(app.state.disabled_builtin_tools)
        if body.enabled:
            disabled.discard(name)
        else:
            disabled.add(name)
        await update_tool_configuration(request, disabled=disabled, custom=app.state.custom_tools)
        return {"name": name, "enabled": body.enabled}

    @app.post("/api/tools/custom", dependencies=auth)
    async def add_custom_tool(request: Request, body: CustomToolDefinition):
        require_admin(request)
        check_local_model_request(request, json_body=True)
        if len(app.state.custom_tools) >= 30:
            raise HTTPException(400, "自定义工具最多保存 30 个")
        if any(item.name == body.name for item in app.state.custom_tools):
            raise HTTPException(409, "这个工具名称已经存在")
        if body.name in {item["name"] for item in builtin_tool_catalog()}:
            raise HTTPException(409, "不能使用内置工具的名称")
        custom = [*app.state.custom_tools, body]
        await update_tool_configuration(
            request, disabled=app.state.disabled_builtin_tools, custom=custom
        )
        return body.public()

    @app.delete("/api/tools/custom/{name}", dependencies=auth)
    async def delete_custom_tool(name: str, request: Request):
        require_admin(request)
        check_local_model_request(request)
        custom = [item for item in app.state.custom_tools if item.name != name]
        if len(custom) == len(app.state.custom_tools):
            raise HTTPException(404, "自定义工具不存在")
        await update_tool_configuration(
            request, disabled=app.state.disabled_builtin_tools, custom=custom
        )
        return {"deleted": name}

    @app.get("/api/sessions", dependencies=auth)
    async def sessions(request: Request):
        results = SQLiteMemory(app.state.settings.database).list_sessions()
        prefix = ""
        if request.state.role != "admin":
            prefix = f"guest_{hashlib.sha256(request.state.subject.encode()).hexdigest()[:12]}_"
            results = [item for item in results if item["id"].startswith(prefix)]
        for item in results:
            item["workspace_id"] = (
                app.state.workspaces[0]["id"]
                if request.state.role != "admin"
                else default_workspace_for_session(item["id"])
            )
            if prefix:
                item["id"] = item["id"][len(prefix):]
        return results

    @app.patch("/api/sessions/{session_id}/title", dependencies=auth)
    async def rename_session(session_id: str, request: Request, body: SessionRename):
        session_id = scoped_session_id(session_id, request)
        title = body.title.strip()
        if not title:
            raise HTTPException(400, "会话名称不能为空")
        memory = SQLiteMemory(app.state.settings.database)
        if not memory.rename_session(session_id, title):
            raise HTTPException(404, "会话不存在")
        return {"id": session_id, "title": title}

    @app.get("/api/sessions/{session_id}", dependencies=auth)
    async def session(session_id: str, request: Request, agent=ready_dependency):
        session_id = scoped_session_id(session_id, request)
        async with agent.session_lock(session_id):
            snapshot = agent.memory.load(session_id)
            return {
                "session_id": session_id,
                "state": snapshot.state,
                "version": snapshot.version,
                "generated_files": guest_files.list_for_session(session_id),
                "messages": [
                    m.model_dump(exclude={"provider_data", "provider"})
                    for m in snapshot.messages
                ],
                "execution_traces": [trace.model_dump(mode="json") for trace in snapshot.execution_traces],
            }

    @app.patch("/api/sessions/{session_id}/state", dependencies=auth)
    async def set_state(
        session_id: str, request: Request, body: StateRequest, agent=ready_dependency
    ):
        session_id = scoped_session_id(session_id, request)
        return await agent.update_state(session_id, body.values)

    @app.delete("/api/sessions/{session_id}", dependencies=auth)
    async def delete_session(session_id: str, request: Request, agent=ready_dependency):
        session_id = scoped_session_id(session_id, request)
        await agent.delete_session(session_id)
        if session_id in app.state.session_workspaces:
            assignments = dict(app.state.session_workspaces)
            assignments.pop(session_id, None)
            try:
                await persist_workspaces(sessions=assignments)
            except OSError:
                raise HTTPException(500, "会话已删除，但工作区记录未能更新") from None
            app.state.session_workspaces = assignments
        return {"deleted": session_id}

    @app.post("/api/workflows/run", dependencies=auth)
    async def run_workflow(
        body: Workflow,
        request: Request,
        session_id: str | None = Query(default=None, pattern=r"^[a-zA-Z0-9_-]{1,64}$"),
    ):
        require_admin(request)
        raise HTTPException(410, "工作流由浏览器调用当前选择的模型；请更新 Agent 页面")

    @app.get("/api/workflows/demo", dependencies=auth)
    async def demo_workflow():
        workflow = Workflow.model_validate_json(
            files("yugan_agent").joinpath("data/greenhouse.json").read_text(encoding="utf-8")
        )
        return {"workflow": workflow.model_dump(), "mermaid": workflow.mermaid()}

    web_root = files("yugan_agent").joinpath("web")
    app.mount("/static", StaticFiles(directory=str(web_root)), name="static")

    @app.get("/", include_in_schema=False)
    async def index():
        return FileResponse(str(web_root.joinpath("index.html")))

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return RedirectResponse("/static/icon.svg")

    return app
