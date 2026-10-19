"""语义检索调试接口（lesson-04）。"""

from fastapi import APIRouter

from app.common.response import Response
from app.dependencies.auth import CurrentAdmin, CurrentProductEditor
from app.schemas.semantic import SemanticSearchRequest, SemanticSearchResponse
from app.services import semantic_search_service

router = APIRouter(prefix="/semantic", tags=["语义检索"])


@router.post("/search")
def semantic_search(
    body: SemanticSearchRequest,
    _: CurrentProductEditor,
):
    """模糊主题 → 向量检索。

    本课只验证检索链路；与结构化查询的路由判断在 lesson-05 实现。
    """
    result = semantic_search_service.search_similar(body.query, body.top_k)
    return Response.success(data=SemanticSearchResponse(**result))


@router.post("/sync")
def sync_semantic_data(_: CurrentAdmin):
    """同步后台完整业务快照，不导出凭证；个人信息脱敏。"""
    result = semantic_search_service.sync_ecommerce_data()
    return Response.success(message="已同步到独立 RAG 知识库", data=result)
