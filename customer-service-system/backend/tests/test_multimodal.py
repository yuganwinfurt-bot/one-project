"""lesson-11 多模态单测：图片描述与向量入库拼接（不调真实大模型）。"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.common.exceptions import BusinessException
from app.config import UPLOAD_DIR
from app.database import Base
from app.models import Order, Product, Review
from app.models.user import User  # noqa: F401  注册 users 表，满足外键解析
from app.multimodal import image_caption
from app.multimodal.image_caption import caption_image, resolve_image_path
from data.seed import index_vectors


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeCompletions:
    """抓下发给大模型的完整 payload，方便断言 vision 传参格式。"""

    def __init__(self, reply="鞋底开胶，胶水溢出"):
        self.reply = reply
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return type("Resp", (), {"choices": [_FakeChoice(self.reply)]})()


class _FakeChat:
    def __init__(self, completions):
        self.completions = completions


class _FakeClient:
    def __init__(self, completions):
        self.chat = _FakeChat(completions)


@pytest.fixture()
def jpg_file(tmp_path):
    """最小合法 JPEG 文件头，内容无所谓（只验证链路，不验证识别效果）。"""
    f = tmp_path / "sample.jpg"
    f.write_bytes(bytes.fromhex("ffd8ffe000104a46494600010101006000600000") + b"\x00" * 64)
    return f


def _patch_llm(monkeypatch, reply="鞋底开胶，胶水溢出"):
    completions = _FakeCompletions(reply=reply)
    monkeypatch.setattr(
        image_caption, "get_llm_client", lambda: _FakeClient(completions)
    )
    return completions


def test_resolve_uploads_url(tmp_path, monkeypatch):
    monkeypatch.setattr(image_caption, "UPLOAD_DIR", tmp_path)
    target = tmp_path / "review_samples" / "a.jpg"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"fake")
    resolved = resolve_image_path("/uploads/review_samples/a.jpg")
    assert resolved == target


def test_resolve_missing_returns_none():
    assert resolve_image_path("/uploads/review_samples/not-exist.jpg") is None
    assert resolve_image_path("") is None


def test_caption_image_sends_vision_payload(jpg_file, monkeypatch):
    completions = _patch_llm(monkeypatch)
    text = caption_image(str(jpg_file))
    assert text == "鞋底开胶，胶水溢出"

    kwargs = completions.last_kwargs
    assert kwargs["temperature"] == 0
    user_content = kwargs["messages"][1]["content"]
    kinds = [block["type"] for block in user_content]
    assert kinds == ["text", "image_url"]
    url = user_content[1]["image_url"]["url"]
    assert url.startswith("data:image/jpeg;base64,")


def test_caption_image_missing_file():
    with pytest.raises(BusinessException):
        caption_image("/uploads/review_samples/not-exist.jpg")


def test_caption_image_rejects_non_image(tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("hello")
    with pytest.raises(BusinessException) as exc:
        caption_image(str(f))
    assert "不支持的图片格式" in exc.value.message


@pytest.fixture()
def db():
    """内存 SQLite：只建索引脚本用到的三张表。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        bind=engine,
        tables=[User.__table__, Product.__table__, Order.__table__, Review.__table__],
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def _seed_review(db, tmp_path, with_image: bool):
    product = Product(
        name="轻云运动跑鞋", category="鞋靴", description="跑鞋", price=299, stock=9
    )
    db.add(product)
    db.flush()
    image_path = None
    if with_image:
        f = tmp_path / "shoe.jpg"
        f.write_bytes(b"\xff\xd8\xff" + b"\x00" * 32)
        image_path = str(f)
    review = Review(
        product_id=product.id, order_id=None, rating=1,
        content="质量太差", img=image_path,
    )
    db.add(review)
    db.commit()
    return review


def test_build_documents_appends_image_caption(db, tmp_path, monkeypatch):
    _seed_review(db, tmp_path, with_image=True)
    monkeypatch.setattr(
        index_vectors, "caption_image", lambda path: "鞋底开胶特写"
    )
    docs = index_vectors.build_documents(db)
    review_docs = [d for d in docs if d["id"].startswith("review:")]
    assert len(review_docs) == 1
    assert "质量太差" in review_docs[0]["text"]
    assert "【晒图内容】鞋底开胶特写" in review_docs[0]["text"]
    assert review_docs[0]["metadata"]["has_image_caption"] is True


def test_build_documents_without_image_skips_caption(db, tmp_path, monkeypatch):
    _seed_review(db, tmp_path, with_image=False)
    called = []
    monkeypatch.setattr(
        index_vectors, "caption_image", lambda path: called.append(path) or "x"
    )
    docs = index_vectors.build_documents(db)
    review_docs = [d for d in docs if d["id"].startswith("review:")]
    assert called == []
    assert review_docs[0]["text"] == "质量太差"
    assert review_docs[0]["metadata"]["has_image_caption"] is False


def test_build_documents_caption_failure_falls_back_to_text(
    db, tmp_path, monkeypatch, capsys
):
    _seed_review(db, tmp_path, with_image=True)

    def _boom(path):
        raise BusinessException(message="未配置 LLM_API_KEY")

    monkeypatch.setattr(index_vectors, "caption_image", _boom)
    docs = index_vectors.build_documents(db)
    review_docs = [d for d in docs if d["id"].startswith("review:")]
    # 图片不行也不耽误文字入库
    assert review_docs[0]["text"] == "质量太差"
    assert review_docs[0]["metadata"]["has_image_caption"] is False
    assert "跳过图片描述" in capsys.readouterr().out
