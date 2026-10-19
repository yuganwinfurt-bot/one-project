from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.user import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    UserResponse,
)


class LoginRequest(BaseModel):
    # 登录不校验密码长度：历史短密码账号需要能正常登录
    username: str
    password: str
    login_type: Literal["backend", "user"] = "backend"


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class RegisterRequest(BaseModel):
    username: str
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    name: str | None = None
