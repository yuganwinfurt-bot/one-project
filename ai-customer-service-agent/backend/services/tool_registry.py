"""Tool registry for AI agent tool calling."""

from sqlalchemy.orm import Session

from models import KnowledgeBase

# ── Tool definitions (OpenAI-compatible format) ──

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "查询订单的状态和物流信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "订单号，例如 ORD-12345",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_refund_policy",
            "description": "查询退款政策和规则",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_manual",
            "description": "查询产品的使用说明或帮助文档",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "产品SKU或产品名称",
                    }
                },
                "required": ["sku"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "将当前工单升级至人工客服处理",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "升级原因",
                    }
                },
                "required": ["reason"],
            },
        },
    },
]

# ── Mock data ──

MOCK_ORDERS = {
    "ORD-12345": {
        "status": "已发货",
        "tracking": "SF1234567890",
        "carrier": "顺丰快递",
        "estimated_delivery": "2026-05-12",
        "items": [{"name": "无线蓝牙耳机", "quantity": 1, "price": 299.0}],
    },
    "ORD-67890": {
        "status": "待发货",
        "tracking": None,
        "carrier": None,
        "estimated_delivery": "2026-05-15",
        "items": [{"name": "智能手表", "quantity": 1, "price": 599.0}],
    },
    "ORD-11111": {
        "status": "已签收",
        "tracking": "YT9876543210",
        "carrier": "圆通快递",
        "estimated_delivery": "2026-05-03",
        "items": [{"name": "手机壳", "quantity": 2, "price": 39.9}],
    },
}


def get_tool_definitions() -> list[dict]:
    return TOOLS


def execute_tool(name: str, params: dict, db: Session | None = None, ticket_id: int | None = None) -> dict:
    if db is not None and ticket_id is not None:
        from models import EcommerceTicket
        link = db.query(EcommerceTicket).filter_by(ticket_id=ticket_id).first()
        if link and name in {"lookup_order", "check_refund_policy"}:
            data = link.snapshot
            if name == "lookup_order":
                requested = str(params.get("order_id", "")).strip()
                if requested and requested not in {data["order_no"], str(data["order_id"])}:
                    return {"error": "只能查询当前售后关联的真实订单", "order_no": data["order_no"]}
                return {"source": "电商真实订单", **(data.get("order") or {}), "product_name": data["product_name"], "after_sale_status": data["status"]}
            return {"source": "当前电商售后流程", "service_type": data["service_type"], "status": data["status"],
                    "completion_blocked_reason": data.get("completion_blocked_reason"), "admin_note": data.get("admin_note"),
                    "policy": "审核、退款及换货由人工在售后处理卡片操作；AI不得承诺已退款或编造到账时间。"}
    if name == "lookup_order":
        return _lookup_order(params.get("order_id", ""))
    elif name == "check_refund_policy":
        return _check_refund_policy(db)
    elif name == "get_product_manual":
        return _get_product_manual(params.get("sku", ""), db)
    elif name == "escalate_to_human":
        return {"escalated": True, "reason": params.get("reason", "用户要求人工服务")}
    else:
        return {"error": f"Unknown tool: {name}"}


def _lookup_order(order_id: str) -> dict:
    if order_id in MOCK_ORDERS:
        return MOCK_ORDERS[order_id]
    for oid, data in MOCK_ORDERS.items():
        if order_id.upper().replace("-", "") == oid.upper().replace("-", ""):
            return data
    return {"error": f"未找到订单 {order_id}", "status": "unknown"}


def _check_refund_policy(db: Session | None) -> dict:
    if db:
        entries = (
            db.query(KnowledgeBase)
            .filter(
                KnowledgeBase.enabled == 1,
                KnowledgeBase.category == "refund",
            )
            .all()
        )
        if entries:
            return {
                "policy": entries[0].content[:500],
                "sources": [e.title for e in entries[:3]],
            }
    return {
        "policy": "7天无理由退货。收到商品后7天内可申请退货退款。商品需保持完好，不影响二次销售。如商品存在质量问题，退货运费由商家承担。退款在仓库签收后3-5个工作日到账。",
        "sources": ["退货退款流程说明"],
    }


def _get_product_manual(sku: str, db: Session | None) -> dict:
    if db:
        entries = (
            db.query(KnowledgeBase)
            .filter(
                KnowledgeBase.enabled == 1,
                KnowledgeBase.category == "product",
            )
            .all()
        )
        if entries:
            return {
                "manual": entries[0].content[:500],
                "sources": [e.title for e in entries[:3]],
            }
    return {
        "manual": f"关于「{sku}」的产品使用说明，请访问官网「帮助中心」查看详细文档。如需进一步帮助，可预约在线客服进行一对一远程演示。",
        "sources": ["产品使用帮助"],
    }
