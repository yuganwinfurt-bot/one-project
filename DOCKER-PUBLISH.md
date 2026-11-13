# Docker Hub 镜像发布

[Compose 服务范围与当前限制](DOCKER.md) · [发布工作流](.github/workflows/publish-images.yml)

仓库把 `yugan-agent`、`rag-assistant`、`ecommerce`、`project-hub`、`web-gateway` 五个镜像放在同一 Docker Hub 仓库中。默认仓库是 `yuganwinfurt/one-project`，例如 `ecommerce-latest` 和 `web-gateway-latest`。当前电商构建路径需先修复，见[审查报告](docs/CODE_QUALITY_REPORT.md)。

## GitHub Actions

1. 在仓库 **Settings → Secrets and variables → Actions** 设置 `DOCKERHUB_TOKEN`，在 Variables 中按需配置 `DOCKERHUB_USERNAME` 和 `DOCKERHUB_REPOSITORY`。
2. 在 **Actions → Publish all Docker images** 手动运行并填写版本。工作流也会在 `main` 上符合路径过滤的推送时运行。
3. 在 Actions 检查各服务的构建日志及镜像标签。矩阵目标为 `linux/amd64`。非 `latest` 版本还会更新相应服务的 `latest` 标签。

发布的产物是容器镜像。站点部署、数据迁移和服务切换属于目标环境的单独操作。未配置发布令牌时，推送触发的任务会跳过发布，手动发布会报告配置缺失。

## 本机发布与拉取

Windows 界面工具的真实入口是 [docker/publish-images.ps1](docker/publish-images.ps1)，在已登录 Docker Hub 的 Docker Desktop 上运行。路径修复并构建后，可从仓库根目录执行 `powershell -File docker/publish-images.ps1` 打开界面。

拉取镜像时可用 [compose.publish.yaml](compose.publish.yaml) 覆盖镜像地址。目标环境仍需准备应用环境文件、主机服务与独立数据。待 Compose 路径核对后，在目标测试环境使用：

```bash
docker compose --env-file .env.docker.example -f compose.yaml -f compose.publish.yaml pull
docker compose --env-file .env.docker.example -f compose.yaml -f compose.publish.yaml up -d --no-build
```
