from fastapi.testclient import TestClient
from pydantic import SecretStr

from yugan_agent.api import create_app
from yugan_agent.auth import hash_password
from yugan_agent.config import Settings


def test_guest_is_read_only_for_global_configuration_but_can_login_as_admin(tmp_path):
    settings = Settings(
        provider="mock",
        workspace=tmp_path / "workspace",
        database=tmp_path / "memory.db",
        log_file=tmp_path / "events.jsonl",
        admin_username="admin-test",
        admin_password_hash=SecretStr(hash_password("test-only-password")),
        auth_signing_secret=SecretStr("test-signing-secret-" * 3),
    )
    origin = "http://127.0.0.1:8020"
    with TestClient(
        create_app(settings, env_path=tmp_path / ".env"),
        base_url=origin,
        client=("127.0.0.1", 50000),
    ) as client:
        guest = client.get("/api/auth/status").json()
        assert guest["role"] == "guest"
        assert guest["subject"]
        workspaces = client.get("/api/workspaces").json()
        assert len(workspaces["workspaces"]) == 1
        assert workspaces["workspaces"][0]["path"] == ""
        assert client.post(
            "/api/workspaces",
            json={"name": "blocked", "path": str(tmp_path / "blocked")},
        ).status_code == 403
        assert client.patch(
            "/api/tools/builtins/calculator", json={"enabled": False}
        ).status_code == 403
        assert client.post(
            "/api/tools/custom",
            json={"name": "guest_tool", "description": "blocked", "endpoint": "https://example.com"},
        ).status_code == 403
        assert all(
            not item["name"].startswith("desktop_")
            for item in client.get("/api/tools/management").json()["builtins"]
        )
        assert client.post(
            "/api/settings/models",
            json={
                "name": "blocked",
                "endpoint": "https://api.example.com/v1",
                "model": "m",
                "api_key": "secret",
            },
        ).status_code == 410

        login = client.post(
            "/api/auth/login",
            json={"username": "admin-test", "password": "test-only-password"},
        )
        assert login.status_code == 200
        assert client.get("/api/auth/status").json()["role"] == "admin"
        assert client.patch(
            "/api/tools/builtins/calculator", json={"enabled": False}
        ).status_code == 200

