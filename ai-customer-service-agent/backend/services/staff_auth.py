"""Authenticate support staff against commerce without copying its account database."""
import hashlib
import asyncio
import json
import os
import secrets
import time
from dataclasses import dataclass

from urllib.error import HTTPError, URLError
from urllib.request import Request as NetworkRequest, build_opener, ProxyHandler
from fastapi import APIRouter, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

COOKIE = 'support_staff_session'
router = APIRouter(prefix='/api/auth', tags=['电商账号登录'])


@dataclass
class StaffSession:
    commerce_token: str
    user: dict
    expires: float
    checked: float


sessions: dict[str, StaffSession] = {}


def session_key(request):
    value = request.cookies.get(COOKIE, '')
    return hashlib.sha256(value.encode()).hexdigest() if value else ''


async def commerce(path, payload=None, token=None):
    url = os.getenv('ECOMMERCE_BASE_URL', 'http://127.0.0.1:8001').rstrip('/') + path
    def read():
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer '+token
        query = NetworkRequest(url, data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
        try:
            with build_opener(ProxyHandler({})).open(query, timeout=12) as response:
                data, status = json.load(response), response.status
        except HTTPError as error:
            try:
                data, status = json.load(error), error.code
            except (ValueError, OSError):
                raise HTTPException(503, '电商账号服务暂时不可用') from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise HTTPException(503, '电商账号服务暂时无法连接，请稍后重试') from None
        if status >= 400 or data.get('code') != 200:
            code = status if status >= 400 else data.get('code', 401)
            raise HTTPException(code if code in {400, 401, 403} else 503,
                                data.get('message') or data.get('detail') or '登录已失效，请重新登录')
        return data.get('data')
    return await asyncio.to_thread(read)


async def current_session(request):
    key = session_key(request)
    session = sessions.get(key)
    if session is None or session.expires <= time.time():
        sessions.pop(key, None)
        raise HTTPException(401, '请登录客服工单系统')
    if time.monotonic() - session.checked >= 3:
        try:
            user = await commerce('/api/user/me', token=session.commerce_token)
        except HTTPException as error:
            if error.status_code in {400, 401, 403}:
                sessions.pop(key, None)
                raise HTTPException(401, '登录已失效或账号已被禁用，请重新登录') from None
            raise
        if user.get('role') not in {'admin', 'user'} or user.get('status') != 1:
            sessions.pop(key, None)
            raise HTTPException(403, '仅管理员和运营账号可以进入客服工单系统')
        session.user, session.checked = user, time.monotonic()
    return session


class Login(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=512)


@router.post('/login')
async def login(body: Login, request: Request, response: Response):
    data = await commerce('/api/auth/login', {'username': body.username.strip(), 'password': body.password, 'login_type': 'backend'})
    user = data['user']
    if user.get('role') not in {'admin', 'user'} or user.get('status') != 1:
        raise HTTPException(403, '请使用电商分析平台的管理员或运营账号')
    # Only an opaque cookie reaches the browser; commerce JWT stays in this process.
    sessions.pop(session_key(request), None)
    for key, session in list(sessions.items()):
        if session.expires <= time.time():
            sessions.pop(key, None)
    cookie = secrets.token_urlsafe(48)
    sessions[hashlib.sha256(cookie.encode()).hexdigest()] = StaffSession(data['token'], user, time.time()+86400, time.monotonic())
    response.set_cookie(COOKIE, cookie, max_age=86400, httponly=True, secure=request.url.scheme == 'https', samesite='lax', path='/api')
    response.headers['Cache-Control'] = 'no-store'
    return {'user': user}


@router.get('/demo-accounts')
async def demo_accounts(response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return {'accounts': await commerce('/api/auth/demo-accounts?mode=backend')}


@router.get('/me')
async def me(request: Request, response: Response):
    session = await current_session(request)
    response.headers['Cache-Control'] = 'no-store'
    return {'user': session.user}


@router.post('/logout')
async def logout(request: Request, response: Response):
    sessions.pop(session_key(request), None)
    response.delete_cookie(COOKIE, path='/api')
    response.headers['Cache-Control'] = 'no-store'
    return {'ok': True}


def install_auth(app: FastAPI):
    @app.middleware('http')
    async def authenticate(request: Request, call_next):
        path = request.url.path
        if request.method == 'OPTIONS' or not path.startswith('/api/'):
            return await call_next(request)
        if request.method not in {'GET', 'HEAD'}:
            origin = request.headers.get('origin')
            if origin and origin not in {'http://127.0.0.1:3000', 'http://localhost:3000', str(request.base_url).rstrip('/')}:
                return JSONResponse({'detail': '请求来源无效'}, status_code=403)
        if path in {'/api/auth/login', '/api/auth/demo-accounts', '/api/auth/logout', '/api/auth/me', '/api/internal/customer-knowledge'}:
            return await call_next(request)
        try:
            session = await current_session(request)
        except HTTPException as error:
            return JSONResponse({'detail': error.detail}, status_code=error.status_code, headers={'Cache-Control': 'no-store'})
        request.state.staff_user = session.user
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        return response

    app.include_router(router)
