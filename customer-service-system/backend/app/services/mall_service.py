"""商城配置、运营资料、真实用户行为、优惠结算与拼团事务。"""
import json
import math
import re
import secrets
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

from sqlalchemy import func
from app.common.exceptions import BusinessException
from app.models.mall import (MallContent, MallSetting, CustomerActivity, MallFeedback, ProductCatalog,
                             CouponClaim, CouponStock, OrderPromotion, GroupPurchase, GroupMember, StaffPermission)
from app.models.after_sale import AfterSaleRequest
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.services.mall_registry import CONTENT, PERMISSIONS, SETTINGS
from app.services.platform_log_service import build_rollback_data, record_changes


def fail(message, code=400):
    raise BusinessException(message=message, code=code)


def stamp(value):
    return value.strftime('%Y-%m-%d %H:%M:%S') if value else None


def money(value):
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def active(entry):
    now = datetime.now()
    return entry.enabled and (not entry.data.get('starts_at') or datetime.fromisoformat(entry.data['starts_at']) <= now) and (not entry.data.get('ends_at') or now < datetime.fromisoformat(entry.data['ends_at']))


def permissions(db, user):
    if user.role == 'admin':
        return list(PERMISSIONS) + ['roles', 'settings']
    if user.role != 'user':
        return []
    membership = db.query(StaffPermission).filter_by(user_id=user.id).first()
    if membership:
        role = db.query(MallContent).filter_by(id=membership.role_id, kind='roles').first()
        return role.data.get('permissions', []) if role and role.enabled else []
    return list(PERMISSIONS)


def require(db, user, key):
    if key not in permissions(db, user):
        fail('当前账号没有此模块权限', 403)


def values(fields, payload):
    if not isinstance(payload, dict) or set(payload) - {item['key'] for item in fields}:
        fail('提交内容含有不支持的字段')
    result = {}
    for item in fields:
        key, kind = item['key'], item['type']
        value = payload.get(key, item.get('default'))
        if value is None or value == '':
            if item.get('required'):
                fail('请填写' + item['label'])
            value = [] if kind in ('products', 'staff', 'permissions') else (None if kind in ('product', 'category') else '')
        if kind in ('number', 'money'):
            try:
                number = float(value or 0)
                if not math.isfinite(number) or number < item.get('min', 0) or number > item.get('max', 99999999):
                    raise ValueError()
                if kind == 'number' and not number.is_integer():
                    raise ValueError()
                value = int(number) if kind == 'number' else float(money(number))
            except (TypeError, ValueError, ArithmeticError):
                fail(item['label'] + '数值无效')
        elif kind in ('products', 'staff', 'permissions'):
            if not isinstance(value, list) or len(value) > 500:
                fail(item['label'] + '格式无效')
            if kind != 'permissions':
                if any(type(v) is not int or v < 1 for v in value):
                    fail(item['label'] + '编号无效')
            elif any(v not in PERMISSIONS for v in value):
                fail('包含未知的权限')
            value = list(dict.fromkeys(value))
        elif kind in ('product', 'category'):
            if value is not None and (type(value) is not int or value < 1):
                fail(item['label'] + '编号无效')
        elif kind == 'switch':
            if type(value) is not bool:
                fail(item['label'] + '格式无效')
        else:
            if not isinstance(value, str):
                fail(item['label'] + '格式无效')
            value = value.strip()
            if len(value) > (10000 if kind == 'textarea' else 500):
                fail(item['label'] + '内容过长')
            if item.get('required') and not value:
                fail('请填写' + item['label'])
            if kind == 'datetime' and value:
                try:
                    date = datetime.fromisoformat(value)
                    if date.tzinfo:
                        fail('请选择本地时间')
                    value = stamp(date)
                except ValueError:
                    fail(item['label'] + '格式无效')
            if kind in ('url', 'image') and value:
                if not ((value.startswith('/') and not value.startswith('//')) or urlsplit(value).scheme in ('http', 'https')) or '\\' in value or re.search(r'[\s\x00-\x1f]', value):
                    fail(item['label'] + '须为网站路径或 HTTP/HTTPS 地址')
            if kind == 'select' and value not in [option['value'] for option in item['options']]:
                fail(item['label'] + '选项无效')
        result[key] = value
    if result.get('starts_at') and result.get('ends_at') and result['starts_at'] >= result['ends_at']:
        fail('结束时间必须晚于开始时间')
    return result


