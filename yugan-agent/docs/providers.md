# 模型配置

将根目录 `.env.example` 复制为 `.env` 后修改。`.env` 已被 Git 忽略，不能提交真实 Key。

也可以在本机网页的“模型设置”中保存多个 API 配置，填写名称、Key、可选 Base URL 和模型 ID。本机支持工具调用的 Ollama 模型直接列在聊天输入框的模型下拉列表中，点击即可保存并启用，无需 API Key。只填 Key 默认 DeepSeek；其他地址按域名选择 OpenAI Responses、Claude Messages 或 OpenAI 兼容协议。未知 HTTPS 服务按兼容协议处理，必须填写模型 ID。本地 Ollama 使用本机 `http://127.0.0.1:11434/v1`。配置（含 API 模式下的明文 Key）保存在本机 `.yugan/model_profiles.json`，当前启用配置还写入 `.env`；两处都被 Git 忽略，网页不会回显 Key。聊天输入框右下角点击模型/强度按钮打开强度弹层，再点其中的模型名称打开可搜索、滚动的模型列表。运行中切换时，正在执行的任务仍使用原模型，下一次任务使用新模型。模型 SDK 客户端会在首次发任务时创建，切换操作不等待建连。不要把其他平台的 Key 配上 DeepSeek 地址。

| `YUGAN_PROVIDER` | 协议 | 其他必填项 |
|---|---|---|
| `mock` | 本地规则演示 | 无 |
| `openai` | OpenAI Responses | `MODEL`、`API_KEY` |
| `compatible` | OpenAI 兼容 Chat Completions | `MODEL`、`API_KEY`、`BASE_URL` |
| `anthropic` | Claude Messages | `MODEL`、`API_KEY` |

### DeepSeek（推荐本机快速接入）

在项目目录的 `.env` 中填写：

```dotenv
YUGAN_PROVIDER=compatible
YUGAN_MODEL=deepseek-flash
YUGAN_API_KEY=你在 DeepSeek 开放平台创建的 Key
YUGAN_BASE_URL=https://api.deepseek.com
YUGAN_THINKING=disabled
```

`deepseek-flash` 支持工具调用。默认网页强度沿用 `YUGAN_THINKING=disabled`；选择低/中/高/极高时会开启思考模式，并在工具调用后回传 `reasoning_content`。DeepSeek 的中、高都映射为其 `high` 档，极高映射为 `max`。`YUGAN_THINKING` 默认是 `auto`，其他兼容供应商无需改动。手动编辑 `.env` 后需重启服务；在网页切换模型无需重启。Key 在 [DeepSeek 开放平台](https://platform.deepseek.com/) 创建，调用可能产生费用。

### Kimi / Moonshot

在网页“模型设置”中填写：配置名称 `Kimi K3`（可选）、API Key 为创建时复制的完整 Key、Base URL 为 `https://api.moonshot.cn/v1`、模型 ID 为 `kimi-k3`，然后点击“保存并启用”。截图中的遮盖版 Key 不能用于连接；未保存完整 Key 时需在 [Kimi 开放平台](https://platform.kimi.com/console/api-keys) 新建。不要把 Key 发到聊天窗口。

若使用 `.env`，对应配置是：

```dotenv
YUGAN_PROVIDER=compatible
YUGAN_MODEL=kimi-k3
YUGAN_API_KEY=创建时保存的完整Key
YUGAN_BASE_URL=https://api.moonshot.cn/v1
```

Kimi K3 支持工具调用和思考强度 `low`、`high`、`max`；网页“中”按 `high` 发送，“默认”沿用 K3 的默认 `max`。工具调用后的下一轮会回传 Kimi 的 `reasoning_content`。K3 目前需要实际充值才能调用，具体条件以[官方快速开始](https://platform.kimi.com/docs/guide/kimi-k3-quickstart)为准；接口地址和模型 ID 见[官方接口概览](https://platform.kimi.com/docs/api/overview)与[模型列表](https://platform.kimi.com/docs/models)。

### OpenAI

```dotenv
YUGAN_PROVIDER=openai
YUGAN_MODEL=填入账户可用且支持工具调用的模型ID
YUGAN_API_KEY=填入Key
```

`openai` 默认请求官方地址。自定义 `BASE_URL` 只有在服务完整兼容 Responses API 时才适用。

### 百炼 / Qwen

```dotenv
YUGAN_PROVIDER=compatible
YUGAN_MODEL=填入已开通且支持工具调用的模型ID
YUGAN_API_KEY=填入百炼Key
YUGAN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

地域与业务空间可能影响 URL，参考[百炼官方 Base URL 表](https://help.aliyun.com/zh/model-studio/base-url)。

### GLM / 智谱

```dotenv
YUGAN_PROVIDER=compatible
YUGAN_MODEL=填入已开通且支持工具调用的模型ID
YUGAN_API_KEY=填入智谱Key
YUGAN_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

地址示例见[智谱官方文档](https://docs.bigmodel.cn/cn/best-practice/case/ai-search-engine)。

### Claude

```dotenv
YUGAN_PROVIDER=anthropic
YUGAN_MODEL=填入账户可用的Claude模型ID
YUGAN_API_KEY=填入Anthropic的Key
```

工具调用格式参考[Claude 官方文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)及[OpenAI Docs](https://developers.openai.com/api/docs/guides/function-calling)。

本项目不会读取或修改 Codex / CC Switch 的配置。现有配置里的 `PROXY_MANAGED` 不表示 Key 坏了。若通过代理接入，先确认其协议、Base URL 和模型 ID。文本接口不能直接分析图片。

真实供应商调用未在无 Key 离线测试中验证。错误时先检查 Key、模型 ID、协议、限流与网络。
