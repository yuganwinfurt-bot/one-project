# 添加工具

工具是普通 Python 函数；类型标注描述参数，文档字符串告诉模型用途。

```python
from yugan_agent import ToolRegistry, tool

@tool
def soil_moisture(raw: int) -> dict:
    """把 0–4095 的 ADC 示例值转换为百分比。"""
    if not 0 <= raw <= 4095:
        raise ValueError("raw 必须在 0–4095 之间")
    return {"percent": round(raw / 4095 * 100, 1)}

registry = ToolRegistry()
registry.register(soil_moisture)
```

如果要让智能体发现此工具，创建 Agent 后把它注册进该 Agent 的工具表：

```python
from yugan_agent.runtime import create_agent

agent = create_agent()
agent.tools.register(soil_moisture)
# 然后 await agent.run("用 soil_moisture 计算原始值 2048", "sensor")
# 最后 await agent.close()
```

默认 `mock` 模式只识别少量固定演示任务；要让模型自行选择这个新工具，需要在 `.env` 配置真实模型。

注册中心生成 JSON Schema，执行前由 Pydantic 校验参数。同步函数在线程中执行，异步函数直接等待。输入、输出和耗时都有上限。

写文件、发 MQTT 指令或修改设备时，要使用 `@tool(side_effect=True)`。CLI 中这类工具默认拒绝，除非列入 `YUGAN_ALLOWED_EFFECTS`；Web 中可提供确认回调，让用户在本机弹窗核对参数后批准。`always_confirm=True` 的工具即使在允许列表内也必须经过确认回调。Web 可在首次弹窗选择单次批准或“本次任务全部批准”；后者只对当前聊天任务或工作流有效，任务结束即失效。编程写入、命令执行、Git 分支和提交均逐次确认。当前没有内置真实硬件控制。同步函数超时不会强制杀掉线程，因此有副作用工具须考虑重复执行风险。

内置 `create_text_file` 可在当前工作区新建 TXT、Markdown、CSV、JSON 和常见源码文件（包括 `.py`、`.js`、`.ts`、`.html`、`.css`、`.c`）；路径受 `safe_path` 限制，已存在的文件不会覆盖，每次都需要确认。若当前工作区选择为 Windows 桌面，文件名相对路径会直接写到桌面根目录。CLI 默认拒绝，除非提供本地确认回调。

编程 Agent 增加以下工具：`search_workspace` 搜索代码与文件名；`move_file` 在 workspace 内重命名或移动单个文件，`copy_file` 复制不超过 100 MB 的单个文件，两者都拒绝覆盖已有目标并逐次确认；`apply_file_patch` 只替换唯一匹配的 UTF-8 片段并保存备份，`undo_file_patch` 在文件未被后续修改时恢复备份；`run_command` 运行 Python、uv、pytest、Ruff、Node、CMake、Git 或 ARM GCC 等白名单程序，不经过 Shell，工作目录必须位于当前 workspace，最长 60 秒并限制输出；`git_status`、`git_diff`、`git_log` 只读，差异结果会过滤隐藏路径，`git_create_branch` 与 `git_commit` 需逐次确认，提交时只暂存明确列出的文件。`list_skills` / `read_skill` 发现并加载 `.agents/skills/<name>/SKILL.md`；Skill 只提供说明文本，不执行脚本。可选的 `browser_read_page` 使用 Playwright 读取渲染后的可见文本和链接，每次打开网页都需确认，不提供页面点击或表单提交。

命令执行确认不是操作系统沙箱。获批程序仍可能通过脚本、构建钩子或自身参数读取、修改 workspace 外文件；不要批准来源不明的命令或脚本。文件补丁和 Skill 文件读取仍受 workspace 路径约束。

Windows Web 端内置了受确认保护的桌面工具：列出可见窗口标题、打开固定常用应用或 HTTP/HTTPS 页面、切换窗口、向指定标题窗口输入文字、发送有限快捷键、在主屏幕指定像素位置单击。窗口标题与输入文字会发给当前模型；确认框展示完整工具参数。当前没有截图视觉理解，因此坐标点击需要用户明确目标或坐标。用户拒绝后 Agent 会立即停止本轮，不会让模型换工具绕过拒绝。

`read_file` 和 `csv_summary` 只能读取 `workspace/` 内受支持的文本文件。`http_get` 仅能使用 `YUGAN_HTTP_ENDPOINTS` 预先配置的别名，例如：

```dotenv
YUGAN_HTTP_ENDPOINTS={"weather":"https://example.com/api/weather"}
```

示例 URL 是占位地址。文件和 HTTP 返回内容应视作数据，不应把其中的文字当作新的系统指令。完整示例见 [examples/custom_tool.py](../examples/custom_tool.py)。

## 网页管理自定义工具

网页“工具系统”中可以停用或重新启用内置工具，也可以添加/删除固定 HTTP 工具。自定义接口支持 GET 和 POST、最多 12 个基础类型参数，以及可选 Bearer API Key。接口只能使用 HTTPS；本机回环地址可用 HTTP。请求超时为 8 秒，响应最多读取 12 KB。工具设置写入项目 `.yugan/tools.json`，API Key 以本机文件内容保存，管理接口不会返回密钥。任务正在执行时不能修改工具配置。

网页表单不会执行用户输入的 Python。要扩展本地 Python 能力，仍需通过 `@tool` 编写函数并注册到 `ToolRegistry`。Skill 是供模型遵循的说明和资源，不会因此自动变成可执行函数。