def content_data(db, entry):
    data = dict(id=entry.id, name=entry.name, enabled=entry.enabled, sort_order=entry.sort_order,
                create_time=stamp(entry.create_time), **entry.data)
    if entry.kind == 'coupons':
        data['claimed'] = db.query(CouponClaim).filter_by(coupon_id=entry.id).count()
        data['used'] = db.query(CouponClaim).filter(CouponClaim.coupon_id == entry.id, CouponClaim.used_at.isnot(None)).count()
    if entry.kind == 'roles':
        data['user_ids'] = [row.user_id for row in db.query(StaffPermission).filter_by(role_id=entry.id).all()]
    return data


def validate_refs(db, kind, data, entry_id=None):
    product_ids = data.get('product_ids', []) + ([data['product_id']] if data.get('product_id') else [])
    if product_ids and db.query(Product).filter(Product.id.in_(product_ids)).count() != len(set(product_ids)):
        fail('部分商品已不存在')
    if kind == 'categories':
        seen = {entry_id} if entry_id else set()
        parent = data.get('parent_id')
        while parent:
            if parent in seen:
                fail('类目不能形成循环层级')
            seen.add(parent)
            ancestor = db.query(MallContent).filter_by(kind='categories', id=parent).first()
            if not ancestor or len(seen) > 10:
                fail('上级类目不存在或层级过深')
            parent = ancestor.data.get('parent_id')
    if kind == 'roles':
        ids = data.get('user_ids', [])
        if ids and db.query(User).filter(User.id.in_(ids), User.role == 'user').count() != len(ids):
            fail('角色只能绑定现有运营账号')
    if kind == 'group-rules':
        product = db.get(Product, data['product_id'])
        if product.variants:
            fail('多规格商品暂不支持团购，请选择单规格商品')
        if money(data['price']) > money(product.price):
            fail('团购价不能高于商品售价')


def save_content(db, user, kind, payload, entry_id=None, *, commit=True):
    require(db, user, kind)
    spec = CONTENT.get(kind)
    if not spec:
        fail('未知的运营模块', 404)
    entry = db.query(MallContent).filter_by(id=entry_id, kind=kind).with_for_update().first() if entry_id else None
    if entry_id and not entry:
        fail('记录不存在', 404)
    data = values(spec['fields'], payload['data'])
    validate_refs(db, kind, data, entry_id)
    before = content_data(db, entry) if entry else None
    if entry and kind == 'coupons' and db.query(CouponClaim).filter_by(coupon_id=entry.id).with_for_update().first():
        if any(data[k] != entry.data[k] for k in ('discount', 'min_amount', 'starts_at', 'ends_at')):
            for claim in db.query(CouponClaim).filter_by(coupon_id=entry.id).with_for_update():
                if not claim.terms:
                    claim.terms = {'name': entry.name, **entry.data}
        if data['quantity'] < coupon_stock(db, entry.id).issued:
            fail('发放总量不能少于已领取数量')
    if not entry:
        entry = MallContent(kind=kind)
        db.add(entry)
    entry.name = payload['name'].strip()
    if not entry.name:
        fail('名称不能为空')
    if kind == 'categories' and len(entry.name) > 50:
        fail('类目名称不能超过 50 个字')
    entry.enabled, entry.sort_order, entry.data = payload['enabled'], payload['sort_order'], data
    db.flush()
    if kind == 'roles':
        db.query(StaffPermission).filter_by(role_id=entry.id).delete(synchronize_session=False)
        for user_id in data['user_ids']:
            membership = db.query(StaffPermission).filter_by(user_id=user_id).first()
            if membership and membership.role_id != entry.id:
                fail('此运营账号已绑定其他角色，请先在原角色中移除')
            db.add(StaffPermission(user_id=user_id, role_id=entry.id))
        db.flush()
    if kind == 'categories':
        mappings = db.query(ProductCatalog).filter_by(category_id=entry.id).all()
        for mapping in mappings:
            product = db.get(Product, mapping.product_id)
            product.category = entry.name[:50]
            if before and before['name'] in (product.tags or []):
                product.tags = list(dict.fromkeys(entry.name if tag == before['name'] else tag for tag in product.tags))
    record_changes(db, user, spec['title'], entry.name, [('内容', before, content_data(db, entry))], verb='保存了')
    if commit:
        db.commit()
    return content_data(db, entry)


