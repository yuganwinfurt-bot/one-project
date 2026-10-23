"""记录并查询平台数据修改历史。"""

import json
from datetime import datetime
from decimal import Decimal

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessException
from app.common.response import PageResponse
from app.models.platform_log import PlatformLog
from app.models.product import Product
from app.models.review import Review
from app.models.mall import MallSetting
from app.services.customer_message_service import notify_favorited_customers_of_price_drop
from app.services.inventory_service import sync_product_inventory
from app.models.user import User
from app.schemas.platform_log import PlatformLogItem


def _format_value(field_label: str, value: object) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, Decimal):
        if field_label in {"售价", "原价"}:
            return f"¥{value:.2f}"
        if field_label == "折扣":
            return f"{value.normalize():f}%"
        return f"{value.normalize():f}"
    if field_label == "库存":
        return f"{value} 件"
    if field_label == "上下架状态":
        return {"on_sale": "在售", "off_shelf": "已下架"}.get(str(value), str(value))
    if field_label == "角色":
        return {"admin": "管理员", "user": "运营", "customer": "用户"}.get(str(value), str(value))
    if field_label == "状态":
        return {"1": "正常", "0": "禁用"}.get(str(value), str(value))
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def build_rollback_data(
    entity_type: str,
    entity_id: int,
    field_values: dict[str, tuple[object, object]],
    *,
    created: bool = False,
) -> dict[str, object] | None:
    fields = {
        field: {"before": before, "after": after}
        for field, (before, after) in field_values.items()
        if before != after
    }
    if not fields:
        return None
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "created": created,
        "fields": fields,
    }


def record_changes(
    db: Session,
    actor: User | None,
    target_type: str,
    target_name: str,
    changes: list[tuple[str, object, object]],
    *,
    verb: str = "修改了",
    rollback_data: dict[str, object] | None = None,
) -> None:
    """一次业务保存只写一条日志，前后值中分别列出本次变化的字段。"""
    if actor is None:
        return

    changed_fields: list[tuple[str, str, str]] = []
    for field_label, before, after in changes:
        before_text = _format_value(field_label, before)
        after_text = _format_value(field_label, after)
        if before_text == after_text:
            continue
        changed_fields.append((field_label, before_text, after_text))

    if not changed_fields:
        return

    labels = [label for label, _, _ in changed_fields]
    if len(labels) == 1:
        change_summary = labels[0]
    elif target_type == "商品" and set(labels).issubset({"售价", "原价", "折扣"}):
        change_summary = "价格"
    else:
        change_summary = f"{target_type}资料"

    db.add(
        PlatformLog(
            actor_id=actor.id,
            actor_username=actor.username,
            actor_name=actor.name,
            actor_role=actor.role,
            operation=f"{verb}{target_type}「{target_name}」的{change_summary}",
            before_value="\n".join(
                f"{label}：{before_text}" for label, before_text, _ in changed_fields
            ),
            after_value="\n".join(
                f"{label}：{after_text}" for label, _, after_text in changed_fields
            ),
            rollback_data=(
                json.dumps(rollback_data, ensure_ascii=False, separators=(",", ":"), default=str)
                if rollback_data
                else None
            ),
        )
    )


def _restore_value(field: str, value: object) -> object:
    if value is None:
        return None
    if field in {"price", "original_price", "discount_percent"}:
        return Decimal(str(value))
    if field in {"stock", "status"}:
        return int(value)
    if field in {"image_urls", "tags"} and isinstance(value, str):
        return json.loads(value)
    return value


def _same_value(field: str, current: object, expected: object) -> bool:
    try:
        return _restore_value(field, current) == _restore_value(field, expected)
    except (ValueError, TypeError, json.JSONDecodeError):
        return False


def _rollback_entity_type(row: PlatformLog) -> str | None:
    if not row.rollback_data:
        return None
    try:
        return json.loads(row.rollback_data).get("entity_type")
    except (AttributeError, TypeError, json.JSONDecodeError):
        return None


def _can_actor_rollback(row: PlatformLog, actor: User, db: Session) -> bool:
    if (
        not row.rollback_data
        or row.rollback_of_id is not None
        or row.rolled_back_at is not None
    ):
        return False
    if actor.role == "admin":
        if _rollback_entity_type(row) == "user":
            try:
                snapshot = json.loads(row.rollback_data)
                if not isinstance(snapshot, dict):
                    return False
                target_id = int(snapshot["entity_id"])
                fields = snapshot.get("fields")
                if not isinstance(fields, dict):
                    return False
                role_change = fields.get("role", {})
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                return False
            target = db.query(User).filter(User.id == target_id).first()
            if target and target.role == "admin":
                return False
            if isinstance(role_change, dict) and "admin" in (
                role_change.get("before"), role_change.get("after")
            ):
                return False
        return True
    # 运营可以撤销业务数据，但日志回退不能成为修改账号、角色或权限的旁路。
    return actor.role == "user" and _rollback_entity_type(row) in {
        "product", "review", "mall_setting"
    }


