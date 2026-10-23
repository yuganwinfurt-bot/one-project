"""售后流程规则。订单原始履约状态与售后状态分别保存。"""

from app.models.after_sale import AfterSaleRequest
from app.common.exceptions import BusinessException
from app.services.product_variant_service import available_stock, select_variant


CLOSED_STATUSES = {"completed", "rejected"}


def after_sale_options(order, latest, product):
    """退款/退货资格由订单和历史售后决定，只有换货检查现有库存。"""
    blocked = ""
    if order.status not in {"paid", "shipped", "completed"}:
        blocked = {"group_pending": "等待成团，暂不能申请售后", "unpaid": "订单尚未付款，可直接取消订单"}.get(order.status, "已取消订单不能申请售后")
    elif latest and latest.status in {"pending", "approved"}:
        blocked = "该订单已有售后正在处理中，请先处理现有申请"
    elif latest and latest.status == "completed":
        if latest.service_type != "exchange":
            blocked = "该订单已完成退款，不能重复申请退款或售后"
        elif order.status != "completed":
            blocked = "请先确认收到换货商品，再申请新的售后"
    result = {kind: {"enabled": not bool(blocked), "reason": blocked} for kind in ("refund", "return", "exchange")}
    if order.status == "paid" and not blocked:
        for kind in ("return", "exchange"):
            result[kind] = {"enabled": False, "reason": "订单尚未发货，请选择仅退款，无需寄回商品"}
    if result["exchange"]["enabled"]:
        try:
            variant = select_variant(product, order.variant_key or None) if product else None
            stock = available_stock(product, variant) if product else 0
        except BusinessException:
            stock = 0
        if stock < order.quantity:
            result["exchange"] = {"enabled": False, "reason": f"换货库存不足，需要{order.quantity}件，当前剩余{stock}件；仍可申请退款或退货退款"}
    return result


def completion_blocked_reason(record: AfterSaleRequest) -> str:
    if record.status == "completed":
        return "售后已完成，会话已关闭"
    if record.status == "rejected":
        return "售后已拒绝，会话已关闭"
    if record.status != "approved":
        return "需先同意售后申请"
    if record.service_type in {"return", "exchange"} and not (
        record.return_shipped and record.return_tracking_no
    ):
        return "等待用户寄回商品并提交物流单号"
    if record.service_type == "exchange":
        if not record.exchange_tracking_no:
            return "等待商家填写换货发货单号"
        if not record.order or record.order.status != "completed":
            return "等待用户确认收到换货商品"
    return ""


def after_sale_flow_data(record: AfterSaleRequest) -> dict:
    """供所有列表、卡片和操作入口使用的同一份流程状态。"""
    order_status = record.order.status if record.order else None
    return {
        "order_status": order_status,
        "conversation_closed": record.status in CLOSED_STATUSES,
        "completion_blocked_reason": completion_blocked_reason(record),
        "can_confirm_exchange_received": (
            record.service_type == "exchange"
            and record.status in {"approved", "completed"}
            and bool(record.exchange_tracking_no)
            and order_status == "shipped"
        ),
    }
