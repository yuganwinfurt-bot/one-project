"""商城运营接口；沿用当前登录与响应格式，新增功能均使用持久化数据。"""
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from app.common.response import Response
from app.config import UPLOAD_DIR
from app.dependencies.auth import CurrentUser, DbSession
from app.models.mall import (MallContent, MallSetting, CustomerActivity, MallFeedback, ProductCatalog,
                             GroupPurchase, CouponClaim)
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.shopping import CustomerAddress, FavoriteProduct
from app.services import mall_service as svc
from app.services.mall_registry import CONTENT, SETTINGS, READONLY, PERMISSIONS, field
from app.services.platform_log_service import record_changes

router = APIRouter(prefix='/mall', tags=['商城运营扩展'])


class ContentPayload(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    enabled: bool = True
    sort_order: int = Field(default=0, ge=0, le=100000)
    data: dict = Field(default_factory=dict, max_length=30)


class FeedbackPayload(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=5000)
    contact: str = Field(default='', max_length=120)


class FeedbackReply(BaseModel):
    reply: str = Field(min_length=1, max_length=5000)


class CatalogPayload(BaseModel):
    brand_id: int | None = Field(default=None, ge=1)
    category_id: int | None = Field(default=None, ge=1)


class ActivityPayload(BaseModel):
    kind: str = Field(pattern='^(footprint|search)$')
    product_id: int | None = Field(default=None, ge=1)
    keyword: str | None = Field(default=None, max_length=100)


class GroupJoin(BaseModel):
    rule_id: int = Field(ge=1)
    group_id: int | None = Field(default=None, ge=1)
    address_id: int = Field(ge=1)


class MemberStatus(BaseModel):
    status: int = Field(ge=0, le=1)


def customer(user):
    if user.role != 'customer':
        svc.fail('仅买家账号可以执行此操作', 403)


def options(db):
    # 表单选项限基础展示字段，不返回密码或其他认证资料。
    return {
        'products': [{'value': row.id, 'label': f'{row.id} · {row.name}'} for row in db.query(Product).order_by(Product.id).limit(5000)],
        'brands': [{'value': row.id, 'label': row.name} for row in db.query(MallContent).filter_by(kind='brands', enabled=True)],
        'categories': [{'value': row.id, 'label': row.name} for row in db.query(MallContent).filter_by(kind='categories', enabled=True)],
        'staff': [{'value': row.id, 'label': row.name + ' · ' + row.username} for row in db.query(User).filter_by(role='user')],
        'permissions': [{'value': key, 'label': label} for key, label in PERMISSIONS.items()],
    }


@router.get('/permissions')
def get_permissions(user: CurrentUser, db: DbSession):
    return Response.success(data={'permissions': svc.permissions(db, user)})


@router.get('/catalog-options')
def catalog_options(user: CurrentUser, db: DbSession):
    if user.role not in ('admin', 'user'):
        svc.fail('仅运营和管理员可以维护商品', 403)
    return Response.success(data={kind: [{'value': r.id, 'label': r.name} for r in db.query(MallContent).filter_by(kind=kind, enabled=True).order_by(MallContent.sort_order, MallContent.id)] for kind in ('brands', 'categories')})


@router.get('/product-catalog/{product_id}')
def product_catalog(product_id: int, user: CurrentUser, db: DbSession):
    product = db.get(Product, product_id)
    if not product or (user.role == 'customer' and (product.shelf_status != 'on_sale' or product.review_status != 'normal')):
        svc.fail('商品不存在或已下架', 404)
    mapping = db.query(ProductCatalog).filter_by(product_id=product_id).first()
    brand = db.get(MallContent, mapping.brand_id) if mapping and mapping.brand_id else None
    return Response.success(data={'brand_id': mapping.brand_id if mapping else None, 'brand_name': brand.name if brand else '', 'category_id': mapping.category_id if mapping else None})


@router.get('/admin/meta/{resource}')
def metadata(resource: str, user: CurrentUser, db: DbSession):
    svc.require(db, user, resource)
    if resource in CONTENT:
        spec = CONTENT[resource]
        fields = [field('name', '名称', required=True), *spec['fields'], field('enabled', '启用', 'switch', default=True), field('sort_order', '排序', 'number', default=0)]
        cols = [field('name', '名称'), *[f for f in spec['fields'] if f['type'] not in ('textarea', 'image', 'products', 'staff', 'permissions')], field('enabled', '启用'), field('sort_order', '排序')]
        if resource == 'coupons':
            cols += [field('claimed', '已领取'), field('used', '已使用')]
        spec = dict(title=spec['title'], fields=fields, columns=cols, editable=True, deletable=True)
    elif resource in READONLY:
        title, cols = READONLY[resource]
        spec = dict(title=title, columns=[field(key, label) for key, label in cols], editable=False, deletable=False, fields=[])
        if resource == 'catalog-products':
            spec.update(editable=True, fields=[field('brand_id', '品牌', 'brand'), field('category_id', '类目', 'category')])
    else:
        svc.fail('未知的运营模块', 404)
    return Response.success(data=spec | {'options': options(db)})


@router.get('/admin/regions')
def get_regions(user: CurrentUser, db: DbSession, parent_id: int = 0):
    svc.require(db, user, 'regions')
    return Response.success(data={'list': [r for r in svc.regions() if r['parent_id'] == parent_id]})


@router.get('/regions')
def address_regions(_user: CurrentUser, parent_id: int = 0):
    return Response.success(data={'list': [r for r in svc.regions() if r['parent_id'] == parent_id]})


@router.get('/admin/settings/{key}')
def get_settings(key: str, user: CurrentUser, db: DbSession):
    svc.require(db, user, 'settings')
    if key not in SETTINGS:
        svc.fail('未知配置', 404)
    return Response.success(data=SETTINGS[key] | {'values': svc.settings_data(db, key)})


@router.put('/admin/settings/{key}')
def put_settings(key: str, payload: dict, user: CurrentUser, db: DbSession):
    return Response.success(data=svc.save_settings(db, user, key, payload))


@router.get('/admin/statistics/{dimension}')
def statistics(dimension: str, user: CurrentUser, db: DbSession, start: str = '', end: str = ''):
    svc.require(db, user, 'statistics')
    try:
        begin = datetime.fromisoformat(start).replace(hour=0, minute=0, second=0) if start else datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=29)
        finish = datetime.fromisoformat(end).replace(hour=0, minute=0, second=0) + timedelta(days=1) if end else datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        if begin >= finish or (finish - begin).days > 366:
            raise ValueError()
    except ValueError:
        svc.fail('请选择一年以内的有效日期范围')
    valid = db.query(Order).filter(Order.create_time >= begin, Order.create_time < finish, Order.status.in_(['paid', 'shipped', 'completed']))
    total, revenue, quantity = valid.with_entities(func.count(Order.id), func.coalesce(func.sum(Order.amount), 0), func.coalesce(func.sum(Order.quantity), 0)).one()
    if dimension == 'users':
        rows = db.query(func.date(User.create_time), func.count(User.id)).filter(User.role == 'customer', User.create_time >= begin, User.create_time < finish).group_by(func.date(User.create_time)).order_by(func.date(User.create_time)).all()
        items = [{'date': str(date), 'count': count} for date, count in rows]
        columns = [field('date', '日期'), field('count', '新增买家')]
    elif dimension == 'orders':
        rows = valid.with_entities(func.date(Order.create_time), func.count(Order.id), func.sum(Order.amount), func.sum(Order.quantity)).group_by(func.date(Order.create_time)).order_by(func.date(Order.create_time)).all()
        items = [dict(date=str(date), count=count, revenue=float(amount), quantity=qty) for date, count, amount, qty in rows]
        columns = [field('date', '日期'), field('count', '有效订单'), field('quantity', '商品件数'), field('revenue', '实付金额（元）')]
    elif dimension == 'products':
        rows = valid.join(Product, Product.id == Order.product_id).with_entities(Product.name, func.count(Order.id), func.sum(Order.quantity), func.sum(Order.amount)).group_by(Product.id, Product.name).order_by(func.sum(Order.amount).desc()).limit(1000).all()
        items = [dict(name=name, count=count, quantity=qty, revenue=float(amount)) for name, count, qty, amount in rows]
        columns = [field('name', '商品'), field('count', '订单数'), field('quantity', '售出件数'), field('revenue', '实付金额（元）')]
    else:
        svc.fail('未知统计维度', 404)
    return Response.success(data=dict(list=items, columns=columns, summary={'有效订单': total, '实付总额': float(revenue), '售出件数': int(quantity)}))