def remove_content(db, user, kind, entry_id, *, commit=True):
    require(db, user, kind)
    entry = db.query(MallContent).filter_by(kind=kind, id=entry_id).with_for_update().first()
    if not entry:
        fail('记录不存在', 404)
    if kind == 'coupons' and db.query(CouponClaim).filter_by(coupon_id=entry_id).with_for_update().first():
        fail('优惠券已被领取，请改为停用以保留记录')
    if kind == 'group-rules' and db.query(GroupPurchase).filter_by(rule_id=entry_id).with_for_update().first():
        fail('规则已有团购记录，请改为停用')
    if kind in ('brands', 'categories'):
        column = ProductCatalog.brand_id if kind == 'brands' else ProductCatalog.category_id
        if db.query(ProductCatalog).filter(column == entry_id).first():
            fail('仍有商品使用此记录，请先调整商品归属')
        if kind == 'categories':
            if any(row.data.get('parent_id') == entry_id for row in db.query(MallContent).filter_by(kind=kind).all()):
                fail('请先移除子类目')
    if kind == 'roles' and db.query(StaffPermission).filter_by(role_id=entry_id).first():
        fail('角色仍绑定运营账号，请先移除绑定')
    record_changes(db, user, CONTENT[kind]['title'], entry.name, [('内容', content_data(db, entry), None)], verb='删除了')
    if kind == 'coupons':
        db.query(CouponStock).filter_by(coupon_id=entry_id).delete(synchronize_session=False)
    db.delete(entry)
    if commit:
        db.commit()
    else:
        db.flush()


def settings_data(db, key):
    row = db.query(MallSetting).filter_by(key=key).first()
    defaults = {item['key']: item.get('default', False if item['type'] == 'switch' else '') for item in SETTINGS[key]['fields']}
    return defaults | (row.data if row else {})


def save_settings(db, user, key, payload, *, commit=True):
    require(db, user, 'settings')
    if key not in SETTINGS:
        fail('未知配置', 404)
    value = values(SETTINGS[key]['fields'], payload)
    row = db.query(MallSetting).filter_by(key=key).populate_existing().with_for_update().first()
    before = settings_data(db, key)
    if not row:
        row = MallSetting(key=key)
        db.add(row)
    row.data = value
    db.flush()
    record_changes(
        db,
        user,
        '商城配置',
        SETTINGS[key]['title'],
        [('内容', before, value)],
        rollback_data=build_rollback_data('mall_setting', row.id, {'data': (before, value)}),
    )
    if commit:
        db.commit()
    return value


def initialize(db):
    # 原有类目可直接在新后台中维护；不导入 litemall 的示例商品或账号。
    if not db.query(MallContent).filter_by(kind='categories').first():
        for (name,) in db.query(Product.category).distinct().all():
            if name:
                db.add(MallContent(kind='categories', name=name, data={'parent_id': None, 'description': '', 'image_url': ''}))
    db.flush()
    categories = {entry.name: entry.id for entry in db.query(MallContent).filter_by(kind='categories')}
    mapped = {row.product_id for row in db.query(ProductCatalog)}
    for product in db.query(Product):
        if product.id not in mapped and product.category in categories:
            db.add(ProductCatalog(product_id=product.id, category_id=categories[product.category]))
    db.commit()


