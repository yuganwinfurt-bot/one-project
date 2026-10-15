"""Shared signed-cookie authentication for the Agent console."""

import base64
import hashlib
import hmac
import json
import secrets
import time
from collections import defaultdict, deque
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

COOKIE_NAME = "yugan_session"
SESSION_SECONDS = 12 * 60 * 60


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def hash_password(password: str, *, salt: str | None = None, rounds: int = 310_000) -> str:
    salt = salt or _b64(secrets.token_bytes(18))
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), rounds)
    return f"pbkdf2_sha256${rounds}${salt}${_b64(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hash_password(password, salt=salt, rounds=int(rounds)).rsplit("$", 1)[1]
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


class AuthManager:
    def __init__(self, username: str, password_hash: str, signing_secret: str):
        self.username = username.strip()
        self.password_hash = password_hash.strip()
        raw_secret = signing_secret.strip().encode()
        self._signing_secret_configured = len(raw_secret) >= 32
        self.signing_secret = (
            raw_secret if self._signing_secret_configured else secrets.token_bytes(48)
        )
        self.attempts: dict[str, deque[float]] = defaultdict(deque)

    @property
    def configured(self) -> bool:
        return bool(self.username and self.password_hash and self._signing_secret_configured)

    def claims(self, request: Request) -> dict:
        token = request.cookies.get(COOKIE_NAME, "")
        try:
            payload_part, signature_part = token.split(".", 1)
            expected = _b64(
                hmac.new(self.signing_secret, payload_part.encode(), hashlib.sha256).digest()
            )
            if not hmac.compare_digest(signature_part, expected):
                return {}
            padded_payload = payload_part + "=" * (-len(payload_part) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded_payload))
            if payload.get("exp", 0) < int(time.time()):
                return {}
            role = payload.get("role")
            if role == "admin" and not hmac.compare_digest(
                str(payload.get("username", "")), self.username
            ):
                return {}
            if role not in {"admin", "guest"} or not isinstance(payload.get("sub"), str):
                return {}
            return payload
        except (ValueError, TypeError, json.JSONDecodeError):
            return {}

    def role(self, request: Request) -> str:
        return self.claims(request).get("role", "guest")

    def subject(self, request: Request) -> str:
        return self.claims(request).get("sub", "anonymous")

    def issue(self) -> str:
        payload = _b64(json.dumps({
            "username": self.username,
            "role": "admin",
            "sub": "admin",
            "exp": int(time.time()) + SESSION_SECONDS,
        }, separators=(",", ":")).encode())
        signature = _b64(hmac.new(self.signing_secret, payload.encode(), hashlib.sha256).digest())
        return f"{payload}.{signature}"

    def issue_guest(self) -> str:
        return self.issue_guest_session()[0]

    def issue_guest_session(self) -> tuple[str, str]:
        subject = uuid4().hex
        payload = _b64(json.dumps({
            "role": "guest",
            "sub": subject,
            "exp": int(time.time()) + SESSION_SECONDS,
        }, separators=(",", ":")).encode())
        signature = _b64(hmac.new(self.signing_secret, payload.encode(), hashlib.sha256).digest())
        return f"{payload}.{signature}", subject

    def authenticate(self, request: Request, username: str, password: str) -> str:
        if not self.configured:
            raise HTTPException(503, "管理员登录尚未配置")
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        attempts = self.attempts[client_ip]
        while attempts and now - attempts[0] > 600:
            attempts.popleft()
        if len(attempts) >= 8:
            raise HTTPException(429, "登录尝试过多，请 10 分钟后再试")
        attempts.append(now)
        name_ok = hmac.compare_digest(username.strip(), self.username)
        password_ok = verify_password(password, self.password_hash)
        if not (name_ok and password_ok):
            raise HTTPException(401, "账号或密码错误")
        attempts.clear()
        return self.issue()

    def set_cookie(self, response: JSONResponse, request: Request, token: str) -> None:
        forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
        response.set_cookie(
            COOKIE_NAME,
            token,
            max_age=SESSION_SECONDS,
            httponly=True,
            secure=request.url.scheme == "https" or forwarded_proto == "https",
            samesite="lax",
            path="/",
        )

    def clear_cookie(self, response: JSONResponse, request: Request) -> None:
        forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
        response.delete_cookie(
            COOKIE_NAME,
            path="/",
            httponly=True,
            secure=request.url.scheme == "https" or forwarded_proto == "https",
            samesite="lax",
        )


class LoginRequest:
    """Marker to keep auth module independent of each app's Pydantic schemas."""