def readonly_query(db, resource, keyword, user_id):
    if resource == 'members':
        query = db.query(User).filter_by(role='customer')
        if keyword:
            query = query.filter(or_(User.username.contains(keyword), User.name.contains(keyword)))
        if user_id:
            query = query.filter(User.id == user_id)
        return query, lambda u: dict(id=u.id, username=u.username, name=u.name, phone=u.phone, email=u.email, status=u.status, create_time=svc.stamp(u.create_time))
    if resource in ('addresses', 'favorites'):
        model = CustomerAddress if resource == 'addresses' else FavoriteProduct
        query = db.query(model, User.username).join(User, User.id == model.user_id)
        if resource == 'favorites':
            query = query.add_columns(Product.name).join(Product, Product.id == model.product_id)
        if user_id:
            query = query.filter(model.user_id == user_id)
        if keyword:
            query = query.filter(User.username.contains(keyword))
        def serialize(row):
            record = row[0]
            result = dict(id=record.id, user_id=record.user_id, username=row[1], create_time=svc.stamp(record.create_time))
            if resource == 'addresses':
                result.update(receiver_name=record.receiver_name, phone=record.phone, address=record.province + record.city + record.district + record.detail, is_default=record.is_default)
            else:
                result.update(product_name=row[2])
            return result
        return query, serialize
    if resource in ('footprints', 'search-history'):
        kind = 'footprint' if resource == 'footprints' else 'search'
        query = db.query(CustomerActivity, User.username, Product.name).join(User, User.id == CustomerActivity.user_id).outerjoin(Product, Product.id == CustomerActivity.product_id).filter(CustomerActivity.kind == kind)
        if user_id:
            query = query.filter(CustomerActivity.user_id == user_id)
        if keyword:
            query = query.filter(or_(User.username.contains(keyword), CustomerActivity.keyword.contains(keyword), Product.name.contains(keyword)))
        return query, lambda r: dict(id=r[0].id, user_id=r[0].user_id, username=r[1], product_name=r[2], keyword=r[0].keyword, create_time=svc.stamp(r[0].create_time))
    if resource == 'feedback':
        query = db.query(MallFeedback, User.username).join(User, User.id == MallFeedback.user_id)
        if user_id:
            query = query.filter(MallFeedback.user_id == user_id)
        if keyword:
            query = query.filter(or_(MallFeedback.name.contains(keyword), MallFeedback.content.contains(keyword), User.username.contains(keyword)))
        return query, lambda r: dict(id=r[0].id, user_id=r[0].user_id, username=r[1], name=r[0].name, content=r[0].content, contact=r[0].contact, reply=r[0].reply, status=r[0].status, create_time=svc.stamp(r[0].create_time))
    if resource == 'catalog-products':
        query = db.query(Product, ProductCatalog).outerjoin(ProductCatalog, ProductCatalog.product_id == Product.id)
        if keyword:
            query = query.filter(Product.name.contains(keyword))
        def serialize(row):
            product, mapping = row
            brand = db.get(MallContent, mapping.brand_id) if mapping and mapping.brand_id else None
            return dict(id=product.id, name=product.name, category=product.category, brand=brand.name if brand else '未设置', brand_id=mapping.brand_id if mapping else None, category_id=mapping.category_id if mapping else None, shelf_status=product.shelf_status)
        return query, serialize
    if resource == 'groups':
        svc.expire_groups(db)
        query = db.query(GroupPurchase)
        if keyword:
            query = query.join(Product, Product.id == GroupPurchase.product_id).filter(Product.name.contains(keyword))
        return query, lambda row: svc.group_data(db, row)
    svc.fail('未知模块', 404)


