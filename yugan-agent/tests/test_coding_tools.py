import asyncio
import shutil
import subprocess

import pytest

from yugan_agent.coding_tools import register_coding_tools
from yugan_agent.tools import ToolRegistry


def coding_registry(tmp_path, *, approve=True):
    async def approval(name, description, arguments):
        approvals.append((name, arguments))
        return approve

    approvals = []
    registry = ToolRegistry(timeout=10, approval_callback=approval)
    register_coding_tools(registry, tmp_path)
    return registry, approvals


@pytest.mark.asyncio
async def test_search_workspace_ignores_hidden_and_dependency_files(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "agent.py").write_text("def target(): pass\n", encoding="utf-8")
    (tmp_path / ".secret").mkdir()
    (tmp_path / ".secret" / "note.md").write_text("target", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "note.js").write_text("target", encoding="utf-8")
    registry, _ = coding_registry(tmp_path)

    result = await registry.execute("search_workspace", {"query": "target"})

    assert result.ok
    assert [hit["path"] for hit in result.data["hits"]] == ["src/agent.py"]


@pytest.mark.asyncio
async def test_patch_requires_approval_and_can_be_undone(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("answer = 1\n", encoding="utf-8")
    registry, approvals = coding_registry(tmp_path)

    changed = await registry.execute(
        "apply_file_patch",
        {"path": "sample.py", "old_text": "answer = 1", "new_text": "answer = 2"},
    )
    assert changed.ok
    assert file.read_text(encoding="utf-8") == "answer = 2\n"
    assert approvals[-1][0] == "apply_file_patch"

    undone = await registry.execute("undo_file_patch", {"backup_id": changed.data["backup_id"]})
    assert undone.ok
    assert file.read_text(encoding="utf-8") == "answer = 1\n"
    assert approvals[-1][0] == "undo_file_patch"


@pytest.mark.asyncio
async def test_move_and_copy_files_require_confirmation_and_refuse_overwrite(tmp_path):
    source = tmp_path / "HelloWorld.txt"
    source.write_text('print("Hello World")', encoding="utf-8")
    registry, approvals = coding_registry(tmp_path)

    copied = await registry.execute(
        "copy_file", {"source": "HelloWorld.txt", "destination": "HelloWorld-copy.py"}
    )
    moved = await registry.execute(
        "move_file", {"source": "HelloWorld.txt", "destination": "HelloWorld.py"}
    )
    overwrite = await registry.execute(
        "copy_file", {"source": "HelloWorld.py", "destination": "HelloWorld-copy.py"}
    )

    assert copied.ok and (tmp_path / "HelloWorld-copy.py").read_text() == 'print("Hello World")'
    assert moved.ok and not source.exists() and (tmp_path / "HelloWorld.py").is_file()
    assert not overwrite.ok and "已存在" in overwrite.error
    assert [item[0] for item in approvals] == ["copy_file", "move_file", "copy_file"]


@pytest.mark.asyncio
async def test_patch_does_not_write_when_user_denies(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("answer = 1\n", encoding="utf-8")
    registry, approvals = coding_registry(tmp_path, approve=False)

    result = await registry.execute(
        "apply_file_patch",
        {"path": "sample.py", "old_text": "answer = 1", "new_text": "answer = 2"},
    )

    assert not result.ok
    assert file.read_text(encoding="utf-8") == "answer = 1\n"
    assert approvals[-1][0] == "apply_file_patch"


@pytest.mark.asyncio
async def test_patch_refuses_ambiguous_or_modified_paths(tmp_path):
    (tmp_path / "duplicate.txt").write_text("x x", encoding="utf-8")
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("safe", encoding="utf-8")
    try:
        (tmp_path / "link.txt").symlink_to(outside)
    except OSError:
        pytest.skip("当前 Windows 环境不允许创建符号链接")
    registry, _ = coding_registry(tmp_path)

    ambiguous = await registry.execute(
        "apply_file_patch", {"path": "duplicate.txt", "old_text": "x", "new_text": "y"}
    )
    escaped = await registry.execute(
        "apply_file_patch", {"path": "link.txt", "old_text": "safe", "new_text": "bad"}
    )
    assert not ambiguous.ok and "只出现一次" in ambiguous.error
    assert not escaped.ok and "符号链接" in escaped.error
    assert outside.read_text(encoding="utf-8") == "safe"


@pytest.mark.asyncio
async def test_patch_undo_refuses_to_overwrite_later_changes(tmp_path):
    file = tmp_path / "sample.md"
    file.write_text("before", encoding="utf-8")
    registry, _ = coding_registry(tmp_path)
    changed = await registry.execute(
        "apply_file_patch", {"path": "sample.md", "old_text": "before", "new_text": "after"}
    )
    file.write_text("someone else's update", encoding="utf-8")

    undone = await registry.execute("undo_file_patch", {"backup_id": changed.data["backup_id"]})

    assert not undone.ok and "又发生变化" in undone.error
    assert file.read_text(encoding="utf-8") == "someone else's update"


@pytest.mark.asyncio
async def test_command_uses_explicit_approval_and_no_shell(tmp_path):
    registry, approvals = coding_registry(tmp_path)
    result = await registry.execute(
        "run_command",
        {"program": "python", "arguments": ["--version"], "timeout_seconds": 5},
    )
    assert result.ok
    assert result.data["exit_code"] == 0
    assert result.data["stdout"].strip().startswith("Python ")
    assert approvals[-1][0] == "run_command"

    rejected_shell = await registry.execute(
        "run_command", {"program": "cmd.exe", "arguments": ["/c", "whoami"]}
    )
    assert not rejected_shell.ok
    assert "白名单" in rejected_shell.error


@pytest.mark.asyncio
async def test_command_can_be_cancelled_without_leaving_child_process(tmp_path):
    registry, _ = coding_registry(tmp_path)
    task = asyncio.create_task(
        registry.execute(
            "run_command",
            {
                "program": "python",
                "arguments": ["-c", "import time; time.sleep(20)"],
                "timeout_seconds": 30,
            },
        )
    )
    await asyncio.sleep(0.1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_git_tools_read_state_and_confirmation_protects_writes(tmp_path):
    if not shutil.which("git"):
        pytest.skip("Git is not installed")
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"], check=True
    )
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    (tmp_path / "a.txt").write_text("first\n", encoding="utf-8")
    (tmp_path / ".env").write_text("old-secret\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "--", "a.txt", ".env"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "initial"],
        check=True,
        capture_output=True,
    )
    registry, approvals = coding_registry(tmp_path)
    (tmp_path / "a.txt").write_text("second\n", encoding="utf-8")
    (tmp_path / ".env").write_text("new-secret\n", encoding="utf-8")

    async def check_git_tools():
        status = await registry.execute("git_status", "{}")
        diff = await registry.execute("git_diff", "{}")
        branch = await registry.execute("git_create_branch", {"name": "feature/test-agent"})
        return status, diff, branch

    status, diff, branch = asyncio.run(check_git_tools())

    assert status.ok and "a.txt" in status.data["status"]
    assert diff.ok and "+second" in diff.data["diff"]
    assert "secret" not in diff.data["diff"]
    assert branch.ok and branch.data["branch"] == "feature/test-agent"
    assert approvals[-1][0] == "git_create_branch"


@pytest.mark.asyncio
async def test_skills_are_loaded_as_text_only(tmp_path):
    skill_dir = tmp_path / ".agents" / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\n---\nUse pytest first.\n", encoding="utf-8"
    )
    registry, _ = coding_registry(tmp_path)

    found = await registry.execute("list_skills", "{}")
    loaded = await registry.execute("read_skill", {"name": "test-skill"})

    assert found.ok and found.data[0]["name"] == "test-skill"
    assert loaded.ok and "Use pytest first" in loaded.data["content"]


@pytest.mark.asyncio
async def test_browser_tool_rejects_non_web_schemes(tmp_path):
    registry, approvals = coding_registry(tmp_path)

    result = await registry.execute("browser_read_page", {"url": "file:///private/data"})

    assert not result.ok and "HTTP 或 HTTPS" in result.error
    assert approvals[-1][0] == "browser_read_page"