def sync_catalog(db, product, payload):
    """在原有商品保存事务内同步品牌和主类目，不额外提交。"""
    category = db.query(MallContent).filter_by(kind='categories', name=product.category).first()
    if not category:
        category = MallContent(kind='categories', name=product.category, data={'parent_id': None, 'description': '', 'image_url': ''})
        db.add(category)
        db.flush()
    elif not category.enabled:
        fail('此类目已停用，请选择其他类目')
    mapping = db.query(ProductCatalog).filter_by(product_id=product.id).first()
    if not mapping:
        mapping = ProductCatalog(product_id=product.id)
        db.add(mapping)
    mapping.category_id = category.id
    if 'brand_id' in payload.model_fields_set:
        brand_id = payload.brand_id
        if brand_id and not db.query(MallContent).filter_by(id=brand_id, kind='brands', enabled=True).first():
            fail('所选品牌不存在或已停用')
        mapping.brand_id = brand_id


@lru_cache(maxsize=1)
def regions():
    return json.loads((Path(__file__).resolve().parents[2] / 'data/mall_regions.json').read_text(encoding='utf-8'))


def track(db, user, kind, product_id=None, keyword=None):
    if user.role != 'customer':
        return
    if kind == 'footprint':
        product = db.get(Product, product_id)
        if not product or product.shelf_status != 'on_sale' or product.review_status != 'normal':
            return
    # 短时间重复加载不刷屏；查询失败不能阻断商城原有流程。
    query = db.query(CustomerActivity).filter_by(user_id=user.id, kind=kind, product_id=product_id, keyword=keyword)
    recent = query.filter(CustomerActivity.create_time > datetime.now() - timedelta(minutes=1)).first()
    if not recent:
        db.add(CustomerActivity(user_id=user.id, kind=kind, product_id=product_id, keyword=keyword))
        db.commit()


def coupon_list(db, user):
    claims = {row.coupon_id: row for row in db.query(CouponClaim).filter_by(user_id=user.id).all()}
    result = []
    for entry in db.query(MallContent).filter_by(kind='coupons').order_by(MallContent.id.desc()).all():
        claim = claims.get(entry.id)
        if not active(entry) and not claim:
            continue
        row = content_data(db, entry)
        terms = claim.terms if claim and claim.terms else {'name': entry.name, **entry.data}
        if claim:
            row.update(terms)
        row.update(claim_id=claim.id if claim else None, used_at=stamp(claim.used_at) if claim else None, reserved=bool(claim and claim.reserved_checkout_id), available=coupon_active(entry, terms))
        result.append(row)
    return result


def claim_coupon(db, user, coupon_id):
    entry = db.query(MallContent).filter_by(kind='coupons', id=coupon_id).populate_existing().with_for_update().first()
    if not entry or not active(entry):
        fail('优惠券未开放领取或已结束')
    if db.query(CouponClaim).filter_by(user_id=user.id, coupon_id=entry.id).with_for_update().first():
        fail('每人限领一次')
    stock = coupon_stock(db, entry.id)
    if stock.issued >= entry.data['quantity']:
        fail('优惠券已领完')
    stock.issued += 1
    db.add(CouponClaim(user_id=user.id, coupon_id=entry.id, terms={'name': entry.name, **entry.data}))
    db.commit()


def coupon_stock(db, coupon_id):
    # 调用方先锁定优惠券定义；避免 MySQL 一致性快照导致并发计数过期。
    stock = db.query(CouponStock).filter_by(coupon_id=coupon_id).populate_existing().with_for_update().first()
    if not stock:
        issued = len(db.query(CouponClaim.id).filter_by(coupon_id=coupon_id).with_for_update().all())
        stock = CouponStock(coupon_id=coupon_id, issued=issued)
        db.add(stock)
        db.flush()
    return stock


def coupon_active(entry, terms):
    now = datetime.now()
    return entry.enabled and (not terms.get('starts_at') or datetime.fromisoformat(terms['starts_at']) <= now) and (not terms.get('ends_at') or now < datetime.fromisoformat(terms['ends_at']))


