"""由模型规划查询范围与证据来源；本模块不生成业务回答。"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.agent.context import prepare_history
from app.services.nl2sql.prompt import DATABASE_SCHEMA
from app.utils.llm import chat_once
from app.services.nl2sql.validate import validate_sql

logger = logging.getLogger(__name__)

ROUTE_STRUCTURED = "structured"
ROUTE_SEMANTIC = "semantic"
ROUTE_CONVERSATION = "conversation"
ROUTE_MANAGEMENT = "management"

QUERY_PLAN_PROMPT = """
你是电商问答的查询规划器，只输出一个 JSON 对象，不回答用户问题，不输出 SQL。
根据用户当前问题的含义选择证据来源，而不是按问句模板匹配答案。

证据工具：
- structured：实时数据库，只读查询；适合精确条件、时间范围、统计、列表、比较和最新状态。
- semantic：知识库中的业务记录、评论图片描述、功能规则等资料；适合寻找相关内容、解释规则。
- conversation：不需要业务数据的对话、澄清或无法执行的请求，不调用数据工具，仍由回答模型生成回复。
- management：后台业务操作，包括新建/上架/下架商品、多规格、价格库存、商品品牌类目、订单发货、取消待付款结算、售后处理和沟通、评价/反馈回复、推广内容和优惠券增删改、通知已读、风险检查、知识库同步、业务日志回退、商城/运费/订单/小程序配置。由业务工具读取实时资料并生成待确认方案；禁止修改用户、管理员、运营账号、密码和角色权限。涉及请求执行上述操作或询问 AI 可操作范围时用本路由，不生成 SQL。
需要两类证据时选择 structured，并设置 needs_semantic=true。
精确数量、排名、完整列表和实时状态应使用数据库；语义 Top K 只能提供候选，不能替代全量统计。

规划要求：
- 保留当前问题的商品、类目、指标、时间、数量限制、排除条件和比较对象，不擅自改成全店巡检。
- 只选择与问题有关的业务维度，不因出现“问题/关注/异常”等词就套用统一指标清单。
- 质量、服务、库存、履约等维度含义不同；证据必须与所问维度有关。
- 需要解释原因或判断反馈含义时，应读取相关正文，不能仅凭评分或售后次数认定原因。
- 结合提供的业务时间解释相对日期。模糊时间可采用合理范围，但必须在 time_scope 明说假设，
  并在 retrieval_question 中保留该范围；不能把“最近”静默当成全部历史。
- 不随意添加 Top N 或只选少数商品；全量诉求标记 requires_complete_data=true。
- products 只填明确提及的已知商品全名；没有指定商品时留空，不能自行挑选几个商品。
- retrieval_question 是保留全部约束的独立查询需求；semantic_query 是保留主题及约束的资料检索词。
- 原始问题优先于历史主题。先理解当前句完整主语及指示词修饰的名词，不能把指示词机械替换成上轮商品。
  当前问题已经明确对象或切换话题时，不继承旧对象；只有当前句确实省略对象时才结合最近对话消解指代。
  助手历史回答提到过某个商品不代表用户选中了它；多个可能对象无法确定时，应澄清，不强行选择。
  context_reason 简述如何理解本轮语境；retrieval_question 只能补充必要的指代，不能替代或歪曲原始问题。
- doc_types 从下述资料类型选择与本轮问题有关的类型，空列表表示不限制类型。资料类型只是检索工具参数，
  不能据此预设答案。功能/规则资料与具体业务记录应按问题选择，不能把商品记录用作平台功能说明。
- analyze_business_records 只有本轮实际分析业务记录时才为 true；介绍功能、解释规则、澄清和闲聊为 false，
  避免仅因检索候选里出现低分评价就触发诊断报告或商品预警。
- request_diagnostics 只有用户明确要求生成诊断报告、巡检或处理风险时才为 true。
  普通查询评价、销量、订单等仅获取数据并回答，不因包含低分记录就要求生成报告/预警。
- structured 路由同时生成 sql，一次完成理解和 SQL 规划；其他路由 sql=null。
  SQL 必须是一条 SELECT，仅查询下面的业务表，不读个人信息、凭证或通配字段。
  保留所问条件、事件发生时间及数量要求，明细带对象名及记录 ID；评价明细保留 review_id、product_id、rating、content。
  聚合只选择分组列或聚合函数；多张一对多表分别聚合再关联，避免重复计数；不得使用 WITH、UNION、变量或锁定读取。
  默认最多 LIMIT 200，用户指定数量则遵从，不能自定少量商品代替完整结果。
- 不得自行执行写操作或泄露账户凭证；management 只规划并交给后台配置工具读取与生成待确认方案，最终权限由服务端校验。

输出格式（布尔值使用 JSON true/false）：
{"route":"structured|semantic|conversation|management","reason":"选择依据",
 "analysis_scope":"本次分析的业务范围","time_scope":"时间范围或不适用",
 "retrieval_question":"完整查询需求","semantic_query":"资料检索词",
 "products":[],"needs_semantic":false,"requires_complete_data":false,
 "context_reason":"本轮语境理解","doc_types":[],"analyze_business_records":false,\n "sql":null,"request_diagnostics":false}

