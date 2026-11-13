# 系统架构与服务边界

[总览与架构图](../README.md#系统架构) · [本地开发](LOCAL_DEVELOPMENT.md)

| 应用 | API、业务与前端入口 | 数据与状态 |
| --- | --- | --- |
| 电商 | [FastAPI 应用](../customer-service-system/backend/app/main.py)注册 `api/` 路由，`services/` 承载交易、分析、客服与确认逻辑，`agent/` 负责图编排。Vue 页面位于 `frontend/src/`。 | SQLAlchemy 使用 `DATABASE_URL` 连接 MySQL。商品、订单、售后、会话、任务和运行记录由电商维护。部分 MCP 检索使用电商自己的 Chroma。 |
| 客服 | [FastAPI 应用](../ai-customer-service-agent/backend/main.py)注册工单、分析、知识与统计路由。`services/` 包含电商同步、身份校验、知识检索、回复和汇总。Next.js 页面位于 `frontend/app/`。 | SQLite 保存工单、消息、知识条目和电商映射。外部工单以电商业务状态为准，本地同步代码维护消息关联与投递记录。 |
| Agent | [API 工厂](../yugan-agent/src/yugan_agent/api.py)装配认证、会话、工作区、模型、审批、文件与工具。`agent.py` 驱动多步调用，`web/` 提供浏览器界面。 | `SQLiteMemory` 管理会话记录，文件放在工作区。共享客服模型当前保存在进程状态中。 |
| RAG | [FastAPI 应用](../rag-assistant/backend/app/main.py)提供项目、会话、文档、检索和同步接口，`rag/` 负责解析、切分、索引与问答。Vue 页面位于 `frontend/src/`。 | SQLite 保存元数据、消息和同步任务，源文件及 Chroma 向量索引存放在配置的数据目录。 |
| 作品集首页 | [Vue 项目配置](../project-hub/src/projects.js)定义页面入口，[首页 API](../project-hub/hub_api.py)提供静态回退、健康检查和身份代理。 | 首页代理身份状态、登录与退出，由 Agent 校验身份。 |

## 跨服务调用

| 方向 | 用途与代码入口 |
| --- | --- |
| 客服 → 电商 | 校验管理员和运营身份，拉取咨询与售后记录，回传人工回复或售后动作。同步依靠 HTTP 请求和本地记录。 [客服身份](../ai-customer-service-agent/backend/services/staff_auth.py) · [电商接入](../ai-customer-service-agent/backend/services/ecommerce_integration.py) · [电商桥接 API](../customer-service-system/backend/app/api/support_bridge.py) |
| 电商 → 客服 | 买家自动回复准备阶段通过内部接口检索客服知识条目。 [回复任务](../customer-service-system/backend/app/services/customer_support_service.py) · [内部知识接口](../ai-customer-service-agent/backend/services/agent_model_bridge.py) |
| 电商 → Agent | 后台任务请求共享客服模型，调用携带服务令牌。Agent 校验回环来源与令牌，再根据已选配置请求模型。 [电商模型适配](../customer-service-system/backend/app/services/support_model_service.py) · [Agent 客服模型](../yugan-agent/src/yugan_agent/support_models.py) |
| 电商、客服 → RAG | 电商助手可检索两套业务知识库。电商和客服分别从各自的同步入口提交快照，RAG 按来源处理索引与任务进度。 [电商检索](../customer-service-system/backend/app/services/semantic_search_service.py) · [客服快照](../ai-customer-service-agent/backend/services/rag_integration.py) · [RAG 任务](../rag-assistant/backend/app/ecommerce_sync_jobs.py) |
| Agent → RAG | Agent 根据会话选中的知识库检索片段，用于生成回答。 [检索桥接](../yugan-agent/src/yugan_agent/rag_bridge.py) |
| 首页 → Agent | 首页后端转发身份状态、登录和退出，保留同源页面的认证流程。 [身份代理](../project-hub/hub_api.py) |

商城自动应答由服务端运行。客服工作台也可先向自己的后端请求上下文，由浏览器按 Agent 所选模型生成回复，再提交给客服后端保存。RAG 支持后端流式问答，以及由浏览器获取检索资料、调用所选模型和保存答案的流程。SSE 用于传送流式事件，商城会话可通过轮询刷新状态。MCP 是电商后端与查询工具之间的 stdio 调用。

## 失败与状态处理

- 电商客服任务记录请求状态。模型超时、连接或配置错误转为可展示的提示。部分 Agent 连接失败场景可使用电商已配置的备用模型。提交回复前复核会话状态和最新消息，避免把过期回复写入已转人工的会话。
- 电商操作先生成计划。确认接口按用户和会话读取检查点，再恢复图执行。当前确认状态依赖进程内检查点，多进程和重启约束见[审查报告](CODE_QUALITY_REPORT.md)。
- RAG 用分片内容与向量模型标识判断可复用的向量。快照提交及任务状态与索引更新分层，失败可通过同步任务结果定位。

## 部署边界

线上入口按首页、`/ecommerce/`、`/support/`、`/agent/` 和 `/rag/` 提供。仓库中的 Nginx 模板定义首页、Agent、RAG、电商及电商上传资源路由。它由 Compose 的 `web-gateway` 镜像使用，Compose 还编排首页、Agent、RAG 和电商 API。MySQL、Ollama 和外层 HTTPS 入口由宿主机提供。

客服线上入口属于独立部署范围。仓库的 `project-hub/deploy/` 提供 Nginx、systemd 和发布脚本示例，当前 Compose 有电商路径不一致的问题。GitHub Actions 负责向 Docker Hub 发布镜像。更多信息见[Docker 说明](../DOCKER.md)。
