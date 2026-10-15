from yugan_agent.config import Settings
from yugan_agent.runtime import build_tool_registry


def test_coding_tools_are_registered_with_clear_write_gates(tmp_path):
    registry = build_tool_registry(Settings(workspace=tmp_path))
    names = {tool["name"] for tool in registry.schemas()}

    assert {
        "search_workspace",
        "apply_file_patch",
        "undo_file_patch",
        "run_command",
        "git_status",
        "git_diff",
        "git_log",
        "git_create_branch",
        "git_commit",
        "list_skills",
        "read_skill",
        "browser_read_page",
    } <= names
    for name in (
        "apply_file_patch",
        "undo_file_patch",
        "run_command",
        "git_create_branch",
        "git_commit",
        "browser_read_page",
    ):
        assert registry._tools[name].side_effect
        assert registry._tools[name].always_confirm
    assert registry._tools["run_command"].timeout >= 60
