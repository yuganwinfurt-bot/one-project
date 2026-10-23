# yugan-agent

一个可以在本机运行的 Python Agent 项目：**Agent 决策、工具调用、JSON 工作流、会话记忆**，并提供命令行与中文浏览器操作页。

本仓库基于 [caizizhen/Cai_Agent](https://github.com/caizizhen/Cai_Agent) 的 Git 历史建立。上游原有的终端编程 Agent 仍在 `yugan-agent/`；本项目新增的轻量通用框架位于 `src/yugan_agent/`，默认运行命令为 `yugan-agent`。见 [上游来源说明](UPSTREAM.md) 与 [开发计划](PLAN.md)。

## 5 分钟运行

Windows 桌面上可以直接双击 **启动 yugan-agent**：它会打开一个命令行窗口，服务就绪后自动打开浏览器 `http://127.0.0.1:8020/`。用完在命令行窗口按 `Ctrl+C` 或关闭窗口即可停止。请勿同时启动两次，否则第二次会提示 8020 端口被占用。如果桌面快捷方式丢失，在项目目录运行 `powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_shortcuts.ps1` 即可重建。初次运行若缺少 `.venv`，先执行下面的依赖安装命令。

在 Windows PowerShell 打开项目目录：

```powershell
cd 'D:\one project\yugan-agent'
& 'C:\Users\yugan\.local\bin\uv.exe' --cache-dir .uv-cache sync --extra dev
.\.venv\Scripts\python.exe -m yugan_agent serve --port 8020
```

浏览器打开 **http://127.0.0.1:8020/**。当前 Web 页面会先进入“模型设置”，填写 API 模型的 Key、Base URL 和模型 ID；本机或服务器 Ollama 可从聊天框的模型菜单选择。`demo` 命令才使用离线演示模式。使用 `Ctrl+C` 停止服务。若校园网无法下载依赖，可为 uv 配置可信镜像；不要修改已有的 `D:\python3.11.9` 环境。

已安装依赖时也可直接用 `yugan-agent` 命令。项目要求 Python 3.11+；本机测试为 Python 3.13。

## 看到什么

| 模块 | 已实现的入口 | 演示 |
|---|---|---|
| Agent | CLI `run` / `chat`；`Agent.run()`；Web 任务页 | 模型或演示模型选择工具、接收结果、继续回答 |
| Tools | `ToolRegistry` / `@tool`；Web 工具页 | 编程文件搜索/精确修改与撤销、受确认的开发命令、Git 状态/差异/分支/提交、Skill 加载、CSV/HTTP 和 Windows 桌面操作 |
| Workflow | `workflow` 命令；Web 工作流页 | 网页填写多步电脑任务并顺序交给同一会话的 Agent；CLI 的农业示例展示条件分支与循环 |
| Context | SQLite；`history`；Web 会话页 | 智能体页左侧直接切换旧会话；按任务内容显示标题和摘要，重启后可继续、会话隔离、状态保存、按完整轮次裁剪 |

网页左侧的“新会话”用于开始新任务，“最近会话”可直接切回或删除旧任务；底部“功能与设置”列出功能介绍、智能体会话、工具系统、工作流、上下文和模型设置。“当前聊天”是智能体会话的快捷入口。聊天页直接显示会话，不再展示介绍横幅。

聊天页右上角的“连接 RAG”可为当前 Agent 会话选择 RAG 项目（自动跟随该项目关联的知识库），或手动勾选多个知识库。选择保存在本机会话中；每轮提问先调用本机 `http://127.0.0.1:8000` 的只读检索接口，再把命中的资料片段交给当前配置的 Agent 模型。需要先启动 RAG 后端与 Ollama 的 `bge-m3` 向量模型；断开连接后 Agent 不再检索。私密资料的片段会发送给当前 Agent 模型供应商，请按资料敏感程度选择范围。

离线演示模式使用固定规则展示实际工具执行，它没有自然语言推理能力。农业 CSV 和阈值是**虚构数据**，农业工作流不会控制真实 STM32 或农业设备。

### Windows 电脑操作

接入真实模型后，Agent 可以读取可见窗口标题、打开记事本/计算器/资源管理器/默认浏览器、打开网址、切换窗口、向指定窗口输入文字、发送有限快捷键，并在主屏幕坐标单击。它还能读取工作区内的文本/CSV 文件，并申请创建新的 TXT、Markdown、CSV 或 JSON 文件。聊天输入框左下角、工作流运行按钮旁的“审批方式”默认逐项确认；发任务前可选择“本次任务全部批准”，这轮聊天任务或工作流的操作会自动通过。也可以在首次确认弹窗中选择“本次任务全部批准”。任务结束后恢复逐项确认，新任务需要重新选择。逐项确认时，拒绝或 120 秒未确认会停止本轮操作。输入文字和快捷键会先重新激活指定标题的窗口，降低焦点跑错位置的风险。

可试：`打开记事本，写入“我的第一个电脑 Agent 任务”`，或`把这段总结保存到 summary.md`。过程中会逐项询问是否允许。左侧“工作区”可创建多个工作目录，最近会话可拖到目标工作区；切换工作区后，新任务会在该会话归属的目录中使用文件工具。工作区列表和会话归属保存在本机 `.yugan/workspaces.json`，旧版 `.yugan/workspace.json` 会自动迁移。文件工具只访问当前会话工作区，新文件不会覆盖旧文件；代码修改使用带备份的精确补丁。桌面操作当前只支持 Windows；不提供任意 PowerShell 操作，也不连接硬件。鼠标只支持主屏幕像素坐标单击，当前没有截图视觉理解，所以复杂页面仍需要你提供明确目标或坐标。电脑窗口标题和你批准输入的文字会作为工具结果/参数发给当前配置的模型，请先检查确认框内容。

### 编程 Agent 工具

智能体可以在当前工作区搜索代码，按唯一匹配的文本片段修改常见文本/代码文件；每次修改会先备份，可用返回的备份 ID 撤销。它可以查看 Git 状态、差异和提交记录；创建分支与提交时会弹出确认，提交只暂存明确列出的文件。需要运行测试或构建时，可使用 `run_command`，从 Python、uv、pytest、Ruff、Node、CMake、Git 和 ARM GCC 等命令中选择，参数以数组传递、不经过 Shell，并在浏览器中逐次确认。命令的工作目录限定在当前工作区，输出有长度和时长上限。网页也可通过 `browser_read_page` 读取渲染后的文本和链接；每次访问都需确认，不会替你点击或提交。

工作区 Skill 放在 `.agents/skills/<技能名>/SKILL.md`。Agent 可以列出并读取说明文件，按需使用其中的流程；Skill 只是说明文本，不会自动运行同目录下的脚本。可先创建 `.agents/skills/test-first/SKILL.md`，写入项目专用的测试要求。

命令确认能让你看清即将启动的程序和参数，但**这不是操作系统沙箱**：已批准运行的 Python 脚本、构建工具或 Git Hook 仍可能访问工作区以外的资源。不要批准来源不明的脚本。浏览器读取需安装可选依赖 `uv sync --extra browser`，在 Windows 优先使用已安装的 Edge；当前仍没有模型视觉识别截图的能力。

网页“工作流”可填写最多 10 个任务步骤，例如先打开记事本、再写入指定文字。点击“运行工作流”后依次调用当前模型；每一步的回答显示在右侧，完整对话保存在当前会话中。步骤草稿保存在本机浏览器；拒绝确认、模型失败或达到执行上限时，后续步骤停止。农业示例仍可通过 CLI 的 `workflow demo` 运行。

## 常用命令

```powershell
.\.venv\Scripts\python.exe -m yugan_agent run "计算 (12 + 8) * 3" --session demo
.\.venv\Scripts\python.exe -m yugan_agent run "分析传感器温度" --session farm
.\.venv\Scripts\python.exe -m yugan_agent chat --session learning
.\.venv\Scripts\python.exe -m yugan_agent tools
.\.venv\Scripts\python.exe -m yugan_agent history
.\.venv\Scripts\python.exe -m yugan_agent workflow demo
.\.venv\Scripts\python.exe -m yugan_agent workflow demo --graph
```

CLI 详细使用见 [快速开始](docs/quickstart.md)。`--graph` 输出 Mermaid 代码，可贴进支持 Mermaid 的 Markdown 查看流程。

## 接入真实模型

```powershell
Copy-Item .env.example .env
notepad .env
```

编辑 `.env`：

```dotenv
YUGAN_PROVIDER=compatible
YUGAN_MODEL=你在供应商控制台选择的支持工具调用的模型ID
YUGAN_API_KEY=你的API_Key
YUGAN_BASE_URL=该供应商的OpenAI兼容接口地址
```

保存后重新启动 CLI 或 Web。`openai` 使用 Responses API，`anthropic` 使用 Claude Messages API，`compatible` 使用 Chat Completions 协议。Kimi、Qwen、GLM 和其他兼容服务的设置方法见 [模型配置](docs/providers.md)。不要把真实 `.env` 提交到 Git。模型调用可能产生费用。

**网页配置模型**：打开左侧“模型设置”，填写配置名称、API Key、Base URL 和模型 ID，点击“保存并启用”。只填 Key 时默认 DeepSeek；其他平台请同时填写对应地址和模型 ID。可保存多个 API 模型。模型配置（含 Key）只保存在当前浏览器的本地存储中，模型请求从浏览器直连供应商接口，不经过 Agent 服务。聊天输入框右下角的模型菜单还可选择用户本机或服务器上的 Ollama；任务执行中切换模型不会改变正在运行的任务。细节见 [模型配置](docs/providers.md)。

## 安全边界

- 文件工具只能从当前会话所属的工作区读取、搜索和修改限定类型的文本文件；补丁写入有备份，路径逃逸和隐藏文件限制仍生效。工作区通过左侧列表创建和切换，创建表单接受文件夹路径。Windows 桌面工具要求本机网页授权，支持单次批准或仅对当前任务生效的全部批准。
- 桌面工具仅支持打开固定常用应用/网址、读取窗口标题、切换窗口、输入文字、白名单快捷键和主屏幕坐标单击；没有截图视觉理解。编程命令只能从白名单程序中选择且每次需确认，但已批准的程序不受操作系统级沙箱限制。
- `http_get` 只能调用 `.env` 中 `YUGAN_HTTP_ENDPOINTS` 预设的固定 URL；默认无端点。
- 自定义有副作用工具默认拒绝，必须逐项列入 `YUGAN_ALLOWED_EFFECTS`。
- Web 默认监听 `127.0.0.1`。要监听外部地址，先设置 `YUGAN_API_TOKEN`；公开部署前还需反向代理、TLS 和额外安全审查。
- SQLite 在 `.yugan/memory.db`，日志在 `.yugan/events.jsonl`；日志只记录运行元信息，不记录提示词或 Key。
- 文件、工具结果和会话状态发送给真实模型时属于模型输入。请勿把密钥或不想上传的资料放入工作区。

当前范围为**本地单用户开发版**；不会声称已具备多租户、真实硬件控制、插件市场或企业生产部署能力。

## 扩展与验证

添加工具见 [工具文档](docs/tools.md) 与 [示例](examples/custom_tool.py)；编写工作流见 [工作流文档](docs/workflows.md)。公共 API 见 [架构说明](docs/YUGAN_ARCHITECTURE.md)，后续方向见 [路线图](docs/roadmap.md)。

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\ruff.exe check src\yugan_agent tests examples
.\.venv\Scripts\ruff.exe format --check src\yugan_agent tests examples
& 'C:\Users\yugan\.local\bin\uv.exe' --cache-dir .uv-cache build --wheel
```

单元测试不需要 Key。真实 DeepSeek API 已通过一次短任务手工调用验证。新增的 Windows 桌面操作与确认弹窗尚待在用户桌面重启服务后手工验收。要重复浏览器页面验证，先安装可选依赖并启动 Web 服务：

```powershell
& 'C:\Users\yugan\.local\bin\uv.exe' --cache-dir .uv-cache sync --extra dev --extra browser
.\.venv\Scripts\python.exe -m yugan_agent serve --port 8020
# 在第二个 PowerShell 窗口执行：
.\.venv\Scripts\python.exe scripts\verify_yugan_web.py
```

原上游的运行方式、文档与代码仍保留在 `yugan-agent/` 及其他原有目录。新包和旧包是两个独立入口；原上游的大型测试集不等于新包的验收结果。
