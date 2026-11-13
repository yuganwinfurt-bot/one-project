# Docker Compose 说明

[本地开发与运行](docs/LOCAL_DEVELOPMENT.md) · [镜像发布](DOCKER-PUBLISH.md)

当前 GitHub 版本的电商源码位于 `customer-service-system/backend/` 和 `customer-service-system/frontend/`，两个 Dockerfile 和 Compose 仍引用多一层同名目录的旧路径。全新检出会在读取旧环境文件或构建 `COPY` 阶段遇到缺失路径。本地开发请使用各应用的启动命令。部署配置待修项、验证与回滚见[审查报告](docs/CODE_QUALITY_REPORT.md)。

## 服务范围

| Compose 服务 | 职责 | 示例备用端口 |
| --- | --- | --- |
| `web-gateway` | Nginx 网关，处理首页、Agent、电商、RAG 和上传资源路径 | 18030 |
| `project-hub` | FastAPI 首页和身份代理 | 18031 |
| `yugan-agent` | Agent API 和网页 | 18020 |
| `rag-assistant` | RAG API，前端静态文件由网关提供 | 18000 |
| `ecommerce` | 电商 API，前端静态文件由网关提供 | 18001 |

现有配置编排五个容器。客服工单系统独立启动，Compose 和网关模板中未定义客服服务。宿主机提供 MySQL、Ollama 和外层 HTTPS。服务使用 host networking 并绑定回环地址，部署前需核对目标 Docker 引擎的 host networking 支持。备用端口避开常用服务端口，测试还需独立的数据库和数据目录。

## 读取配置

使用支持 `--no-env-resolution` 的 Docker Compose，在仓库根目录运行以下命令验证结构和列出服务。该检查跳过应用环境文件读取。

```bash
docker compose --env-file .env.docker.example config --no-env-resolution --quiet
docker compose --env-file .env.docker.example config --no-env-resolution --services
```

`.env.docker.example` 提供端口模板。应用配置分别使用 Agent、RAG 后端、电商后端的 `.env.example`。模型凭据、数据库连接和服务令牌在运行环境中填写。RAG Compose 将 Agent 的状态目录只读挂载，用于读取模型配置。变更前逐项核对 [Compose](compose.yaml)、[Nginx 模板](docker/nginx.conf.template)和[服务配置配对](docs/LOCAL_DEVELOPMENT.md#配置配对与检查)。

## 构建后的检查

待路径修复通过审查后，在具备独立测试数据的环境执行 `docker compose --env-file .env.docker.example build`。容器启动后用 `docker compose ps`、`docker compose logs --tail=50` 和网关的 `/api/health` 检查。各应用健康检查见[本地开发文档](docs/LOCAL_DEVELOPMENT.md#配置配对与检查)。
