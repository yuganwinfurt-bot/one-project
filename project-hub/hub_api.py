"""Public, read-only gateway for the Vue project homepage."""

import os
import re
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
AGENT_API_URL = os.environ.get("PROJECT_HUB_AGENT_API_URL", "http://127.0.0.1:8020").rstrip("/")
app = FastAPI(title="项目实验室公开入口", docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    return response


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.api_route("/api/public/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def retired_public_api(path: str):
    raise HTTPException(status_code=410, detail="在线体验已改为浏览器直连模型服务")


@app.api_route("/api/auth/{action}", methods=["GET", "POST"])
async def auth_proxy(action: str, request: Request):
    methods = {"status": "GET", "login": "POST", "logout": "POST"}
    method = methods.get(action)
    if method is None:
        raise HTTPException(status_code=404, detail="身份接口不存在")
    if request.method != method:
        raise HTTPException(status_code=405, detail="请求方式不允许")
    origin = request.headers.get("origin")
    if origin and origin != str(request.base_url).rstrip("/"):
        raise HTTPException(status_code=403, detail="不接受跨源请求")

    body = await request.body() if method == "POST" else b""
    if len(body) > 4096:
        raise HTTPException(status_code=413, detail="登录请求内容过大")
    headers = {"Origin": AGENT_API_URL, "Accept": "application/json"}
    if request.client and request.client.host:
        headers["X-Forwarded-For"] = request.client.host
    session = request.cookies.get("yugan_session", "")
    if re.fullmatch(r"[A-Za-z0-9_.-]{1,2048}", session):
        headers["Cookie"] = f"yugan_session={session}"
    if body:
        headers["Content-Type"] = request.headers.get("content-type", "application/json")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream = await client.request(
                method,
                f"{AGENT_API_URL}/api/auth/{action}",
                headers=headers,
                content=body,
            )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="身份服务暂不可用") from None

    response = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type", "application/json"),
    )
    response.headers["Cache-Control"] = "no-store"
    for cookie in upstream.headers.get_list("set-cookie"):
        if request.url.scheme == "https" and "secure" not in cookie.lower():
            cookie = f"{cookie}; Secure"
        response.headers.append("set-cookie", cookie)
    return response


@app.get("/{path:path}", include_in_schema=False)
async def site(path: str):
    target = (DIST / path).resolve()
    if path and target.is_relative_to(DIST) and target.is_file():
        return FileResponse(target)
    index = DIST / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="请先运行 npm run build")
