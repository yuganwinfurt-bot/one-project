"""SQL 安全校验的单元测试（不依赖大模型与数据库）。

在 backend 目录执行：
    python -m pytest tests/test_sql_validate.py -q
"""

import pytest

from app.common.exceptions import BusinessException
from app.services.nl2sql.validate import (
    MAX_ROW_LIMIT,
    _cap_limit,
    _extract_limit,
    validate_sql,
)


def test_allow_simple_select():
    sql = validate_sql("SELECT id, name FROM products LIMIT 10")
    assert "products" in sql.lower()


def test_allow_join():
    sql = validate_sql(
        """
        SELECT p.name, r.content
        FROM reviews r
        JOIN products p ON p.id = r.product_id
        WHERE r.rating <= 2
        LIMIT 20
        """
    )
    assert "reviews" in sql.lower()


def test_reject_update():
    with pytest.raises(BusinessException) as exc:
        validate_sql("UPDATE products SET price = 1 WHERE id = 1")
    assert "SELECT" in exc.value.message or "禁止" in exc.value.message


def test_reject_delete():
    with pytest.raises(BusinessException):
        validate_sql("DELETE FROM orders WHERE id = 1")


def test_reject_drop():
    with pytest.raises(BusinessException):
        validate_sql("DROP TABLE products")


def test_reject_table_outside_whitelist():
    with pytest.raises(BusinessException) as exc:
        validate_sql("SELECT * FROM users")
    assert "白名单" in exc.value.message


def test_strip_markdown_fence():
    sql = validate_sql("```sql\nSELECT id FROM products LIMIT 5\n```")
    assert sql.upper().startswith("SELECT")


def test_reject_sleep_function():
    with pytest.raises(BusinessException) as exc:
        validate_sql("SELECT SLEEP(5) FROM products")
    assert "SLEEP" in exc.value.message


def test_reject_load_file_function():
    """LOAD_FILE 不能靠 \\bLOAD\\b 拦截，必须匹配函数名。"""
    with pytest.raises(BusinessException) as exc:
        validate_sql("SELECT LOAD_FILE('/etc/passwd') FROM products")
    assert "LOAD_FILE" in exc.value.message


def test_reject_benchmark_function():
    with pytest.raises(BusinessException):
        validate_sql("SELECT BENCHMARK(1000000, SHA1('x')) FROM products")


def test_reject_multi_statement():
    with pytest.raises(BusinessException):
        validate_sql("SELECT id FROM products; DROP TABLE products")


def test_reject_comma_joined_non_whitelist():
    """逗号连接同样会引入表：FROM products, users 必须拦下。"""
    with pytest.raises(BusinessException) as exc:
        validate_sql("SELECT * FROM products, users")
    assert "白名单" in exc.value.message


def test_reject_comma_joined_with_alias():
    with pytest.raises(BusinessException):
        validate_sql("SELECT p.name FROM products p, users u WHERE p.id = 1")


def test_allow_comma_joined_whitelist_tables():
    sql = validate_sql(
        "SELECT * FROM reviews r, products p WHERE r.product_id = p.id LIMIT 20"
    )
    assert "reviews" in sql.lower()


def test_extract_limit_offset_forms():
    """LIMIT offset, count 取第二个数；LIMIT n OFFSET m 取 n。"""
    assert _extract_limit("SELECT id FROM products LIMIT 100000") == 100000
    assert _extract_limit("SELECT id FROM products LIMIT 10, 200") == 200
    assert _extract_limit("SELECT id FROM products LIMIT 5 OFFSET 2") == 5
    assert _extract_limit("SELECT id FROM products") is None


def test_cap_limit_rewrites_oversize():
    assert f"LIMIT {MAX_ROW_LIMIT}" in _cap_limit(
        "SELECT id FROM products LIMIT 100000"
    )
    assert "LIMIT 10, 200" in _cap_limit("SELECT id FROM products LIMIT 10, 200")
    capped = _cap_limit("SELECT id FROM products LIMIT 10, 5000")
    assert "LIMIT 200 OFFSET 10" in capped
    assert "LIMIT 200 OFFSET" in _cap_limit(
        "SELECT id FROM products LIMIT 5000 OFFSET 2"
    )
    # 不超限原样返回
    assert (
        _cap_limit("SELECT id FROM products LIMIT 20")
        == "SELECT id FROM products LIMIT 20"
    )


@pytest.mark.parametrize("sql", [
    "SELECT (SELECT password FROM/**/users LIMIT 1) FROM products LIMIT 1",
    "SELECT u.password FROM products p JOIN reviews r ON r.product_id=p.id, users u LIMIT 1",
    "SELECT * FROM other_database.products",
    "SELECT SLEEP/**/(5) FROM products",
    "SELECT * FROM products FOR SHARE",
    "WITH p AS (SELECT * FROM products) SELECT * FROM p",
    "SELECT * FROM products UNION SELECT * FROM reviews",
    "SELECT @secret FROM products",
    "SELECT /*+ MAX_EXECUTION_TIME(0) */ * FROM products",
])
def test_reject_query_boundary_bypasses(sql):
    with pytest.raises(BusinessException):
        validate_sql(sql)


def test_outer_limit_ignores_comments_and_subqueries():
    assert _extract_limit("SELECT * FROM reviews -- LIMIT 1") is None
    sql = "SELECT * FROM reviews WHERE product_id IN (SELECT id FROM products LIMIT 1) LIMIT 100000"
    assert _extract_limit(sql) == 100000
    assert _extract_limit(_cap_limit(sql)) == MAX_ROW_LIMIT


def test_comment_removal_preserves_string_values():
    sql = validate_sql("SELECT content FROM reviews WHERE content='UPDATE; LIMIT 1' -- LIMIT 9")
    assert "UPDATE; LIMIT 1" in sql
    assert _extract_limit(sql) is None


@pytest.mark.parametrize("sql, expected", [
    ("SELECT * FROM reviews -- LIMIT 1", 50),
    ("SELECT * FROM reviews WHERE product_id IN (SELECT id FROM products LIMIT 1) LIMIT 100000", 200),
    ("SELECT * FROM reviews LIMIT 0", 0),
    ("SELECT * FROM reviews LIMIT 10, 5000", 200),
])
def test_execute_select_enforces_limit_on_real_result(sql, expected):
    """仅跳过 MySQL 专属 SET，实际执行 SELECT，验证返回数量和资源关闭。"""
    from sqlalchemy import create_engine, text
    from app.services.nl2sql import execute_select

    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE products(id INTEGER)"))
        conn.execute(text("CREATE TABLE reviews(id INTEGER, product_id INTEGER)"))
        conn.execute(text("INSERT INTO products VALUES (1)"))
        conn.execute(text("WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x<250) INSERT INTO reviews SELECT x,1 FROM n"))

    class Adapter:
        result = None

        def execute(self, statement):
            if str(statement).startswith("SET SESSION"):
                return None
            self.result = conn.execute(statement)
            return self.result

    try:
        with engine.connect() as conn:
            adapter = Adapter()
            rows, truncated = execute_select(adapter, sql)
            assert len(rows) == expected
            assert truncated is (expected > 0)
            assert adapter.result.closed
    finally:
        engine.dispose()
