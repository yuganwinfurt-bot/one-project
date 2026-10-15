"""JSON 工作流：工具节点、状态节点、条件分支、Agent 节点和有界循环。"""

import copy
import json
import operator
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .agent import Agent
from .tools import ToolRegistry


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$")


class ToolNode(Node):
    kind: Literal["tool"]
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    output: str
    next: str | None = None


class SetNode(Node):
    kind: Literal["set"]
    values: dict[str, Any]
    next: str | None = None


class ConditionNode(Node):
    kind: Literal["condition"]
    left: Any
    op: Literal["eq", "ne", "gt", "ge", "lt", "le", "contains"]
    right: Any
    then: str | None
    otherwise: str | None


class AgentNode(Node):
    kind: Literal["agent"]
    prompt: str | dict
    output: str
    next: str | None = None


class Workflow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    start: str
    max_steps: int = Field(default=50, ge=1, le=500)
    initial_state: dict[str, Any] = Field(default_factory=dict)
    nodes: list[
        Annotated[ToolNode | SetNode | ConditionNode | AgentNode, Field(discriminator="kind")]
    ] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_graph(self):
        names = [n.id for n in self.nodes]
        if len(set(names)) != len(names):
            raise ValueError("节点 ID 不能重复")
        if self.start not in names:
            raise ValueError("start 不是有效节点")
        for node in self.nodes:
            targets = (
                [node.then, node.otherwise] if isinstance(node, ConditionNode) else [node.next]
            )
            if any(target is not None and target not in names for target in targets):
                raise ValueError(f"节点 {node.id} 指向了不存在的节点")
        return self

    def mermaid(self) -> str:
        lines = ["flowchart TD"]
        for node in self.nodes:
            lines.append(f'  {node.id}["{node.id} · {node.kind}"]')
            if isinstance(node, ConditionNode):
                for target, label in ((node.then, "是"), (node.otherwise, "否")):
                    if target is not None:
                        lines.append(f"  {node.id} -->|{label}| {target}")
            elif node.next is not None:
                lines.append(f"  {node.id} --> {node.next}")
        return "\n".join(lines)


def resolve(value: Any, state: dict, depth: int = 0) -> Any:
    if depth > 20:
        raise ValueError("工作流表达式嵌套超过 20 层")
    if isinstance(value, dict):
        if set(value) == {"$ref"}:
            current = state
            for part in value["$ref"].split("."):
                current = current[part]
            return copy.deepcopy(current)
        if set(value) == {"$add"}:
            operands = resolve(value["$add"], state, depth + 1)
            if len(operands) != 2 or any(type(v) not in (int, float) for v in operands):
                raise ValueError("$add 需要两个数值")
            return operands[0] + operands[1]
        return {k: resolve(v, state, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v, state, depth + 1) for v in value]
    return value


class WorkflowResult(BaseModel):
    name: str
    status: Literal["completed", "limited", "error"]
    state: dict[str, Any]
    trace: list[dict]
    error: str | None = None


class WorkflowRunner:
    def __init__(self, tools: ToolRegistry, agent: Agent | None = None):
        self.tools, self.agent = tools, agent

    async def run(
        self, workflow: Workflow, state: dict | None = None, *, session_id: str | None = None
    ) -> WorkflowResult:
        data = copy.deepcopy({**workflow.initial_state, **(state or {})})
        trace = []
        nodes = {n.id: n for n in workflow.nodes}
        current = workflow.start
        operations = {
            "eq": operator.eq,
            "ne": operator.ne,
            "gt": operator.gt,
            "ge": operator.ge,
            "lt": operator.lt,
            "le": operator.le,
            "contains": operator.contains,
        }
        try:
            for step in range(1, workflow.max_steps + 1):
                if current is None:
                    break
                node = nodes[current]
                item = {"step": step, "node": current, "kind": node.kind}
                trace.append(item)
                if isinstance(node, ToolNode):
                    result = await self.tools.execute(node.tool, resolve(node.arguments, data))
                    if not result.ok:
                        raise ValueError(f"工具 {node.tool}: {result.error}")
                    data[node.output] = result.data
                    current = node.next
                elif isinstance(node, SetNode):
                    data.update(resolve(node.values, data))
                    current = node.next
                elif isinstance(node, ConditionNode):
                    matched = operations[node.op](
                        resolve(node.left, data), resolve(node.right, data)
                    )
                    item["matched"] = matched
                    current = node.then if matched else node.otherwise
                elif isinstance(node, AgentNode):
                    if self.agent is None:
                        raise ValueError("Agent 节点需要提供 agent 实例")
                    from uuid import uuid4

                    prompt = resolve(node.prompt, data)
                    if not isinstance(prompt, str):
                        raise ValueError("Agent prompt 必须解析为字符串")
                    result = await self.agent.run(prompt, session_id or "wf_" + uuid4().hex)
                    if result.status != "completed":
                        raise ValueError(result.answer)
                    data[node.output] = result.answer
                    current = node.next
                if len(json.dumps(data, ensure_ascii=False, allow_nan=False)) > 100000:
                    raise ValueError("工作流状态超过 100000 字符")
            status = "completed" if current is None else "limited"
            return WorkflowResult(
                name=workflow.name,
                status=status,
                state=data,
                trace=trace,
                error=None if current is None else "达到工作流最大步数，循环已停止",
            )
        except Exception as exc:
            # 工具层已净化异常；未知异常只展示类型。
            error = (
                str(exc)[:500] if isinstance(exc, (ValueError, KeyError)) else type(exc).__name__
            )
            return WorkflowResult(
                name=workflow.name, status="error", state=data, trace=trace, error=error
            )
