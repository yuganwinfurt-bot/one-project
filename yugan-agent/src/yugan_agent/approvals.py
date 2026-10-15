"""浏览器中的一次性电脑操作确认。"""

import asyncio
import secrets
import time


class ApprovalBroker:
    def __init__(self, timeout_seconds: int = 120):
        self.timeout_seconds = timeout_seconds
        self._pending: dict[str, dict] = {}
        self._active_scopes: set[str] = set()
        self._approved_scopes: set[str] = set()

    def begin(self, scope: str) -> bool:
        if scope in self._active_scopes:
            return False
        self._active_scopes.add(scope)
        return True

    def end(self, scope: str) -> None:
        self._approved_scopes.discard(scope)
        self._active_scopes.discard(scope)
        for item in self._pending.values():
            if item["scope"] == scope and not item["future"].done():
                item["future"].set_result(False)

    async def request(
        self, name: str, description: str, arguments: dict, *, scope: str | None = None
    ) -> bool:
        if scope is not None and scope in self._approved_scopes:
            return True
        approval_id = secrets.token_urlsafe(18)
        future = asyncio.get_running_loop().create_future()
        self._pending[approval_id] = {
            "id": approval_id,
            "name": name,
            "description": description,
            "arguments": arguments,
            "scope": scope,
            "created_at": time.time(),
            "future": future,
        }
        try:
            return await asyncio.wait_for(future, timeout=self.timeout_seconds)
        except TimeoutError:
            return False
        finally:
            self._pending.pop(approval_id, None)

    def list_pending(self, scope: str | None = None) -> list[dict]:
        now = time.time()
        return [
            {
                "id": item["id"],
                "name": item["name"],
                "description": item["description"],
                "arguments": item["arguments"],
                "expires_in": max(0, int(self.timeout_seconds - (now - item["created_at"]))),
            }
            for item in self._pending.values()
            if scope is None or item["scope"] == scope
        ]

    def approve_all(self, scope: str) -> bool:
        if scope not in self._active_scopes:
            return False
        pending = [
            item
            for item in self._pending.values()
            if item["scope"] == scope and not item["future"].done()
        ]
        if not pending:
            return False
        self._approved_scopes.add(scope)
        for item in pending:
            if not item["future"].done():
                item["future"].set_result(True)
        return True

    def decide(self, approval_id: str, approved: bool) -> bool:
        item = self._pending.get(approval_id)
        if item is None or item["future"].done():
            return False
        item["future"].set_result(approved)
        return True
