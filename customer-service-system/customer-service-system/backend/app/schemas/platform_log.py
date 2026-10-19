"""平台日志查询结果。"""

from datetime import datetime

from pydantic import field_serializer

from app.schemas.base import RowItem


class PlatformLogItem(RowItem):
    id: int
    actor_username: str
    actor_name: str
    actor_role: str
    operation: str
    before_value: str | None = None
    after_value: str | None = None
    create_time: datetime | None = None
    rolled_back_at: datetime | None = None
    rollback_of_id: int | None = None
    can_rollback: bool = False

    @field_serializer("create_time")
    def _time(self, value: datetime | None) -> str | None:
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None