@router.get('/admin/{resource}')
def list_records(resource: str, user: CurrentUser, db: DbSession, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), keyword: str = Query('', max_length=100), user_id: int | None = Query(None, ge=1)):
    svc.require(db, user, resource)
    if resource in CONTENT:
        query = db.query(MallContent).filter_by(kind=resource)
        if keyword:
            query = query.filter(MallContent.name.contains(keyword))
        total = query.count()
        rows = query.order_by(MallContent.sort_order, MallContent.id.desc()).offset((page-1)*page_size).limit(page_size).all()
        items = [svc.content_data(db, row) for row in rows]
    elif resource == 'storage':
        paths = sorted((p for p in UPLOAD_DIR.rglob('*') if p.is_file() and not p.is_symlink() and (not keyword or keyword.lower() in p.name.lower())), key=lambda p: p.stat().st_mtime, reverse=True)
        total = len(paths)
        items = [dict(id=p.relative_to(UPLOAD_DIR).as_posix(), name=p.name, size=p.stat().st_size, url='/uploads/'+quote(p.relative_to(UPLOAD_DIR).as_posix()), update_time=svc.stamp(datetime.fromtimestamp(p.stat().st_mtime))) for p in paths[(page-1)*page_size:page*page_size]]
    else:
        query, serialize = readonly_query(db, resource, keyword, user_id)
        total = query.count()
        first_entity = query.column_descriptions[0]['entity']
        items = [serialize(row) for row in query.order_by(first_entity.id.desc()).offset((page-1)*page_size).limit(page_size).all()]
    return Response.success(data={'list': items, 'total': total})


