# 用 Docker Compose 启动整个 one-project

此配置面向当前的 Ubuntu 服务器部署方式：Docker 管项目里的 Agent、RAG、电商 API、项目首页和前端网关；MySQL、Ollama、Nginx/HTTPS 证书以及应用数据仍由服务器现有环境提供。它不会把 MySQL 或 Ollama 的数据复制进容器。

Compose 使用 `network_mode: host`，让容器里的 API 能继续访问服务器本机的 MySQL（`127.0.0.1:3306`）和 Ollama（`127.0.0.1:11434`）。这套配置按 Ubuntu/Linux 服务器设计；Docker Desktop 4.34 及以上虽支持 host networking，但需要在设置中开启，而且与 Linux 主机网络的表现有差异。

Host networking 会让容器共享服务器网络栈，容器没有独立网络隔离。因此这套配置只适合信任的项目代码；网关和各 API 都绑定到 `127.0.0.1`，公网仍只应经过服务器现有的 HTTPS Nginx。

## 首次准备

进入服务器项目目录：

```bash
cd /home/ubuntu/one-project
```

Docker Compose 需要三个应用自己的环境文件。已有配置时保留原文件；只有文件不存在时，才从示例创建：

```bash
test -f yugan-agent/.env || cp yugan-agent/.env.example yugan-agent/.env
test -f rag-assistant/backend/.env || cp rag-assistant/backend/.env.example rag-assistant/backend/.env
test -f customer-service-system/customer-service-system/backend/.env || cp customer-service-system/customer-service-system/backend/.env.example customer-service-system/customer-service-system/backend/.env
```

检查并按当前服务器值设置这些项：

- Agent 和 RAG 使用相同的 `YUGAN_ADMIN_USERNAME`、`YUGAN_ADMIN_PASSWORD_HASH`、`YUGAN_AUTH_SIGNING_SECRET`。
- Agent 和 RAG 的浏览器来源设置应包含实际 HTTPS 域名；RAG 的 `ECOM_RAG_SYNC_TOKEN` 必须与电商 `.env` 的 `RAG_SYNC_TOKEN` 相同。
- 电商 `.env` 的 `DATABASE_URL` 指向当前 MySQL 数据库，`JWT_SECRET_KEY`、模型 Key 保持现有值。
- RAG 和 Agent 的 Ollama 地址保留 `http://127.0.0.1:11434`。

`env_file` 中有密码或 API Key，不要提交到 Git，也不要贴到聊天里。

## 先构建镜像

仓库提供的 `.env.docker.example` 使用 `18000` 段备用端口，构建和预览时不会占用当前 systemd 服务的 `8000/8001/8020/8030` 端口：

```bash
docker compose --env-file .env.docker.example build
```

构建只打包代码与前端资源，不启动容器，也不重启现有服务。需要 Docker Engine 和 Docker Compose 插件；本地 Windows 没有 Docker 命令时，应在 Ubuntu 服务器上执行。

### Windows / Docker Desktop 构建

先打开 Docker Desktop，确认引擎正在运行。若本机通过 HTTP 代理访问 Docker Hub，除 Desktop 界面中的代理设置外，也给当前 PowerShell 构建进程设置代理：

```powershell
cd "D:\one project"
$env:HTTP_PROXY = "http://127.0.0.1:7877"
$env:HTTPS_PROXY = "http://127.0.0.1:7877"
docker compose --env-file .env.docker.example build
```

`7877` 是本机当前使用的代理端口；换用其他代理时需按实际地址修改。上述环境变量只在当前 PowerShell 会话内生效，代理程序需要保持运行。

如果报错包含 `failed to fetch anonymous token` 和 Windows 的 `connectex`，先确认这个构建进程已设置代理。可用以下命令检查 Windows 到 Docker Hub 的代理连接：

```powershell
curl.exe --max-time 20 -I -x http://127.0.0.1:7877 https://auth.docker.io/token
```

出现 `200 Connection established` 后再收到 `405 Method Not Allowed`，表示已连接到服务，但该接口不支持这次测试使用的 HEAD 方法。

本步骤仅构建镜像；应用启动仍需满足下文的数据、端口及主机服务要求。

## 启动前先确认冲突

应用容器会挂载并继续使用这几个原有目录：

- `yugan-agent/workspace`、`yugan-agent/.yugan`
- `rag-assistant/backend/storage`
- `customer-service-system/customer-service-system/backend/data`、`uploads`

首次切换前，不要让容器和现有 systemd 服务同时写这些目录或同一个 MySQL 数据库。`.env.docker.example` 里的备用端口只避开端口占用，**不会隔离 MySQL 或项目数据**，所以不能在当前项目目录用它与旧服务并行运行。先构建镜像，再安排维护时段切换。

```bash
systemctl list-units --type=service --all | grep -Ei 'yugan|rag|ecommerce|project-hub'
```

停哪些服务要以服务器实际列出的单元为准。旧服务停止后，复制端口模板并改成正式端口：

```bash
cp .env.docker.example .env.docker
nano .env.docker
```

把五项端口设为 `WEB_PORT=8030`、`HUB_PORT=8031`、`AGENT_PORT=8020`、`RAG_PORT=8000`、`ECOMMERCE_PORT=8001`。若服务器项目目录所有者不是 UID/GID 1000，再把 `DOCKER_UID`、`DOCKER_GID` 加到 `.env.docker` 并设成该用户的数字 ID。

切换期间，现有 HTTPS Nginx 应将 `/`、`/api/`、`/agent/`、`/rag/`、`/ecommerce/`、`/uploads/` 统一转发到 `127.0.0.1:8030`。当前外层 Nginx 若为这些路径配置了更具体的独立转发规则，它们会优先于 `/`，切换前应检查并调整。不要把 8000、8001、8020、11434 或 3306 暴露到公网。

## 启动和管理

确认旧服务已停止、原数据目录仍在后，再在维护时段启动正式端口配置：

```bash
docker compose --env-file .env.docker config
docker compose --env-file .env.docker up -d
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs -f --tail=100
```

`.env.docker.example` 的 18000 段端口只适合隔离的测试副本；正式服务器应按上面的步骤改成正式端口。`.env.docker` 已被 Git 忽略，不要提交。外层 HTTPS Nginx 的反代地址也应指向 `127.0.0.1:8030`。

常用命令：

```bash
docker compose --env-file .env.docker logs -f yugan-agent
docker compose --env-file .env.docker restart yugan-agent
docker compose --env-file .env.docker down
```

`down` 会停止并移除容器，但不会删除上面挂载的项目数据目录。不要加 `-v`；这套 Compose 没有管理 MySQL/Ollama 数据的 Docker 卷。

## 公开审批权限提示

当前 Agent 源码包含你之前要求的公开一键批准逻辑。公开访客的任务可能因此自动执行文件改动或命令操作；公网开放前请确认 Agent 的工具白名单、工作区范围和可执行命令限制符合你的预期。Docker 不会改变这些权限规则。
