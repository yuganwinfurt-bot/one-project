from .agent import Agent
from .builtins import register_builtins
from .coding_tools import register_coding_tools
from .computer import register_computer_tools
from .config import Settings
from .custom_tools import CustomToolDefinition, register_custom_tools
from .memory import SQLiteMemory
from .providers import create_provider
from .tools import ToolRegistry


def build_tool_registry(
    settings: Settings,
    *,
    approval_callback=None,
    disabled_builtins: set[str] | None = None,
    custom_tools: list[CustomToolDefinition] | None = None,
) -> ToolRegistry:
    registry = ToolRegistry(
        timeout=settings.tool_timeout,
        allowed_effects=settings.allowed_effects,
        approval_callback=approval_callback,
    )
    register_builtins(registry, settings.workspace, settings.http_endpoints)
    register_coding_tools(registry, settings.workspace)
    register_computer_tools(registry)
    builtin_names = {item["name"] for item in registry.schemas()}
    unknown = (disabled_builtins or set()) - builtin_names
    if unknown:
        raise ValueError("尝试停用不存在的内置工具")
    for name in disabled_builtins or set():
        registry.unregister(name)
    custom_names = [item.name for item in custom_tools or []]
    if len(set(custom_names)) != len(custom_names) or set(custom_names) & builtin_names:
        raise ValueError("自定义工具名称重复或与内置工具冲突")
    register_custom_tools(registry, custom_tools or [])
    return registry


def create_agent(settings: Settings | None = None, *, approval_callback=None) -> Agent:
    settings = settings or Settings()
    if settings.provider != "mock" and not settings.api_key.get_secret_value():
        raise ValueError("真实模型需要 API Key；请先在网页的模型设置中填写")
    registry = build_tool_registry(settings, approval_callback=approval_callback)
    return Agent(create_provider(settings), registry, SQLiteMemory(settings.database), settings)