@router.post('/admin/{resource}')
def create_record(resource: str, payload: ContentPayload, user: CurrentUser, db: DbSession):
    return Response.success(data=svc.save_content(db, user, resource, payload.model_dump()))


@router.put('/admin/catalog-products/{product_id}')
def catalog(product_id: int, payload: CatalogPayload, user: CurrentUser, db: DbSession):
    svc.require(db, user, 'catalog-products')
    product = db.query(Product).filter_by(id=product_id).with_for_update().first()
    if not product:
        svc.fail('商品不存在', 404)
    for kind, id_ in [('brands', payload.brand_id), ('categories', payload.category_id)]:
        if id_ and not db.query(MallContent).filter_by(kind=kind, id=id_, enabled=True).first():
            svc.fail('请选择有效品牌或类目')
    row = db.query(ProductCatalog).filter_by(product_id=product_id).first()
    before = {'category': product.category, 'brand_id': row.brand_id if row else None}
    if not row:
        row = ProductCatalog(product_id=product_id)
        db.add(row)
    row.brand_id, row.category_id = payload.brand_id, payload.category_id
    if payload.category_id:
        old_category = product.category
        product.category = db.get(MallContent, payload.category_id).name[:50]
        extra_tags = [tag for tag in (product.tags or []) if tag not in (old_category, product.category)]
        product.tags = list(dict.fromkeys([product.category, *extra_tags]))
    record_changes(db, user, '商品', product.name, [('品牌与类目', before, payload.model_dump())])
    db.commit()
    return Response.success()


@router.put('/admin/members/{record_id}/status')
def member_status(record_id: int, payload: MemberStatus, user: CurrentUser, db: DbSession):
    if user.role != 'admin':
        svc.fail('仅管理员可修改会员状态', 403)
    row = db.query(User).filter_by(id=record_id, role='customer').with_for_update().first()
    if not row:
        svc.fail('会员不存在', 404)
    record_changes(db, user, '会员', row.username, [('状态', row.status, payload.status)])
    row.status = payload.status
    db.commit()
    return Response.success()


@router.put('/admin/feedback/{record_id}')
def reply_feedback(record_id: int, payload: FeedbackReply, user: CurrentUser, db: DbSession):
    svc.require(db, user, 'feedback')
    row = db.get(MallFeedback, record_id)
    if not row:
        svc.fail('反馈不存在', 404)
    reply = payload.reply.strip()
    if not reply:
        svc.fail('回复不能为空')
    record_changes(db, user, '反馈', row.name, [('回复', row.reply, reply)])
    row.reply, row.status = reply, 'replied'
    db.commit()
    return Response.success()


@router.put('/admin/{resource}/{record_id}')
def update_record(resource: str, record_id: int, payload: ContentPayload, user: CurrentUser, db: DbSession):
    return Response.success(data=svc.save_content(db, user, resource, payload.model_dump(), record_id))


