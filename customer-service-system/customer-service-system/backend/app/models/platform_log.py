"""用户对平台数据执行的修改记录。"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PlatformLog(Base):
    __tablename__ = "platform_logs"
    __table_args__ = {"comment": "平台操作日志"}

    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="操作者ID快照")
    actor_username: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作者账号")
    actor_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作者名称")
    actor_role: Mapped[str] = mapped_column(String(30), nullable=False, comment="操作者角色")
    operation: Mapped[str] = mapped_column(String(300), nullable=False, comment="操作说明")
    before_value: Mapped[str | None] = mapped_column(Text, nullable=True, comment="修改前")
    after_value: Mapped[str | None] = mapped_column(Text, nullable=True, comment="修改后")
    rollback_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="回退所需的数据快照")
    rollback_of_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="本条日志回退的原日志ID")
    rollback_log_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="回退本日志的操作日志ID")
    rolled_back_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="回退时间")
