"""MCP 工具：语义检索查 Chroma。"""

import json
from typing import Any

from app.services import semantic_search_service


def query_chroma(
    query: str, top_k: int = 8, product_ids: list[int] | None = None,
    doc_types: list[str] | None = None,
) -> str:
    """在指定资料类型及商品范围内检索业务知识，返回 JSON 字符串。

    参数:
        query: 检索词或自然语言主题
        top_k: 返回条数上限
    """
    try:
        top_k = max(1, min(int(top_k or 8), 20))
        result = semantic_search_service.search_similar(
            query, top_k=top_k, product_ids=product_ids, doc_types=doc_types,
        )
        payload: dict[str, Any] = {
            "ok": True,
            "query": result["query"],
            "top_k": result["top_k"],
            "hit_count": result["hit_count"],
            "hits": result["hits"],
            "collection_size": result["collection_size"],
            "via": "mcp:query_chroma",
        }
        return json.dumps(payload, ensure_ascii=False, default=str)
    except Exception as exc:
        message = getattr(exc, "message", None) or str(exc) or exc.__class__.__name__
        return json.dumps(
            {"ok": False, "error": message, "via": "mcp:query_chroma"},
            ensure_ascii=False,
        )
