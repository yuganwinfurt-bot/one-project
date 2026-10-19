"""向量模型调用封装（OpenAI 兼容 embeddings 接口）。

教学说明：
- 调用方只关心「文本 → 向量」，不直接碰第三方 SDK 细节
- 默认对接百炼 qwen3.7-text-embedding-flash（便宜的中文向量模型），与 LLM 共用同一个 Key；
  换供应商时改 .env 即可
- 该模型用默认 1024 维，不传 dimensions 参数（百炼官方只给 v3/v4 开了该参数）
- 换向量模型后必须重跑 index_vectors 重建 Chroma（不同模型的向量空间不可混用）
"""

from openai import OpenAI, APITimeoutError, APIError

from app.common.exceptions import BusinessException
from app.config import settings

# 百炼 embeddings 单次输入上限 25 条，留点余量按 20 条分批
_EMBED_BATCH_SIZE = 20


def get_embedding_client() -> OpenAI:
    """创建 embeddings 用的 OpenAI 兼容客户端。"""
    api_key = settings.EMBEDDING_API_KEY or settings.LLM_API_KEY
    if not api_key:
        raise BusinessException(
            message="未配置 EMBEDDING_API_KEY（或 LLM_API_KEY），请先在 .env 中填写"
        )
    return OpenAI(
        api_key=api_key,
        base_url=settings.EMBEDDING_BASE_URL,
        timeout=settings.EMBEDDING_TIMEOUT,
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量把文本转成向量。空列表直接返回空。

    百炼的 embeddings 接口单次最多 25 条（超过会报 batch size invalid），
    这里统一按 20 条分批，调用方不必关心上限。
    """
    if not texts:
        return []

    # 过滤空串，避免部分接口报错；占位用零向量会破坏检索，直接拒绝
    cleaned = [t.strip() for t in texts]
    if any(not t for t in cleaned):
        raise BusinessException(message="向量化文本不能为空")

    client = get_embedding_client()
    vectors: list[list[float]] = []
    for start in range(0, len(cleaned), _EMBED_BATCH_SIZE):
        batch = cleaned[start : start + _EMBED_BATCH_SIZE]
        try:
            response = client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=batch,
            )
        except APITimeoutError as exc:
            raise BusinessException(message="向量模型调用超时，请稍后重试") from exc
        except APIError as exc:
            raise BusinessException(message=f"向量模型调用失败：{exc.message}") from exc

        # OpenAI 兼容接口按 index 对齐返回
        sorted_items = sorted(response.data, key=lambda item: item.index)
        vectors.extend(item.embedding for item in sorted_items)
    return vectors


def embed_text(text: str) -> list[float]:
    """单条文本转向量。"""
    return embed_texts([text])[0]
