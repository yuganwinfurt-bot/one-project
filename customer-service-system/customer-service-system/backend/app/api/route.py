"""查询路由调试接口：只返回判断结果，不执行查询。"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent.router import decide_query_route
from app.common.response import Response
from app.dependencies.auth import CurrentUser, DbSession
from app.models.product import Product

router = APIRouter(prefix="/route", tags=["查询路由"])


class RouteRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


@router.post("/decide")
def decide_route(
    body: RouteRequest,
    db: DbSession,
    _: CurrentUser,
):
    """对问题做一次路由判断，方便课堂演示与联调。"""
    names = [r[0] for r in db.query(Product.name).all() if r[0]]
    decision = decide_query_route(body.question, known_product_names=names)
    return Response.success(data=decision.to_dict())