资料类型：
platform_feature（功能与业务规则）、product（商品资料）、order（订单）、review（商品评价）、
review_reply（追加与回复）、after_sale（售后申请）、after_sale_message（售后沟通）、
after_sale_risk（售后风险汇总）、inventory_state（库存监测）、alert（预警）、diagnosis_report（历史报告）、
platform_log（操作日志）、agent_run（历史问答）、agent_step（执行步骤）、agent_feedback（问答反馈）、
favorite（收藏）、cart_item（购物车）、restock_notice（到货通知）、customer_notice（降价通知）、
shipment_notice（发货通知）、review_notice（评论通知）、staff_notice（商家通知）、
direct_conversation（私聊会话）、direct_message（私聊消息）、user_summary（匿名用户概况）、address_summary（收货区域）、
cart_variant（规格购物车）、brand（品牌）、catalog_category（商品类目）、product_catalog（商品品牌类目归属）、
faq（通用问题）、search_keyword（商城关键词）、advertisement（广告）、topic（专题）、
coupon（优惠券规则）、coupon_claim（领取核销）、coupon_stock（发券库存）、order_promotion（订单优惠运费）、
group_rule（团购规则）、group_purchase（团购活动）、group_member（匿名团购成员）、
customer_footprint（浏览足迹）、customer_search（搜索历史）、mall_feedback（意见反馈与回复）、
mall_notice（商城公告）、role_definition（角色模块权限）、staff_permission（匿名运营角色关联）、
mall_setting（商城运费订单展示配置）、region_reference（行政区划）、storage_file（文件元数据，不含正文）、statistics_summary（统计快照概况）。
这些资料是手动同步的快照；精确数量、实时状态和完整统计继续使用实时只读查询，不用检索片段代替全量统计。

数据库能力：
""".strip() + "\n" + DATABASE_SCHEMA


@dataclass
class RouteDecision:
    route: str
    reason: str
    signals: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"route": self.route, "reason": self.reason, "signals": self.signals}


def query_plan_messages(question: str, names: list[str], history: list[dict] | None = None) -> list[dict]:
    now = datetime.now(timezone(timedelta(hours=8)))
    return [
        {"role": "system", "content": QUERY_PLAN_PROMPT},
        {"role": "user", "content": json.dumps({
            "current_time": now.isoformat(timespec="seconds"), "timezone": "Asia/Shanghai",
            "question": question, "recent_conversation": prepare_history(history),
            "known_product_names": names,
        }, ensure_ascii=False)},
    ]


def parse_query_plan(raw: str, names: list[str]) -> RouteDecision:
    """校验模型规划及 SQL；任何模型返回的 SQL 都不能绕过只读约束。"""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    plan = json.loads(raw)
    if not isinstance(plan, dict):
        raise ValueError("查询规划必须为对象")
    route = plan.get("route")
    if route not in {ROUTE_STRUCTURED, ROUTE_SEMANTIC, ROUTE_CONVERSATION, ROUTE_MANAGEMENT}:
        raise ValueError("查询规划的 route 无效")
    for key in ("reason", "analysis_scope", "time_scope", "retrieval_question", "semantic_query"):
        if not isinstance(plan.get(key), str):
            raise ValueError(f"查询规划缺少 {key}")
    for key in ("needs_semantic", "requires_complete_data", "analyze_business_records"):
        if not isinstance(plan.get(key), bool):
            raise ValueError(f"查询规划的 {key} 必须为布尔值")
    products = plan.get("products")
    if not isinstance(products, list):
        raise ValueError("查询规划的 products 必须为列表")
    doc_types = plan.get("doc_types")
    if not isinstance(doc_types, list) or any(not isinstance(item, str) for item in doc_types):
        raise ValueError("查询规划的 doc_types 必须为字符串列表")
    if route != ROUTE_CONVERSATION and not plan["retrieval_question"].strip():
        raise ValueError("查询需求不能为空")
    sql = None
    if route == ROUTE_STRUCTURED:
        if not isinstance(plan.get("sql"), str) or not plan["sql"].strip():
            raise ValueError("structured 路由必须在 sql 字段提供一条 SELECT")
        sql = validate_sql(plan["sql"])
    return RouteDecision(route, plan["reason"][:300], {
        "planner": "model", "products": [name for name in names if name in products],
        "analysis_scope": plan["analysis_scope"][:1000], "time_scope": plan["time_scope"][:500],
        "retrieval_question": plan["retrieval_question"][:4000],
        "semantic_query": plan["semantic_query"][:1000] or plan["retrieval_question"][:1000],
        "context_reason": str(plan.get("context_reason") or "")[:1000],
        "doc_types": list(dict.fromkeys(doc_types))[:30],
        "analyze_business_records": plan["analyze_business_records"],
        "request_diagnostics": plan.get("request_diagnostics") is True,
        "needs_semantic": route == ROUTE_STRUCTURED and plan["needs_semantic"],
        "requires_complete_data": route != ROUTE_CONVERSATION and plan["requires_complete_data"],
        "sql": sql,
    })


def decide_query_route(
    question: str, known_product_names: list[str] | None = None,
    history: list[dict] | None = None,
) -> RouteDecision:
    """服务端调用的兼容入口；浏览器问答由其当前模型完成同样的规划。"""
    names = known_product_names or []
    messages = query_plan_messages(question, names, history)
    try:
        raw = chat_once(messages[0]["content"], messages[1]["content"])
        return parse_query_plan(raw, names)
    except Exception as exc:
        logger.warning("模型查询规划未完成：%s", type(exc).__name__)
        return RouteDecision(ROUTE_SEMANTIC, "查询规划暂不可用，先检索原问题的相关资料", {
            "planner": "unavailable", "planning_failed": True,
            "products": [], "semantic_query": question,
            "analysis_scope": question, "time_scope": "未能确定，不能声称已完成指定时间的查询",
            "requires_complete_data": False,
        })
