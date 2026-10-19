"""chat_service 辅助函数单测（不依赖大模型）。"""

from datetime import date, datetime
from decimal import Decimal
import json

from app.services.chat_service import _json_default, _shrink_rows


def test_json_default_handles_date_and_datetime():
    assert _json_default(date(2026, 9, 27)) == "2026-09-27"
    assert _json_default(datetime(2026, 9, 27, 12, 30, 5)).startswith("2026-09-27")
    assert _json_default(Decimal("12.50")) == 12.5


def test_json_dumps_with_date_column():
    """模拟 DATE(create_time) 返回 date 时不应抛 TypeError。"""
    payload = {"d": date(2026, 1, 2), "t": datetime(2026, 1, 2, 3, 4, 5)}
    text = json.dumps(payload, default=_json_default)
    assert "2026-01-02" in text


def test_shrink_rows_masks_sensitive_fields():
    rows = [
        {
            "buyer_name": "小明",
            "order_no": "EO20260001",
            "content": "鞋底开胶了",
            "rating": 1,
        }
    ]
    out = _shrink_rows(rows)
    assert out[0]["buyer_name"] == "小*"
    assert out[0]["order_no"].startswith("E")
    assert "*" in out[0]["order_no"]
    assert out[0]["content"] == "鞋底开胶了"
