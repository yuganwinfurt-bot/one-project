# 代码质量与工程审查

审查基线为 `9e61aad`。递归枚举 Git 树，共 4,374 个文件，核对五个应用目录及 Docker、Nginx、工作流和 Windows 辅助脚本。对主要 Python 源码做 AST 统计和重点链路人工阅读。导入资料目录按 Git 路径、类型和文件大小盘点。

## 优先处理的问题

| 优先级 | 源码证据与影响 | 建议及范围 |
| --- | --- | --- |
| P1 | 电商已在 `customer-service-system/backend` 和 `frontend`，容器构建仍引用额外一层同名目录。Compose 挂载、镜像发布的路径过滤及部分部署模板也使用旧路径。全新检出缺少相应 `COPY` 源文件。 [电商 Dockerfile](../docker/ecommerce.Dockerfile#L8) · [Web Dockerfile](../docker/web.Dockerfile#L7) · [Compose](../compose.yaml#L42) · [发布流程](../.github/workflows/publish-images.yml#L9) · [旧 systemd 示例](../project-hub/deploy/ecommerce-api.service#L10) | 将构建源路径、运行数据路径和发布触发路径逐项核对，先修构建与触发。运行挂载需要单独确认数据位置。约 4 个构建配置文件，部署模板另评审。 |
| P1 | 客服 `routers/agent.py` 第 22 行仍是无效的占位语句，AST 解析失败。客服入口的实际流程定义在 `main.py`，它没有导入该占位模块。静态检查整包或未来挂载此路由时会失败。 [占位模块](../ai-customer-service-agent/backend/routers/agent.py#L22) · [实际入口](../ai-customer-service-agent/backend/main.py#L683) | 查清同目录各路由文件的引用与重复内容。先处理无效占位，确认路由契约后再迁移生效代码。第一步约 1–2 个文件。 |
| P1 | 公开树中 `rag-assistant/imports/` 含 3,123 个文件、约 383 MiB，包括原始资料、派生文档、OCR 缓存、运行日志和 Windows DLL。电商另有 SQL 示例与评价图片。大文件拖慢检出，并增加资料授权、公开范围和来源核查成本。 [导入目录](../rag-assistant/imports/) · [SQL 目录](../customer-service-system/sql/) | 核对资料再发布许可与数据归属，区分可运行的最小示例与离线导入产物。对生成目录补忽略策略，将许可确认过的可选资源单独分发。删除跟踪内容前确认运行和回滚路径。 |
| P2 | 客服 `main.py` 约 1,209 行，承担启动、同步、工单路由、知识、统计和 SSE。单票工作流约 189 行，SSE 路径另有分析、检索、状态更新。两条路径可能在同类需求上产生差异。 [单票流程](../ai-customer-service-agent/backend/main.py#L743) · [流式入口](../ai-customer-service-agent/backend/main.py#L1026) | 先提取共享的工单分析、上下文准备和回复提交服务，再按工单、知识、统计拆路由，固定现有 API 和 SSE 事件格式。预计 5–8 个文件。 |
| P2 | 电商 `customer_store.py` 约 1,342 行，消息汇总约 137 行，结算约 90 行。角色检查、查询、序列化和写入事务在同一接口模块内。`customer_support.py` 借用其私有角色校验。 [买家消息](../customer-service-system/backend/app/api/customer_store.py#L432) · [结算](../customer-service-system/backend/app/api/customer_store.py#L845) · [客服 API](../customer-service-system/backend/app/api/customer_support.py) | 将消息聚合、订单结算与售后领域规则逐步移入服务层。把角色校验放到共享依赖。先冻结请求响应和事务边界。首批 3–5 个文件。 |
| P2 | Agent `create_app` 约 1,192 行，闭包内混合工作区、模型设置、会话、工具、审批、文件和静态页装配。改变依赖或路由顺序容易影响其他功能。 [应用工厂](../yugan-agent/src/yugan_agent/api.py#L143) | 先将已具备独立边界的模型、会话与文件路由抽出。用明确的依赖参数保留共享状态。保留入口签名和路由行为，约 4–6 个文件。 |
| P2 | RAG `main.py` 约 1,312 行。快照同步约 130 行，流式问答约 181 行。API 层同时承担快照文件、索引更新、SQLite 元数据与事件输出。 [快照同步](../rag-assistant/backend/app/main.py#L485) · [流式问答](../rag-assistant/backend/app/main.py#L1132) | 先把快照生命周期与问答事件生成分别移到服务层。验证中断恢复、重跑和分片引用一致性。预计 3–5 个文件。 |

## 服务耦合、状态与测试

- 电商和客服存在双向 HTTP 依赖。客服拉取业务和账号，电商自动答复准备阶段访问客服知识条目。发现的是运行时依赖，并未在本轮检查的入口间发现已生效的跨应用 Python 循环导入。建议保留明确的请求超时、消息来源 ID、已转人工状态校验和独立健康检查。 [客服同步](../ai-customer-service-agent/backend/services/ecommerce_integration.py#L172) · [电商准备回复](../customer-service-system/backend/app/services/customer_support_service.py#L98)
- 自动回复由电商后台任务驱动，失败可通过任务状态呈现。Agent 的共享客服模型及电商 LangGraph 确认检查点有进程内状态。单实例可以保留现有实现，扩展多进程前再评估持久化、幂等和恢复策略。 [回复任务](../customer-service-system/backend/app/services/customer_support_service.py#L220) · [确认恢复](../customer-service-system/backend/app/services/confirmation_service.py#L50) · [Agent 模型状态](../yugan-agent/src/yugan_agent/support_models.py#L32)
- `request.test.js` 通过 VM 和手写模块映射装载拦截器。真实导入变化后，测试在链接阶段失败，四项断言没有执行。优先让测试使用实际模块解析，保留 HTTP 响应、待办状态和跳转行为断言。模型桥接测试已覆盖错误回退等分支，后续补充跨服务认证、重复投递与转人工竞争场景。 [前端测试](../customer-service-system/frontend/tests/request.test.js#L9) · [模型桥接测试](../customer-service-system/backend/tests/test_support_model_service.py)
- `local_projects_gui.py` 和 `local_admin_*.py` 承担 Windows 本机图形界面与账号管理，依赖 Git 忽略的启动器核心或本机数据。可保留为作者辅助工具。后续若迁移到 `tools/windows/`，先清点导入、快捷方式、路径定位和本机启动脚本。 [图形入口](../local_projects_gui.py#L21) · [忽略规则](../.gitignore)
- `yugan-agent/yugan-agent/` 是保留的上游工程。当前应用入口位于 `yugan-agent/src/yugan_agent/`。两套代码的依赖、文档和测试应分别读，当前可保留来源与目录。 [当前 Agent](../yugan-agent/README.md) · [上游来源](../yugan-agent/UPSTREAM.md)

## 验证记录

基线测试使用 Node.js 24 和 Python 3.13，在隔离检出中运行。Python 测试使用进程内 SQLite 和替代凭据。

| 位置与命令 | 结果 |
| --- | --- |
| 电商前端：`npm test` | 30 通过、4 失败。VM 测试加载器缺少请求模块新增的用户状态依赖。 |
| 电商后端：`python -m pytest -q -p no:cacheprovider tests/test_sql_validate.py` | 24 通过、7 失败。部分夹具使用当前校验器已拒绝的通配列，导致断言在预期检查前失败。建议改用明确列名，让各测试继续命中其原有的风险分支。 [测试](../customer-service-system/backend/tests/test_sql_validate.py) · [校验](../customer-service-system/backend/app/services/nl2sql/validate.py) |
| 电商后端：`python -m pytest -q -p no:cacheprovider tests/test_support_model_service.py` | 9 通过，使用模拟 HTTP 响应。 |
| 仓库根目录：`docker compose --env-file .env.docker.example config --no-env-resolution --quiet` | 配置解析通过。镜像构建和容器联调留待路径修复后验证。 |

## 待评审的修改方案与回滚

| 方案 | 影响与验证 | 回滚 |
| --- | --- | --- |
| 修正 Docker 构建路径 | 修改两个 Dockerfile、发布工作流和必要的 Compose 配置。用干净检出验证构建，再用隔离的数据目录和测试库验证网关、端口与健康检查。保留现有生产数据路径，客服容器化作为单独变更。 | 对该变更做 Git revert，并使用上一条已验证的镜像标签。若以后切换挂载，在测试环境先记录旧配置和恢复顺序。 |
| 分阶段拆 Python 模块 | 按客服、电商、Agent、RAG 分成独立变更。覆盖路由契约、事务边界、重复消息、转人工、流式事件与索引恢复。第一阶段避免改数据库结构。 | 按模块 revert，保留原入口的调用契约和存储格式。 |
| 缩减可选资料和本地工具 | 先列出需要重新授权或迁移的资料，保留最小示例。只有明确需要迁移时才调整脚本入口，并验证 Windows 快捷方式、导入及发布流程。 | 使用 Git revert 恢复跟踪目录和入口。若发现真实凭据，应独立轮换并复核公开历史。 |

以上三类变更需要单独评审。当前分支的变更范围是文档。
