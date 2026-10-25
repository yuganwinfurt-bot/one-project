"""Customer-service model requests, independent of a staff browser staying open."""
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class SupportModelError(Exception):
    """A safe message that can be shown to a buyer without provider credentials."""


async def complete_support_reply(messages):
    fallback_ready = bool(settings.LLM_API_KEY.strip() and settings.LLM_MODEL.strip())
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(105, connect=8), trust_env=False) as client:
            if settings.SUPPORT_BRIDGE_TOKEN:
                try:
                    response = await client.post(
                        settings.AGENT_SERVICE_URL.rstrip('/') + '/api/support-model/completions',
                        headers={'X-Support-Token': settings.SUPPORT_BRIDGE_TOKEN},
                        json={'messages': messages, 'max_tokens': 1500},
                    )
                except httpx.ConnectError:
                    if not fallback_ready:
                        raise
                    logger.warning('Agent客服连接不可用，使用已有的服务端模型配置')
                else:
                    if response.status_code in {403, 404, 503} and fallback_ready:
                        logger.warning('Agent客服模型未就绪 status=%s，使用已有的服务端模型配置', response.status_code)
                    else:
                        response.raise_for_status()
                        result = response.json()
                        if not isinstance(result.get('content'), str) or not result['content'].strip():
                            raise ValueError('empty reply')
                        return {'content': result['content'].strip(), 'model_name': result.get('model_name') or '客服模型'}

            if not fallback_ready:
                raise SupportModelError('AI客服尚未连接模型，可以稍后重试或申请人工客服')

            # Reuse the server's existing model configuration. Browser API keys
            # are never requested from buyers or copied into the commerce backend.
            response = await client.post(
                settings.LLM_BASE_URL.rstrip('/') + '/chat/completions',
                headers={'Authorization': 'Bearer ' + settings.LLM_API_KEY},
                json={'model': settings.LLM_MODEL, 'messages': messages,
                      'max_tokens': 1500, 'stream': False},
                timeout=min(settings.LLM_TIMEOUT, 105),
            )
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            if not isinstance(content, str) or not content.strip():
                raise ValueError('empty reply')
            return {'content': content.strip(), 'model_name': settings.LLM_MODEL}
    except httpx.TimeoutException:
        raise SupportModelError('AI客服回复超时，请重试或申请人工客服') from None
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        logger.warning('客服模型接口请求失败 status=%s', status)
        if status == 429:
            message = 'AI客服当前繁忙，请稍后重试或申请人工客服'
        elif status in {401, 403}:
            message = 'AI客服模型连接配置异常，可以申请人工客服'
        elif status in {404, 503}:
            message = 'AI客服尚未连接模型，可以稍后重试或申请人工客服'
        else:
            message = 'AI客服模型暂时无法回复，请重试或申请人工客服'
        raise SupportModelError(message) from None
    except httpx.TransportError:
        raise SupportModelError('AI客服服务连接中断，请重试或申请人工客服') from None
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        raise SupportModelError('AI客服未返回有效回复，请重试或申请人工客服') from None
