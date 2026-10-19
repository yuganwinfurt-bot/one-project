from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.common.exceptions import BusinessException
from app.common.response import Response
from app.dependencies.auth import (
    CurrentAdmin,
    CurrentUser,
    DbSession,
    get_current_server_admin,
)
from app.schemas.auth import LoginResponse
from app.schemas.user import (
    PasswordUpdateRequest,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services import user_service
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/user", tags=["用户信息接口"])


@router.get("/me")
def get_user_info(current_user: CurrentUser):
    """获取当前登录用户信息"""
    return Response.success(data=user_service.get_user_info(current_user))


@router.put("/me")
def update_user_info(
    data: UserUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """更新当前用户信息"""
    res = user_service.update_user_info(db, current_user, data)
    return Response.success(data=res)


@router.put("/password")
def update_password(
    data: PasswordUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    user_service.update_password(db, current_user, data)
    return Response.success()


@router.post("/heartbeat")
def heartbeat(
    current_user: CurrentUser,
    db: DbSession,
):
    """更新当前用户的在线状态。"""
    user_service.heartbeat(db, current_user)
    return Response.success()


@router.post("/logout")
def logout(
    current_user: CurrentUser,
    db: DbSession,
):
    """清除当前账号的在线状态。"""
    user_service.logout(db, current_user)
    return Response.success()


@router.get("/list")
def get_user_list(
    _admin: CurrentAdmin,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
):
    res = user_service.get_user_page_list(db, page, page_size, keywords)
    return Response.success(data=res)


@router.post("/{user_id}/login-as")
def login_as_user(
    user_id: int,
    _admin: CurrentAdmin,
    db: DbSession,
):
    """Allow a platform administrator to open an enabled operator account in another tab."""
    user = user_service.get_user_for_update(db, user_id)
    if user.role not in {"user", "customer"}:
        raise BusinessException(message="不能切换为管理员账号")
    if user.status != 1:
        raise BusinessException(message="该账号已禁用，无法登录")

    user.last_seen_at = datetime.now()
    db.commit()
    db.refresh(user)
    return Response.success(
        message="已创建账号会话",
        data=LoginResponse(
            token=create_access_token(user.id),
            user=UserResponse.from_user(user),
        ),
    )


@router.post("")
def create_user(
    data: UserCreateRequest,
    admin: CurrentAdmin,
    db: DbSession,
):
    res = user_service.create_user(db, data, actor=admin)
    return Response.success(data=res)


@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    _admin: CurrentAdmin,
    request: Request,
    db: DbSession,
):
    user = user_service.get_user_for_update(db, user_id)
    server_admin = False
    if user.role == "admin" or data.role is not None:
        get_current_server_admin(request)
        server_admin = True
    res = user_service.update_user(
        db, user, data, actor=_admin, is_server_admin=server_admin
    )
    return Response.success(data=res)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: CurrentAdmin,
    db: DbSession,
):
    # delete 需要当前管理员对象，用于禁止删自己等业务校验
    user_service.delete_user(db, user_id, current_user)
    return Response.success()
