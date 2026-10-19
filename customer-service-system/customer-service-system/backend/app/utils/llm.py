"""大模型调用的统一封装（OpenAI 兼容接口）。

教学说明：后续章节用 LangChain 的 ChatOpenAI 也可以，
本课先用官方 openai SDK，调用链路更直观。
"""

from openai import OpenAI, APITimeoutError, APIError

from app.common.exceptions import BusinessException
from app.config import settings


def get_llm_client() -> OpenAI:
    """创建 OpenAI 兼容客户端（DeepSeek / Qwen / 硅基流动等均可）。"""
    if not settings.LLM_API_KEY:
        raise BusinessException(message="未配置 LLM_API_KEY，请先在 .env 中填写")
    return OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        timeout=settings.LLM_TIMEOUT,
        # 默认重试 2 次会让最坏耗时翻三倍（60s x 3），这里按配置收紧
        max_retries=settings.LLM_MAX_RETRIES,
    )


def chat_once(system_prompt: str, user_prompt: str, temperature: float = 0) -> str:
    """发起一次非流式对话，返回助手文本。出错时转成业务异常。"""
    client = get_llm_client()
    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
    except APITimeoutError as exc:
        raise BusinessException(message="大模型调用超时，请稍后重试") from exc
    except APIError as exc:
        raise BusinessException(message=f"大模型调用失败：{exc.message}") from exc

    content = response.choices[0].message.content
    if not content:
        raise BusinessException(message="大模型返回空内容")
    return content.strip()


def chat_stream(system_prompt: str, user_prompt: str, temperature: float = 0.3):
    """流式对话：逐段 yield 文本片段（token）。

    教学说明：前端通过 SSE 的 token 事件把这些片段拼成完整回答。
    """
    client = get_llm_client()
    try:
        stream = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            # 部分兼容接口会推送空 choices（如仅含 role / 结束标记），需跳过
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if not delta or not delta.content:
                continue
            yield delta.content
    except APITimeoutError as exc:
        raise BusinessException(message="大模型调用超时，请稍后重试") from exc
    except APIError as exc:
        raise BusinessException(message=f"大模型调用失败：{exc.message}") from exc
