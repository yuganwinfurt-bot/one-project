import json

import httpx
from fastapi.testclient import TestClient

import hub_api


def test_public_api_is_retired_even_if_old_server_settings_exist(monkeypatch):
    monkeypatch.setenv("PUBLIC_DEMO_ENABLED", "1")
    monkeypatch.setenv("PUBLIC_AGENT_API_KEY", "old-server-key")
    client = TestClient(hub_api.app)
    response = client.post("/api/public/chat", json={"mode": "agent", "question": "hello"})
    assert response.status_code == 410
    assert response.json()["detail"] == "在线体验已改为浏览器直连模型服务"


def test_site_csp_keeps_connections_same_origin():
    response = TestClient(hub_api.app).get("/api/health")
    assert response.status_code == 200
    policy = response.headers["Content-Security-Policy"]
    assert "connect-src 'self';" in policy
    assert "connect-src 'self' https:" not in policy


def test_auth_proxy_forwards_cookie_and_sets_same_origin_cookie(monkeypatch):
    captured = {}

    class FakeUpstreamResponse:
        status_code = 200
        content = b'{"role":"guest"}'
        headers = httpx.Headers({
            "content-type": "application/json",
            "set-cookie": "yugan_session=guest.token; HttpOnly; Path=/; SameSite=lax",
        })

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def request(self, method, url, *, headers, content):
            captured.update(method=method, url=url, headers=headers, content=content)
            return FakeUpstreamResponse()

    monkeypatch.setattr(hub_api.httpx, "AsyncClient", lambda **_kwargs: FakeAsyncClient())
    client = TestClient(hub_api.app, base_url="https://portfolio.test")
    response = client.get(
        "/api/auth/status",
        headers={"Origin": "https://portfolio.test", "Cookie": "yugan_session=guest.token"},
    )

    assert response.status_code == 200
    assert response.json() == {"role": "guest"}
    assert response.headers["cache-control"] == "no-store"
    assert "yugan_session=guest.token" in response.headers["set-cookie"]
    assert captured["method"] == "GET"
    assert captured["headers"]["Cookie"] == "yugan_session=guest.token"
    assert captured["headers"]["X-Forwarded-For"] == "testclient"
    assert "; Secure" in response.headers["set-cookie"]


def test_auth_proxy_forwards_admin_login_to_agent(monkeypatch):
    captured = {}

    class FakeUpstreamResponse:
        status_code = 200
        content = b'{"role":"admin"}'
        headers = httpx.Headers({"content-type": "application/json"})

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def request(self, method, url, *, headers, content):
            captured.update(method=method, url=url, headers=headers, content=content)
            return FakeUpstreamResponse()

    monkeypatch.setattr(hub_api.httpx, "AsyncClient", lambda **_kwargs: FakeAsyncClient())
    client = TestClient(hub_api.app, base_url="http://portfolio.test")
    response = client.post(
        "/api/auth/login",
        headers={"Origin": "http://portfolio.test"},
        json={"username": "admin-test", "password": "test-password"},
    )

    assert response.status_code == 200
    assert response.json() == {"role": "admin"}
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/api/auth/login")
    assert json.loads(captured["content"]) == {
        "username": "admin-test",
        "password": "test-password",
    }


def test_auth_proxy_rejects_cross_origin_requests_before_forwarding(monkeypatch):
    def unexpected_client(**_kwargs):
        raise AssertionError("cross-origin request must not reach Agent")

    monkeypatch.setattr(hub_api.httpx, "AsyncClient", unexpected_client)
    client = TestClient(hub_api.app, base_url="https://portfolio.test")
    response = client.post(
        "/api/auth/login",
        headers={"Origin": "https://evil.test"},
        json={"username": "someone", "password": "wrong"},
    )

    assert response.status_code == 403
