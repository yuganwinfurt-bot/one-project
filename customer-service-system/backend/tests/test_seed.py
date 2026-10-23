"""种子重置只在内存数据库验证，不触碰实际教学数据。"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.database import Base
from app.models import AlertNotification, DiagnosisReport, Product, Review, Order, User
from app.observability.models import AgentFeedback, AgentRun, AgentRunStep
from data.seed import seed_ecommerce


def test_bundled_review_images_exist():
    seed_ecommerce._ensure_review_sample_images()


def test_missing_review_image_is_not_replaced_with_avatar(tmp_path, monkeypatch):
    monkeypatch.setattr(seed_ecommerce, "BACKEND_ROOT", tmp_path)
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    (uploads / "avatar.jpg").write_bytes(b"unrelated-avatar" * 100)
    with pytest.raises(FileNotFoundError, match="shoe_glue-demo.jpg"):
        seed_ecommerce._ensure_review_sample_images()
    assert not (uploads / "review_samples").exists()


@pytest.fixture()
def db(monkeypatch):
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(conn, record):
        conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    monkeypatch.setattr(seed_ecommerce, "engine", engine)
    monkeypatch.setattr(seed_ecommerce, "_ensure_review_sample_images", lambda: None)
    with Session(engine) as session:
        user = User(username="tester", password="x", name="测试", role="user", status=1)
        session.add(user)
        session.flush()
        product = Product(name="original", category="c", description="d", price=1, stock=1)
        session.add(product)
        session.flush()
        session.add(DiagnosisReport(question="q", summary="s", product_id=product.id))
        session.add(AlertNotification(title="t", content="c", product_id=product.id))
        run = AgentRun(thread_id="fixture-thread", question="q", status="success")
        session.add(run)
        session.flush()
        session.add(AgentRunStep(run_id=run.id, step_order=1, step_name="routing", summary="s"))
        session.add(AgentFeedback(run_id=run.id, user_id=user.id, rating=1))
        session.commit()
        # CLI 使用新 Session，测试也不保留旧商品的 identity map。
        session.expunge_all()
        yield session
    engine.dispose()


def test_seed_can_reset_after_report_and_alert(db):
    seed_ecommerce.seed(db)
    assert db.query(DiagnosisReport).count() == 0
    assert db.query(AlertNotification).count() == 0
    # 观测数据也在清理范围内：运行 / 步骤 / 反馈（录课前重跑不会带着上次演示的记录）
    assert db.query(AgentRun).count() == 0
    assert db.query(AgentRunStep).count() == 0
    assert db.query(AgentFeedback).count() == 0
    assert db.query(Product).count() == len(seed_ecommerce.PRODUCTS)
    assert db.query(Review).count() == len(seed_ecommerce.REVIEW_SPECS)
    # 订单 = 每条评价对应的订单 + 状态演示用的几笔（不带评价）
    assert db.query(Order).count() == len(seed_ecommerce.REVIEW_SPECS) + len(
        seed_ecommerce.STATUS_DEMO_ORDERS
    )
    # 用户表不在清理范围内：演示账号清掉就没法登录了
    assert db.query(User).count() == 1


def test_seed_failure_rolls_back_cleanup(db, monkeypatch):
    def fail_insert(session):
        raise RuntimeError("模拟写入失败")

    monkeypatch.setattr(seed_ecommerce, "_insert_ecommerce_data", fail_insert)
    with pytest.raises(RuntimeError):
        seed_ecommerce.seed(db)
    assert db.query(Product).one().name == "original"
    assert db.query(DiagnosisReport).count() == 1
    assert db.query(AlertNotification).count() == 1
