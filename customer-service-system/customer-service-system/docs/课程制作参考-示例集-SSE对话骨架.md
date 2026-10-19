# 示例集节奏参考：SSE 对话骨架

> 用途：拿这一集当"节奏样板"——看手敲什么、给代码什么、每段讲多久。
> 集数按 `课程制作参考-带敲清单与集数浮动规则.md` 浮动，本集是"业务读取模块"之后的那个主题；顺序可改，文档按主题命名、不绑集号。
> 为免后续调号导致文档过期，涉及之后各集的地方用主题代称（如"接入真实链路那一集"）。
> 下面手敲的代码已实跑验证：事件帧格式与前端解析规则一致，可直接照敲。

## 一、本集目标与设计意图

**目标**：打通"提问 → 事件流 → 逐字显示"这条管道。不接数据库、不接大模型，回复是固定文本。

**设计意图（要讲的第一个道理）**：把"管道"和"内容"分开。本集只定义事件协议（`status` / `token` / `done` / `error`），接入真实链路那一集起把固定回复换成真实查询时，**前端一行都不用改**。这是让后面每一集都接得上的关键。

## 二、时间轴（约 38 分钟）

| 时间 | 环节 | 内容 |
| --- | --- | --- |
| 0:00–0:03 | 演示成品 | 在对话页输入「洗衣液 2L 有哪些评价？」，看过程区出现"准备分析"、回答逐字出现 |
| 0:03–0:13 | 讲原理（不敲） | ① 为什么用 SSE（对比轮询与 WebSocket）② 四类事件各管什么 ③ 为什么必须 POST + `fetch`（`EventSource` 只支持 GET、带不了 `Authorization` 头；axios 读不了流）④ 前端怎么按空行切事件块 |
| 0:13–0:33 | 手敲 ≈65 行 | 三个文件，一行一讲；中途跑两次（先看原始事件帧，再看浏览器逐字效果） |
| 0:33–0:36 | 验证 | 空问题返回 `error` 事件；手动断开连接；刷新页面会话还在（缓存是给代码的） |
| 0:36–0:38 | 小结与预告 | 本集只定义了管道；下一集把固定回复换成"生成 SQL 去查" |

手敲 20 分钟 ÷ 65 行 ≈ **每行 18 秒**，正好落在"边写边讲 15~30 秒/行"的预算内。若讲得慢，就把第四节的"可敲可不敲"删掉（那部分可以先不讲）。

## 三、事件协议（本集的核心产出，建议边讲边画一张表）

| 事件 | 时机 | 携带字段 | 前端行为 |
| --- | --- | --- | --- |
| `status` | 收到问题、开始处理 | `stage`、`message` | 往过程区追加一条步骤 |
| `token` | 生成回复的每一小段 | `content` | 追加到回答区（逐字效果） |
| `done` | 正常结束 | `route`、`row_count` | 收尾、标记这次运行结束 |
| `error` | 参数/运行出错 | `message` | 提示错误，不显示回答 |

约定：**一条事件的格式是 `event: 名称` + `data: JSON` + 一个空行**；空行是分帧标记，前端按 `\n\n` 切块。

## 四、手敲代码（≈65 行）

### 4.1 `backend/app/schemas/chat.py`（5 行）

```python
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000, description="用户问题")
```

**讲解点**：请求体为什么单独建模（校验 + 文档），`min_length=1` 挡掉空问题（前端也挡一次）。

### 4.2 `backend/app/api/chat.py`（20 行）

```python
"""对话接口：SSE 流式下发。"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.dependencies.auth import CurrentUser
from app.schemas.chat import ChatRequest
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["对话"])


@router.post("/stream")
def chat_stream(body: ChatRequest, current_user: CurrentUser):
    """流式对话：本集先返回固定回复，下一集起接入真实链路。"""
    return StreamingResponse(
        chat_service.stream_chat(body.question, user_id=current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

**讲解点**：
- 返回的是 `StreamingResponse`，所以函数不是 `async` 也行——它只是把生成器交出去；
- `media_type="text/event-stream"` 是 SSE 的约定；
- `X-Accel-Buffering: no` 这个头是**踩过坑才加的**：不加的话某些代理会缓冲整段再一次性吐出，表现就是"一直卡着不出字"；
- 鉴权用现成的 `CurrentUser` 依赖（`dependencies/auth.py` 给代码，讲一句"它是从请求头里的 JWT 解析出当前用户"）。

### 4.3 `backend/app/services/chat_service.py`（本集只敲这一小段，40 行）

```python
"""对话服务：本集只做事件协议骨架。"""

import json
from typing import Any, Generator

# 固定回复：下一集起换成"查数据 + 总结"的真实链路
SKELETON_REPLY = "已收到问题：{question}。当前是对话骨架，还没有接入数据查询。"


def _sse(event: str, data: dict[str, Any]) -> str:
    """按 SSE 格式拼一条事件：event 行 + data 行 + 空行。"""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


def _reply_chunks(text: str, size: int = 8) -> Generator[str, None, None]:
    """把回复切成小块，制造逐字下发的效果。"""
    for i in range(0, len(text), size):
        yield text[i : i + size]


