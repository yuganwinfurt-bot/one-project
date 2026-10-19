"""MCP 工具：自然语言查 MySQL（内部走 NL2SQL + 白名单校验）。"""

import json
from typing import Any

from app.database import SessionLocal
from app.services.nl2sql import query_by_question
from app.services.nl2sql.service import _bounded_select, execute_select


def execute_mysql_select(sql: str) -> str:
    """执行模型提供的 SQL，仍受表、字段、只读、超时和行数限制。"""
    with SessionLocal() as db:
        try:
            safe_sql, _ = _bounded_select(sql)
            rows, truncated = execute_select(db, safe_sql)
            return json.dumps({"ok": True, "sql": safe_sql, "rows": rows,
                               "row_count": len(rows), "truncated": truncated}, ensure_ascii=False, default=str)
        except Exception as exc:
            detail = getattr(getattr(exc, "__cause__", None), "orig", None)
            message = str(detail)[:500] if detail is not None else (getattr(exc, "message", None) or "数据库查询失败")
            return json.dumps({"ok": False, "error": message}, ensure_ascii=False)


def query_mysql(question: str) -> str:
    """根据自然语言问题查询电商 MySQL，返回 JSON 字符串。

    参数:
        question: 用户问题，例如「轻云运动跑鞋评分≤2 的评价」
    """
    db = SessionLocal()
    try:
        result = query_by_question(db, question)
        payload: dict[str, Any] = {
            "ok": True,
            "question": result["question"],
            "sql": result["sql"],
            "row_count": result["row_count"],
            "truncated": result["truncated"],
            "rows": result["rows"],
            "via": "mcp:query_mysql",
        }
        return json.dumps(payload, ensure_ascii=False, default=str)
    except Exception as exc:
        message = getattr(exc, "message", None) or str(exc) or exc.__class__.__name__
        return json.dumps(
            {"ok": False, "error": message, "via": "mcp:query_mysql"},
            ensure_ascii=False,
        )
    finally:
        db.close()
