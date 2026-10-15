import asyncio

from starlette.requests import Request

from app.main import authenticate_and_limit_guests


def make_request(method: str, path: str) -> Request:
    return Request({
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 50000),
        "server": ("127.0.0.1", 8000),
    })


def test_guest_write_access_is_limited_to_chat_and_retrieval():
    async def reached_route(_request):
        from starlette.responses import Response

        return Response(status_code=204)

    forbidden = [
        ("POST", "/api/projects"),
        ("POST", "/api/knowledge-bases"),
        ("POST", "/api/knowledge-bases/kb/documents"),
        ("DELETE", "/api/knowledge-bases/kb/documents/documents/chunks/chunk"),
        ("DELETE", "/api/knowledge-bases/kb/documents/document"),
    ]
    for method, path in forbidden:
        response = asyncio.run(authenticate_and_limit_guests(make_request(method, path), reached_route))
        assert response.status_code == 403

    for method, path in [
        ("POST", "/api/projects/project/chats"),
        ("POST", "/api/chats/chat/retrieve"),
        ("POST", "/api/chats/chat/answer"),
        ("DELETE", "/api/chats/chat"),
    ]:
        response = asyncio.run(authenticate_and_limit_guests(make_request(method, path), reached_route))
        assert response.status_code == 204

