"""专用于公开演示登录的凭据，不进入用户资料接口或 RAG 导出。"""

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DemoLoginCredential(Base):
    __tablename__ = "demo_login_credentials"
    __table_args__ = {"comment": "公开演示账号的展示密码，与登录密码摘要同步"}

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    display_password: Mapped[str] = mapped_column(String(64), nullable=False)
    # 检测绕过账号服务直接改库的情况，避免展示已失效的密码。
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_customer_demo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
