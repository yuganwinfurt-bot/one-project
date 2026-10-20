"""电商快照增量向量化；新快照写好后再由调用方提交文档并删除旧索引。"""

import csv
import hashlib
import json
import logging
import time
from collections import Counter
from pathlib import Path
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import OLLAMA_EMBED_MODEL, RAG_EMBED_BATCH_SIZE
from .embedding_cache import read_cached_vectors, save_cached_vectors, text_hash
from .pipeline import get_embeddings, get_vector_store, load_file

logger = logging.getLogger(__name__)


def embedding_profile(model: str, digest: str) -> str:
    # digest 隔离同名模型的不同版本。统一默认 latest 的两种写法。
    name = model if ":" in model else model + ":latest"
    return hashlib.sha256(json.dumps([name, digest], ensure_ascii=False).encode()).hexdigest()


def snapshot_changes(current_path: Path, previous_paths: list[Path]) -> dict:
    def fingerprints(paths):
        records = {}
        for path in paths:
            if not path.is_file():
                continue
            with path.open(encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    if row.get("record_id"):
                        records[row["record_id"]] = text_hash(json.dumps(row, sort_keys=True, ensure_ascii=False))
        return records

    before, after = fingerprints(previous_paths), fingerprints([current_path])
    common = before.keys() & after.keys()
    changed = sum(before[key] != after[key] for key in common)
    return {
        "added_records": len(after.keys() - before.keys()),
        "updated_records": changed,
        "deleted_records": len(before.keys() - after.keys()),
        "unchanged_records": len(common) - changed,
    }


def _seed_from_snapshot(store, previous_ids, model_key, required_hashes, *, legacy):
    """从已登记的上次快照读取现成向量，让升级后的第一次同步也能复用。"""
    found = {}
    for start in range(0, len(previous_ids), 128):
        if not required_hashes:
            break
        previous = store._collection.get(
            ids=previous_ids[start:start + 128], include=["documents", "embeddings"]
        )
        embeddings = previous.get("embeddings")
        if embeddings is None:
            continue
        batch = {}
        for content, vector in zip(previous.get("documents") or [], embeddings):
            if not isinstance(content, str):
                continue
            digest = text_hash(content)
            if digest not in required_hashes or vector is None:
                continue
            values = [float(value) for value in vector]
            # 旧版本没有模型标记，只迁移本项目原有 bge-m3 的 1024 维快照。
            if legacy and len(values) != 1024:
                continue
            batch[digest] = values
            required_hashes.discard(digest)
        save_cached_vectors(model_key, batch)
        found.update(batch)
    return found


def _embed_batch(embedder, texts):
    for attempt, delay in enumerate((0, 1.5, 4)):
        if delay:
            time.sleep(delay)
        try:
            vectors = embedder.embed_documents(texts)
            if len(vectors) != len(texts):
                raise ValueError("向量服务返回的条数与输入不一致")
            return vectors
        except Exception as exc:
            retryable = any(marker in str(exc).lower() for marker in (
                "status code: 502", "status code: 503", "status code: 429",
                "temporarily unavailable", "connection refused",
            ))
            if not retryable or attempt == 2:
                raise
            logger.warning("电商向量计算暂时失败，准备重试：%s", type(exc).__name__)


def index_ecommerce_snapshot(knowledge_base_id, document_id, path, original_filename,
                             previous_ids, model_key, legacy, progress=None):
    documents = load_file(path, original_filename)
    chunks = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120).split_documents(documents)
    if not chunks:
        raise ValueError("电商快照中没有可索引的文字")
    hashes = [text_hash(chunk.page_content) for chunk in chunks]
    occurrences = Counter(hashes)
    texts = {digest: chunk.page_content for digest, chunk in zip(hashes, chunks)}
    vectors = read_cached_vectors(model_key, hashes)
    store = get_vector_store(knowledge_base_id)
    missing = set(hashes) - vectors.keys()
    if missing and previous_ids:
        vectors.update(_seed_from_snapshot(store, previous_ids, model_key, missing, legacy=legacy))

    ready = sum(occurrences[key] for key in vectors)
    embedded = 0

    def report(stage="indexing"):
        if progress:
            progress(ready, len(chunks), reused_chunks=ready - embedded,
                     embedded_chunks=embedded, stage=stage)

    report()
    pending = [digest for digest in texts if digest not in vectors]
    if pending:
        embedder = get_embeddings()
        for start in range(0, len(pending), RAG_EMBED_BATCH_SIZE):
            batch = pending[start:start + RAG_EMBED_BATCH_SIZE]
            calculated = _embed_batch(embedder, [texts[digest] for digest in batch])
            cached = {digest: [float(value) for value in vector] for digest, vector in zip(batch, calculated)}
            # 每批独立落盘，即便后续批次失败，重试仍可复用已计算的向量。
            save_cached_vectors(model_key, cached)
            vectors.update(cached)
            embedded += len(batch)
            ready += sum(occurrences[key] for key in batch)
            report()

    vector_ids = [f"{document_id}-{index}-{uuid4().hex[:8]}" for index in range(len(chunks))]
    for index, chunk in enumerate(chunks):
        chunk.metadata.update({
            "knowledge_base_id": knowledge_base_id, "document_id": document_id,
            "filename": original_filename, "chunk_index": index + 1,
            "chunk_id": vector_ids[index], "embedding_profile": model_key,
            "embedding_model": OLLAMA_EMBED_MODEL,
        })
    report("writing")
    try:
        for start in range(0, len(chunks), 128):
            end = start + 128
            # 显式提供向量，禁止 Chroma 再次调用 embedding function。
            store._collection.upsert(
                ids=vector_ids[start:end],
                documents=[chunk.page_content for chunk in chunks[start:end]],
                metadatas=[chunk.metadata for chunk in chunks[start:end]],
                embeddings=[vectors[digest] for digest in hashes[start:end]],
            )
    except Exception:
        try:
            store.delete(ids=vector_ids)
        except Exception:
            logger.exception("清理未提交的电商快照失败：%s", document_id)
        raise
    return len(chunks), vector_ids, {
        "embedded_chunks": embedded,
        "reused_chunks": len(chunks) - embedded,
        "incremental": True,
    }