def stream_chat(question: str, user_id: int | None = None) -> Generator[str, None, None]:
    """SSE：把一次对话按事件协议下发。"""
    if not question.strip():
        yield _sse("error", {"message": "问题不能为空"})
        return

    yield _sse("status", {"stage": "accepted", "message": "已收到问题，准备分析…"})

    reply = SKELETON_REPLY.format(question=question.strip())
    for piece in _reply_chunks(reply):
        yield _sse("token", {"content": piece})

    yield _sse("done", {"route": None, "row_count": 0})
```

**讲解点**：
- `ensure_ascii=False`：不写这句中文会变成 `\u6d17\u8863...`，虽然能解析但原始帧看不懂，调试时很痛苦；
- `_reply_chunks` 为什么要分块：一次发完就没有打字机效果，而前端不需要为此改代码（协议不变）；
- 生成器里 `yield` 的每一段都是一次网络下发——"流式"的本质就在这里；
- 跑一次看原始帧：Swagger 里调 `/api/chat/stream`，或 `curl -N -X POST ...`，能看到 `event: status` → 多个 `event: token` → `event: done`。

## 五、给代码（AI 生成，讲解 3~5 分钟，不敲）

| 文件 | 规模 | 讲解要点 |
| --- | --- | --- |
| `frontend/src/api/chat.js` | 155 行 | `fetch` + `response.body.getReader()` 读流；按 `\n\n` 切块；`event:` / `data:` 解析；401 单独处理（fetch 不走 axios 拦截器） |
| `frontend/src/views/Chat.vue` | 937 行 | 过程区与回答区**为什么分开**（事件类型决定 UI 分区）；`keep-alive` 保住会话；Enter 发送 / Shift+Enter 换行 |
| `frontend/src/utils/chatCache.js` | 36 行 | 会话写进 localStorage，刷新不丢；只缓存文本，不缓存"进行中"状态 |
| `frontend/src/utils/request.js` | 56 行 | axios 统一封装与拦截器（业务码 500 也走提示，HTTP 401 才登出） |
| `backend/app/dependencies/auth.py` | 53 行 | JWT 依赖怎么拿到当前用户（一句话带过） |
| `backend/app/common/response.py` | 25 行 | 为什么这个接口**不用**统一响应体：SSE 是流，不是一次性 JSON |
| `backend/app/main.py` 装配 | — | CORS、异常处理器注册顺序（全局兜底必须最后注册） |

前端关键片段（讲协议对接时对着看，约 20 行）：

```js
const response = await fetch('/api/chat/stream', { method: 'POST', body, headers, signal })
const reader = response.body.getReader()
const decoder = new TextDecoder('utf-8')
let buffer = ''
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  buffer += decoder.decode(value, { stream: true })
  const parts = buffer.split('\n\n')   // 空行分帧
  buffer = parts.pop() || ''
  for (const part of parts) dispatch(parseSseBlock(part))
}
```

## 六、可敲可不敲（时间富余时加，约 25 行）

- 调 `_reply_chunks` 的 `size`（8 字符），实测打字机效果与请求帧数；
- 把 `Cache-Control` / `X-Accel-Buffering` 两个头删掉再跑一次，亲眼看到"卡着不出字"，再讲为什么加回来；
- 前端加一个"停止生成"按钮（`AbortController`）。

## 七、学生做完能看到什么

1. Swagger 或 `curl -N` 能看到原始事件帧：`status` → 多个 `token` → `done`；
2. 对话页里回答逐字出现，过程区有一条"准备分析"；
3. 输入空白 → 返回 `error` 事件，前端提示不显示回答。

## 八、必须讲清的"与成品的差异"

| 本集 | 成品 | 什么时候补上 |
| --- | --- | --- |
| 回复是固定文本 | 真实查询 + 模型总结 | 接入真实链路那一集 |
| `done` 里 `route` / `row_count` 为 `null` | 填路由与证据条数 | NL2SQL 与向量检索两集 |
| 没有 `run_id` / `elapsed_ms` | 有，用于运行历史 | 可观测那一集 |
| 没有 `action_pending` 事件 | 有，用于人工确认 | 人工确认那一集 |
| 前端已有完整对话页 | 同一套页面 | 前端全程给代码 |

**收尾话术（要点）**：这一集只搭了管道，管道搭好之后，后面每一集都是在管道里换"内容"，界面和协议都不动——这就是为什么先把协议定下来。

## 九、承接关系

- **上一集**（业务读取模块）：已经能用接口查到商品、订单、评价的只读数据；
- **本集**：把这些查询接进对话，先把"管道"搭好，回复仍是固定文本；
- **下一集**：把固定回复换成"生成 SQL 去查真实数据"——即 NL2SQL。

## 十、行数核对

| 项 | 行数 |
| --- | --- |
| 手敲（三个文件） | ≈ 65 |
| 参考文档原估 | ~90 |
| 加第六节的可选内容 | +25 → ≈ 90 |

结论：参考文档里 EP03 的 90 行估算偏保守；录制时按"必敲 65 行 + 可选 25 行"安排即可，两种节奏都在每集 70~90 行的区间内。
