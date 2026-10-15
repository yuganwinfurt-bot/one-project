# 快速开始

在项目目录的 PowerShell 中运行：

```powershell
cd 'D:\one project\yugan-agent'
& 'C:\Users\yugan\.local\bin\uv.exe' --cache-dir .uv-cache sync --extra dev
.\.venv\Scripts\python.exe -m yugan_agent demo
```

`demo` 先执行真实的 Python 计算函数，再运行农业工作流。默认 `mock` 模式不连接模型服务，工作流输入是固定虚构数值。

启动浏览器操作页：

```powershell
.\.venv\Scripts\python.exe -m yugan_agent serve --port 8020
```

打开 <http://127.0.0.1:8020/>；API 文档在 <http://127.0.0.1:8020/docs>。默认只允许本机访问。如果 8020 被占用，可改成 `--port 8021`。

主要命令：

```text
demo                     无 Key 演示
run "任务" --session 名称    执行任务；加 --json 输出结构化结果
chat --session 名称        连续对话；/new 新会话，/exit 退出
tools                    列出已注册工具
history                  列出会话
history --session 名称     查看消息与状态
workflow demo            运行内置农业工作流
workflow demo --graph    输出 Mermaid 流程图
serve --port 8020        运行浏览器页和 API
```

同名 session 会继续之前的历史，数据存在 `.yugan/memory.db`。上下文裁剪不删除数据库里的原文。

浏览器页面默认以游客身份使用。管理员账号由 `.env` 中的 `YUGAN_ADMIN_USERNAME`、`YUGAN_ADMIN_PASSWORD_HASH` 和至少 32 个字符的 `YUGAN_AUTH_SIGNING_SECRET` 配置；RAG 后端需使用同一组值。模型设置里的 API Key 保存在该浏览器的 `localStorage`，浏览器直接访问模型接口，Agent 后端不会接收或保存 Key。生产部署请使用 HTTPS，并确认模型服务允许网页跨源请求。

如果 PowerShell 把中文显示为乱码，可先执行 `$env:PYTHONIOENCODING='utf-8'`，再运行命令。展示乱码不代表数据库损坏。
