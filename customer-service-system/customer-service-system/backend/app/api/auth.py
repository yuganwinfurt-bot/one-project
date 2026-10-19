from fastapi import APIRouter

from app.common.response import Response
from app.dependencies.auth import DbSession
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["权限验证"])


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
