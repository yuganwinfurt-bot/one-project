"""自然语言转 SQL 的调试接口（本课用于验证结构化查询）。"""

from fastapi import APIRouter

from app.common.response import Response
from app.dependencies.auth import CurrentUser, DbSession
from app.schemas.nl2sql import Nl2SqlRequest, Nl2SqlResponse
from app.services.nl2sql import query_by_question

router = APIRouter(prefix="/nl2sql", tags=["结构化查询"])


@router.post("/query")
def query_by_natural_language(
    body: Nl2SqlRequest,
    db: DbSession,
    _: CurrentUser,
):
    """把自然语言问题转成 SQL 并执行（只读）。

    返回生成的 SQL 与查询结果，方便在 Swagger 里直接验证。
    后续对话接口会在此基础上再让大模型总结成自然语言回答。
    """
    result = query_by_question(db, body.question)
    return Response.success(data=Nl2SqlResponse(**result))
