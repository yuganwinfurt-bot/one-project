"""日常对话 / 无关输入的兜底。

两类拦截：
1. 入口规则（classify_input）：寒暄（“你好”“在吗”）与过于简短的输入（“商品”）
   在进入 LangGraph 之前就拦掉，直接回引导语，不跑 Agent、不写运行记录；
2. 相关度兜底（配合 nodes.py 的低相关判断）：语义检索命中的最小距离仍大于
   阈值时，认为问题与业务数据无关，直接回引导语、不调用大模型、也不写诊断报告。

本模块同时存放这几段兜底回复文案，便于统一维护。

取舍说明：规则法零成本、行为可预期，但覆盖有限——例如“今天天气怎么样”
既不打招呼、也不含业务词，规则层拦不住，靠向量距离的相关度兜底来补。
"""

import re

from app.agent.router_rules import product_aliases

# 命中闲聊时直接返回的引导语（顺带把三个示例问题带出来）
SMALL_TALK_REPLY = (
    "你好！我是电商数据分析助手，主要处理商品、订单和评价相关的数据问题。\n\n"
    "可以试试这样问：\n"
    "- 洗衣液 2L 有哪些评价？\n"
    "- 跑鞋脱胶\n"
    "- 轻云运动跑鞋的差评有点多，帮我看看并处理"
)

VAGUE_QUERY_REPLY = (
    "问题有点简短，我没太理解要查什么。\n\n"
    "可以补充商品、时间范围或指标，例如：\n"
    "- 洗衣液 2L 有哪些评价？\n"
    "- 最近哪些商品差评最多\n"
    "- 轻云运动跑鞋的差评有点多，帮我看看并处理"
)

# 相关度兜底：语义检索都没找到相关内容时回这句（不调用大模型）
NO_RELEVANT_DATA_REPLY = (
    "没有找到与这个问题相关的业务数据。\n\n"
    "我主要负责商品、订单和评价相关的数据分析，可以补充商品名、时间范围或指标后再问我，例如：\n"
    "- 洗衣液 2L 有哪些评价？\n"
    "- 跑鞋脱胶\n"
    "- 轻云运动跑鞋的差评有点多，帮我看看并处理"
)

# 只有由这些片段（外加标点、语气词）拼成时才算闲聊，例如「你好呀」「你好，你是谁」
_SMALL_TALK_CHUNKS = (
    "你好", "您好", "哈喽", "哈啰", "嗨", "hi", "hello", "hey", "ok", "okay",
    "thanks", "thx", "3q", "thankyou",
    "早上好", "中午好", "下午好", "晚上好", "早安", "晚安",
    "在吗", "在么", "在不在", "在的", "有人吗", "测试", "test",
    "谢谢", "多谢", "感谢", "辛苦了", "好的", "收到", "明白了", "再见", "拜拜", "bye",
    "你是谁", "你叫什么", "你能做什么", "你会什么", "介绍一下", "你自己", "自我介绍",
)

# 关于助手自身 / 寒暄式的问题，即使句子稍长也按闲聊处理。
# 注意：不要放「好不好用」「好用吗」这类词——「保温杯好不好用」是正常业务问题。
_META_KEYWORDS = (
    "你是谁", "你叫什么", "你能做什么", "你会什么", "能干什么", "帮我做什么",
    "有什么功能", "怎么用", "怎么问", "使用说明", "自我介绍", "介绍一下你",
    "随便问问", "随便聊聊", "聊聊天", "闲聊", "没事就问问",
)
_META_MAX_LENGTH = 15

# 业务相关词：出现任意一个就不当闲聊（“你好，帮我查跑鞋差评”要走正常流程）
_DOMAIN_KEYWORDS = (
    "商品", "订单", "评价", "评分", "星级", "差评", "好评", "口碑", "销量", "销售",
    "库存", "价格", "折扣", "优惠", "退货", "售后", "上架", "下架", "类目", "品牌",
    "店铺", "买家", "顾客", "排行", "统计", "多少", "哪些", "几个", "趋势",
)

# 常见无关话题词：出现且不含任何业务词/商品名时，判为无关输入。
# 说明：相似度闸门实测不可靠（业务问题 0.36~0.96、无关问题 0.23~0.58 相互重叠），
# 所以这里用显式词表覆盖演示中最常见的闲聊/跑题，词表可按需扩充。
_OFF_TOPIC_KEYWORDS = (
    "天气", "气温", "下雨", "空气质量",
    "周几", "星期几", "礼拜几", "几点", "几号", "今天日期",
    "笑话", "段子", "绕口令", "脑筋急转弯",
    "古诗", "写诗", "首诗", "对联", "作文",
    "翻译", "英文", "语法",
    "数学", "方程", "微积分", "算数",
    "电影", "电视剧", "综艺", "小说", "音乐", "歌曲", "游戏",
    "股票", "基金", "汇率", "彩票", "房价",
    "新闻", "时事", "体育", "足球", "篮球",
    "减肥", "健身", "养生", "菜谱", "旅游", "星座", "运势",
    "怎么学", "学习路线", "面试题", "写代码", "编程",
)

