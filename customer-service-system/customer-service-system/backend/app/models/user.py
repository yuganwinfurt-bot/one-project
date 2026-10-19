from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String
from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户信息表"}

    username: Mapped[str] = mapped_column(
        String(50), comment="账号", unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(255), comment="密码", nullable=False)
    name: Mapped[str] = mapped_column(String(50), comment="名称", nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), comment="角色：admin-管理员，user-运营，customer-普通用户", nullable=False
    )
    email: Mapped[str | None] = mapped_column(String(50), comment="邮箱")
    phone: Mapped[str | None] = mapped_column(String(50), comment="手机号")
    avatar: Mapped[str | None] = mapped_column(String(50), comment="头像")
    status: Mapped[int] = mapped_column(default=1, comment="状态：0-禁用，1-正常")
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="最近在线心跳时间"
    )