def price_orders(db, user, orders, claim_id=None):
    """同一购物车拆成多订单时按分摊金额保存，金额与库存处于同一事务。"""
    config = settings_data(db, 'order')
    if not config['checkout_enabled']:
        fail('商城暂时关闭下单，请稍后再试')
    if any(order.quantity > config['max_quantity'] for order in orders):
        fail('购买数量超过商城设置的单项上限')
    subtotal = sum((money(order.amount) for order in orders), Decimal('0'))
    discount, claim = Decimal('0'), None
    if claim_id:
        snapshot = db.query(CouponClaim).filter_by(id=claim_id, user_id=user.id).first()
        if not snapshot:
            fail('找不到属于你的优惠券')
        coupon = db.query(MallContent).filter_by(id=snapshot.coupon_id, kind='coupons').with_for_update().first()
        claim = db.query(CouponClaim).filter_by(id=claim_id, user_id=user.id).populate_existing().with_for_update().first()
        terms = (claim.terms or coupon.data) if coupon else {}
        if claim.used_at or claim.reserved_checkout_id or not coupon or not coupon_active(coupon, terms):
            fail('优惠券已使用、已停用或不在有效期内')
        if subtotal < money(terms['min_amount']):
            fail('商品金额未达到优惠券使用门槛')
        discount = min(money(terms['discount']), max(Decimal('0'), subtotal - Decimal('0.01')))
        if not claim.terms:
            claim.terms = {'name': coupon.name, **coupon.data}
        if orders[0].status == 'unpaid' and orders[0].checkout_id:
            claim.reserved_checkout_id = orders[0].checkout_id
        else:
            claim.used_at = datetime.now()
    config = settings_data(db, 'shipping')
    shipping = Decimal('0') if subtotal >= money(config['free_over']) and money(config['free_over']) > 0 else money(config['base_fee'])
    discount_cents = int(discount * 100)
    weights = [money(order.amount) for order in orders]
    exact = [Decimal(discount_cents) * weight / subtotal for weight in weights]
    allocations = [int(value) for value in exact]
    for index in sorted(range(len(orders)), key=lambda i: exact[i] - allocations[i], reverse=True)[:discount_cents - sum(allocations)]:
        allocations[index] += 1
    shipping_so_far = Decimal('0')
    for index, order in enumerate(orders):
        last = index == len(orders) - 1
        part_discount = Decimal(allocations[index]) / 100
        part_shipping = shipping - shipping_so_far if last else (shipping * money(order.amount) / subtotal).quantize(Decimal('0.01'), rounding='ROUND_DOWN')
        order.amount = money(order.amount) - part_discount + part_shipping
        shipping_so_far += part_shipping
        db.flush()
        db.add(OrderPromotion(order_id=order.id, coupon_claim_id=claim.id if claim else None, discount=part_discount, shipping_fee=part_shipping))


def promotion_data(db, order_id):
    promotion = db.query(OrderPromotion).filter_by(order_id=order_id).first()
    return {'discount': float(promotion.discount), 'shipping_fee': float(promotion.shipping_fee)} if promotion else {'discount': 0, 'shipping_fee': 0}


def group_data(db, group):
    product, leader = db.get(Product, group.product_id), db.get(User, group.leader_id)
    return dict(id=group.id, rule_id=group.rule_id, product_id=group.product_id, product_name=product.name if product else '已删除商品',
                leader=leader.name if leader else '', member_count=db.query(GroupMember).filter_by(group_id=group.id).count(),
                target_size=group.target_size, price=float(group.price), status=group.status, expires_at=stamp(group.expires_at))


def expire_groups(db):
    from app.services.inventory_service import sync_product_inventory
    groups = db.query(GroupPurchase).filter(GroupPurchase.status == 'forming', GroupPurchase.expires_at <= datetime.now()).order_by(GroupPurchase.id).with_for_update().all()
    for group in groups:
        group.status = 'expired'
        product = db.query(Product).filter_by(id=group.product_id).with_for_update().first()
        for member in db.query(GroupMember).filter_by(group_id=group.id).with_for_update().all():
            order = db.query(Order).filter_by(id=member.order_id).with_for_update().first()
            if order and order.status == 'group_pending':
                order.status = 'cancelled'
                if product:
                    product.stock += order.quantity
        if product:
            sync_product_inventory(db, product.id)
    db.commit()


