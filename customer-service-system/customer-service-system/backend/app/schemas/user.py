from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# 密码长度规则：只约束“设置新密码”的入口（注册 / 管理员建用户 / 修改密码）。
# 登录接口不做长度校验，否则历史短密码账号（如演示账号 123）会无法登录。
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 64


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    role: str
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    status: int
    online: bool = False

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_user(cls, user):
        response = cls.model_validate(user)
        last_seen_at = getattr(user, "last_seen_at", None)
        response.online = bool(
            user.status == 1
            and last_seen_at is not None
            and datetime.now() - last_seen_at <= timedelta(seconds=90)
        )
        return response


class UserCreateRequest(BaseModel):
    username: str
    password: str = Field(
        default="123456", min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    status: int = 1


class UserUpdateRequest(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    role: Literal["admin", "user", "customer"] | None = None
    status: int | None = None
    password: str | None = Field(
        default=None, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )


class PasswordUpdateRequest(BaseModel):
    """修改密码的请求参数"""

    old_password: str
    new_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
