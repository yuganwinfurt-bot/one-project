from typing import Literal

from fastapi import APIRouter, Response as HttpResponse

from app.common.response import Response
from app.dependencies.auth import DbSession
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services import auth_service
from app.services.demo_login_service import list_demo_accounts

router = APIRouter(prefix="/auth", tags=["权限验证"])


@router.get("/demo-accounts")
def demo_accounts(db: DbSession, response: HttpResponse, mode: Literal["backend", "user"] = "backend"):
    """公开演示入口：后台账号或专用体验买家，按登录模式分别返回。"""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return Response.success(data=list_demo_accounts(db, mode))


@router.post("/login")
def login(data: LoginRequest, db: DbSession):
    """登录"""
    result = auth_service.login(db, data)
    # 返回信息
    return Response.success(
        message="登录成功",
        data=result,
    )


@router.post("/register")
def register(data: RegisterRequest, db: DbSession):
    """注册"""
    auth_service.register(db, data)
    # 返回信息
    return Response.success(message="注册成功")
