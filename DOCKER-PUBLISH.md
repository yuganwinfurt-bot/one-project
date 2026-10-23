# 整个项目一次上传到 Docker Hub

## 同一个项目、同一个镜像仓库

五个服务统一发布到 **yuganwinfurt/one-project**，用标签区分：

| 服务 | 默认发布地址 |
|---|---|
| Agent | `yuganwinfurt/one-project:yugan-agent-latest` |
| RAG | `yuganwinfurt/one-project:rag-assistant-latest` |
| 电商客服 | `yuganwinfurt/one-project:ecommerce-latest` |
| 项目首页 | `yuganwinfurt/one-project:project-hub-latest` |
| 网页网关 | `yuganwinfurt/one-project:web-gateway-latest` |

仓库页面：https://hub.docker.com/r/yuganwinfurt/one-project/tags

这仍然是五个服务镜像，由 Compose 统一运行。发布时会临时给现有镜像添加上传名称，再上传到同一个仓库。上传成功后自动清理这些本地上传名称，保留原来的五个 `one-project/<服务名>:local` 镜像；云端镜像保留。正在被容器引用的上传名称，以及指向不同镜像的名称，会保留并在窗口中说明。

## 方法一：双击打开窗口，批量发布

1. 打开 Docker Desktop，确认 Linux 引擎已启动、账号已登录为 `yuganwinfurt`。
2. 双击项目根目录的 **一键上传Docker镜像.bat**。
3. 窗口中的仓库保持 `yuganwinfurt/one-project`，版本保持 `latest`。
4. **发布当前已经构建的镜像**：保持“发布前重新构建”未勾选。源镜像是当前本机的五个 `one-project/<服务名>:local`。
5. **源码有修改时**：勾选“发布前重新构建”。构建成功后也会更新本机的 `one-project/<服务名>:local` 标签，供下次继续发布。
6. 点击 **发布全部五个镜像**，等待窗口显示“发布完成”。
7. 回到 Docker Desktop 的“镜像 → 我的镜像”，即可查看 `yuganwinfurt/one-project`。仓库不存在时，首次成功推送会按账号默认隐私设置创建；公开或私有以 Docker Hub 的实际设置为准。

想保留某个版本，可把版本标签改为 `v1.0.0` 等，此时发布地址例如 `yuganwinfurt/one-project:ecommerce-v1.0.0`。再次发布同一标签会更新该标签指向的镜像。

窗口会自动处理所有镜像的标签与上传，不需要在 Portainer 里逐个操作。重建时，构建进程会尝试继承 Windows 系统代理；镜像上传沿用 Docker Desktop 配置。

启动时会保留一个控制台窗口，用于显示启动错误；关闭发布窗口后，控制台会自动退出。入口不再使用隐藏窗口或 `Bypass` 模式，仅为本次 PowerShell 进程使用 `RemoteSigned`，不修改系统的执行策略。该策略允许本机编写的脚本运行，来自互联网的未签名脚本可能会被拒绝，参见 [Microsoft 执行策略说明](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-5.1)。

常见提示：

- 没有上传权限：确认 Docker Desktop 当前账号、仓库前缀一致，然后重新发布。
- 缺少本地镜像：勾选“发布前重新构建”。
- 上传中断：部分镜像可能已成功；修复网络后重新点发布，Docker 会复用已上传的镜像层。
- 本地名称清理失败：上传成功后，个别上传名称可能仍显示在 Local 中。窗口会说明原因，不会强制删除镜像或容器；相同镜像 ID 的名称共用同一份镜像内容。
- 发布过程中请等待完成后关闭窗口。发布只构建/上传镜像，不启动或重启应用容器。

## 方法二：像 GitHub 一样，推送代码后自动上传镜像

仓库中的 `.github/workflows/publish-images.yml` 提供自动发布：

**GitHub Desktop 提交并 Push origin → GitHub 自动构建五个镜像 → 全部上传到同一个 Docker Hub 仓库。**

第一次需要配置一次凭据：

1. 在 Docker 账号设置的 **Personal access tokens** 中创建一个有镜像仓库读取、写入权限的 Token；无需删除权限。
2. 在 GitHub 项目网页进入 **Settings → Secrets and variables → Actions → Secrets → New repository secret**。
3. 名称填写 **DOCKERHUB_TOKEN**，值填写刚生成的 Docker Token。Token 仅填写在 GitHub 的 Secret 框，不放进代码、聊天或 `.env.example`。
4. 当前用户名默认是 `yuganwinfurt`。换账号时，在同一页面的 **Variables** 中添加 `DOCKERHUB_USERNAME`；自定义仓库时添加 `DOCKERHUB_REPOSITORY`，值例如 `其他用户名/one-project`。
5. 在 GitHub Desktop 中提交这些发布文件，并点 **Push origin**。
6. 进入 GitHub 项目的 **Actions → Publish all Docker images** 查看进度。也可点 **Run workflow** 手动发布，并填写版本号。

没有配置 `DOCKERHUB_TOKEN` 时，正常代码推送会跳过镜像发布并显示提示；手动点 Run workflow 则会明确报告缺少 Token。

自动发布仅由 `main` 分支中应用代码、Docker 构建文件等相关改动触发，不由 Pull Request 触发。每次自动发布都会更新五个 `服务名-latest` 标签，并额外保留 `服务名-sha-提交号` 标签；手动指定版本时则保留指定的版本标签。

这些工作流只发布镜像，不连接服务器、不部署或重启服务器上的程序。当前构建目标为 `linux/amd64`，对应你现在的 Intel/AMD 电脑和同架构 Linux 服务器；ARM 电脑需要另行准备相应架构镜像。

## 对方如何统一下载并启动

`compose.publish.yaml` 既能独立用于构建/上传，也能叠加到原 `compose.yaml` 上，将五个服务的镜像地址统一指向 Docker Hub：

```bash
docker compose --env-file .env.docker.example -f compose.yaml -f compose.publish.yaml pull
docker compose --env-file .env.docker.example -f compose.yaml -f compose.publish.yaml up -d --no-build
```

这两条仅用于已经按 `DOCKER.md` 准备好的目标电脑。使用固定版本时，在 `.env.docker.example` 对应的实际环境配置中设置 `IMAGE_VERSION=v1.0.0`；换仓库时设置 `DOCKER_HUB_REPOSITORY=用户名/仓库名`。

发布到同一仓库不会自动迁移运行数据。目标电脑仍需准备应用自己的 `.env`、MySQL、Ollama、所用模型以及需要迁移的资料；这些准备完成后才能完整使用项目。

## 参考

- Docker Compose 批量上传：https://docs.docker.com/reference/cli/docker/compose/push/
- Docker 官方 GitHub Actions：https://docs.docker.com/build/ci/github-actions/
- Docker Hub Token：https://docs.docker.com/security/access-tokens/personal-access-tokens/
- GitHub 仓库 Secret：https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
