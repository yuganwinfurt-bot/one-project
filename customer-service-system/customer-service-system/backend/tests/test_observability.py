"""观测服务单元测试（不依赖大模型）。"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.common.exceptions import BusinessException
from app.database import Base
from app.models.user import User  # noqa: F401  注册 users 表，满足外键解析
from app.observability import service as obs_service
from app.observability.models import AgentFeedback, AgentRun, AgentRunStep


@pytest.fixture()
def db():
    """内存 SQLite，隔离每次测试。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # 观测表外键指向 users，需一并建表
    Base.metadata.create_all(
        bind=engine,
        tables=[
            User.__table__,
            AgentRun.__table__,
            AgentRunStep.__table__,
            AgentFeedback.__table__,
        ],
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_create_run_and_steps(db):
    run = obs_service.create_run(
        db, thread_id="t-1", question="轻云跑鞋差评？", user_id=1
    )
    assert run.id is not None
    assert run.status == "running"

    s1 = obs_service.add_step(
        db, run.id, step_name="routing", summary="判断查询方式", elapsed_ms=12
    )
    s2 = obs_service.add_step(
        db, run.id, step_name="querying", summary="查到 3 条"
    )
    assert s1.step_order == 1
    assert s2.step_order == 2

    obs_service.finish_run(
        db,
        run.id,
        status="success",
        elapsed_ms=100,
        route="structured",
        answer_preview="有 3 条差评",
    )
    detail = obs_service.get_run_detail(db, run.id)
    assert detail["status"] == "success"
    assert detail["route"] == "structured"
    assert len(detail["steps"]) == 2


def test_list_runs_only_mine(db):
    obs_service.create_run(db, thread_id="a", question="q1", user_id=1)
    obs_service.create_run(db, thread_id="b", question="q2", user_id=2)
    page = obs_service.list_runs(db, page=1, page_size=10, user_id=1, only_mine=True)
    assert page.total == 1
    assert page.list[0]["question"] == "q1"


def test_feedback_upsert(db):
    run = obs_service.create_run(db, thread_id="t", question="q", user_id=1)
    obs_service.finish_run(db, run.id, status="success")
    fb1 = obs_service.submit_feedback(db, run_id=run.id, user_id=1, rating=1)
    assert fb1["rating"] == 1
    fb2 = obs_service.submit_feedback(db, run_id=run.id, user_id=1, rating=-1)
    assert fb2["rating"] == -1
    assert fb1["id"] == fb2["id"]


def test_feedback_invalid_rating(db):
    run = obs_service.create_run(db, thread_id="t", question="q", user_id=1)
    with pytest.raises(BusinessException):
        obs_service.submit_feedback(db, run_id=run.id, user_id=1, rating=0)


def test_get_run_forbidden_for_other_user(db):
    run = obs_service.create_run(db, thread_id="t", question="q", user_id=1)
    with pytest.raises(BusinessException):
        obs_service.get_run_detail(db, run.id, user_id=2)


def test_feedback_forbidden_for_other_user(db):
    run = obs_service.create_run(db, thread_id="private", question="q", user_id=1)
    with pytest.raises(BusinessException) as exc:
        obs_service.submit_feedback(db, run_id=run.id, user_id=2, rating=-1)
    assert exc.value.code == 403
    assert db.query(AgentFeedback).count() == 0


def test_admin_can_submit_feedback_for_other_user(db):
    run = obs_service.create_run(db, thread_id="admin-view", question="q", user_id=1)
    result = obs_service.submit_feedback(db, run_id=run.id, user_id=2, rating=1, is_admin=True)
    assert result["user_id"] == 2
