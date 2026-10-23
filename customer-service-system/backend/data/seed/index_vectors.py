"""把 MySQL 里的评价原文、商品描述写入 Chroma（不做切分）。

用法（在 backend 目录、已激活虚拟环境）：
    python -m data.seed.index_vectors

说明：
- 会先清空向量集合再全量重建
- 需要可用的 EMBEDDING_API_KEY（硅基流动等）
- 评价、商品描述各作为独立文档入库
- lesson-11：带图评价先调图片描述（multimodal），把描述拼进 text 再向量化，
  这样语义检索能命中「基于图片内容」的匹配；无 LLM Key 或描述失败时降级为纯文本
"""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import SessionLocal
from app.models import Product, Review
from app.multimodal.image_caption import caption_image, resolve_image_path
from app.vectorstore import chroma_store

# 每批调用一次向量接口（百炼单批行数上限充足，取 10 兼顾稳定与速度）
BATCH_SIZE = 10

# 图片描述拼进文档时的分隔标记（检索与展示都能一眼区分图片语义部分）
IMAGE_CAPTION_PREFIX = "【晒图内容】"


def _batched(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def build_documents(db) -> list[dict]:
    """从数据库组装待入库文档列表。"""
    docs: list[dict] = []

    products = db.query(Product).order_by(Product.id.asc()).all()
    for product in products:
        # 商品：名称 + 描述拼在一起，方便「某类商品」类模糊问题命中
        text = f"{product.name}。{product.description}".strip()
        docs.append(
            {
                "id": f"product:{product.id}",
                "text": text,
                "metadata": {
                    "doc_type": "product",
                    "product_id": product.id,
                    "name": product.name,
                    "category": product.category,
                },
            }
        )

    reviews = db.query(Review).order_by(Review.id.asc()).all()
    for review in reviews:
        text = review.content.strip()
        # 有图评价：先拿图片描述拼进 text，再整体向量化（lesson-11）
        has_image_caption = False
        if review.img:
            caption = _describe_review_image(review.img)
            if caption:
                text = f"{text}\n{IMAGE_CAPTION_PREFIX}{caption}"
                has_image_caption = True
        docs.append(
            {
                "id": f"review:{review.id}",
                "text": text,
                "metadata": {
                    "doc_type": "review",
                    "review_id": review.id,
                    "product_id": review.product_id,
                    "rating": review.rating,
                    "has_image": bool(review.img),
                    "has_image_caption": has_image_caption,
                },
            }
        )

    return docs


def _describe_review_image(image_path: str) -> str:
    """给单张评价晒图生成描述；文件缺失 / 无 Key / 调用失败都返回空串并打印原因。

    入库脚本要保证「图片不行也不耽误文字入库」，所以这里只警告不抛异常。
    """
    if resolve_image_path(image_path) is None:
        print(f"  跳过图片描述（文件不存在）：{image_path}")
        return ""
    try:
        return caption_image(image_path)
    except Exception as exc:
        message = getattr(exc, "message", None) or str(exc)
        print(f"  跳过图片描述（{message}）：{image_path}")
        return ""


def index_all() -> None:
    db = SessionLocal()
    try:
        docs = build_documents(db)
        if not docs:
            print("数据库里没有商品/评价，请先运行：python -m data.seed.seed_ecommerce")
            return

        print(f"准备入库 {len(docs)} 条文档，先清空旧集合…")
        chroma_store.reset_collection()

        total = 0
        for batch in _batched(docs, BATCH_SIZE):
            total += chroma_store.add_documents(batch)
            print(f"  已写入 {total}/{len(docs)}")

        print(f"完成。当前集合文档数：{chroma_store.count_documents()}")
    finally:
        db.close()


def main() -> None:
    index_all()


if __name__ == "__main__":
    main()
