"""FastMCP Server（stdio）：注册三个只读查询工具。

启动方式（由主程序 MCP 客户端拉起子进程，一般不用手动跑）：
    python -m app.mcp_server.server

教学重点：
- 工具实现仍复用现有 service，但 LangGraph 节点只通过 MCP 调用
- 传输用 stdio，不占端口、不单独部署
"""

from mcp.server.fastmcp import FastMCP

from app.mcp_server.tools_chroma import query_chroma
from app.mcp_server.tools_logs import query_logs
from app.mcp_server.tools_mysql import query_mysql, execute_mysql_select

# 服务名会出现在 MCP 握手信息里，方便日志辨认
mcp = FastMCP("ecom-analysis-tools")


@mcp.tool()
def query_mysql_tool(question: str) -> str:
    """查 MySQL：把自然语言问题转成只读 SQL 并执行，返回 JSON。"""
    return query_mysql(question)


@mcp.tool()
def execute_mysql_select_tool(sql: str) -> str:
    """校验并执行一条只读 SELECT，不调用模型。"""
    return execute_mysql_select(sql)


@mcp.tool()
def query_chroma_tool(
    query: str, top_k: int = 8, product_ids: list[int] | None = None,
    doc_types: list[str] | None = None,
) -> str:
    """按商品与资料类型筛选业务知识，再进行语义检索，返回 JSON。"""
    return query_chroma(query, top_k=top_k, product_ids=product_ids, doc_types=doc_types)


@mcp.tool()
def query_logs_tool(keyword: str = "", limit: int = 5) -> str:
    """查日志：读取本地观测表中的历史运行记录，返回 JSON。"""
    return query_logs(keyword=keyword, limit=limit)


def main() -> None:
    """以 stdio 方式运行 MCP Server（阻塞）。"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
