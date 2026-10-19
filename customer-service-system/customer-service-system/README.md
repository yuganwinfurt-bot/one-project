# 电商数据分析 Agent

基于 FastAPI + Vue3 脚手架扩展的教学项目：用自然语言提问，Agent 查询电商数据并给出诊断建议。

> 当前进度：**lesson-11 多模态**（图片描述接入语义检索）

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
- Python 3.12+（本仓库本地亦可用 3.14）
- MySQL 8.0+

## 1. 准备数据库

```sql
CREATE DATABASE ecom_analysis_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```powershell
mysql -u root -p ecom_analysis_agent < sql/ecommerce.sql
```

`sql/ecommerce.sql` 一次建好全部表：用户表（含 3 个演示账号 admin / aaa / bbb）、
商品 / 订单 / 评价三张业务表，以及 Agent 的观测与产物表（运行记录、步骤、反馈、诊断报告、预警）。
业务数据（20 商品 / 49 订单 / 46 评价）由下一节的种子脚本生成；
也可以不执行这个脚本，直接依赖后端启动时的 `create_all` 建表。

## 2. 配置后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

参考 `.env.example` 配置 `.env`（含 `DATABASE_URL`、`LLM_*`、`EMBEDDING_*` 和独立 RAG 服务地址）。改 `.env` 后需重启 uvicorn。`RAG_SYNC_TOKEN` 要与 `D:\one project\rag-assistant\backend\.env` 中的 `ECOM_RAG_SYNC_TOKEN` 一致。

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

```powershell
# 后端
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端
cd frontend
npm install
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

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| `admin` | `admin` | 管理员 |
| `aaa` | `123` | 普通用户 |
| `bbb` | `123` | 普通用户 |

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

电商平台的「语义检索」现在通过本机 RAG 服务检索。管理员首次使用或商品/评价数据变更后，点击“同步商品/评价到 RAG”；新资料会出现在独立 RAG 的“电商商品与评价”知识库中。电商平台的 Agent 对话也复用此知识库。

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

- 只读诊断工具：禁止 Agent 改订单/库存/价格/上下架
- SQL 校验使用 SQLGlot 解析查询结构，支持白名单表的 SELECT、JOIN、分组统计和子查询；本课暂不支持 CTE / UNION、跨库查询、变量、锁定读取和优化器提示。执行时最多返回 200 行。
- 人工确认采用单进程锁，避免同时确认重复执行。检查点使用 MemorySaver，重启后待确认任务失效；历史详情仅在当前检查点仍可恢复时显示确认入口。多进程部署需要共享检查点与动作幂等机制。
- 调试接口 `/api/nl2sql`、`/api/semantic` 仍可直接调 service；**对话图内查询走 MCP**
- 请勿提交含真实密钥的 `.env`
- lesson-11 已完成：图片描述接入语义检索（`app/multimodal/image_caption.py` + `index_vectors.py` 有图拼接 + `tests/test_multimodal.py`）