def rollback_platform_log(
    db: Session,
    actor: User,
    log_id: int,
    *, commit: bool = True,
) -> PlatformLogItem:
    """回退受支持的字段变更，并在原日志上标记回退关系。"""
    original = (
        db.query(PlatformLog)
        .filter(PlatformLog.id == log_id)
        .with_for_update()
        .first()
    )
    if not original:
        raise BusinessException(message="日志不存在")
    if original.rollback_of_id is not None:
        raise BusinessException(message="回退记录不能再次回退")
    if original.rolled_back_at is not None or original.rollback_log_id is not None:
        raise BusinessException(message="这条日志已经回退")
    if not original.rollback_data:
        raise BusinessException(message="这类操作暂不支持回退")

    try:
        snapshot = json.loads(original.rollback_data)
        entity_type = snapshot["entity_type"]
        entity_id = int(snapshot["entity_id"])
        fields = snapshot["fields"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise BusinessException(message="日志缺少有效的回退数据") from None

    models = {"product": Product, "user": User, "review": Review, "mall_setting": MallSetting}
    model = models.get(entity_type)
    if model is None or not fields:
        raise BusinessException(message="这类操作暂不支持回退")
    target = db.query(model).filter(model.id == entity_id).with_for_update().first()
    if not target:
        raise BusinessException(message="原数据已不存在，无法回退")
    if entity_type == "user":
        role_change = fields.get("role", {}) if isinstance(fields, dict) else {}
        if target.role == "admin" or (
            isinstance(role_change, dict)
            and "admin" in (role_change.get("before"), role_change.get("after"))
        ):
            raise BusinessException(message="管理员账号资料修改功能已下架，不能通过日志回退", code=403)
    if not _can_actor_rollback(original, actor, db):
        raise BusinessException(message="运营只能回退商品、评价和后台配置，不能回退账号变更", code=403)
    previous_price = target.price if entity_type == "product" else None

    allowed_fields = {
        "product": {
            "name", "category", "description", "image_url", "image_urls",
            "ai_detail", "price", "original_price", "discount_percent",
            "stock", "shelf_status", "tags",
        },
        "user": {"username", "name", "email", "phone", "avatar", "role", "status"},
        "review": {"merchant_reply"},
        "mall_setting": {"data"},
    }[entity_type]
    if set(fields) - allowed_fields:
        raise BusinessException(message="日志包含不支持回退的字段")

    for field, values in fields.items():
        if not isinstance(values, dict) or "before" not in values or "after" not in values:
            raise BusinessException(message="日志回退数据格式无效")
        if not _same_value(field, getattr(target, field), values["after"]):
            raise BusinessException(
                message="原数据在这条日志之后又有修改，请先处理较新的日志"
            )

    if snapshot.get("created"):
        if entity_type == "product":
            # 新建商品使用下架撤销发布，保留商品及其关联数据。
            target.shelf_status = "off_shelf"
        elif entity_type == "user" and target.role in {"user", "customer"}:
            # 新建账号使用禁用撤销创建，保留可能存在的关联记录。
            target.status = 0
        else:
            raise BusinessException(message="暂不支持回退这类新建操作")
    else:
        for field, values in fields.items():
            setattr(target, field, _restore_value(field, values["before"]))
        if entity_type == "product":
            if "image_urls" in fields:
                target.image_url = target.image_urls[0] if target.image_urls else None
            if "tags" in fields:
                target.category = target.tags[0] if target.tags else target.category
            elif "category" in fields and target.tags:
                target.tags = [target.category, *[tag for tag in target.tags if tag != fields["category"]["after"]]]

    if entity_type == "product":
        notify_favorited_customers_of_price_drop(db, target, previous_price)
        sync_product_inventory(db, target.id, actor.id)

    rollback_log = PlatformLog(
        actor_id=actor.id,
        actor_username=actor.username,
        actor_name=actor.name,
        actor_role=actor.role,
        operation=f"{'管理员' if actor.role == 'admin' else '运营'}回退了序号{original.id}",
        before_value=original.after_value,
        after_value=original.before_value,
        rollback_of_id=original.id,
    )
    db.add(rollback_log)
    original.rolled_back_at = datetime.now()
    db.flush()
    original.rollback_log_id = rollback_log.id
    if commit:
        db.commit()
    else:
        db.flush()
    db.refresh(rollback_log)
    return PlatformLogItem.model_validate(rollback_log).model_copy(
        update={"can_rollback": False}
    )


def list_platform_logs(
    db: Session,
    page: int,
    page_size: int,
    keywords: str | None = None,
    actor: User | None = None,
) -> PageResponse:
    query = db.query(PlatformLog)
    if keywords and keywords.strip():
        pattern = f"%{keywords.strip()}%"
        query = query.filter(
            or_(
                PlatformLog.actor_username.ilike(pattern),
                PlatformLog.actor_name.ilike(pattern),
                PlatformLog.operation.ilike(pattern),
                PlatformLog.before_value.ilike(pattern),
                PlatformLog.after_value.ilike(pattern),
            )
        )

    total = query.count()
    rows = (
        query.order_by(PlatformLog.create_time.desc(), PlatformLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        PlatformLogItem.model_validate(row).model_copy(
            update={
                "can_rollback": _can_actor_rollback(row, actor, db) if actor else False
            }
        )
        for row in rows
    ]
    return PageResponse(list=items, total=total)
