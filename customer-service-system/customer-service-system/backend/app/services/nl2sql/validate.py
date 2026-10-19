"""SQL 安全校验：解析查询树 → 表白名单、写操作拦截、危险函数、行数封顶。"""

import re

from sqlglot import exp, parse
from sqlglot.errors import SqlglotError

from app.common.exceptions import BusinessException

TABLE_WHITELIST = {"products", "orders", "reviews", "after_sale_requests"}

PRIVATE_COLUMNS = {
    "shipping_address", "exchange_shipping_address", "password", "password_hash",
    "password_digest", "token", "api_key", "secret", "phone", "email",
    "buyer_user_id", "user_id", "processed_by",
}

DEFAULT_ROW_LIMIT = 50

MAX_ROW_LIMIT = 200

FORBIDDEN_FUNCTIONS = [
    "SLEEP",
    "BENCHMARK",
    "LOAD_FILE",
    "GET_LOCK",
    "RELEASE_LOCK",
    "IS_FREE_LOCK",
    "IS_USED_LOCK",
    "UPDATEXML",
    "EXTRACTVALUE",
    "GTID_SUBSET",
    "GTID_SUBTRACT",
]


def _strip_code_fence(sql: str) -> str:
    """去掉模型偶尔包上的 ```sql ... ```。"""
    text_sql = sql.strip()
    if text_sql.startswith("```"):
        text_sql = re.sub(r"^```(?:sql)?\s*", "", text_sql, flags=re.IGNORECASE)
        text_sql = re.sub(r"\s*```$", "", text_sql)
    return text_sql.strip().rstrip(";")


def _parse_select(sql: str) -> exp.Select:
    """解析查询结构；检查语句数量，而不是用正则猜测 SQL。"""
    cleaned = _strip_code_fence(sql)
    if not cleaned:
        raise BusinessException(message="生成的 SQL 为空")
    try:
        statements = [item for item in parse(cleaned, read="mysql") if item is not None]
    except SqlglotError as exc:
        raise BusinessException(message="SQL 语法无法解析，请调整问题后重试") from exc
    if len(statements) != 1:
        raise BusinessException(message="只允许执行单条查询语句")
    query = statements[0]
    if not isinstance(query, exp.Select):
        raise BusinessException(message="只允许执行查询语句（SELECT）")
    return query


def _outer_limit(query: exp.Select) -> int | None:
    """只读取最外层 LIMIT，子查询和注释里的数字不会影响返回上限。"""
    limit = query.args.get("limit")
    if limit is None:
        return None
    count = limit.expression
    if not isinstance(count, exp.Literal) or not count.is_int or int(count.this) < 0:
        raise BusinessException(message="LIMIT 必须是非负整数")
    return int(count.this)


def _extract_limit(sql: str) -> int | None:
    return _outer_limit(_parse_select(sql))


def _cap_limit(sql: str, cap: int = MAX_ROW_LIMIT) -> str:
    query = _parse_select(sql)
    count = _outer_limit(query)
    if count is not None and count > cap:
        query = query.limit(cap)
        return query.sql(dialect="mysql", comments=False)
    return sql


def validate_sql(sql: str) -> str:
    """按查询树检查所有表和函数；执行的是重新生成的无注释 SQL。"""
    query = _parse_select(sql)
    # 限定本课支持的只读查询范围，暂不支持 CTE / UNION / 变量 / 锁定读取。
    # 优化器提示也禁止，避免模型通过 MAX_EXECUTION_TIME 提示改写超时限制。
    forbidden = (
        exp.DDL, exp.DML, exp.Into, exp.Lock, exp.With, exp.Hint,
        exp.SetOperation, exp.Parameter, exp.SessionParameter,
    )
    if any(isinstance(node, forbidden) for node in query.walk()):
        raise BusinessException(message="查询包含禁止或暂不支持的 SQL 结构")
    for column in query.find_all(exp.Column):
        if column.name.lower() in PRIVATE_COLUMNS:
            raise BusinessException(message="查询包含不允许读取的个人信息或凭证字段")
    # COUNT(*) 不读取字段值；禁止其余通配字段，避免绕过敏感列限制。
    for star in query.find_all(exp.Star):
        if not isinstance(star.parent, exp.Count):
            raise BusinessException(message="请明确选择所需业务字段，不允许使用通配字段")
    for func in query.find_all(exp.Func):
        name = func.name if isinstance(func, exp.Anonymous) else func.sql_name()
        if name.upper() in FORBIDDEN_FUNCTIONS:
            raise BusinessException(message=f"检测到禁止的 SQL 函数：{name}")

    tables = list(query.find_all(exp.Table))
    if not tables:
        raise BusinessException(message="SQL 中未识别到表名")
    for table in tables:
        if table.db or table.catalog or not isinstance(table.this, exp.Identifier):
            raise BusinessException(message="不允许访问其他数据库或动态表名")
        if table.name.lower() not in TABLE_WHITELIST:
            raise BusinessException(
                message=f"表 `{table.name}` 不在白名单内，允许的表：{sorted(TABLE_WHITELIST)}"
            )
    _outer_limit(query)
    return query.sql(dialect="mysql", comments=False)
