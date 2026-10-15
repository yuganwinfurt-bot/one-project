from importlib.resources import files
from types import SimpleNamespace

import pytest

from yugan_agent.builtins import register_builtins, safe_path
from yugan_agent.tools import ToolRegistry
from yugan_agent.workflow import Workflow, WorkflowRunner


def load_demo():
    return Workflow.model_validate_json(
        files("yugan_agent").joinpath("data/greenhouse.json").read_text(encoding="utf-8")
    )


@pytest.mark.asyncio
async def test_greenhouse_branches_and_bounded_loop(tmp_path):
    registry = ToolRegistry()
    register_builtins(registry, tmp_path, {})
    runner = WorkflowRunner(registry)
    workflow = load_demo()
    hot = await runner.run(workflow)
    cool = await runner.run(workflow, {"temperatures": [20.0, 22.0]})
    assert hot.status == cool.status == "completed"
    assert hot.state["alert"] is True
    assert cool.state["alert"] is False
    assert hot.state["checks"] == cool.state["checks"] == 3
    assert "too_hot -->|是| advise_cooling" in workflow.mermaid()


def test_invalid_graph_rejected():
    with pytest.raises(ValueError, match="不存在"):
        Workflow.model_validate(
            {
                "name": "bad",
                "start": "one",
                "nodes": [
                    {"id": "one", "kind": "set", "values": {}, "next": "missing"},
                ],
            }
        )


def test_file_tool_cannot_escape_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    with pytest.raises(PermissionError):
        safe_path(workspace, "../outside.txt")
    with pytest.raises(PermissionError):
        safe_path(workspace, str(tmp_path / "outside.txt"))
    with pytest.raises(PermissionError):
        safe_path(workspace, ".env")


@pytest.mark.asyncio
async def test_loop_stops_at_limit(tmp_path):
    workflow = Workflow.model_validate(
        {
            "name": "loop",
            "start": "again",
            "max_steps": 3,
            "nodes": [{"id": "again", "kind": "set", "values": {}, "next": "again"}],
        }
    )
    result = await WorkflowRunner(ToolRegistry()).run(workflow)
    assert result.status == "limited"
    assert len(result.trace) == 3


@pytest.mark.asyncio
async def test_agent_workflow_stops_before_later_steps_after_denial():
    class DenyingAgent:
        def __init__(self):
            self.calls = []

        async def run(self, prompt, session_id):
            self.calls.append((prompt, session_id))
            if prompt == "第二步":
                return SimpleNamespace(status="limited", answer="用户拒绝了电脑操作")
            return SimpleNamespace(status="completed", answer="已完成")

    agent = DenyingAgent()
    workflow = Workflow.model_validate(
        {
            "name": "电脑任务",
            "start": "first",
            "nodes": [
                {
                    "id": "first",
                    "kind": "agent",
                    "prompt": "第一步",
                    "output": "one",
                    "next": "second",
                },
                {
                    "id": "second",
                    "kind": "agent",
                    "prompt": "第二步",
                    "output": "two",
                    "next": "third",
                },
                {"id": "third", "kind": "agent", "prompt": "第三步", "output": "three"},
            ],
        }
    )
    result = await WorkflowRunner(ToolRegistry(), agent).run(workflow, session_id="computer_1")
    assert result.status == "error"
    assert result.error == "用户拒绝了电脑操作"
    assert agent.calls == [("第一步", "computer_1"), ("第二步", "computer_1")]
    assert result.state["one"] == "已完成"
    assert "two" not in result.state


@pytest.mark.asyncio
async def test_invalid_csv_value_returns_tool_failure(tmp_path):
    (tmp_path / "sensor.csv").write_text("temperature\n30\nnot-a-number\n", encoding="utf-8")
    registry = ToolRegistry()
    register_builtins(registry, tmp_path, {})
    result = await registry.execute("csv_summary", {"path": "sensor.csv", "column": "temperature"})
    assert result.ok is False
