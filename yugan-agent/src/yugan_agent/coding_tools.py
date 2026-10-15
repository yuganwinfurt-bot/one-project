"""Workspace-scoped coding tools with per-write approval and recoverable edits."""

import asyncio
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit
from uuid import uuid4

from pydantic import Field

from .tools import ToolRegistry, tool

TEXT_SUFFIXES = {
    ".py",
    ".pyi",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cs",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".md",
    ".rst",
    ".txt",
    ".csv",
    ".xml",
    ".sql",
    ".sh",
    ".ps1",
    ".bat",
    ".env.example",
    ".ini",
    ".cfg",
    ".log",
    ".gitignore",
    ".dockerignore",
    ".makefile",
}
IGNORED_DIRS = {".git", ".venv", ".uv-cache", "__pycache__", "node_modules", ".yugan"}
ALLOWED_PROGRAMS = {
    "python",
    "python.exe",
    "py",
    "py.exe",
    "uv",
    "uv.exe",
    "ruff",
    "ruff.exe",
    "pytest",
    "pytest.exe",
    "node",
    "node.exe",
    "cmake",
    "cmake.exe",
    "arm-none-eabi-gcc",
    "arm-none-eabi-gcc.exe",
    "git",
    "git.exe",
}


def _target(root: Path, relative: str, *, allow_hidden: bool = False) -> Path:
    base = root.resolve()
    raw = Path(relative)
    if not relative or raw.is_absolute() or raw.drive or ":" in relative:
        raise PermissionError("请使用 workspace 内的相对路径")
    parts = raw.parts
    if not allow_hidden and any(part.startswith(".") for part in parts):
        raise PermissionError("不允许访问隐藏文件或目录")
    current = base
    for part in parts:
        if part in {"", ".", ".."}:
            if part == "..":
                raise PermissionError("文件路径超出 workspace")
            continue
        current = current / part
        if current.is_symlink():
            raise PermissionError("不允许通过符号链接访问或修改文件")
    resolved = current.resolve()
    if not resolved.is_relative_to(base):
        raise PermissionError("文件路径超出 workspace")
    return resolved


def _read_bytes(path: Path, *, maximum: int = 1_000_000) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError("文件超过 1 MB，无法安全处理")
    return data


async def _capture_stream(stream: asyncio.StreamReader, maximum: int = 12000) -> tuple[bytes, bool]:
    """Drain a child stream without letting a noisy command grow memory without bound."""
    kept = bytearray()
    truncated = False
    while chunk := await stream.read(4096):
        kept.extend(chunk)
        if len(kept) > maximum:
            del kept[: len(kept) - maximum]
            truncated = True
    return bytes(kept), truncated


def _skills_root(workspace: Path) -> Path | None:
    base = workspace.resolve()
    agent_dir = base / ".agents"
    skills_dir = agent_dir / "skills"
    if agent_dir.is_symlink() or skills_dir.is_symlink() or not skills_dir.is_dir():
        return None
    resolved = skills_dir.resolve()
    return resolved if resolved.is_relative_to(base) else None


def _atomic_write(path: Path, data: bytes) -> None:
    if not path.parent.is_dir():
        raise FileNotFoundError("目标文件夹不存在")
    fd, temporary = tempfile.mkstemp(prefix=".yugan-edit-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _backup_dir(root: Path) -> Path:
    base = root.resolve()
    yugan = base / ".yugan"
    backups = yugan / "coding-backups"
    if yugan.is_symlink() or backups.is_symlink():
        raise PermissionError("备份目录不能是符号链接")
    backups.mkdir(parents=True, exist_ok=True)
    if not backups.resolve().is_relative_to(base):
        raise PermissionError("备份目录超出 workspace")
    return backups


def _git(root: Path, *arguments: str, timeout: float = 8) -> subprocess.CompletedProcess:
    if not shutil.which("git"):
        raise FileNotFoundError("没有找到 Git，请先安装 Git for Windows")
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root.resolve()),
                "-c",
                "color.ui=false",
                "-c",
                "core.fsmonitor=false",
                *arguments,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError("Git 操作超时") from None
    if result.returncode:
        message = (result.stderr or result.stdout).strip()
        if "not a git repository" in message.lower():
            raise ValueError("当前 workspace 不是 Git 仓库")
        raise ValueError(message[:1000] or f"Git 退出码 {result.returncode}")
    return result


