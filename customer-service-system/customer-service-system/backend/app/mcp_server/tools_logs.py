"""MCP 工具：查本地观测日志（agent_runs / steps）。"""

import json
from typing import Any

from app.database import SessionLocal
from app.observability.models import AgentRun, AgentRunStep


def query_logs(keyword: str = "", limit: int = 5) -> str:
    """查询最近的 Agent 运行记录，可选按问题关键词过滤。

    参数:
        keyword: 问题里包含的关键词，空则返回最近若干条
        limit: 返回条数上限
    """
    limit = max(1, min(int(limit or 5), 20))
    db = SessionLocal()
    try:
        query = db.query(AgentRun).order_by(AgentRun.id.desc())
        if keyword and keyword.strip():
            like = f"%{keyword.strip()}%"
            query = query.filter(AgentRun.question.like(like))
        runs = query.limit(limit).all()

        items: list[dict[str, Any]] = []
        for run in runs:
            steps = (
                db.query(AgentRunStep)
                .filter(AgentRunStep.run_id == run.id)
                .order_by(AgentRunStep.step_order.asc())
                .all()
            )
            items.append(
                {
                    "run_id": run.id,
                    "question": run.question,
                    "status": run.status,
                    "route": run.route,
                    "elapsed_ms": run.elapsed_ms,
                    "step_count": len(steps),
                    "steps_preview": [
                        {
                            "order": s.step_order,
                            "name": s.step_name,
                            "summary": s.summary,
                        }
                        for s in steps[:8]
                    ],
                }
            )

        payload = {
            "ok": True,
            "keyword": keyword or "",
            "count": len(items),
            "runs": items,
            "via": "mcp:query_logs",
        }
        return json.dumps(payload, ensure_ascii=False, default=str)
    except Exception as exc:
        message = getattr(exc, "message", None) or str(exc) or exc.__class__.__name__
        return json.dumps(
            {"ok": False, "error": message, "via": "mcp:query_logs"},
            ensure_ascii=False,
        )
    finally:
        db.close()
