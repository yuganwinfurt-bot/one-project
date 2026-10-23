"""兼容旧调用的文本识别辅助，以及多轮上下文使用的商品别名。

主问答的查询规划由 router.py 调用模型完成，不用这些关键词决定业务回答。
"""

import re


# 时间范围：最近 N 天/周/月、本周/本月、具体年月等
_TIME_PATTERNS = [
    r"最近\s*\d+\s*(天|日|周|星期|个月|月)",
    r"最近\s*[一二两三四五六七八九十几]\s*(天|日|周|星期|个月|月)",
    r"近\s*\d+\s*(天|日|周|星期|个月|月)",
    r"过去\s*\d+\s*(天|日|周|星期|个月|月)",
    r"本周|本月|今年|上周|上月|昨日|昨天|今天",
    r"\d{4}\s*年\s*\d{1,2}\s*月",
    r"\d{1,2}\s*月\s*\d{1,2}\s*日",
]

# 评分 / 星级区间
_RATING_PATTERNS = [
    r"评分\s*[<>≤≥=]=?\s*\d",
    r"[一二三四五12345]\s*分\s*(以下|以上|及以下|及以上)?",
    r"(低于|高于|小于|大于|不超过|不少于)\s*[一二三四五12345]\s*分",
    r"(差评|好评|中评)",
    r"[1-5]\s*星",
]

# 更像「模糊主题」的问法（没有具体筛选条件时，倾向语义检索）
_FUZZY_THEME_PATTERNS = [
    r"有没有.*(相关|之类|投诉|反馈|讨论)",
    r"(跟|和|与).*(相关|有关)",
    r"(什么|哪些).*(问题|槽点|吐槽|抱怨)",
    r"问题.*(是什么|什么|哪些)",
    r"(大家|用户).*(说|觉得|反映)",
]

# 聚合/统计意图：没有点名商品，但问的是数量、排名、最高最低、平均、趋势等。
# 这类问题 SQL 用 COUNT/SUM/AVG + GROUP BY 就能算，走语义检索只能拿到评价文本，
# 答不出「订单量多少、谁卖得最好」这类问题。
_AGGREGATE_PATTERNS = [
    r"(销量|销售额|订单量|订单数|评价数|数量|金额|总额|总价)",
    r"(卖得最好|卖得最差|最畅销|最热销|销量最高|销量最低)",
    r"(排名|排行|排行榜|前几|前\s*\d|top\s*\d)",
    r"(最多|最少|最高|最低|最大|最小)",
    r"(平均|均值|中位数)",
    r"(占比|比例|百分比)",
    r"(趋势|走势|同比|环比)",
    r"(总共|一共|合计|总计)",
    r"(多少|几条|几个|几笔)",
    r"(统计|汇总|对比)",
]


def _has_time_filter(question: str) -> bool:
    return any(re.search(p, question) for p in _TIME_PATTERNS)


def _has_rating_filter(question: str) -> bool:
    return any(re.search(p, question) for p in _RATING_PATTERNS)


def _has_fuzzy_theme(question: str) -> bool:
    return any(re.search(p, question) for p in _FUZZY_THEME_PATTERNS)


def _has_aggregate_intent(question: str) -> bool:
    return any(re.search(p, question) for p in _AGGREGATE_PATTERNS)


def product_aliases(known_product_names: list[str]) -> dict[str, str]:
    """商品别名表：原名 + 去掉规格后缀的名字（第一个空格前的部分）。

    库里商品名带规格（「洗衣液 2L」「保温杯 500ml」），用户往往只说「洗衣液」。
    只按全名匹配会漏，明明点名了商品却走语义检索，答案只能从评价文本里拼凑。

    刻意不加「尾词」别名（如把「轻云运动跑鞋」缩成「跑鞋」）：那样会把
    「跑鞋脱胶」这类主题型问题也拉去 SQL，丢掉语义检索在措辞无关场景的价值。
    """
    alias: dict[str, str] = {}
    for name in known_product_names or []:
        if not name:
            continue
        alias.setdefault(name, name)
        core = re.split(r"[\s　]+", name)[0].strip()
        if len(core) >= 2:
            alias.setdefault(core, name)
    return alias


def _find_product_mentions(question: str, known_product_names: list[str]) -> list[str]:
    """在问题里匹配已知商品名（含去规格别名，长名优先，避免短词误伤）。"""
    aliases = product_aliases(known_product_names)
    hit: list[str] = []
    for text in sorted(aliases, key=len, reverse=True):
        if text in question:
            canonical = aliases[text]
            if canonical not in hit:
                hit.append(canonical)
    return hit


def _has_order_no(question: str) -> bool:
    """订单号一类的明确标识。"""
    return bool(re.search(r"(订单号|订单编号|EO\d{6,})", question, re.IGNORECASE))
