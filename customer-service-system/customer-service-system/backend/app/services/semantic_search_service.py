"""Connect e-commerce semantic retrieval to the standalone local RAG library."""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any

from app.common.exceptions import BusinessException
from app.config import settings
from app.vectorstore import chroma_store
from app.services.knowledge_export_service import build_platform_export


def _post_rag(path: str, payload: dict[str, Any], timeout: float, *, sync: bool = False) -> dict[str, Any]:
    base_url = settings.RAG_BASE_URL.rstrip("/")
    headers = {"Content-Type": "application/json"}
    if settings.RAG_SYNC_TOKEN:
        headers["X-Integration-Key"] = settings.RAG_SYNC_TOKEN
    if sync:
        if not settings.RAG_SYNC_TOKEN:
            raise BusinessException("未配置独立 RAG 同步密钥", code=503)
        headers["X-Integration-Key"] = settings.RAG_SYNC_TOKEN
    request = Request(
        f"{base_url}{path}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
            detail = body.get("detail") or body.get("message") or str(exc)
        except (UnicodeDecodeError, json.JSONDecodeError):
            detail = str(exc)
        raise BusinessException(f"独立 RAG 请求失败：{detail}", code=503) from exc
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise BusinessException("无法连接独立 RAG 服务，请确认它在 127.0.0.1:8000 运行", code=503) from exc


def _field(raw: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:[ \t]*(.*)$", raw)
    return match.group(1).strip() if match else None


def _as_int(value: Any) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _as_bool(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"true", "1", "yes"}


def _clean_record_text(raw: str) -> str:
    match = re.search(r"(?m)^content:[ \t]?", raw)
    return raw[match.end():].strip() if match else raw


def search_similar(
    query: str, top_k: int = 5, product_ids: list[int] | None = None,
    doc_types: list[str] | None = None,
) -> dict[str, Any]:
    """Search the e-commerce knowledge base hosted by the standalone RAG app."""
    query = query.strip()
    if not query:
        raise BusinessException("检索 query 不能为空")
    result = _post_rag(
        "/api/integrations/agent/retrieve",
        {
            "query": query,
            "knowledge_base_ids": [settings.RAG_ECOM_KNOWLEDGE_BASE_ID],
            "knowledge_base_name": "电商分析平台",
            "top_k": max(1, min(int(top_k or 5), 20)),
            "product_ids": product_ids or None,
            "doc_types": doc_types or None,
        },
        settings.RAG_SEARCH_TIMEOUT_SECONDS,
    )
    matches = result.get("matches") or []
    hits = []
    for match in matches:
        raw = str(match.get("content") or "")
        supplied_metadata = match.get("metadata") or {}
        metadata = dict(supplied_metadata) if isinstance(supplied_metadata, dict) else {}
        for key in ("record_id", "doc_type", "source_table", "source_id", "product_id", "review_id", "rating", "name", "category", "has_image", "create_time", "update_time"):
            if metadata.get(key) in (None, ""):
                value = _field(raw, key)
                if value is not None:
                    metadata[key] = value
        metadata["product_id"] = _as_int(metadata.get("product_id"))
        metadata["review_id"] = _as_int(metadata.get("review_id"))
        metadata["rating"] = _as_int(metadata.get("rating"))
        if "has_image" in metadata:
            metadata["has_image"] = _as_bool(metadata["has_image"])
        try:
            score = float(match.get("score"))
        except (TypeError, ValueError):
            continue
        record_id = metadata.get("record_id") or _field(raw, "record_id")
        record_text = _clean_record_text(raw)
        try:
            record = json.loads(record_text)
        except (ValueError, TypeError):
            record = None
        if isinstance(record, dict):
            for key in ("create_time", "update_time"):
                if not metadata.get(key) and isinstance(record.get(key), str):
                    metadata[key] = record[key]
        hits.append({
            # 同一记录的多个分片需要保留，不能都用 record_id 导致后续去重丢失正文。
            "id": match.get("chunk_id") or record_id or f"rag:{len(hits) + 1}",
            "text": record_text,
            "metadata": metadata,
            "distance": round(1.0 - score, 6),
        })

    return {
        "query": query,
        "top_k": top_k,
        "hit_count": len(hits),
        "hits": hits,
        "collection_size": int(result.get("collection_size") or 0),
    }


def _build_platform_snapshot():
    """导出全部后台业务，并保留历史图片描述。"""
    indexed_reviews: dict[str, str] = {}
    try:
        indexed = chroma_store._get_collection().get(include=["documents"])
        indexed_reviews = {
            doc_id: text or ""
            for doc_id, text in zip(indexed.get("ids") or [], indexed.get("documents") or [])
            if str(doc_id).startswith("review:")
        }
    except Exception:
        # The previous Chroma index is optional during future syncs.
        indexed_reviews = {}

    return build_platform_export(indexed_reviews)


def _build_ecommerce_records() -> list[dict[str, Any]]:
    return _build_platform_snapshot()[0]


def sync_ecommerce_data() -> dict[str, Any]:
    """更新完整后台快照；重复同步替换本平台的受管理文件。"""
    records, summary = _build_platform_snapshot()
    if not records:
        raise BusinessException("没有可同步的后台业务数据，未执行同步")
    result = _post_rag(
        "/api/integrations/agent/sync-ecommerce",
        {"records": records},
        settings.RAG_SYNC_TIMEOUT_SECONDS,
        sync=True,
    )
    return {**summary, **result}
