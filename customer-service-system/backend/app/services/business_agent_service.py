"""AI 后台业务工具：复用业务校验、人工确认和事务；永不操作账号或角色。"""
import json
import re
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.common.exceptions import BusinessException
from app.models.after_sale import AfterSaleRequest
from app.models.alert_notification import AlertNotification
from app.models.mall import MallContent, MallFeedback, ProductCatalog
from app.models.order import Order
from app.models.platform_log import PlatformLog
from app.models.product import Product
from app.models.review import Review
from app.models.staff_inbox import StaffInboxEvent
from app.models.community import DirectConversation, DirectMessage, ReviewReplyNotification
from app.models.user import User
from app.schemas.after_sale import AfterSaleProcess, AfterSaleExchangeShipmentUpdate, AfterSaleMessageCreate
from app.schemas.ecommerce import ProductListingCreate, ProductListingUpdate, ProductTagsUpdate, ProductAiDetailUpdate, OrderShipmentUpdate, ReviewReplyUpdate
from app.services import ecommerce_service as ecommerce, mall_service as mall
from app.services.mall_registry import CONTENT
from app.services.platform_log_service import record_changes


class ContentEnvelope(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    name: str = Field(min_length=1, max_length=120)
    enabled: bool = True
    sort_order: int = Field(default=0, ge=0, le=100000)
    data: dict


class DirectMessagePayload(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    content: str = Field(min_length=1, max_length=2000)


class StartConversationPayload(DirectMessagePayload):
    user_id: int = Field(ge=1)


class ReviewCommentPayload(DirectMessagePayload):
    reply_to_user_id: int | None = Field(default=None, ge=1)


PRODUCT_FIELDS = {
    'name': '商品名称', 'category': '类目', 'brand_id': '品牌编号', 'category_id': '类目编号',
    'description': '商品介绍', 'price': '售价（元）', 'stock': '可售库存', 'discount_percent': '优惠（%）',
    'variant_name': '规格名称', 'variants': '规格售价与库存', 'image_urls': '商品图片',
    'shelf_status': '上下架状态', 'review_status': '复核状态', 'tags': '标签', 'ai_detail': '商品详情文案',
}
MODELS = {'products': Product, 'orders': Order, 'after-sales': AfterSaleRequest, 'reviews': Review,
          'feedback': MallFeedback, 'alerts': AlertNotification, 'messages': StaffInboxEvent, 'logs': PlatformLog,
          'conversations': DirectConversation, 'reply-notifications': ReviewReplyNotification}
ROW_FIELDS = {
    'orders': ['order_no', 'product_id', 'variant_key', 'quantity', 'amount', 'status', 'tracking_no', 'checkout_id'],
    'after-sales': ['order_id', 'order_no', 'product_id', 'product_name', 'service_type', 'reason', 'description',
                    'status', 'admin_note', 'return_shipped', 'return_tracking_no', 'exchange_tracking_no'],
    'reviews': ['product_id', 'order_id', 'rating', 'content', 'merchant_reply'],
    'feedback': ['name', 'content', 'reply', 'status'],
    'alerts': ['title', 'content', 'level', 'product_id', 'is_read'],
    'messages': ['event_type', 'target_id', 'title', 'content', 'is_read'],
    'logs': ['operation', 'before_value', 'after_value', 'rollback_data', 'rollback_of_id', 'rolled_back_at', 'rollback_log_id'],
    'conversations': ['staff_id', 'customer_id'],
    'reply-notifications': ['user_id', 'product_id', 'product_name', 'content', 'is_read'],
}
OPERATIONS = {
    'products': ['create', 'update'], 'orders': ['ship', 'cancel-unpaid'],
    'after-sales': ['process', 'exchange-shipment', 'message'], 'reviews': ['reply', 'comment'], 'feedback': ['reply'],
    'alerts': ['read', 'read-all'], 'messages': ['read', 'read-all'],
    'risks': ['scan', 'review'], 'logs': ['rollback'], 'knowledge': ['sync'],
    'conversations': ['create', 'message', 'read'], 'reply-notifications': ['read'],
}
TITLES = {'products': '商品', 'orders': '订单', 'after-sales': '售后', 'reviews': '商品评价',
          'feedback': '意见反馈', 'alerts': '预警', 'messages': '消息', 'risks': '风险检查',
          'logs': '操作日志', 'knowledge': '知识库同步', 'conversations': '买家私聊', 'reply-notifications': '回复通知'}
OP_LABELS = {'create': '创建', 'update': '修改', 'delete': '删除', 'ship': '发货 / 补录物流',
             'cancel-unpaid': '取消整笔待付款结算', 'process': '处理售后', 'exchange-shipment': '换货发货',
             'message': '发送售后消息', 'reply': '回复', 'read': '标记已读', 'read-all': '全部标记已读',
             'scan': '检查售后风险', 'review': '标记风险商品待复核', 'rollback': '回退业务修改', 'sync': '同步后台资料到知识库', 'comment': '追加评价回复'}
FIELD_LABELS = {'name': '名称', 'enabled': '启用', 'sort_order': '排序', 'tracking_no': '物流单号',
                'status': '状态', 'admin_note': '处理说明', 'exchange_tracking_no': '换货物流单号',
                'content': '发送内容', 'merchant_reply': '商家回复', 'reply': '回复内容',
                'action': '售后操作', 'user_id': '收信买家编号', 'reply_to_user_id': '回复对象编号'}


def json_value(value):
    return json.loads(json.dumps(value, ensure_ascii=False, default=lambda v: float(v) if isinstance(v, Decimal) else v.isoformat() if isinstance(v, datetime) else str(v)))


def display(value):
    if value is None or value == '':
        return '未设置'
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    return str(value)


def display_field(key, value):
    if key == 'variants' and isinstance(value, list):
        return '；'.join(f"{v['name']}：¥{float(v['price']):.2f}，库存 {v['stock']} 件" for v in value) or '单规格'
    if key in {'status', 'shelf_status', 'review_status', 'action'}:
        return {'on_sale': '在售', 'off_shelf': '已下架', 'normal': '正常', 'pending_review': '待复核',
                'unpaid': '待付款', 'paid': '已支付', 'shipped': '已发货', 'completed': '已完成',
                'cancelled': '已取消', 'pending': '待审核', 'approved': '已同意', 'rejected': '已拒绝',
                'approve': '同意', 'reject': '拒绝', 'complete': '完成'}.get(value, display(value))
    return display(value)


def is_content(resource):
    return resource in CONTENT and resource != 'roles'


def require_business(db, user, resource):
    # 只有显式业务资源能够到达执行器；members/users/admin/staff/roles 永远不在目录中。
    if user.role not in {'admin', 'user'} or user.status != 1:
        raise BusinessException(message='当前账号不能操作后台业务', code=403)
    if is_content(resource) or resource == 'feedback':
        mall.require(db, user, resource)
    elif resource not in OPERATIONS:
        raise BusinessException(message='AI 禁止修改用户、管理员、运营账号和角色权限，也不能执行未知资源', code=403)
    if resource in {'logs', 'knowledge'} and user.role != 'admin':
        raise BusinessException(message='此操作需要当前登录账号具有管理员权限', code=403)


def operation_catalog(db, user):
    catalog = {key: dict(operations=ops, title=TITLES[key]) for key, ops in OPERATIONS.items()
               if key not in {'logs', 'knowledge'} or user.role == 'admin'}
    if 'feedback' not in mall.permissions(db, user):
        catalog.pop('feedback', None)
    for kind, spec in CONTENT.items():
        if is_content(kind) and kind in mall.permissions(db, user):
            catalog[kind] = dict(title=spec['title'], operations=['create', 'update', 'delete'], fields=spec['fields'],
                                 common_fields={'name': '名称（必填）', 'enabled': '布尔值，默认 true', 'sort_order': '整数，默认 0'},
                                 patch_format='公共字段和 fields 的 key 平铺在 patch 内，不要嵌套 data')
    catalog['products']['create_schema'] = ProductListingCreate.model_json_schema()
    catalog['products']['update_fields'] = PRODUCT_FIELDS
    catalog['products']['notes'] = '售价为折后价；variants=[{key,name,price,stock}]；单规格用空数组。新建会直接上架。修改保留未提及字段和原上下架状态；指定上架需 shelf_status=on_sale。更新规格必须带完整规格列表并保留已有 key。'
    catalog['orders']['patches'] = {'ship': {'tracking_no': '真实物流单号（必填）'}, 'cancel-unpaid': {}}
    catalog['after-sales']['patches'] = {'process': {'action': 'approve|reject|complete', 'admin_note': '处理说明；拒绝必填'}, 'exchange-shipment': {'exchange_tracking_no': '真实物流单号'}, 'message': {'content': '发送内容'}}
    catalog['reviews']['patches'] = {'reply': {'merchant_reply': '回复正文'}, 'comment': {'content': '追加回复内容', 'reply_to_user_id': '参与评价的用户编号，可省略'}}
    catalog['conversations']['patches'] = {'create': {'user_id': '现有买家编号，不修改其账号', 'content': '首条私聊消息'}, 'message': {'content': '发送给该会话买家的内容'}, 'read': {}}
    if 'feedback' in catalog:
        catalog['feedback']['patches'] = {'reply': {'reply': '回复正文'}}
    return catalog


def _row(db, resource, row_id, *, lock=False):
    if type(row_id) is not int or row_id <= 0:
        raise BusinessException(message='请明确要操作的现有记录编号')
    query = db.query(MallContent).filter_by(kind=resource, id=row_id) if is_content(resource) else db.query(MODELS[resource]).filter_by(id=row_id)
    if lock:
        query = query.populate_existing().with_for_update()
    row = query.first()
    if not row:
        raise BusinessException(message='指定的业务记录不存在', code=404)
    return row


def snapshot(db, resource, row):
    if is_content(resource):
        return dict(name=row.name, enabled=row.enabled, sort_order=row.sort_order, data=json_value(row.data))
    if resource == 'products':
        mapping = db.query(ProductCatalog).filter_by(product_id=row.id).first()
        result = {key: getattr(row, key) for key in PRODUCT_FIELDS if key not in {'brand_id', 'category_id'}}
        result.update(brand_id=mapping.brand_id if mapping else None, category_id=mapping.category_id if mapping else None)
        result['variants'] = result['variants'] or []
        result['image_urls'] = result['image_urls'] or ([row.image_url] if row.image_url else [])
        result['discount_percent'] = result['discount_percent'] or 0
        result['tags'] = result['tags'] or [row.category]
    else:
        result = {key: getattr(row, key) for key in ROW_FIELDS[resource]}
    result['update_time'] = row.update_time
    if resource == 'orders' and row.status == 'unpaid':
        from app.services.order_lifecycle_service import checkout_orders
        result['checkout_items'] = [dict(id=o.id, status=o.status, product_id=o.product_id, variant_key=o.variant_key, quantity=o.quantity) for o in checkout_orders(db, row.id)]
    if resource == 'after-sales':
        result['order_status'] = row.order.status if row.order else None
    return json_value(result)


def _keys(patch, allowed):
    if set(patch) - set(allowed):
        raise BusinessException(message='包含不支持的业务字段：' + '、'.join(sorted(set(patch) - set(allowed))))


def _validate_product(db, patch, before=None):
    _keys(patch, PRODUCT_FIELDS)
    source = {key: val for key, val in (before or {}).items() if key in PRODUCT_FIELDS}
    source.update(patch)
    if before and before.get('variants') and {'price', 'stock'} & set(patch) and 'variants' not in patch:
        raise BusinessException(message='该商品有多种规格，请指定规格及新价格或库存，不能只改汇总数')
    if 'category_id' in patch and patch['category_id'] is not None:
        category = db.query(MallContent).filter_by(id=patch['category_id'], kind='categories', enabled=True).first()
        if not category:
            raise BusinessException(message='所选商品类目不存在或已停用')
        if 'category' in patch and category.name != patch['category']:
            raise BusinessException(message='类目名称与类目编号不一致')
        source['category'] = category.name
    if source.get('brand_id'):
        if type(source['brand_id']) is not int or not db.query(MallContent).filter_by(id=source['brand_id'], kind='brands', enabled=True).first():
            raise BusinessException(message='所选品牌不存在或已停用')
    # 数字、SKU 数量/价格、规格唯一性沿用页面的 Pydantic 校验。
    listing = (ProductListingUpdate if before else ProductListingCreate).model_validate({key: value for key, value in source.items() if key in ProductListingCreate.model_fields})
    ecommerce._listing_prices(listing)
    for url in listing.image_urls:
        mall.values([{'key': 'url', 'type': 'image', 'label': '商品图片'}], {'url': url})
    result = json_value(listing.model_dump())
    for key, options in [('shelf_status', {'on_sale', 'off_shelf'}), ('review_status', {'normal', 'pending_review'})]:
        result[key] = source.get(key) or ('on_sale' if key == 'shelf_status' else 'normal')
        if result[key] not in options:
            raise BusinessException(message=PRODUCT_FIELDS[key] + '无效')
    result['tags'] = ProductTagsUpdate(tags=source.get('tags') or [listing.category]).tags
    result['tags'] = list(dict.fromkeys([listing.category, *result['tags']]))
    result['ai_detail'] = source.get('ai_detail')
    if result['ai_detail']:
        ProductAiDetailUpdate(ai_detail=result['ai_detail'])
    if listing.variants:
        result['price'] = min(float(sku.price) for sku in listing.variants)
        result['stock'] = sum(sku.stock for sku in listing.variants)
    if result['stock'] > 2147483647:
        raise BusinessException(message='商品库存合计超出范围')
    category = db.query(MallContent).filter_by(kind='categories', name=listing.category).first()
    result['category_id'] = category.id if category else None
    return result


def _content_payload(db, resource, patch, before):
    fields = CONTENT[resource]['fields']
    _keys(patch, ['name', 'enabled', 'sort_order', *[f['key'] for f in fields]])
    base = before or {'name': '', 'enabled': True, 'sort_order': 0, 'data': {}}
    after = {key: patch.get(key, base[key]) for key in ('name', 'enabled', 'sort_order')}
    after['data'] = mall.values(fields, base['data'] | {key: value for key, value in patch.items() if key not in after})
    after = ContentEnvelope.model_validate(after).model_dump()
    if not after['name'].strip():
        raise BusinessException(message='名称不能为空')
    mall.validate_refs(db, resource, after['data'])
    return after


def _validate_command(db, resource, op, patch, before):
    if is_content(resource):
        if op == 'delete':
            _keys(patch, [])
            return {'deleted': True}
        return _content_payload(db, resource, patch, before)
    if resource == 'products':
        return _validate_product(db, patch, before)
    schemas = {('orders', 'ship'): OrderShipmentUpdate, ('after-sales', 'process'): AfterSaleProcess,
               ('after-sales', 'exchange-shipment'): AfterSaleExchangeShipmentUpdate,
               ('after-sales', 'message'): AfterSaleMessageCreate, ('reviews', 'reply'): ReviewReplyUpdate,
               ('reviews', 'comment'): ReviewCommentPayload, ('conversations', 'create'): StartConversationPayload,
               ('conversations', 'message'): DirectMessagePayload}
    schema = schemas.get((resource, op))
    if schema:
        _keys(patch, schema.model_fields)
        return schema.model_validate(patch).model_dump(mode='json')
    if resource == 'feedback':
        _keys(patch, ['reply'])
        reply = patch.get('reply')
        if not isinstance(reply, str) or not 1 <= len(reply.strip()) <= 5000:
            raise BusinessException(message='请填写 1～5000 字的回复')
        return {'reply': reply.strip()}
    _keys(patch, [])
    return {}


def build_business_action(db, user, change):
    resource, row_id, patch = change['resource'], change['id'], change['patch']
    op = change.get('operation', 'update')
    require_business(db, user, resource)
    if op not in (['create', 'update', 'delete'] if is_content(resource) else OPERATIONS[resource]):
        raise BusinessException(message='此业务模块不支持该操作')
    global_op = op in {'create', 'read-all', 'scan', 'sync'}
    if global_op and row_id is not None:
        raise BusinessException(message='新建或全局操作的 id 必须为 null')
    if not global_op and row_id is None:
        raise BusinessException(message='该操作需要明确记录编号')
    snapshot_resource = 'products' if resource == 'risks' and op == 'review' else resource
    row = None if global_op else _row(db, snapshot_resource, row_id)
    if resource == 'conversations' and row and row.staff_id != user.id:
        raise BusinessException(message='只能操作属于当前账号的私聊', code=403)
    if resource == 'reply-notifications' and row.user_id != user.id:
        raise BusinessException(message='只能操作当前账号的回复通知', code=403)
    before = snapshot(db, snapshot_resource, row) if row else None
    if resource == 'logs':
        rollback = json.loads(row.rollback_data or '{}')
        if rollback.get('entity_type') not in {'product', 'review', 'mall_setting'}:
            raise BusinessException(message='AI 禁止回退任何用户、管理员或运营账号的修改', code=403)
        target_product = db.get(Product, rollback.get('entity_id')) if rollback['entity_type'] == 'product' else None
        if target_product and target_product.variants and {'stock', 'price', 'original_price', 'discount_percent'} & set(rollback.get('fields', {})):
            raise BusinessException(message='多规格商品请直接修改各规格，不能回退单规格价格或库存')
    try:
        after = _validate_command(db, resource, op, patch, before)
    except ValidationError as exc:
        raise BusinessException(message='业务参数无效：' + '；'.join(f"{'.'.join(map(str, e['loc']))} {e['msg']}" for e in exc.errors(include_url=False))) from None
    if resource == 'products' and op == 'update':
        # 方案阶段也检查占用规格，真正执行时仍再次检查。
        from app.models.order import Order
        keys = {sku['key'] for sku in after['variants']}
        if any((order.variant_key and order.variant_key not in keys) or (not order.variant_key and keys)
               for order in db.query(Order).filter(Order.product_id == row_id, Order.status.in_(['unpaid', 'group_pending']))):
            raise BusinessException(message='存在待付款或待成团订单，不能移除已占用的规格；可修改价格或补货')
    if resource == 'conversations' and op == 'create':
        if not db.query(User.id).filter_by(id=after['user_id'], role='customer', status=1).first():
            raise BusinessException(message='指定的买家不存在或无法接收消息')
    flat_before = ({**before['data'], **{k: before[k] for k in ['name', 'enabled', 'sort_order']}} if before and is_content(resource) else before) or {}
    flat_after = ({**after['data'], **{k: after[k] for k in ['name', 'enabled', 'sort_order']}} if is_content(resource) and op != 'delete' else after)
    labels = FIELD_LABELS | (PRODUCT_FIELDS if resource == 'products' else {field['key']: field['label'] for field in CONTENT[resource]['fields']} if is_content(resource) else {})
    differences = [dict(key=key, label=labels.get(key, key), before=display_field(key, flat_before.get(key)), after=display_field(key, value))
                   for key, value in flat_after.items() if key != 'category_id' and (not before or flat_before.get(key) != value)]
    if op not in {'create', 'update'} or not differences:
        if op in {'create', 'update'} and not differences:
            return None
        if op == 'delete':
            differences = [dict(key='record', label='记录名称', before=flat_before.get('name'), after='删除记录')]
        elif differences:
            pass
        else:
            differences = [dict(key='operation', label='执行操作', before=display_field('status', (before or {}).get('status')),
                                after=OP_LABELS[op])]
    title = OP_LABELS[op] + (CONTENT[resource]['title'] if is_content(resource) else TITLES[resource]) + (f'「{getattr(row, "name", None) or getattr(row, "order_no", None) or row_id}」' if row else '')
    action = dict(type='manage_business', resource=resource, operation=op, record_id=row_id,
                  before=before, after=after, title=title, changes=differences,
                  summary=title + '：' + '；'.join(f"{d['label']} {d['before']} → {d['after']}" for d in differences))
    if op == 'cancel-unpaid':
        action['notice'] = '同次结算的所有待付款商品会一起取消，库存与优惠券一起返还。'
    if op == 'create' and resource == 'products':
        action['notice'] = '确认后将真实创建商品并上架；未指定图片时保留空图，不会伪造商品图片。'
    if op == 'delete':
        action['notice'] = '确认后删除该条运营资料；已被领取、使用或关联的记录仍受原业务规则保护。'
    if op == 'sync':
        action['notice'] = '确认后提交脱敏资料同步任务，任务进度在语义检索页面查看。'
    if op in {'message', 'comment', 'reply'} or resource == 'conversations' and op == 'create':
        action['notice'] = '确认后将以当前登录账号的身份发布以上内容。'
    if op == 'exchange-shipment':
        action['notice'] = '确认后扣减原订单相应规格的换货库存，并向买家发送换货发货通知。'
    return action


def _save_product(db, user, action):
    data = action['after']
    listing = {key: val for key, val in data.items() if key in ProductListingCreate.model_fields}
    if action['operation'] == 'create':
        result = ecommerce.create_product_listing(db, ProductListingCreate(**listing), user, commit=False)
        product = db.get(Product, result.id)
    else:
        ecommerce.update_product_listing(db, action['record_id'], ProductListingUpdate(**listing), user, commit=False, publish=False)
        product = db.get(Product, action['record_id'])
    for key in ['shelf_status', 'review_status', 'tags', 'ai_detail']:
        setattr(product, key, data[key])
    from app.services.inventory_service import sync_product_inventory
    sync_product_inventory(db, product.id, user.id)
    db.flush()
    return product.id


def execute_business_action(db, action, user):
    resource, op, row_id = action['resource'], action['operation'], action['record_id']
    require_business(db, user, resource)
    # 执行时再从目录重建校验，不能信任历史检查点或浏览器传回的参数。
    if op not in (['create', 'update', 'delete'] if is_content(resource) else OPERATIONS[resource]):
        raise BusinessException(message='未知业务操作', code=403)
    global_op = op in {'create', 'read-all', 'scan', 'sync'}
    row = None if global_op else _row(db, 'products' if resource == 'risks' else resource, row_id, lock=True)
    if resource == 'conversations' and row and row.staff_id != user.id:
        raise BusinessException(message='只能操作属于当前账号的私聊', code=403)
    if resource == 'reply-notifications' and row.user_id != user.id:
        raise BusinessException(message='只能操作当前账号的回复通知', code=403)
    if row is not None and snapshot(db, 'products' if resource == 'risks' else resource, row) != action['before']:
        raise BusinessException(message='业务数据在生成方案后已经变化，请重新提问生成方案')
    data = action['after']
    result = None
    if is_content(resource):
        if op == 'delete':
            mall.remove_content(db, user, resource, row_id, commit=False)
        else:
            ContentEnvelope.model_validate(data)
            result = mall.save_content(db, user, resource, data, row_id, commit=False)
    elif resource == 'products':
        _validate_product(db, data, action['before'])
        result = {'product_id': _save_product(db, user, action)}
    elif resource == 'orders':
        if op == 'ship':
            payload = OrderShipmentUpdate(**data)
            result = ecommerce.ship_order(db, row_id, payload.tracking_no, commit=False)
        else:
            from app.services.order_lifecycle_service import _cancel_locked, checkout_orders
            orders = checkout_orders(db, row_id)
            _cancel_locked(db, orders)
            result = {'cancelled_order_ids': [order.id for order in orders]}
    elif resource == 'after-sales':
        from app.services import merchant_operations_service as merchant
        if op == 'process':
            merchant.process_after_sale(db, user, row_id, AfterSaleProcess(**data), commit=False)
        elif op == 'exchange-shipment':
            merchant.exchange_shipment(db, user, row_id, AfterSaleExchangeShipmentUpdate(**data), commit=False)
        else:
            merchant.send_after_sale_message(db, user, row_id, AfterSaleMessageCreate(**data), commit=False)
    elif resource == 'reviews':
        if op == 'comment':
            payload = ReviewCommentPayload(**data)
            from app.services.community_service import add_review_comment
            comment = add_review_comment(db, row, user, payload.content, payload.reply_to_user_id)
            result = {'comment_id': comment.id}
        else:
            payload = ReviewReplyUpdate(**data)
            ecommerce.update_review_reply(db, row_id, payload.merchant_reply, user, commit=False)
    elif resource == 'feedback':
        normalized = _validate_command(db, resource, op, data, action['before'])
        row.reply, row.status = normalized['reply'], 'replied'
    elif resource in {'alerts', 'messages'}:
        model = MODELS[resource]
        if op == 'read-all':
            result = {'updated': db.query(model).filter(model.is_read == 0).update({model.is_read: True}, synchronize_session=False)}
            if resource == 'messages':
                from app.models.community import ReviewReplyNotification
                db.query(ReviewReplyNotification).filter_by(user_id=user.id, is_read=False).update({ReviewReplyNotification.is_read: True}, synchronize_session=False)
        else:
            row.is_read = True
    elif resource == 'risks':
        from app.services.after_sale_risk_service import sync_all_after_sale_risks, confirm_after_sale_risk_review
        result = sync_all_after_sale_risks(db, user.id) if op == 'scan' else confirm_after_sale_risk_review(db, row_id, user)
    elif resource == 'logs':
        rollback = json.loads(row.rollback_data or '{}')
        if rollback.get('entity_type') not in {'product', 'review', 'mall_setting'}:
            raise BusinessException(message='AI 禁止回退任何账号或角色修改', code=403)
        target_product = db.get(Product, rollback.get('entity_id')) if rollback['entity_type'] == 'product' else None
        if target_product and target_product.variants and {'stock', 'price', 'original_price', 'discount_percent'} & set(rollback.get('fields', {})):
            raise BusinessException(message='商品规格已经变化，请直接维护各规格，不能回退单规格价格或库存')
        from app.services.platform_log_service import rollback_platform_log
        rollback_platform_log(db, user, row_id, commit=False)
    elif resource == 'conversations':
        if op == 'create':
            payload = StartConversationPayload(**data)
            # 锁定已有买家以串行化会话创建；只读取/加锁，绝不修改账号。
            customer = db.query(User).filter_by(id=payload.user_id, role='customer', status=1).with_for_update().first()
            if not customer:
                raise BusinessException(message='该买家不能接收私聊')
            row = db.query(DirectConversation).filter_by(staff_id=user.id, customer_id=customer.id).first()
            if not row:
                row = DirectConversation(staff_id=user.id, customer_id=customer.id)
                db.add(row)
                db.flush()
        if op == 'read':
            db.query(DirectMessage).filter(DirectMessage.conversation_id == row.id, DirectMessage.sender_id != user.id).update({DirectMessage.is_read: True}, synchronize_session=False)
        else:
            payload = DirectMessagePayload(**{'content': data['content']})
            if not payload.content.strip() or not db.query(User.id).filter_by(id=row.customer_id, role='customer', status=1).first():
                raise BusinessException(message='消息内容为空或买家暂不能接收私聊')
            db.add(DirectMessage(conversation_id=row.id, sender_id=user.id, content=payload.content.strip()))
            result = {'conversation_id': row.id}
    elif resource == 'reply-notifications':
        row.is_read = True
    elif resource == 'knowledge':
        from app.services.semantic_search_service import sync_ecommerce_data
        result = sync_ecommerce_data()
    record_changes(db, user, 'AI 后台操作', action['title'], [('操作方案', action['before'], data)], verb='执行了')
    db.flush()
    return {'type': 'manage_business', 'ok': True, 'summary': action['summary'], 'changes': action['changes'],
            'result': json_value(result.model_dump(mode='json') if isinstance(result, BaseModel) else result)}


def business_context(db, user, question='', history=None):
    """小目录用于选对象；明细明确标注范围，不能把候选当作全部统计。"""
    catalog = operation_catalog(db, user)
    text = question + '\n' + json.dumps((history or [])[-6:], ensure_ascii=False)
    ids = {int(value) for value in re.findall(r'(?<!\d)\d{1,9}(?!\d)', text)}
    products = db.query(Product).order_by(Product.id.desc()).limit(1000).all()
    matched = [row for row in products if row.id in ids or row.name in text]
    selected = list({p.id: p for p in [*matched[:30], *products[:10]]}.values())
    product_ids = {row.id for row in selected}
    result = dict(allowed_operations=catalog, forbidden='禁止创建、修改、删除用户/管理员/运营账号、密码、身份、角色和模块授权；禁止用日志回退绕过限制。',
                  now=datetime.now().isoformat(timespec='seconds'),
                  products=dict(total=db.query(Product).count(), directory_limit=1000,
                                directory=[dict(id=p.id, name=p.name, category=p.category, shelf_status=p.shelf_status, has_variants=bool(p.variants)) for p in products],
                                details=[dict(id=p.id, **snapshot(db, 'products', p)) for p in selected]))
    # 仅提供买家编号和展示名供业务沟通选对象；不读取密码、手机号或管理员信息。
    buyers = db.query(User.id, User.name).filter_by(role='customer', status=1).order_by(User.id.desc()).limit(200).all()
    result['buyer_directory'] = [{'id': r.id, 'display_name': r.name} for r in buyers]
    for kind in CONTENT:
        if is_content(kind) and kind in catalog:
            rows = db.query(MallContent).filter_by(kind=kind).order_by(MallContent.id.desc()).all()
            chosen = list({r.id: r for r in [*[r for r in rows if r.id in ids or r.name in text][:30], *rows[:60]]}.values())
            result[kind] = dict(total=len(rows), complete=len(chosen) == len(rows), records=[dict(id=r.id, **snapshot(db, kind, r)) for r in chosen])
    for resource in ['orders', 'after-sales', 'reviews', 'feedback', 'alerts', 'messages', 'logs', 'conversations', 'reply-notifications']:
        if resource not in catalog:
            continue
        query = db.query(MODELS[resource])
        if resource == 'conversations':
            query = query.filter(DirectConversation.staff_id == user.id)
        if resource == 'reply-notifications':
            query = query.filter(ReviewReplyNotification.user_id == user.id)
        if resource == 'logs':
            query = query.filter(PlatformLog.rollback_data.isnot(None))
        recent = query.order_by(MODELS[resource].id.desc()).limit(30).all()
        relevant_query = query.filter(MODELS[resource].id.in_(ids)) if ids else None
        relevant = relevant_query.limit(30).all() if relevant_query is not None else []
        if resource in {'orders', 'after-sales', 'reviews', 'alerts'}:
            relevant += query.filter(MODELS[resource].product_id.in_(product_ids)).order_by(MODELS[resource].id.desc()).limit(30).all()
        rows = list({r.id: r for r in [*relevant, *recent]}.values())
        if resource == 'logs':
            rows = [r for r in rows if json.loads(r.rollback_data or '{}').get('entity_type') in {'product', 'review', 'mall_setting'}]
        result[resource] = dict(total=query.count(), scope='仅最近记录及本轮对象的相关候选；精确全量查询使用只读数据分析',
                                records=[dict(id=r.id, **snapshot(db, resource, r)) for r in rows])
    return result