def register_coding_tools(registry: ToolRegistry, workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)

    @tool
    def search_workspace(
        query: Annotated[str, Field(min_length=1, max_length=240)],
        directory: Annotated[str, Field(max_length=240)] = ".",
        limit: Annotated[int, Field(ge=1, le=50)] = 25,
    ) -> dict:
        """在当前 workspace 搜索文件名和文本内容，忽略依赖、隐藏目录和二进制文件。"""
        folder = _target(workspace, directory)
        if not folder.is_dir():
            raise FileNotFoundError("搜索目录不存在")
        needle = query.casefold()
        hits = []
        scanned = 0
        scanned_directories = 0
        scanned_bytes = 0
        for current, dirs, files in os.walk(folder, followlinks=False):
            scanned_directories += 1
            if scanned_directories > 2000:
                return {"hits": hits, "scanned_files": scanned, "truncated": True}
            dirs[:] = [
                name
                for name in dirs
                if not name.startswith(".")
                and name not in IGNORED_DIRS
                and not (Path(current) / name).is_symlink()
            ]
            for filename in files:
                path = Path(current) / filename
                if filename.startswith(".") or path.is_symlink():
                    continue
                scanned += 1
                if scanned > 1000:
                    return {"hits": hits, "scanned_files": 1000, "truncated": True}
                relative = path.relative_to(workspace.resolve()).as_posix()
                if needle in filename.casefold():
                    hits.append({"path": relative, "kind": "filename"})
                    if len(hits) >= limit:
                        return {"hits": hits, "scanned_files": scanned, "truncated": True}
                suffix = path.suffix.casefold()
                if suffix not in TEXT_SUFFIXES and not filename.casefold().endswith(
                    ("makefile", ".gitignore", ".env.example")
                ):
                    continue
                try:
                    data = _read_bytes(path)
                    content = data.decode("utf-8-sig")
                except (OSError, UnicodeDecodeError, ValueError):
                    continue
                scanned_bytes += len(data)
                if scanned_bytes > 25_000_000:
                    return {"hits": hits, "scanned_files": scanned, "truncated": True}
                for line_number, line in enumerate(content.splitlines(), start=1):
                    if needle in line.casefold():
                        hits.append({"path": relative, "line": line_number, "text": line[:240]})
                        if len(hits) >= limit:
                            return {"hits": hits, "scanned_files": scanned, "truncated": True}
        return {"hits": hits, "scanned_files": scanned, "truncated": False}

    @tool(side_effect=True, always_confirm=True)
    def move_file(
        source: Annotated[str, Field(min_length=1, max_length=240)],
        destination: Annotated[str, Field(min_length=1, max_length=240)],
    ) -> dict:
        """在当前 workspace 内重命名或移动单个文件；目标必须不存在，每次都需确认。"""
        original = _target(workspace, source)
        target = _target(workspace, destination)
        if original == target:
            raise ValueError("源文件和目标路径相同")
        if not original.is_file():
            raise FileNotFoundError("源文件不存在或不是普通文件")
        if not target.parent.is_dir():
            raise FileNotFoundError("目标文件夹不存在")
        if target.exists():
            raise ValueError("目标文件已存在；为防覆盖，不能移动")

        # Reserve the destination exclusively before replacing the placeholder with
        # the source. This prevents accidental overwrites when two operations race.
        try:
            with target.open("xb"):
                pass
        except FileExistsError:
            raise ValueError("目标文件已存在；为防覆盖，不能移动") from None
        try:
            os.replace(original, target)
        except OSError:
            try:
                if target.is_file() and target.stat().st_size == 0:
                    target.unlink()
            except OSError:
                pass
            raise
        return {
            "source": source,
            "destination": destination,
            "moved": True,
        }

    @tool(side_effect=True, always_confirm=True)
    def copy_file(
        source: Annotated[str, Field(min_length=1, max_length=240)],
        destination: Annotated[str, Field(min_length=1, max_length=240)],
    ) -> dict:
        """在当前 workspace 内复制单个文件（最大 100 MB）；目标必须不存在，每次都需确认。"""
        original = _target(workspace, source)
        target = _target(workspace, destination)
        if original == target:
            raise ValueError("源文件和目标路径相同")
        if not original.is_file():
            raise FileNotFoundError("源文件不存在或不是普通文件")
        if original.stat().st_size > 100_000_000:
            raise ValueError("文件超过 100 MB，不能通过工具复制")
        if not target.parent.is_dir():
            raise FileNotFoundError("目标文件夹不存在")
        copied_bytes = 0
        try:
            with original.open("rb") as source_stream, target.open("xb") as target_stream:
                while chunk := source_stream.read(1024 * 1024):
                    copied_bytes += len(chunk)
                    if copied_bytes > 100_000_000:
                        raise ValueError("文件超过 100 MB，不能通过工具复制")
                    target_stream.write(chunk)
                target_stream.flush()
                os.fsync(target_stream.fileno())
            shutil.copystat(original, target, follow_symlinks=False)
        except FileExistsError:
            raise ValueError("目标文件已存在；为防覆盖，不能复制") from None
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return {
            "source": source,
            "destination": destination,
            "bytes": copied_bytes,
            "copied": True,
        }

    @tool(side_effect=True, always_confirm=True)
    def apply_file_patch(
        path: Annotated[str, Field(min_length=1, max_length=240)],
        old_text: Annotated[str, Field(min_length=1, max_length=12000)],
        new_text: Annotated[str, Field(max_length=12000)],
    ) -> dict:
        """将文件中唯一一段精确文本替换为新文本；先备份，返回可撤销 ID，每次都需确认。"""
        target = _target(workspace, path)
        if target.suffix.casefold() not in TEXT_SUFFIXES:
            raise PermissionError("仅允许修改常见文本/代码文件")
        if not target.is_file():
            raise FileNotFoundError("目标文件不存在")
        original = _read_bytes(target)
        try:
            content = original.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError("目标文件不是 UTF-8 文本，未作修改") from None
        occurrences = content.count(old_text)
        if occurrences != 1:
            raise ValueError(f"精确文本必须只出现一次；实际出现 {occurrences} 次，请先重新读取文件")
        updated = content.replace(old_text, new_text, 1)
        encoded = (
            "\ufeff" if original.startswith(b"\xef\xbb\xbf") else ""
        ).encode() + updated.encode("utf-8")
        if len(encoded) > 1_000_000:
            raise ValueError("修改后文件超过 1 MB")
        backup_id = uuid4().hex
        backups = _backup_dir(workspace)
        metadata = {
            "path": target.relative_to(workspace.resolve()).as_posix(),
            "original_base64": base64.b64encode(original).decode("ascii"),
            "updated_sha256": hashlib.sha256(encoded).hexdigest(),
        }
        (backups / f"{backup_id}.json").write_text(
            json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
        )
        try:
            _atomic_write(target, encoded)
        except Exception:
            (backups / f"{backup_id}.json").unlink(missing_ok=True)
            raise
        return {"path": metadata["path"], "backup_id": backup_id, "changed": True}

    @tool(side_effect=True, always_confirm=True)
    def undo_file_patch(backup_id: Annotated[str, Field(pattern=r"^[a-f0-9]{32}$")]) -> dict:
        """使用 apply_file_patch 返回的备份 ID 撤销修改；若文件后来又变动则拒绝覆盖。"""
        backup_file = _backup_dir(workspace) / f"{backup_id}.json"
        if not backup_file.is_file():
            raise FileNotFoundError("找不到这个修改备份，可能已撤销")
        metadata = json.loads(backup_file.read_text(encoding="utf-8"))
        target = _target(workspace, metadata["path"])
        if not target.is_file():
            raise FileNotFoundError("被修改的文件已不存在，不能自动撤销")
        current = _read_bytes(target)
        if hashlib.sha256(current).hexdigest() != metadata["updated_sha256"]:
            raise ValueError("文件在本次修改后又发生变化；为避免覆盖新内容，未撤销")
        original = base64.b64decode(metadata["original_base64"], validate=True)
        _atomic_write(target, original)
        backup_file.unlink()
        return {"path": metadata["path"], "restored": True}

    @tool(side_effect=True, always_confirm=True, timeout=65)
    async def run_command(
        program: Annotated[str, Field(min_length=1, max_length=80)],
        arguments: Annotated[list[str] | None, Field(max_length=40)] = None,
        working_directory: Annotated[str, Field(max_length=240)] = ".",
        timeout_seconds: Annotated[int, Field(ge=1, le=60)] = 20,
    ) -> dict:
        """在 workspace 内运行白名单开发命令，不经过 Shell；每次运行都需确认。"""
        if Path(program).name.casefold() not in ALLOWED_PROGRAMS or Path(program).name != program:
            raise PermissionError(
                "命令不在白名单中；允许 Python/uv/pytest/Ruff/Node/CMake/Git 等工具"
            )
        arguments = arguments or []
        if any(
            not isinstance(item, str) or len(item) > 2000 or "\x00" in item for item in arguments
        ):
            raise ValueError("命令参数无效或过长")
        if sum(map(len, arguments)) > 8000:
            raise ValueError("命令参数总长度不能超过 8000 字符")
        cwd = _target(workspace, working_directory)
        if not cwd.is_dir():
            raise FileNotFoundError("工作目录不存在")
        try:
            process = await asyncio.create_subprocess_exec(
                program,
                *arguments,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"当前环境找不到命令 {program}") from None
        try:
            stdout_task = asyncio.create_task(_capture_stream(process.stdout))
            stderr_task = asyncio.create_task(_capture_stream(process.stderr))
            await asyncio.wait_for(process.wait(), timeout_seconds)
            (stdout, stdout_cut), (stderr, stderr_cut) = await asyncio.gather(
                stdout_task, stderr_task
            )
        except TimeoutError:
            if process.returncode is None:
                process.kill()
            await process.wait()
            stdout_task.cancel()
            stderr_task.cancel()
            await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)
            raise TimeoutError(f"命令运行超过 {timeout_seconds} 秒，已终止") from None
        except asyncio.CancelledError:
            if process.returncode is None:
                process.kill()
            await process.wait()
            stdout_task.cancel()
            stderr_task.cancel()
            await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)
            raise
        return {
            "command": [program, *arguments],
            "working_directory": str(cwd),
            "exit_code": process.returncode,
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "truncated": stdout_cut or stderr_cut,
        }

    @tool
    def git_status() -> dict:
        """查看当前 workspace 的 Git 分支和未提交文件，不修改仓库。"""
        result = _git(workspace, "status", "--short", "--branch")
        return {"status": result.stdout[:12000]}

    @tool
    def git_diff(
        staged: bool = False,
        path: Annotated[str, Field(max_length=240)] = "",
    ) -> dict:
        """查看当前 workspace 的 Git 差异；不读取隐藏文件，不修改仓库。"""
        base_args = ["diff", "--no-ext-diff", "--no-textconv", "--no-renames"]
        if staged:
            base_args.append("--cached")
        if path:
            target = _target(workspace, path)
            if target.is_dir():
                raise ValueError("请指定单个文件查看差异")
            paths = [target.relative_to(workspace.resolve()).as_posix()]
        else:
            names = _git(workspace, *base_args, "--name-only", "-z")
            paths = []
            for candidate in names.stdout.split("\0"):
                if not candidate:
                    continue
                try:
                    target = _target(workspace, candidate)
                except (PermissionError, OSError):
                    continue
                paths.append(target.relative_to(workspace.resolve()).as_posix())
                if len(paths) >= 100:
                    break
        pieces = []
        total = 0
        truncated = len(paths) >= 100
        for candidate in paths:
            result = _git(workspace, *base_args, "--", candidate)
            total += len(result.stdout)
            if total > 14000:
                remaining = max(0, 14000 - sum(map(len, pieces)))
                if remaining:
                    pieces.append(result.stdout[:remaining])
                truncated = True
                break
            pieces.append(result.stdout)
        return {"diff": "".join(pieces), "truncated": truncated}

    @tool
    def git_log(limit: Annotated[int, Field(ge=1, le=30)] = 10) -> list[str]:
        """查看最近 Git 提交记录。"""
        result = _git(workspace, "log", f"-{limit}", "--oneline", "--decorate")
        return result.stdout.splitlines()

    @tool(side_effect=True, always_confirm=True)
    def git_create_branch(name: Annotated[str, Field(min_length=1, max_length=120)]) -> dict:
        """在当前 workspace 创建并切换到新 Git 分支；每次都需确认。"""
        checked = _git(workspace, "check-ref-format", "--branch", name)
        branch = checked.stdout.strip()
        _git(workspace, "switch", "-c", branch)
        return {"branch": branch, "created": True}

    @tool(side_effect=True, always_confirm=True)
    def git_commit(
        message: Annotated[str, Field(min_length=1, max_length=500)],
        paths: Annotated[list[str], Field(min_length=1, max_length=30)],
    ) -> dict:
        """只暂存并提交明确列出的 workspace 相对路径；不会自动提交全部文件。"""
        checked = []
        for path in paths:
            target = _target(workspace, path)
            if not target.is_file():
                raise ValueError(f"只能提交明确列出的文件: {path}")
            checked.append(target.relative_to(workspace.resolve()).as_posix())
        _git(workspace, "add", "--", *checked)
        result = _git(workspace, "commit", "-m", message, timeout=30)
        return {"committed": True, "paths": checked, "summary": result.stdout[-2000:]}

    @tool
    def list_skills() -> list[dict]:
        """列出 workspace/.agents/skills 中可加载的 Skill；Skill 只包含说明，不执行脚本。"""
        skills_root = _skills_root(workspace)
        if skills_root is None:
            return []
        found = []
        for folder in sorted(skills_root.iterdir()):
            if len(found) >= 100:
                break
            skill_file = folder / "SKILL.md"
            if (
                folder.is_symlink()
                or not folder.is_dir()
                or skill_file.is_symlink()
                or not skill_file.is_file()
            ):
                continue
            try:
                text = _read_bytes(skill_file, maximum=20000).decode("utf-8-sig")
            except (OSError, UnicodeDecodeError, ValueError):
                continue
            summary = next(
                (
                    line.strip(" #\t")
                    for line in text.splitlines()
                    if line.strip() and not line.startswith("---")
                ),
                "",
            )
            found.append({"name": folder.name, "summary": summary[:240]})
        return found

    @tool
    def read_skill(name: Annotated[str, Field(min_length=1, max_length=80)]) -> dict:
        """读取 workspace/.agents/skills/<名称>/SKILL.md；不会执行 Skill 中的代码。"""
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
            raise ValueError("Skill 名称只能包含字母、数字、下划线和连字符")
        skills_root = _skills_root(workspace)
        if skills_root is None:
            raise FileNotFoundError("没有找到可用的 workspace Skill 目录")
        skill_file = skills_root / name / "SKILL.md"
        if (
            (skills_root / name).is_symlink()
            or skill_file.is_symlink()
            or not skill_file.resolve().is_relative_to(skills_root)
            or not skill_file.is_file()
        ):
            raise FileNotFoundError("没有找到这个 Skill 的 SKILL.md")
        try:
            content = _read_bytes(skill_file, maximum=20000).decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError("Skill 文件必须是 UTF-8 文本") from None
        return {"name": name, "content": content}

    @tool(side_effect=True, always_confirm=True, timeout=35)
    async def browser_read_page(
        url: Annotated[str, Field(min_length=8, max_length=2048)],
    ) -> dict:
        """经确认后用无痕 Edge/Chromium 打开网页并读取可见 DOM 文本与链接，不执行点击或表单提交。"""
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("只允许打开完整的 HTTP 或 HTTPS 网页地址")
        if parsed.username or parsed.password:
            raise ValueError("网址中不能包含用户名或密码")
        try:
            from playwright.async_api import (
                TimeoutError as PlaywrightTimeoutError,
            )
            from playwright.async_api import (
                async_playwright,
            )
        except ImportError:
            raise ValueError("浏览器读取需要可选依赖：uv sync --extra browser") from None

        async with async_playwright() as playwright:
            try:
                if os.name == "nt":
                    try:
                        browser = await playwright.chromium.launch(channel="msedge", headless=True)
                    except Exception:
                        browser = await playwright.chromium.launch(headless=True)
                else:
                    browser = await playwright.chromium.launch(headless=True)
            except Exception:
                raise ValueError(
                    "无法启动浏览器；请安装 Microsoft Edge，或运行 playwright install chromium"
                ) from None
            try:
                context = await browser.new_context()

                async def allow_web_protocol(route):
                    request_url = urlsplit(route.request.url)
                    if (
                        request_url.scheme not in {"http", "https"}
                        or request_url.username
                        or request_url.password
                    ):
                        await route.abort("blockedbyclient")
                    else:
                        await route.continue_()

                await context.route("**/*", allow_web_protocol)
                page = await context.new_page()
                response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                try:
                    await page.wait_for_load_state("networkidle", timeout=1500)
                except PlaywrightTimeoutError:
                    pass
                body = await page.locator("body").inner_text(timeout=3000)
                links = await page.locator("a:visible").evaluate_all(
                    "elements => elements.slice(0, 80).map(a => {"
                    "const text = (a.innerText || a.getAttribute('aria-label') || '').trim();"
                    "return {text: text.slice(0, 120), href: a.href}; })"
                )
                return {
                    "url": page.url,
                    "title": (await page.title())[:300],
                    "status": response.status if response else None,
                    "text": body[:12000],
                    "links": links,
                    "truncated": len(body) > 12000,
                }
            except PlaywrightTimeoutError:
                raise ValueError("网页加载或读取超时") from None
            finally:
                await browser.close()

    for entry in (
        search_workspace,
        move_file,
        copy_file,
        apply_file_patch,
        undo_file_patch,
        run_command,
        git_status,
        git_diff,
        git_log,
        git_create_branch,
        git_commit,
        list_skills,
        read_skill,
        browser_read_page,
    ):
        registry.register(entry)
