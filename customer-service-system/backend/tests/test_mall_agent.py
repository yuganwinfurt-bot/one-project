"""配置助手的权限、确认、过期预览和批量回滚回归；只使用临时内存库。"""
import json
from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.common.exceptions import BusinessException
from app.database import Base
from app.models import User
from app.models.mall import CouponClaim, MallContent, MallSetting
from app.services.action_service import execute_actions
from app.services.mall_agent_service import build_management_actions, parse_management_plan
from app.services.mall_service import coupon_list, settings_data


@pytest.fixture()
def shop():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine, autoflush=False) as db:
        admin = User(username='admin', name='Admin', password='test', role='admin', status=1)
        buyer = User(username='buyer', name='Buyer', password='test', role='customer', status=1)
        staff = User(username='staff', name='Staff', password='test', role='user', status=1)
        coupon = MallContent(kind='coupons', name='满199减25', enabled=True, sort_order=0, data={
            'discount': 25, 'min_amount': 199, 'quantity': 100,
            'starts_at': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
        })
        db.add_all([admin, buyer, staff, coupon]); db.commit()
        yield SimpleNamespace(db=db, engine=engine, admin=admin, buyer=buyer, staff=staff, coupon=coupon)
    engine.dispose()


def plan(shop, patch=None):
    return {'message': '调整优惠金额，等待确认', 'changes': [{'resource': 'coupons', 'id': shop.coupon.id, 'patch': patch or {'discount': 30}}]}


def test_plan_is_read_only_and_preserves_unmentioned_fields(shop):
    actions = build_management_actions(shop.db, shop.admin.id, plan(shop))
    assert shop.coupon.data['discount'] == 25
    assert actions[0]['after']['name'] == '满199减30'
    assert actions[0]['after']['data']['min_amount'] == 199
    assert actions[0]['changes'][0]['before'] == '25'
    execute_actions(shop.db, actions, {'user_id': shop.admin.id})
    assert shop.coupon.data['discount'] == 30 and shop.coupon.name == '满199减30'


def test_permissions_are_checked_again_at_execution(shop):
    actions = build_management_actions(shop.db, shop.admin.id, plan(shop))
    with pytest.raises(BusinessException):
        execute_actions(shop.db, actions, {'user_id': shop.buyer.id})
    assert shop.coupon.data['discount'] == 25
    setting_plan = {'message': 'change', 'changes': [{'resource': 'settings-order', 'id': None, 'patch': {'unpaid_timeout_minutes': 45}}]}
    actions = build_management_actions(shop.db, shop.admin.id, setting_plan)
    with pytest.raises(BusinessException):
        execute_actions(shop.db, actions, {'user_id': shop.staff.id})
    assert settings_data(shop.db, 'order')['unpaid_timeout_minutes'] == 30


def test_stale_second_action_rolls_back_first_and_its_audit(shop):
    proposal = plan(shop)
    proposal['changes'].insert(0, {'resource': 'settings-order', 'id': None, 'patch': {'unpaid_timeout_minutes': 45}})
    actions = build_management_actions(shop.db, shop.admin.id, proposal)
    shop.coupon.name = '其他操作刚修改过名称'
    shop.db.commit()
    with pytest.raises(BusinessException):
        execute_actions(shop.db, actions, {'user_id': shop.admin.id})
    assert shop.db.query(MallSetting).count() == 0
    assert shop.coupon.data['discount'] == 25


def test_editing_coupon_keeps_claimed_terms_and_updates_new_claims(shop):
    claim = CouponClaim(user_id=shop.buyer.id, coupon_id=shop.coupon.id)
    shop.db.add(claim); shop.db.commit()
    actions = build_management_actions(shop.db, shop.admin.id, plan(shop))
    execute_actions(shop.db, actions, {'user_id': shop.admin.id})
    assert claim.terms['discount'] == 25 and claim.terms['name'] == '满199减25'
    assert coupon_list(shop.db, shop.buyer)[0]['discount'] == 25
    assert coupon_list(shop.db, shop.staff)[0]['discount'] == 30


@pytest.mark.parametrize('resource,patch', [('coupons', {'discount': -1}), ('coupons', {'password': 'bad'}), ('settings-order', {'unpaid_timeout_minutes': 0}), ('orders', {'status': 'paid'})])
def test_invalid_or_unrelated_mutations_are_rejected(shop, resource, patch):
    with pytest.raises(BusinessException):
        build_management_actions(shop.db, shop.admin.id, {'message': 'x', 'changes': [{'resource': resource, 'id': shop.coupon.id if resource == 'coupons' else None, 'patch': patch}]})
    assert shop.coupon.data['discount'] == 25 and shop.db.query(MallSetting).count() == 0


def test_graph_waits_for_same_user_confirmation_then_saves(shop, monkeypatch):
    from app.agent import nodes
    from app.agent.graph import build_analysis_graph
    from app.agent.router import RouteDecision
    from app.services import confirmation_service
    import app.utils.llm as llm
    monkeypatch.setattr(nodes, 'SessionLocal', lambda: Session(shop.engine, autoflush=False))
    monkeypatch.setattr(confirmation_service, 'SessionLocal', lambda: Session(shop.engine, autoflush=False))
    monkeypatch.setattr(nodes, 'decide_query_route', lambda *args: RouteDecision('management', '修改优惠券', {}))
    monkeypatch.setattr(llm, 'chat_once', lambda *args: json.dumps(plan(shop), ensure_ascii=False))
    graph = build_analysis_graph()
    monkeypatch.setattr(confirmation_service, 'get_analysis_graph', lambda: graph)
    thread = str(uuid4())
    from app.observability import service as obs
    run = obs.create_run(shop.db, thread_id=thread, question='调整优惠券', user_id=shop.admin.id)
    run.answer_text = '修改方案待确认，尚未保存。'
    shop.db.commit()
    graph.invoke({'question': '把满199减25改成满199减30', 'user_id': shop.admin.id, 'use_agent_model': False, 'actions_executed': []}, {'configurable': {'thread_id': thread}})
    shop.db.expire_all()
    assert shop.coupon.data['discount'] == 25
    pending = confirmation_service.get_pending_confirmation(thread, shop.admin.id)
    assert pending['actions'][0]['changes']
    assert confirmation_service.get_pending_confirmation(thread, shop.buyer.id) is None
    with pytest.raises(BusinessException):
        confirmation_service.resume_actions(thread, True, shop.buyer.id)
    result = confirmation_service.resume_actions(thread, True, shop.admin.id)
    assert result['actions_executed'][0]['ok']
    assert '配置已保存' in result['answer'] and '配置执行结果' in result['answer']
    shop.db.expire_all()
    assert shop.coupon.data['discount'] == 30
    with pytest.raises(BusinessException):
        confirmation_service.resume_actions(thread, True, shop.admin.id)


def test_management_query_plan_cannot_bypass_sql_or_use_invalid_ids():
    from app.agent.router import parse_query_plan
    raw = dict(route='management', reason='config', analysis_scope='order', time_scope='now', retrieval_question='config', semantic_query='', products=[], needs_semantic=False, requires_complete_data=False, doc_types=[], analyze_business_records=False, sql='UPDATE users SET role=admin')
    assert parse_query_plan(json.dumps(raw), []).signals['sql'] is None
    with pytest.raises(ValueError):
        parse_management_plan(json.dumps({'message': 'x', 'changes': [{'resource': 'coupons', 'id': {}, 'patch': {'discount': 2}}]}))
