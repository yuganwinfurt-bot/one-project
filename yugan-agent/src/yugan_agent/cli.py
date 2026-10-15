"""Rich 命令行入口。所有异步资源在同一个事件循环内创建并关闭。"""

import argparse
import asyncio
import json
import threading
import time
import webbrowser
from importlib.resources import files
from pathlib import Path
from uuid import uuid4

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import Settings
from .runtime import create_agent
from .workflow import Workflow, WorkflowRunner

console = Console()


def show_result(result):
    console.print(
        Panel(Text(result.answer), title=f"yugan-agent · {result.status}", border_style="cyan")
    )
    for event in result.events:
        if event.kind == "tool":
            console.print(
                f"  {'[OK]' if event.ok else '[ERR]'} {event.name}  {event.duration_ms} ms"
            )
    console.print(f"会话: {result.session_id}", style="dim")


def load_workflow(path: str) -> Workflow:
    source = files("yugan_agent").joinpath("data/greenhouse.json") if path == "demo" else Path(path)
    return Workflow.model_validate_json(source.read_text(encoding="utf-8-sig"))


async def execute(args) -> int:
    settings = Settings(provider="mock", model="demo") if args.command == "demo" else Settings()
    agent = create_agent(settings)
    try:
        if args.command == "run":
            result = await agent.run(args.prompt, args.session)
            if args.json:
                print(result.model_dump_json(indent=2))
            else:
                show_result(result)
            return 0 if result.status == "completed" else 1
        if args.command == "chat":
            console.print("yugan-agent · 输入 /exit 退出，/new 新会话", style="bold cyan")
            console.print(f"当前模式: {settings.provider} / {settings.model}")
            session = args.session
            while True:
                try:
                    prompt = await asyncio.to_thread(console.input, "[cyan]你 > [/cyan]")
                except EOFError:
                    break
                if prompt.strip() == "/exit":
                    break
                if prompt.strip() == "/new":
                    session = uuid4().hex
                    console.print(f"新会话: {session}")
                elif prompt.strip():
                    show_result(await agent.run(prompt, session))
        elif args.command == "tools":
            table = Table("工具", "说明")
            for entry in agent.tools.schemas():
                table.add_row(entry["name"], entry["description"])
            console.print(table)
        elif args.command == "history":
            value = (
                agent.memory.load(args.session).model_dump(
                    exclude={"messages": {"__all__": {"provider_data", "provider"}}}
                )
                if args.session
                else agent.memory.list_sessions()
            )
            print(json.dumps(value, ensure_ascii=False, indent=2))
        elif args.command in {"workflow", "demo"}:
            if args.command == "demo":
                console.print("离线演示：无 API Key、无模型费用", style="bold cyan")
                show_result(await agent.run("计算 (12 + 8) * 3", "demo_" + uuid4().hex[:12]))
            workflow = load_workflow("demo" if args.command == "demo" else args.file)
            if getattr(args, "graph", False):
                print(workflow.mermaid())
            else:
                result = await WorkflowRunner(agent.tools, agent).run(workflow)
                console.print_json(result.model_dump_json())
                return 0 if result.status == "completed" else 1
        return 0
    finally:
        await agent.close()


def main():
    parser = argparse.ArgumentParser(prog="yugan-agent", description="轻量模块化 AI Agent 框架")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="运行不需要 Key 的离线示例")
    run = commands.add_parser("run", help="执行一次任务")
    run.add_argument("prompt")
    run.add_argument("--session", default="default")
    run.add_argument("--json", action="store_true")
    chat = commands.add_parser("chat", help="交互式多轮对话")
    chat.add_argument("--session", default="default")
    commands.add_parser("tools", help="列出已注册工具")
    history = commands.add_parser("history", help="列出会话或查看历史")
    history.add_argument("--session")
    workflow = commands.add_parser("workflow", help="执行 JSON 工作流；demo 为内置示例")
    workflow.add_argument("file")
    workflow.add_argument("--graph", action="store_true", help="输出 Mermaid 流程图")
    serve = commands.add_parser("serve", help="启动 Web 控制台与 API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8020)
    serve.add_argument("--open-browser", action="store_true", help="服务就绪后打开浏览器")
    args = parser.parse_args()
    try:
        if args.command == "serve":
            import uvicorn

            from .api import create_app

            settings = Settings()
            if args.host not in {"127.0.0.1", "localhost", "::1"}:
                if not settings.api_token.get_secret_value():
                    parser.error("监听外部地址前，请设置 YUGAN_API_TOKEN")
            server = uvicorn.Server(
                uvicorn.Config(create_app(settings), host=args.host, port=args.port)
            )
            if args.open_browser:

                def open_when_ready():
                    for _ in range(200):
                        if server.started:
                            host = "[::1]" if args.host == "::1" else "127.0.0.1"
                            webbrowser.open(f"http://{host}:{args.port}/")
                            return
                        if server.should_exit:
                            return
                        time.sleep(0.1)

                threading.Thread(target=open_when_ready, daemon=True).start()
            server.run()
        else:
            raise SystemExit(asyncio.run(execute(args)))
    except KeyboardInterrupt:
        console.print("已停止。")
    except Exception as exc:
        from pydantic import ValidationError

        if isinstance(exc, ValidationError):
            details = "; ".join(error["msg"] for error in exc.errors())
            console.print(f"配置错误：{details}", style="red")
        else:
            console.print(
                f"启动失败 ({type(exc).__name__})。请检查 .env、文件路径和接口配置。",
                style="red",
            )
        raise SystemExit(1) from None
