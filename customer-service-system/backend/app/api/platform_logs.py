"""平台日志查询接口。"""

from typing import Annotated

from fastapi import APIRouter, Query

from app.common.response import Response
from app.common.exceptions import BusinessException
from app.dependencies.auth import CurrentUser, DbSession
from app.services.platform_log_service import list_platform_logs, rollback_platform_log

router = APIRouter(prefix="/platform-logs", tags=["平台操作日志"])


@router.get("")
def get_platform_logs(
    user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
):
    if user.role not in {"admin", "user"}:
        raise BusinessException(message="仅管理员和运营可以查看平台操作日志", code=403)
    return Response.success(data=list_platform_logs(db, page, page_size, keywords, user))


@router.post("/{log_id}/rollback")
def rollback_log(
    log_id: int,
    user: CurrentUser,
    db: DbSession,
):
    if user.role not in {"admin", "user"}:
        raise BusinessException(message="仅管理员和运营可以回退平台操作日志", code=403)
    return Response.success(
        message="日志回退成功",
        data=rollback_platform_log(db, user, log_id),
    )
