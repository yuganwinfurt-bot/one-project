# 架构说明

```text
CLI / FastAPI / Python SDK
       |
       +--> Agent  <---> Provider (mock / openai / compatible / anthropic)
       |       +--> ToolRegistry --> @tool Python 函数
       |       +--> SQLiteMemory (会话消息与状态)
       |       +--> Event (执行记录)
       +--> WorkflowRunner --> tool / set / condition / agent 节点
```

| 文件 | 职责 |
|---|---|
| `src/yugan_agent/agent.py` | 工具反馈循环、上限、会话串行与执行事件 |
| `src/yugan_agent/providers.py` | 转换供应商消息和工具调用格式 |
| `src/yugan_agent/tools.py` | 工具参数校验、超时和输出限制 |
| `src/yugan_agent/builtins.py` | 文件、CSV、计算、时间、HTTP 示例工具 |
| `src/yugan_agent/memory.py` | SQLite 持久化、完整轮次上下文裁剪 |
| `src/yugan_agent/workflow.py` | 工作流节点、条件分支和有界循环 |
| `src/yugan_agent/api.py` | REST API 和浏览器页面 |
| `src/yugan_agent/cli.py` | 命令行入口 |

Agent 最多执行 `YUGAN_MAX_STEPS` 次模型请求和 `YUGAN_MAX_TOOL_CALLS` 次工具调用。供应商返回截断输出不算成功。工作流有独立 `max_steps`，防止循环无法结束。

上下文预算按消息序列化后的字符数估算，不是精确 Token 计数；早期轮次仅从模型输入中省略，SQLite 原文继续保留。工作流状态仅在当前流程共享，会话状态按 session 隔离。

本仓库保留上游 `cai-agent/`，其 LangGraph 运行时不是新增 yugan-agent 包的默认依赖。
