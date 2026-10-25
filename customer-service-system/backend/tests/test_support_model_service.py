import asyncio
from types import SimpleNamespace

import httpx
import pytest

from app.services import support_model_service as service

RealAsyncClient = httpx.AsyncClient
MESSAGES = [{'role': 'user', 'content': '请问如何申请退货？'}]


def configure(monkeypatch, handler, **overrides):
    config = dict(LLM_API_KEY='test-server-secret', LLM_MODEL='server-model',
                  LLM_BASE_URL='https://provider.test/v1', LLM_TIMEOUT=60,
                  SUPPORT_BRIDGE_TOKEN='test-bridge-secret', AGENT_SERVICE_URL='http://agent.test')
    config.update(overrides)
    monkeypatch.setattr(service, 'settings', SimpleNamespace(**config))
    monkeypatch.setattr(service.httpx, 'AsyncClient',
                        lambda **kw: RealAsyncClient(**kw, transport=httpx.MockTransport(handler)))


def test_selected_agent_model_is_used_without_fallback(monkeypatch):
    def handle(request):
        assert request.url.host == 'agent.test'
        assert request.headers['x-support-token'] == 'test-bridge-secret'
        assert 'authorization' not in request.headers
        return httpx.Response(200, json={'content': '可以从订单申请退货。', 'model_name': 'selected-model'})
    configure(monkeypatch, handle)
    assert asyncio.run(service.complete_support_reply(MESSAGES))['model_name'] == 'selected-model'


@pytest.mark.parametrize('status', [403, 404, 503])
def test_unavailable_relay_uses_existing_server_configuration(monkeypatch, status):
    hosts = []
    def handle(request):
        hosts.append(request.url.host)
        if request.url.host == 'agent.test':
            return httpx.Response(status, json={'detail': 'not ready'})
        assert 'x-support-token' not in request.headers
        assert request.headers['authorization'] == 'Bearer test-server-secret'
        return httpx.Response(200, json={'choices': [{'message': {'content': ' 请在订单页申请售后。 '}}]})
    configure(monkeypatch, handle)
    result = asyncio.run(service.complete_support_reply(MESSAGES))
    assert hosts == ['agent.test', 'provider.test']
    assert result == {'content': '请在订单页申请售后。', 'model_name': 'server-model'}


def test_server_configuration_works_without_a_bridge_token(monkeypatch):
    def handle(request):
        assert request.url.host == 'provider.test'
        return httpx.Response(200, json={'choices': [{'message': {'content': '您好。'}}]})
    configure(monkeypatch, handle, SUPPORT_BRIDGE_TOKEN='')
    assert asyncio.run(service.complete_support_reply(MESSAGES))['content'] == '您好。'


def test_missing_configuration_is_actionable_without_making_requests(monkeypatch):
    def handle(request):
        pytest.fail('No model configured: no request should be made')
    configure(monkeypatch, handle, SUPPORT_BRIDGE_TOKEN='', LLM_API_KEY='')
    with pytest.raises(service.SupportModelError, match='尚未连接模型'):
        asyncio.run(service.complete_support_reply(MESSAGES))


def test_provider_failure_does_not_leak_credentials_or_silently_change_model(monkeypatch):
    def handle(request):
        assert request.url.host == 'agent.test'
        return httpx.Response(502, json={'detail': 'secret-provider-error test-server-secret'})
    configure(monkeypatch, handle)
    with pytest.raises(service.SupportModelError) as exc:
        asyncio.run(service.complete_support_reply(MESSAGES))
    assert 'secret' not in str(exc.value)
    assert '申请人工客服' in str(exc.value)


def test_timeout_is_not_retried_against_a_different_model(monkeypatch):
    def handle(request):
        assert request.url.host == 'agent.test'
        raise httpx.ReadTimeout('provider secret', request=request)
    configure(monkeypatch, handle)
    with pytest.raises(service.SupportModelError, match='回复超时'):
        asyncio.run(service.complete_support_reply(MESSAGES))


def test_empty_response_cannot_be_saved_as_a_successful_reply(monkeypatch):
    configure(monkeypatch, lambda request: httpx.Response(200, json={'content': '', 'model_name': 'model'}))
    with pytest.raises(service.SupportModelError, match='未返回有效回复'):
        asyncio.run(service.complete_support_reply(MESSAGES))
