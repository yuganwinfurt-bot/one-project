"""LangGraph 共享状态（教学用 TypedDict，字段尽量直白）。"""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """一次对话分析在图里流转的全部数据。"""

    # 输入
    question: str
    conversation_history: list[dict[str, str]]
    product_names: list[str]
    user_id: int | None
    run_id: int | None
    use_agent_model: bool

    # 路由
    route: str
    route_reason: str
    route_signals: dict[str, Any]

    # 结构化查询结果
    sql: str | None
    structured_rows: list[dict[str, Any]]
    structured_row_count: int
    structured_truncated: bool

    # 语义检索结果（首轮或深挖）
    semantic_hits: list[dict[str, Any]]
    semantic_row_count: int
    semantic_failed: bool

    # 多轮：结构化发现异常后，是否再查语义
    need_deepen: bool
    deepen_reason: str

    # 汇总给大模型的证据
    evidence: list[dict[str, Any]]
    evidence_source: str  # structured / semantic / mixed

    # lesson-09：经 MCP 查到的相关历史运行（可选）
    recent_logs: list[dict[str, Any]]

    # lesson-10：多智能体协作
    current_agent: str  # scheduler / analysis / decision
    agent_label: str  # 中文显示名
    next_agent: str  # 调度节点指定的下一个 Agent

    # lesson-07：行动与人工确认
    pending_actions: list[dict[str, Any]]
    risk_level: str
    need_human_confirm: bool
    decide_reason: str
    product_id: int | None
    low_rating_count: int
    human_approved: bool | None
    actions_executed: list[dict[str, Any]]

    # 节点给前端看的一句话状态（可选）
    status_message: str

    # 相关度兜底（lesson：无关问题不写报告、直接回引导语）
    best_distance: float | None  # 语义证据里的最小向量距离（越小越相关）
    low_relevance: bool  # 语义证据与问题相关性不足时置 True

    # 结构化查询失败时改走语义兜底（避免整轮报错）
    structured_failed: bool
    structured_fail_reason: str
    statistics_unavailable: bool  # SQL 失败后不能用语义片段代替统计
    target_product_ids: list[int]  # 深挖限定的已知商品
