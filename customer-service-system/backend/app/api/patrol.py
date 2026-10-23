"""系统触发的巡检接口：用固定问题驱动同一张 Agent 图。

和对话的区别只在触发方：这里是人点按钮、系统挑问题，走完全相同的
路由 / 多角色分析 / 动作决策链路，产出的较重动作同样要人工确认。
"""

from fastapi import APIRouter

from app.common.response import Response
from app.dependencies.auth import CurrentProductEditor
from app.services import patrol_service

router = APIRouter(prefix="/patrol", tags=["巡检"])


@router.get("/question")
def get_patrol_question(_user: CurrentProductEditor):
    """前端展示用：当前巡检用的固定问题。"""
    return Response.success(data={"question": patrol_service.PATROL_QUESTION})


@router.post("/run")
def run_patrol(current_user: CurrentProductEditor):
    """执行一次巡检。

    同步跑完（不流式），返回结论、运行 ID 与待确认动作。
    有 pending 动作时前端会引导用户去「运行历史」确认执行。
    运行记录挂在当前用户名下，否则运行历史（默认只看自己）里看不到。
    """
    data = patrol_service.run_patrol(user_id=current_user.id)
    return Response.success(data=data)
