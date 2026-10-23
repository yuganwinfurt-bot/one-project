"""自然语言转 SQL 的完整流程：生成 → 校验 → 执行 → 失败自纠一次。

校验规则见 validate.py；提示词见 prompt.py。
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessException
from app.services.nl2sql.prompt import SCHEMA_PROMPT
from app.services.nl2sql.validate import (
    DEFAULT_ROW_LIMIT,
    MAX_ROW_LIMIT,
    _outer_limit,
    _parse_select,
    validate_sql,
)
from app.utils.llm import chat_once

logger = logging.getLogger(__name__)

# 单条查询最长执行时间（毫秒），执行时通过 SET SESSION 下发
QUERY_TIMEOUT_MS = 5000

SQL_FIX_MAX_ATTEMPTS = 1


def _query_context(question: str) -> str:
    now = datetime.now(timezone(timedelta(hours=8)))
    return f"当前业务时间（Asia/Shanghai）：{now.isoformat(timespec='seconds')}\n查询需求：\n{question.strip()}"


def generate_sql(question: str) -> str:
    """调用大模型，把自然语言问题转成 SQL。"""
    if not question or not question.strip():
        raise BusinessException(message="问题不能为空")

    raw = chat_once(
        system_prompt=SCHEMA_PROMPT,
        user_prompt=_query_context(question),
    )
    try:
        return validate_sql(raw)
    except BusinessException as exc:
        logger.warning("生成的 SQL 未通过校验，交给模型修正：%s", exc.message)
        return generate_sql_fix(question, raw, exc.message)


def generate_sql_fix(question: str, failed_sql: str, error: str) -> str:
    """把失败 SQL 和数据库报错一起喂回模型，让它自己改一版。

    有些错误（例如 MySQL 严格模式拒绝聚合里混明细列）只有真执行才知道，
    提示词写不干净；带上原始报错让模型自纠，比直接放弃走兜底更划算。
    """
    if not question or not question.strip():
        raise BusinessException(message="问题不能为空")

    raw = chat_once(
        system_prompt=SCHEMA_PROMPT,
        user_prompt=(
            f"{_query_context(question)}\n\n"
            f"上一版 SQL 被数据库拒绝了，请修正后重新输出一条 SELECT：\n"
            f"{failed_sql}\n\n"
            f"数据库报错：{error}"
        ),
    )
    return validate_sql(raw)


def _bounded_select(sql: str, limit: int = DEFAULT_ROW_LIMIT) -> tuple[str, int]:
    """统一执行上限，确保返回给流程的 SQL 与实际执行的查询一致。"""
    query = _parse_select(validate_sql(sql))
    count = _outer_limit(query)
    effective_limit = min(count if count is not None else max(0, limit), MAX_ROW_LIMIT)
    return query.limit(effective_limit).sql(dialect="mysql", comments=False), effective_limit


def execute_select(
    db: Session, sql: str, limit: int = DEFAULT_ROW_LIMIT
) -> tuple[list[dict[str, Any]], bool]:
    """执行已通过校验的 SELECT。

    返回：(行列表, 是否可能被截断)
    「截断」指取回行数达到本次 LIMIT，真实总量可能更多。
    """
    safe_sql, effective_limit = _bounded_select(sql, limit)

    try:
        # MySQL：限制单条语句最长执行时间（毫秒）
        db.execute(text(f"SET SESSION MAX_EXECUTION_TIME = {QUERY_TIMEOUT_MS}"))
        result = db.execute(text(safe_sql))
    except Exception as exc:
        logger.exception("SQL 执行失败: %s", safe_sql)
        # 不把驱动原始错误回给前端，避免泄露 SQL / 路径细节；
        # 但原始报错挂在异常上，供上层喂回模型自纠
        error = BusinessException(message="SQL 执行失败，请调整问题后重试")
        error.sql_error = str(exc)[:500]
        raise error from exc

    # SQL 层和取数层都限制行数，不再无上限地调用 all()。
    try:
        rows = (
            [dict(row) for row in result.mappings().fetchmany(effective_limit)]
            if effective_limit else []
        )
    finally:
        result.close()
    truncated = effective_limit > 0 and len(rows) >= effective_limit
    return rows, truncated


def query_by_question(db: Session, question: str) -> dict[str, Any]:
    """完整流程：问题 → 生成 SQL → 校验 → 执行 → 返回结果摘要。

    执行失败时带着数据库报错让模型自纠一次（SQL_FIX_MAX_ATTEMPTS）；
    再失败就照旧抛业务异常，由调用方回退到语义检索。
    """
    sql = generate_sql(question)
    for attempt in range(SQL_FIX_MAX_ATTEMPTS + 1):
        try:
            sql, _ = _bounded_select(sql)
            rows, truncated = execute_select(db, sql)
        except BusinessException as exc:
            if attempt >= SQL_FIX_MAX_ATTEMPTS:
                raise
            detail = getattr(exc, "sql_error", exc.message)
            logger.warning("SQL 执行失败，带报错让模型自纠：%s", detail)
            try:
                sql = generate_sql_fix(question, sql, detail)
            except BusinessException as fix_exc:
                # 自纠也没产出合法 SQL：保持原来的错误信息，交给上层兜底
                raise exc from fix_exc
            continue

        return {
            "question": question,
            "sql": sql,
            "row_count": len(rows),
            "truncated": truncated,
            "rows": rows,
        }

    # 循环必然在最后一次 attempt 里 return 或 raise，这里只为类型完整
    raise BusinessException(message="SQL 执行失败，请调整问题后重试")
