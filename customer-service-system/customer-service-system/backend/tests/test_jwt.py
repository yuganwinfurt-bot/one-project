"""JWT 有效期用 UTC 计算，不受部署机器本地时区影响。"""
from datetime import datetime, timezone

from app.config import settings
from app.utils import jwt as jwt_utils


def test_token_expiry_matches_configured_duration(monkeypatch):
    fixed = datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc)

    class Clock:
        @staticmethod
        def now(tz=None):
            # 模拟 UTC+8 机器：无时区 now() 的值与 UTC now() 不同。
            if tz is None:
                return fixed.replace(hour=8, tzinfo=None)
            return fixed.astimezone(tz)

    monkeypatch.setattr(jwt_utils, "datetime", Clock)
    token = jwt_utils.create_access_token(1)
    import jwt
    payload = jwt.decode(token, settings.JWT_SECRET_KEY,
                         algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
    assert payload["exp"] == int(fixed.timestamp()) + settings.JWT_EXPIRE_HOURS * 3600
