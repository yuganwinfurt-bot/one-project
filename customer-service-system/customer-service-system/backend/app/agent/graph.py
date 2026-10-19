"""LangGraph 图定义（lesson-06～10）。

流程图（lesson-10 起带多智能体调度）：

    START → scheduler_start
         → 查询分析 Agent：route → structured/semantic → … → prepare_evidence
         → scheduler_handoff
         → 报告决策 Agent：decide_actions → execute_automatic_actions → confirm_gate → execute_actions
         → END

人工确认依赖 MemorySaver checkpointer + thread_id。
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent import analysis_agent, decision_agent, scheduler
from app.agent.state import AgentState

import functools
from typing import Any

# 异常透出时挂在异常对象上的节点名字段名（chat_service 用它定位 failed_node）
FAILED_NODE_ATTR = "_failed_node"


def tag_node_failure(
    node_name: str, func: Any
) -> Any:
    """包一层节点函数：异常透出前把节点名挂到异常上。

    背景：图 stream 过程中某节点抛异常时，该节点不会产出 update，
    chat_service 的 current_node 还停在上一个节点。用包装函数携带真实出错节点，
    不改变 add_node(name, func) 的调用方式与节点签名。
    """

    @functools.wraps(func)
    def _wrapped(state: AgentState) -> dict[str, Any]:
        try:
            return func(state)
        except Exception as exc:
            setattr(exc, FAILED_NODE_ATTR, node_name)
            raise

    return _wrapped

_compiled_graph = None
_checkpointer = MemorySaver()


def build_analysis_graph():
    """搭建并编译分析图（带检查点，支持中断恢复）。"""
    graph = StateGraph(AgentState)

    # —— 调度 ——
    graph.add_node(
        "scheduler_start",
        tag_node_failure("scheduler_start", scheduler.node_scheduler_start),
    )
    graph.add_node(
        "scheduler_handoff",
        tag_node_failure("scheduler_handoff", scheduler.node_scheduler_handoff),
    )

    # —— 查询分析 Agent ——
    graph.add_node(
        "route_question",
        tag_node_failure("route_question", analysis_agent.route_question),
    )
    graph.add_node(
        "structured_query",
        tag_node_failure("structured_query", analysis_agent.structured_query),
    )
    graph.add_node(
        "semantic_query",
        tag_node_failure("semantic_query", analysis_agent.semantic_query),
    )
    graph.add_node(
        "judge_deepen",
        tag_node_failure("judge_deepen", analysis_agent.judge_deepen),
    )
    graph.add_node(
        "deepen_semantic",
        tag_node_failure("deepen_semantic", analysis_agent.deepen_semantic),
    )
    graph.add_node(
        "prepare_evidence",
        tag_node_failure("prepare_evidence", analysis_agent.prepare_evidence),
    )

    # —— 报告决策 Agent ——
    graph.add_node(
        "decide_actions",
        tag_node_failure("decide_actions", decision_agent.decide_actions),
    )
    graph.add_node(
        "execute_automatic_actions",
        tag_node_failure("execute_automatic_actions", decision_agent.execute_automatic_actions),
    )
    graph.add_node(
        "confirm_gate", tag_node_failure("confirm_gate", decision_agent.confirm_gate)
    )
    graph.add_node(
        "execute_actions",
        tag_node_failure("execute_actions", decision_agent.execute_actions),
    )

    graph.add_edge(START, "scheduler_start")
    graph.add_edge("scheduler_start", "route_question")
    graph.add_conditional_edges(
        "route_question",
        analysis_agent.select_query_branch,
        {
            "structured": "structured_query",
            "semantic": "semantic_query",
            "conversation": "prepare_evidence",
        },
    )
    # 结构化查询失败（SQL 生成/校验/执行出错）时改走语义检索兜底，而不是整轮报错
    graph.add_conditional_edges(
        "structured_query",
        analysis_agent.select_after_structured,
        {
            "continue": "judge_deepen",
            "fallback": "semantic_query",
        },
    )
    graph.add_edge("semantic_query", "prepare_evidence")
    graph.add_conditional_edges(
        "judge_deepen",
        analysis_agent.select_after_judge,
        {
            "deepen": "deepen_semantic",
            "prepare": "prepare_evidence",
        },
    )
    graph.add_edge("deepen_semantic", "prepare_evidence")
    graph.add_edge("prepare_evidence", "scheduler_handoff")
    graph.add_edge("scheduler_handoff", "decide_actions")
    graph.add_edge("decide_actions", "execute_automatic_actions")
    graph.add_edge("execute_automatic_actions", "confirm_gate")
    graph.add_edge("confirm_gate", "execute_actions")
    graph.add_edge("execute_actions", END)

    return graph.compile(checkpointer=_checkpointer)


def get_analysis_graph():
    """获取编译后的图（懒加载单例，共用同一 checkpointer）。"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_analysis_graph()
    return _compiled_graph


def reset_analysis_graph() -> None:
    """测试用：清空单例，强制重建。"""
    global _compiled_graph, _checkpointer
    _compiled_graph = None
    _checkpointer = MemorySaver()
