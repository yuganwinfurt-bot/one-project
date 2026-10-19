"""查询路由判断的单元测试（不依赖大模型与数据库）。"""

from app.agent.router import (
    ROUTE_SEMANTIC,
    ROUTE_STRUCTURED,
    decide_query_route,
)

PRODUCTS = ["轻云运动跑鞋", "柔棉短袖T恤", "静音蓝牙耳机", "保温杯 500ml"]


def test_structured_when_product_and_rating():
    d = decide_query_route(
        "轻云运动跑鞋评分小于等于2分的评价有哪些？",
        known_product_names=PRODUCTS,
    )
    assert d.route == ROUTE_STRUCTURED
    assert "轻云运动跑鞋" in d.signals["products"]
    assert d.signals["has_rating_filter"] is True


def test_structured_when_product_and_time():
    d = decide_query_route(
        "轻云运动跑鞋最近两周的差评",
        known_product_names=PRODUCTS,
    )
    assert d.route == ROUTE_STRUCTURED
    assert d.signals["has_time_filter"] is True


def test_structured_when_only_product_name():
    d = decide_query_route(
        "静音蓝牙耳机的评价怎么样",
        known_product_names=PRODUCTS,
    )
    assert d.route == ROUTE_STRUCTURED


def test_structured_when_order_no():
    d = decide_query_route(
        "帮我查一下订单号 EO20260001 的信息",
        known_product_names=PRODUCTS,
    )
    assert d.route == ROUTE_STRUCTURED
    assert d.signals["has_order_no"] is True


def test_semantic_for_fuzzy_size_theme():
    d = decide_query_route(
        "最近有没有跟尺码相关的投诉",
        known_product_names=PRODUCTS,
    )
    assert d.route == ROUTE_SEMANTIC
    assert d.signals["products"] == []


def test_semantic_for_vague_quality_topic():
    d = decide_query_route(
        "用户都在吐槽什么包装问题",
        known_product_names=PRODUCTS,
    )
    assert d.route == ROUTE_SEMANTIC


def test_empty_question_defaults_semantic():
    d = decide_query_route("  ", known_product_names=PRODUCTS)
    assert d.route == ROUTE_SEMANTIC
