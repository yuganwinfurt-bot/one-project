# 电商数据分析 Agent

基于 FastAPI 与 Vue 3 的电商管理和智能分析应用。提供商城、运营工作台、订单、评价与售后管理，也可通过自然语言查询业务数据。

[线上入口](https://www.yuganwinfurt.top/ecommerce/) · [项目总览](../README.md) · [本地开发与联动](../docs/LOCAL_DEVELOPMENT.md#电商)

## 技术栈

| 端 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Element Plus + Axios |
| 后端 | FastAPI + SQLAlchemy + JWT |
| 数据库 | MySQL 8 |
| 向量库 | 独立本地 RAG 知识库（电商语义检索与 Agent 共用） |
| 编排 | LangGraph |
| 工具协议 | MCP（官方 SDK 的 FastMCP，stdio 子进程） |
| 大模型 / 向量模型 | OpenAI 兼容接口（可配置切换） |
| 图片描述 | OpenAI 兼容 vision（Chat Completions + base64 data URL） |

## 环境要求

- Node.js：见 `frontend/package.json` 的 `engines`（建议 Node 22 LTS）
- Python 3.12+
- MySQL 8.0+

## 1. 准备数据库

在本机 MySQL 创建独立开发库。

```sql
CREATE DATABASE ecom_analysis_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

后端首次启动时会创建当前模型所需的表。若需要仓库提供的 SQL 快照用于演示，先确认目标是可丢弃的开发库。该文件包含 DROP TABLE 语句。

```bash
mysql -u root -p ecom_analysis_agent < sql/ecommerce.sql
```

## 2. 配置后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

参考 `.env.example` 配置 `.env`（含 `DATABASE_URL`、`LLM_*`、`EMBEDDING_*` 和独立 RAG 服务地址）。改 `.env` 后需重启 uvicorn。`RAG_SYNC_TOKEN` 要与 RAG 后端 `.env` 中的 `ECOM_RAG_SYNC_TOKEN` 一致。

## 3. 导入示例数据

**清空范围**：商品、订单、评价，以及 Agent 的产物与观测数据——诊断报告、预警通知、运行记录、运行步骤、点踩点赞反馈。
**保留**：用户表（演示账号清掉就没法登录）。
只在教学库执行；清空与重新插入放在同一事务，失败会回滚。重跑后评价 id 会变，因此向量库需要重建（见下一行的 `index_vectors`）。

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m data.seed.seed_ecommerce
python -m data.seed.index_vectors
```

## 4. 启动后端 / 前端

以下两组命令分别在项目目录下的两个终端执行。

```powershell
# 后端
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

```

```powershell
# 前端
cd frontend
npm ci
npm run dev
```

MCP Server **不必单独启动**：对话跑图时，主程序会以 stdio 子进程方式拉起 `python -m app.mcp_server.server`。

可选手动验证 Server：

```powershell
cd backend
python -m app.mcp_server.server
# 等待 stdin；Ctrl+C 退出。正常教学流程不手动跑。
```

## 5. 演示账号

后台与买家有独立的登录入口。后台管理使用测试库中的管理员或运营账号，买家端可使用页面显示的专用演示买家或注册一个测试买家。需要预置后台账号时，先核对 `sql/ecommerce.sql`，仅导入独立的测试库。登录页会按当前启用账号和演示凭据状态显示可用入口。

## 6. 如何验证

### 单测

```powershell
cd backend
python -m pytest tests/ -q
```

前端业务错误处理测试与构建：

```powershell
cd frontend
npm test
npm run build
```

回归测试使用隔离数据库和替代模型，覆盖 SQL 越界与行数限制、并发确认、回答失败后的确认恢复、证据合并、JWT 有效期、种子事务和反馈权限；不依赖真实模型调用。

### lesson-11：多模态（图片描述接入语义检索）

1. 有图评价入库：`python -m data.seed.index_vectors`（有图自动调图片描述拼进文档，无 Key/失败时降级纯文本）
2. 语义检索验证：`POST /api/semantic/search` 用图片内容词查询（如“鞋底开胶”），应命中带图评价（含 `【晒图内容】`）
3. 单测：`python -m pytest tests/test_multimodal.py -q`

电商平台的「语义检索」现在通过本机 RAG 服务检索。管理员可以手动同步电商业务快照至独立 RAG。电商助手还可检索同步后的客服知识库。

### lesson-10：多智能体协作

1. 对话提问后，过程区应依次出现 **调度 → 查询分析 Agent → 调度交接 → 报告决策 Agent**
2. SSE 事件含 `agent_step`（`agent` / `agent_label` / `node`）
3. 单测：`python -m pytest tests/test_multi_agent.py tests/test_langgraph.py -q`

流程图（教学重点）：

```text
START → scheduler_start
     → 查询分析 Agent（route / query / deepen / evidence）
     → scheduler_handoff
     → 报告决策 Agent（decide / confirm / execute）
     → END
```

### lesson-09：MCP

过程区可见「经 MCP 查 MySQL / Chroma / 历史运行」；单测 `tests/test_mcp.py`。

### lesson-08：运行历史与反馈

侧栏「运行历史」+ 对话「有用/没用」；接口见 `/api/observability/*`。

## 目录结构（截至 lesson-10）

```text
backend/app/agent/
  analysis_agent.py   # 查询分析 Agent（薄包装）
  decision_agent.py   # 报告决策 Agent（薄包装）
  scheduler.py        # 调度节点
  graph.py / nodes.py # 图组装 + 具体节点
backend/app/multimodal/       # lesson-11：图片描述（image_caption.py）
backend/app/mcp_server/     # FastMCP Server + 三个工具
backend/app/mcp_client/     # 主程序 stdio 客户端
backend/app/observability/  # 运行记录 + 反馈
```

## 说明

- 新订单通知：立即购买和购物车结算成功后，每个新订单在同一事务内写入一条“新订单待发货”商家通知。后台铃铛、消息中心显示未读提醒；已打开的运营/管理员页面约每 5 秒同步，新收到的订单弹窗可点击定位，初次加载不重弹历史订单。发货或转入售后后该提醒自动已读；不对历史订单批量补发通知。
- 诊断查询按只读规则执行。受支持的业务写入按权限生成操作计划，等待对应用户确认后执行。
- SQL 校验使用 SQLGlot 解析查询结构，支持白名单表的 SELECT、JOIN、分组统计和子查询；本课暂不支持 CTE / UNION、跨库查询、变量、锁定读取和优化器提示。执行时最多返回 200 行。
- 人工确认采用单进程锁，避免同时确认重复执行。检查点使用 MemorySaver，重启后待确认任务失效；历史详情仅在当前检查点仍可恢复时显示确认入口。多进程部署需要共享检查点与动作幂等机制。
- 调试接口 `/api/nl2sql`、`/api/semantic` 仍可直接调 service；**对话图内查询走 MCP**
- 请勿提交含真实密钥的 `.env`
- lesson-11 已完成：图片描述接入语义检索（`app/multimodal/image_caption.py` + `index_vectors.py` 有图拼接 + `tests/test_multimodal.py`）
