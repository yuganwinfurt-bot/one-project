"""Chroma 封装单测：用假向量，不调用真实 embedding 接口。"""

from app.vectorstore import chroma_store


def _fake_vec(seed: float) -> list[float]:
    return [seed, 1.0 - seed, 0.1, 0.2]


def test_add_and_search_with_fake_embeddings(tmp_path, monkeypatch):
    persist_dir = tmp_path / "chroma"
    persist_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(chroma_store, "CHROMA_DIR", persist_dir)
    chroma_store._client = None
    chroma_store._collection = None

    chroma_store.add_document(
        "review:1",
        "鞋码偏大，穿着松垮",
        {"doc_type": "review", "rating": 2, "product_id": 1},
        embedding=_fake_vec(0.9),
    )
    chroma_store.add_document(
        "review:2",
        "保温杯保温很好",
        {"doc_type": "review", "rating": 5, "product_id": 2},
        embedding=_fake_vec(0.1),
    )

    # 查询向量靠近「尺码」那条
    monkeypatch.setattr(
        chroma_store,
        "embed_text",
        lambda _q: _fake_vec(0.88),
    )
    results = chroma_store.search("尺码太大", top_k=2)
    assert len(results) == 2
    assert results[0]["id"] == "review:1"
    assert "鞋码" in results[0]["text"]

    # 即使另一商品的向量更相似，也只能返回指定商品的文档。
    filtered = chroma_store.search("尺码太大", top_k=2, product_ids=[2])
    assert [hit["id"] for hit in filtered] == ["review:2"]
    assert chroma_store.search("尺码太大", product_ids=[99]) == []

    # 清理模块缓存，避免影响其他用例
    chroma_store._client = None
    chroma_store._collection = None
