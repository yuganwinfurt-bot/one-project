# 本地开发与运行

从本仓库根目录开始。建议使用 Python 3.12+、Node.js 22.18+（22 系列）或 24.12+、npm。电商需要 MySQL，RAG 向量化需要可访问的 Ollama。命令适用于 Linux 或 Windows 上的 WSL（Bash）。若在原生 PowerShell 运行，复制配置请用 `if (-not (Test-Path .env)) { Copy-Item .env.example .env }`，虚拟环境解释器路径改为 `.\.venv\Scripts\python.exe`。

每个代码块在独立终端运行，前端和后端分别保持运行。复制示例配置前检查目标文件是否存在。示例中的数据库连接、模型凭据和令牌由本机填写。电商启动会建表、补齐部分旧字段并初始化部分数据，使用独立的开发数据库。

## Agent

```bash
cd yugan-agent
test -f .env || cp .env.example .env
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m yugan_agent serve --host 127.0.0.1 --port 8020
```

示例的 `YUGAN_PROVIDER=mock` 可用于无模型凭据的基础体验。真实对话按[模型配置](../yugan-agent/README.md#接入真实模型)设置。电商前端使用下表端口时，将 `YUGAN_ECOMMERCE_WEB_ORIGIN` 设为 `http://127.0.0.1:35173`。

## RAG

启动 Ollama 后下载 `bge-m3`。使用后端 Ollama 问答时另下载 `OLLAMA_CHAT_MODEL` 对应模型。浏览器模型流程可连接 Agent，向量化仍由 RAG 后端完成。

```bash
cd rag-assistant/backend
test -f .env || cp .env.example .env
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd rag-assistant/frontend
npm ci
npm run dev
```

## 电商

创建独立 MySQL 开发库，在 `backend/.env` 填 `DATABASE_URL` 和独立的 `JWT_SECRET_KEY`，再启动 API。模型 Key、Embedding Key 和外部 RAG 配置按体验功能填写。可选种子脚本会清理并重建部分业务表的数据，仅对可丢弃的开发库使用。管理员或运营账号准备见[电商说明](../customer-service-system/README.md#5-演示账号)。

```bash
cd customer-service-system/backend
test -f .env || cp .env.example .env
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# 填好 .env 后启动
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

```bash
cd customer-service-system/frontend
npm ci
npm run dev
```

## 客服工单

电商 API 先启动。工作台登录复用电商的管理员或运营账号。首次启动用本地 `tickets.db`，配置示例可从[客服环境文件](../ai-customer-service-agent/backend/.env.example)复制。需要电商联动时，补齐下文的配对配置并重启本地服务。

```bash
cd ai-customer-service-agent/backend
test -f .env || cp .env.example .env
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8002
```

```bash
cd ai-customer-service-agent/frontend
npm ci
npm run dev -- --hostname 127.0.0.1 --port 3000
```

本机默认 API 地址是 `http://127.0.0.1:8002`。如修改地址，在客服前端设置 `NEXT_PUBLIC_API_URL`。完整说明见[客服 README](../ai-customer-service-agent/README.md)。

## 作品集首页

```bash
cd project-hub
npm ci
npm run build
python -m venv .venv
.venv/bin/python -m pip install -r deploy/requirements.txt
.venv/bin/python -m uvicorn hub_api:app --host 127.0.0.1 --port 8030
```

## 配置配对与检查

| 需求 | 本地配置 |
| --- | --- |
| 电商与客服互通 | 电商 `SUPPORT_BRIDGE_TOKEN` 与客服 `ECOMMERCE_BRIDGE_TOKEN` 使用同一个本地随机值。电商 `SUPPORT_OPERATOR_ID` 指向实际启用的电商运营或管理员账号。默认接口为 `8001` 和 `8002`。 |
| 商城 AI 客服 | Agent 的 `YUGAN_SUPPORT_SERVICE_TOKEN` 与电商 `SUPPORT_BRIDGE_TOKEN` 同值。保持电商 `AGENT_SERVICE_URL=http://127.0.0.1:8020`。管理员在 Agent 控制台选择共享客服模型，Agent 重启后可能需要重选。 |
| 同步业务知识 | 电商 `RAG_SYNC_TOKEN` 对应 RAG 的 `ECOM_RAG_SYNC_TOKEN`。客服与 RAG 的 `SUPPORT_RAG_SYNC_TOKEN` 同值。使用各自页面的同步入口。 |
| 首页与 RAG 管理员 | 首页通过 `PROJECT_HUB_AGENT_API_URL` 请求 Agent。Agent 和 RAG 的管理员身份配置与签名设置需要匹配，浏览器来源按各自 `.env.example` 设置。 |

| 服务 | 本机页面 | 检查方式 |
| --- | --- | --- |
| 首页 | <http://127.0.0.1:8030/> | `curl -fsS http://127.0.0.1:8030/api/health` |
| 电商 | <http://127.0.0.1:35173/> | `curl -fsS http://127.0.0.1:8001/` |
| 客服 | <http://127.0.0.1:3000/> | 打开登录页，使用电商后台账号登录并加载工单列表。 |
| Agent | <http://127.0.0.1:8020/> | `curl -fsS http://127.0.0.1:8020/health` |
| RAG | <http://127.0.0.1:4173/rag/> | `curl -fsS http://127.0.0.1:8000/api/health` |

完整联调时，从商城发一条测试咨询，查看自动回复及客服工作台的工单状态，再验证转人工后的消息投递。Agent 的 `/api/support-model/status` 可检查是否选中共享模型，实际收发一条消息可验证服务令牌、模型调用与回复保存。

Docker 构建限制和容器覆盖范围见[Docker 说明](../DOCKER.md)。Windows 图形启动器需要[本机专用文件](../本地启动说明.md)。
