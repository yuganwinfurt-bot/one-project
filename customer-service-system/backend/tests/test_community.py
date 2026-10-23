"""用户资料、私聊及评论互动。临时数据库与真实依赖权限检查。"""
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Header
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api import community, customer_store, ecommerce
from app.common.exceptions import BusinessException, business_exception_handler
from app.database import Base, get_db
from app.dependencies.auth import get_current_user
from app.models import (
    CustomerReviewReply, DirectMessage, Order, Product, Review, ReviewComment,
    ReviewReplyNotification, User,
)
from app.services import ecommerce_service
from app.services.user_service import delete_user


@pytest.fixture()
def shop():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        buyer = User(username="buyer", name="买家", password="secret", role="customer", email="buyer@example.test")
        other = User(username="other", name="其他买家", password="secret", role="customer")
        staff = User(username="staff", name="商家", password="secret", role="user")
        staff2 = User(username="staff2", name="其他商家", password="secret", role="user")
        product = Product(name="商品", category="测试", description="测试商品", price=59, stock=10)
        db.add_all([buyer, other, staff, staff2, product])
        db.flush()
        order = Order(order_no="COMMUNITY-1", product_id=product.id, buyer_user_id=buyer.id,
                      buyer_name=buyer.name, quantity=1, amount=59, status="completed")
        db.add(order)
        db.flush()
        review = Review(product_id=product.id, order_id=order.id, rating=4, content="原始评价")
        db.add(review)
        db.commit()
        app = FastAPI()
        app.add_exception_handler(BusinessException, business_exception_handler)
        app.include_router(community.router)
        app.include_router(customer_store.router)
        app.include_router(ecommerce.router)
        def test_db():
            yield db
        def test_user(x_user_id: int = Header()):
            return db.get(User, x_user_id)
        app.dependency_overrides[get_db] = test_db
        app.dependency_overrides[get_current_user] = test_user
        with TestClient(app) as client:
            yield SimpleNamespace(db=db, client=client, buyer=buyer, other=other, staff=staff,
                                  staff2=staff2, product=product, order=order, review=review)
    engine.dispose()


def request(shop, user, method, path, data=None, code=200):
    response = shop.client.request(method, path, json=data, headers={"X-User-Id": str(user.id)})
    body = response.json()
    assert body.get("code", response.status_code) == code, body
    return body.get("data")


def comment(shop, actor, content, target=None):
    return request(shop, actor, "POST", f"/community/reviews/{shop.review.id}/comments",
                   {"content": content, "reply_to_user_id": target})


def conversation(shop):
    return request(shop, shop.staff, "POST", "/community/conversations", {"user_id": shop.buyer.id})["conversation_id"]


def test_profile_is_staff_only_and_never_returns_password(shop):
    data = request(shop, shop.staff, "GET", f"/community/users/{shop.buyer.id}")
    assert data["email"] == "buyer@example.test"
    assert data["order_count"] == 1 and data["order_amount"] == 59
    assert "password" not in data and "token" not in data
    request(shop, shop.other, "GET", f"/community/users/{shop.buyer.id}", code=403)
    request(shop, shop.staff, "GET", f"/community/users/{shop.staff2.id}", code=404)
    request(shop, shop.buyer, "POST", "/community/conversations", {"user_id": shop.other.id}, code=403)


def test_direct_chat_is_unique_private_bidirectional_and_read_scoped(shop):
    cid = conversation(shop)
    assert conversation(shop) == cid
    request(shop, shop.staff, "POST", f"/community/conversations/{cid}/messages", {"content": " 商家私聊 "})
    data = customer_store.get_customer_messages(shop.buyer, shop.db).data
    assert data["unread_count"] == 1
    assert data["list"][0]["preview"] == "商家私聊"
    assert data["list"][0]["peer_id"] == shop.staff.id
    for outsider in [shop.other, shop.staff2]:
        request(shop, outsider, "GET", f"/community/conversations/{cid}/messages", code=404)
        request(shop, outsider, "POST", f"/community/conversations/{cid}/messages", {"content": "越权"}, code=404)
        assert request(shop, outsider, "GET", "/community/conversations")["list"] == []
    request(shop, shop.staff, "GET", f"/community/conversations/{cid}/messages")
    assert not shop.db.query(DirectMessage).one().is_read  # 发件人读取不能消掉收件人的未读
    data = request(shop, shop.buyer, "GET", f"/community/conversations/{cid}/messages")
    assert data["unread_count"] == 1 and data["list"][0]["content"] == "商家私聊"
    assert customer_store.get_customer_messages(shop.buyer, shop.db).data["unread_count"] == 0
    request(shop, shop.buyer, "POST", f"/community/conversations/{cid}/messages", {"content": "买家回复"})
    staff_data = ecommerce.get_staff_message_center(shop.staff, shop.db).data
    assert staff_data["unread_count"] == 1
    assert staff_data["direct_conversations"][0]["peer_id"] == shop.buyer.id
    assert ecommerce.get_staff_message_center(shop.staff2, shop.db).data["unread_count"] == 0


def test_chat_and_comments_reject_blank_and_disabled_recipient(shop):
    cid = conversation(shop)
    for path in [f"/community/conversations/{cid}/messages", f"/community/reviews/{shop.review.id}/comments"]:
        request(shop, shop.staff, "POST", path, {"content": "  \n "}, code=422)
        request(shop, shop.staff, "POST", path, {"content": "x" * 2001}, code=422)
    shop.buyer.status = 0
    shop.db.commit()
    request(shop, shop.staff, "POST", "/community/conversations", {"user_id": shop.buyer.id}, code=404)
    request(shop, shop.staff, "POST", f"/community/conversations/{cid}/messages", {"content": "hello"}, code=500)