@router.delete('/admin/{resource}/{record_id}')
def delete_record(resource: str, record_id: int, user: CurrentUser, db: DbSession):
    if resource not in CONTENT:
        svc.fail('此模块保留原始记录，不支持删除')
    svc.remove_content(db, user, resource, record_id)
    return Response.success()


@router.get('/portal')
def portal(user: CurrentUser, db: DbSession):
    # 商品首页需要展示对买家公开的优惠券和团购规则。
    kinds = ('ads', 'topics', 'keywords', 'faqs', 'notices', 'brands', 'coupons', 'group-rules')
    result = {kind: [] for kind in kinds}
    for entry in db.query(MallContent).filter(MallContent.kind.in_(kinds), MallContent.enabled.is_(True)).order_by(MallContent.sort_order, MallContent.id.desc()):
        if not svc.active(entry) or (entry.kind == 'notices' and entry.data.get('audience', 'all') not in ('all', user.role)):
            continue
        result[entry.kind].append(svc.content_data(db, entry))
    result.update(shop=svc.settings_data(db, 'mall'), shipping=svc.settings_data(db, 'shipping'), order=svc.settings_data(db, 'order'))
    return Response.success(data=result)


@router.get('/topics/{topic_id}/products')
def topic_products(topic_id: int, _user: CurrentUser, db: DbSession):
    entry = db.query(MallContent).filter_by(id=topic_id, kind='topics').first()
    if not entry or not svc.active(entry):
        svc.fail('专题已下线', 404)
    return Response.success(data={'list': [dict(id=p.id, name=p.name, price=float(p.price), image_url=p.image_url) for p in db.query(Product).filter(Product.id.in_(entry.data.get('product_ids', [])), Product.shelf_status == 'on_sale', Product.review_status == 'normal')]})


@router.post('/activities')
def activity(payload: ActivityPayload, user: CurrentUser, db: DbSession):
    customer(user)
    if payload.kind == 'footprint' and not payload.product_id:
        svc.fail('缺少商品编号')
    keyword = (payload.keyword or '').strip()
    if payload.kind == 'search' and not keyword:
        svc.fail('关键词不能为空')
    svc.track(db, user, payload.kind, payload.product_id if payload.kind == 'footprint' else None, keyword if payload.kind == 'search' else None)
    return Response.success()


@router.get('/my/feedback')
def my_feedback(user: CurrentUser, db: DbSession):
    customer(user)
    rows = db.query(MallFeedback).filter_by(user_id=user.id).order_by(MallFeedback.id.desc()).limit(200).all()
    return Response.success(data={'list': [dict(id=r.id, name=r.name, content=r.content, reply=r.reply, status=r.status, create_time=svc.stamp(r.create_time)) for r in rows]})


@router.post('/my/feedback')
def send_feedback(payload: FeedbackPayload, user: CurrentUser, db: DbSession):
    customer(user)
    if not payload.name.strip() or not payload.content.strip():
        svc.fail('主题和内容不能为空')
    db.add(MallFeedback(user_id=user.id, **payload.model_dump()))
    db.commit()
    return Response.success()


@router.get('/my/coupons')
def my_coupons(user: CurrentUser, db: DbSession):
    customer(user)
    return Response.success(data={'list': svc.coupon_list(db, user)})


@router.post('/my/coupons/{coupon_id}/claim')
def receive_coupon(coupon_id: int, user: CurrentUser, db: DbSession):
    customer(user)
    svc.claim_coupon(db, user, coupon_id)
    return Response.success(message='优惠券已领取')


@router.get('/my/groups')
def groups(user: CurrentUser, db: DbSession):
    customer(user)
    svc.expire_groups(db)
    rules = db.query(MallContent).filter_by(kind='group-rules', enabled=True).order_by(MallContent.id.desc()).all()
    sessions = db.query(GroupPurchase).order_by(GroupPurchase.id.desc()).limit(200).all()
    return Response.success(data={'rules': [svc.content_data(db, r) for r in rules if svc.active(r)], 'groups': [svc.group_data(db, r) for r in sessions]})


@router.post('/my/groups')
def participate(payload: GroupJoin, user: CurrentUser, db: DbSession):
    customer(user)
    svc.expire_groups(db)
    return Response.success(data=svc.join_group(db, user, payload.rule_id, payload.group_id, payload.address_id))