def expire_shipped_orders(db):
    """按订单配置自动确认已发货订单；处理中售后订单保留原状态。"""
    config = settings_data(db, 'order')
    cutoff = datetime.now() - timedelta(days=config['auto_confirm_days'])
    orders = (
        db.query(Order)
        .filter(
            Order.status == 'shipped',
            func.coalesce(Order.shipped_at, Order.update_time) <= cutoff,
        )
        .with_for_update()
        .all()
    )
    changed = False
    for order in orders:
        active_after_sale = db.query(AfterSaleRequest.id).filter(
            AfterSaleRequest.order_id == order.id,
            AfterSaleRequest.status.in_(('pending', 'approved')),
        ).first()
        if active_after_sale:
            continue
        order.status = 'completed'
        order.received_at = datetime.now()
        changed = True
    if changed:
        db.commit()
    return changed


def join_group(db, user, rule_id, group_id, address_id):
    from app.models.shopping import CustomerAddress
    from app.services.inventory_service import sync_product_inventory
    from app.services.staff_inbox_service import notify_order_paid
    config = settings_data(db, 'order')
    if not config['checkout_enabled']:
        fail('商城暂时关闭下单')
    rule = db.query(MallContent).filter_by(id=rule_id, kind='group-rules').with_for_update().first()
    if not rule or not active(rule):
        fail('团购规则不存在或活动已结束')
    address = db.query(CustomerAddress).filter_by(id=address_id, user_id=user.id).first()
    if not address:
        fail('请选择自己的收货地址')
    if group_id:
        group = db.query(GroupPurchase).filter_by(id=group_id, rule_id=rule_id).with_for_update().first()
        if not group or group.status != 'forming' or group.expires_at <= datetime.now():
            fail('此团已结束，请选择其他团')
        if db.query(GroupMember).filter_by(group_id=group.id, user_id=user.id).with_for_update().first():
            fail('你已经参加了这个团')
    else:
        group = GroupPurchase(rule_id=rule.id, product_id=rule.data['product_id'], leader_id=user.id,
                              target_size=rule.data['target_size'], price=money(rule.data['price']),
                              expires_at=min(datetime.now() + timedelta(hours=rule.data['hours']), datetime.fromisoformat(rule.data['ends_at'])))
        db.add(group)
        db.flush()
    count = len(db.query(GroupMember).filter_by(group_id=group.id).with_for_update().all())
    if count >= group.target_size:
        fail('该团已满')
    product = db.query(Product).filter_by(id=group.product_id).with_for_update().first()
    if product and product.variants:
        fail('多规格商品暂不支持团购')
    if not product or product.stock < 1 or product.shelf_status != 'on_sale' or product.review_status != 'normal':
        fail('商品库存不足或当前不可购买')
    product.stock -= 1
    order = Order(order_no=f'G{datetime.now():%y%m%d%H%M%S}{secrets.token_hex(3).upper()}', product_id=product.id,
                  buyer_name=user.name or user.username, buyer_user_id=user.id,
                  shipping_address=f'{address.receiver_name}，{address.phone}，{address.province}{address.city}{address.district}{address.detail}',
                  quantity=1, amount=group.price, status='group_pending')
    db.add(order)
    db.flush()
    db.add(GroupMember(group_id=group.id, user_id=user.id, order_id=order.id))
    if count + 1 >= group.target_size:
        group.status = 'completed'
        db.flush()
        for member in db.query(GroupMember).filter_by(group_id=group.id).with_for_update().all():
            member_order = db.get(Order, member.order_id)
            if member_order.status == 'group_pending':
                member_order.status = 'paid'
                notify_order_paid(db, member_order, product.name)
    sync_product_inventory(db, product.id)
    db.commit()
    return group_data(db, group)