def test_append_preserves_original_and_legacy_comments_without_self_notification(shop):
    shop.db.add(CustomerReviewReply(review_id=shop.review.id, user_id=shop.buyer.id, content="历史追加"))
    shop.db.commit()
    first = comment(shop, shop.buyer, "第一次追加")
    second = comment(shop, shop.buyer, "第二次追加")
    assert first["kind"] == second["kind"] == "append"
    assert shop.review.content == "原始评价"
    assert shop.db.query(ReviewReplyNotification).count() == 0
    rows = customer_store.get_customer_review_replies(shop.review.id, shop.buyer, shop.db).data["list"]
    assert {row["content"] for row in rows} == {"历史追加", "第一次追加", "第二次追加"}
    assert all(row["kind"] == "append" for row in rows)
    listed = ecommerce_service.list_reviews(shop.db, page=1, page_size=10, product_id=shop.product.id)
    assert listed.list[0].buyer_user_id == shop.buyer.id


def test_staff_and_customer_replies_notify_and_link_to_review(shop):
    staff_comment = comment(shop, shop.staff, "商家回复")
    assert staff_comment["user_role"] == "user"
    assert shop.review.merchant_reply == "商家回复"
    comment(shop, shop.other, "其他买家回复")
    inbox = customer_store.get_customer_messages(shop.buyer, shop.db).data
    assert inbox["unread_count"] == 2
    assert all(row["type"] == "review_reply" and row["review_id"] == shop.review.id for row in inbox["list"])
    assert all(row["product_id"] == shop.product.id for row in inbox["list"])
    nid = inbox["list"][0]["notification_id"]
    request(shop, shop.other, "POST", f"/community/notifications/{nid}/read", code=404)
    request(shop, shop.buyer, "POST", f"/community/notifications/{nid}/read")
    assert customer_store.get_customer_messages(shop.buyer, shop.db).data["unread_count"] == 1
    # 回复商家自己的评论，只通知该商家；其他商家不能读取。
    comment(shop, shop.buyer, "回复商家", target=shop.staff.id)
    staff_inbox = ecommerce.get_staff_message_center(shop.staff, shop.db).data
    assert staff_inbox["unread_count"] == 1
    event = staff_inbox["events"][0]
    assert event["event_type"] == "review_reply"
    assert event["review_id"] == shop.review.id
    assert ecommerce.get_staff_message_center(shop.staff2, shop.db).data["events"] == []
    ecommerce.mark_all_staff_message_events_read(shop.staff, shop.db)
    shop.db.expire_all()
    assert ecommerce.get_staff_message_center(shop.staff, shop.db).data["unread_count"] == 0


def test_reply_target_must_be_participant_and_notifies_target_only(shop):
    request(shop, shop.buyer, "POST", f"/community/reviews/{shop.review.id}/comments",
            {"content": "任意指定收件人", "reply_to_user_id": shop.staff2.id}, code=400)
    comment(shop, shop.other, "其他人的评论")
    comment(shop, shop.buyer, "回复其他人", target=shop.other.id)
    assert customer_store.get_customer_messages(shop.other, shop.db).data["unread_count"] == 1
    assert shop.db.query(ReviewComment).count() == 2


def test_read_all_only_affects_current_recipient(shop):
    cid = conversation(shop)
    request(shop, shop.staff, "POST", f"/community/conversations/{cid}/messages", {"content": "私聊"})
    comment(shop, shop.other, "他人回复")
    comment(shop, shop.buyer, "回复其他人", target=shop.other.id)
    assert customer_store.get_customer_messages(shop.buyer, shop.db).data["unread_count"] == 2
    customer_store.mark_customer_messages_read(shop.buyer, shop.db)
    shop.db.expire_all()
    assert customer_store.get_customer_messages(shop.buyer, shop.db).data["unread_count"] == 0
    assert customer_store.get_customer_messages(shop.other, shop.db).data["unread_count"] == 1


def test_legacy_merchant_reply_also_notifies_without_duplicate_on_same_text(shop):
    ecommerce_service.update_review_reply(shop.db, shop.review.id, "旧入口商家回复", shop.staff)
    ecommerce_service.update_review_reply(shop.db, shop.review.id, "旧入口商家回复", shop.staff)
    assert shop.db.query(ReviewReplyNotification).count() == 1


def test_new_merchant_replies_preserve_legacy_reply_and_all_new_comments(shop):
    shop.review.merchant_reply = "历史商家回复"
    shop.db.commit()
    comment(shop, shop.staff, "新回复一")
    comment(shop, shop.staff, "新回复二")
    assert shop.review.merchant_reply == "历史商家回复"
    assert [row.content for row in shop.db.query(ReviewComment).order_by(ReviewComment.id)] == ["新回复一", "新回复二"]


def test_deleting_chat_or_comment_participant_retains_history(shop):
    conversation(shop)
    comment(shop, shop.other, "需保留的评论")
    for user in [shop.staff, shop.buyer, shop.other]:
        with pytest.raises(BusinessException, match="停用"):
            delete_user(shop.db, user.id, shop.staff2)
        assert shop.db.get(User, user.id) is not None
