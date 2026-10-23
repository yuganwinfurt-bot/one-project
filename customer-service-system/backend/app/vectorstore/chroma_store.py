"""Chroma 向量库封装。

对外只暴露两个函数，调用方不直接接触 chromadb API，方便以后替换实现：
- add_document(id, text, metadata)
- search(query, top_k)

教学约定（lesson-04）：
- 评价原文、商品描述各自作为独立文档，不做切分
- 不做重排序、不做查询改写、不做混合检索
"""

from typing import TYPE_CHECKING, Any

import chromadb

if TYPE_CHECKING:
    # 运行期 PersistentClient 是工厂函数（不是类型），只能在类型检查期引用真正的客户端类型
    from chromadb.api import ClientAPI

from app.common.exceptions import BusinessException
from app.config import CHROMA_DIR, settings
from app.utils.embedding import embed_text, embed_texts

# 模块级懒加载，避免 import 时就连磁盘
_client: "ClientAPI | None" = None
_collection = None


def _get_collection():
    """获取（或创建）默认集合。embedding 由我们外部计算，不使用 Chroma 内置模型。"""
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # cosine：语义相似度常用度量
    _collection = _client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def reset_collection() -> None:
    """清空并重建集合（入库脚本重复执行时用）。"""
    global _collection
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(settings.CHROMA_COLLECTION)
    except Exception:
        # 集合不存在时忽略
        pass
    _collection = None
    _get_collection()


def add_document(
    doc_id: str,
    text: str,
    metadata: dict[str, Any] | None = None,
    embedding: list[float] | None = None,
) -> None:
    """写入（或覆盖）一条文档。

    Parameters
    ----------
    doc_id : 业务侧唯一 ID，例如 review:12 / product:3
    text : 原文（不做切分）
    metadata : 附加信息，值需为 Chroma 支持的基础类型
    embedding : 可选；单测时可传入假向量，跳过真实模型调用
    """
    if not doc_id or not str(doc_id).strip():
        raise BusinessException(message="文档 id 不能为空")
    if not text or not text.strip():
        raise BusinessException(message="文档 text 不能为空")

    meta = _normalize_metadata(metadata or {})
    vector = embedding if embedding is not None else embed_text(text.strip())

    collection = _get_collection()
    # upsert：重复入库同一 id 时覆盖，方便种子脚本重跑
    collection.upsert(
        ids=[str(doc_id)],
        documents=[text.strip()],
        metadatas=[meta],
        embeddings=[vector],
    )


def add_documents(
    items: list[dict[str, Any]],
    embeddings: list[list[float]] | None = None,
) -> int:
    """批量写入，减少向量接口往返次数。

    每个 item 形如：{"id": "...", "text": "...", "metadata": {...}}
    """
    if not items:
        return 0

    ids = [str(item["id"]) for item in items]
    texts = [str(item["text"]).strip() for item in items]
    metas = [_normalize_metadata(item.get("metadata") or {}) for item in items]

    if any(not t for t in texts):
        raise BusinessException(message="批量写入时存在空文本")

    if embeddings is None:
        vectors = embed_texts(texts)
    else:
        if len(embeddings) != len(items):
            raise BusinessException(message="embeddings 数量与文档数量不一致")
        vectors = embeddings

    collection = _get_collection()
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metas,
        embeddings=vectors,
    )
    return len(items)


def search(query: str, top_k: int = 5, product_ids: list[int] | None = None) -> list[dict[str, Any]]:
    """语义检索：问题 → 向量 → 取最相似的 top_k 条。

    返回列表，每项包含：id / text / metadata / distance
    distance 越小越相似（cosine 空间下 Chroma 返回的是距离而非分数）。
    """
    if not query or not query.strip():
        raise BusinessException(message="检索 query 不能为空")
    if top_k <= 0:
        raise BusinessException(message="top_k 必须大于 0")

    collection = _get_collection()
    if collection.count() == 0:
        return []

    query_vector = embed_text(query.strip())
    result = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
        **({"where": {"product_id": {"$in": product_ids}}} if product_ids else {}),
    )

    # Chroma 返回的是「按查询分组」的二维列表，这里只有一个 query
    ids = (result.get("ids") or [[]])[0]
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    hits: list[dict[str, Any]] = []
    for i, doc_id in enumerate(ids):
        hits.append(
            {
                "id": doc_id,
                "text": documents[i] if i < len(documents) else "",
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distances[i] if i < len(distances) else None,
            }
        )
    return hits


def count_documents() -> int:
    """当前集合文档数，便于入库脚本打印进度。"""
    return _get_collection().count()


def _normalize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Chroma metadata 只接受 str / int / float / bool，其余转成字符串。"""
    normalized: dict[str, Any] = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            normalized[str(key)] = value
        else:
            normalized[str(key)] = str(value)
    return normalized