# 疑问词：出现就不算“过短难以理解”
_QUESTION_WORDS = ("吗", "呢", "怎么", "如何", "为什么", "什么", "多少", "哪些", "哪个", "几")

# 统计口径词（与路由的聚合意图保持一致）：出现就不按“无关话题”处理，
# 例如「按日期统计订单量」虽然含“日期”，也属于业务问题。
_METRIC_PATTERNS = (
    r"(销量|销售额|订单量|订单数|评价数|数量|金额|总额|总价)",
    r"(排名|排行|排行榜|前几|最多|最少|最高|最低|平均|占比|比例|趋势|走势|统计|汇总|对比)",
)

# 去掉标点与语气词后不超过这个字数、且不含业务词的，按噪音处理（如「嗯」「在」）
_NOISE_MAX_LENGTH = 2
# 去掉标点后不超过这个字数、无数字、无疑问词 → 判为“过于简短”（如「商品」「价格」）。
# 只拦 1~2 个字的裸名词：3 个字以上宁可不拦，避免误伤「跑鞋脱胶」这类简短但有效的问题。
_VAGUE_MAX_LENGTH = 2

_PUNCT = " \t\r\n，,。.！!？?；;：:、~～…·-—_（）()【】[]\"'“”‘’"
_FILLER = "呀啊哦呢吧嘛哈啦咯哟诶嗯"

_META_PATTERN = re.compile("|".join(re.escape(k) for k in _META_KEYWORDS))


def _squeeze(text: str) -> str:
    """去掉空白、标点与常见语气词，便于判断“只剩寒暄”。"""
    for ch in _PUNCT + _FILLER:
        text = text.replace(ch, "")
    return text.lower()


def _is_only_small_talk_chunks(text: str) -> bool:
    """整句能否被 _SMALL_TALK_CHUNKS 从头到尾拼完。"""
    rest = text
    changed = True
    while rest and changed:
        changed = False
        for chunk in _SMALL_TALK_CHUNKS:
            if rest.startswith(chunk):
                rest = rest[len(chunk):]
                changed = True
                break
    return not rest


def _is_vague(text: str, raw: str) -> bool:
    """过于简短、没有任何可执行信息（如「商品」「价格」）。"""
    if len(text) > _VAGUE_MAX_LENGTH:
        return False
    if any(ch.isdigit() for ch in text):
        return False
    if any(word in raw for word in _QUESTION_WORDS):
        return False
    return True


def classify_input(question: str, product_names=None) -> str | None:
    """入口兜底判断。

    - 返回 None：正常业务问题，进入 Agent 流程
    - 返回 "smalltalk"：寒暄，如「你好」「在吗」「ok thanks」
    - 返回 "vague"：过于简短难以理解，如「商品」「价格」
    """
    raw = (question or "").strip()
    if not raw:
        return None

    # 商品名（含去规格别名）是最强的业务信号：出现就直接交给 Agent
    aliases = product_aliases(product_names or [])
    if any(alias in raw for alias in aliases):
        return None

    squeezed = _squeeze(raw)
    has_domain = any(word in raw for word in _DOMAIN_KEYWORDS)
    has_metric = any(re.search(p, raw) for p in _METRIC_PATTERNS)

    # 寒暄（含只输入标点/语气词）
    if not squeezed:
        return "smalltalk"
    if _is_only_small_talk_chunks(squeezed):
        return "smalltalk"
    if len(squeezed) <= _META_MAX_LENGTH and _META_PATTERN.search(squeezed):
        return "smalltalk"

    # 常见无关话题（无业务词、也无统计口径时按无关处理，优先于“过于简短”）
    if not has_domain and not has_metric and any(word in raw for word in _OFF_TOPIC_KEYWORDS):
        return "off_topic"

    # 短、无疑问词，即使含业务名词也无法执行（如「商品」「价格」）→ 判为过于简短
    if _is_vague(squeezed, raw):
        return "vague"

    # 很短又没有业务信息（如「嗯」「在」）；含数字（可能是商品/订单号）则放行
    if len(squeezed) <= _NOISE_MAX_LENGTH and not any(ch.isdigit() for ch in squeezed):
        return "smalltalk"

    # 含业务词 → 业务问题（「你好，帮我查跑鞋差评」这类也走这里）
    if has_domain:
        return None
    return None


def is_small_talk(question: str, product_names=None) -> bool:
    """是否为日常寒暄（保留给只需要布尔结果的调用方）。"""
    return classify_input(question, product_names=product_names) == "smalltalk"
