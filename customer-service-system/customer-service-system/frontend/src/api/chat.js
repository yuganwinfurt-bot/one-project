/**
 * 对话相关 API。
 * SSE 不能用 axios 方便地读流，所以单独用 fetch。
 */
import { ElMessage } from 'element-plus'
import router from '@/router'
import { getToken, logout } from '@/utils/auth'
import request from '@/utils/request'
import { apiUrl } from '@/utils/apiBase'

/**
 * 发起流式对话。
 */
export async function streamChat(question, handlers = {}) {
  const {
    onStatus,
    onRoute,
    onAgentStep,
    onToken,
    onActionPending,
    onAgentModelContext,
    onAgentModelRequest,
    onDone,
    onError,
    signal,
    history,
    useAgentModel
  } = handlers
  const token = getToken()

  const response = await fetch(apiUrl('/api/chat/stream'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : ''
    },
    // history：最近几轮对话，后端用它做多轮指代消解（「看下它的评价」里的「它」）
    body: JSON.stringify({
      question,
      history: history || [],
      use_agent_model: Boolean(useAgentModel),
      model_protocol: 2
    }),
    signal
  })

  if (!response.ok) {
    // fetch 不走 axios 拦截器，这里单独处理登录失效：清登录态并回到登录页
    if (response.status === 401) {
      ElMessage.error('登录状态已失效，请重新登录')
      logout()
      router.push('/login')
      throw new Error('登录状态已失效，请重新登录')
    }
    const message = `请求失败（HTTP ${response.status}）`
    onError?.({ message })
    throw new Error(message)
  }

  if (!response.body) throw new Error('服务器未返回对话数据流')
  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  let receivedTerminal = false
  const eventHandlers = { onStatus, onRoute, onAgentStep, onToken, onActionPending, onAgentModelContext, onAgentModelRequest, onDone, onError }
  async function deliver(event) {
    if (event.event === 'done' || event.event === 'error') receivedTerminal = true
    await dispatchSseEvent(event, eventHandlers)
  }

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        buffer += decoder.decode()
        break
      }

      buffer = (buffer + decoder.decode(value, { stream: true })).replace(/\r\n/g, '\n')
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''

      for (const part of parts) {
        const event = parseSseBlock(part)
        if (event) await deliver(event)
      }
    }

    if (buffer.trim()) {
      const event = parseSseBlock(buffer)
      if (event) await deliver(event)
    }
    if (!receivedTerminal) {
      const error = new Error('连接在回答完成前断开，已保存的分析可以继续生成回答')
      error.code = 'STREAM_INTERRUPTED'
      throw error
    }
  } finally {
    reader.releaseLock()
  }
}

/** 读取已保存的分析上下文或完整回答，不重跑业务动作 */
export function getRunAnswerContext(runId) {
  return request.get(`/api/chat/runs/${runId}/answer-context`)
}

export function submitModelResult(runId, requestId, content = '', error = null, cancelled = false) {
  return request.post(`/api/chat/runs/${runId}/model-requests/${requestId}`, { content, error, cancelled })
}

export function saveRunReport(runId) {
  return request.post(`/api/chat/runs/${runId}/report`)
}

/** 确认或取消商品复核动作 */
export function confirmActions(threadId, approved) {
  return request.post('/api/chat/actions/confirm', {
    thread_id: threadId,
    approved
  })
}

function parseSseBlock(block) {
  let eventName = 'message'
  const dataLines = []

  for (const rawLine of block.split('\n')) {
    const line = rawLine.replace(/\r$/, '')
    if (!line || line.startsWith(':')) continue
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim())
    }
  }

  if (!dataLines.length) return null

  let data
  try {
    data = JSON.parse(dataLines.join('\n'))
  } catch {
    data = { message: dataLines.join('\n') }
  }
  return { event: eventName, data }
}

async function dispatchSseEvent(event, handlers) {
  const {
    onStatus,
    onRoute,
    onAgentStep,
    onToken,
    onActionPending,
    onAgentModelContext,
    onAgentModelRequest,
    onDone,
    onError
  } = handlers
  switch (event.event) {
    case 'status':
      onStatus?.(event.data)
      break
    case 'route':
      onRoute?.(event.data)
      break
    case 'agent_step':
      onAgentStep?.(event.data)
      break
    case 'token':
      onToken?.(event.data)
      break
    case 'action_pending':
      onActionPending?.(event.data)
      break
    case 'agent_model_context':
      await onAgentModelContext?.(event.data)
      break
    case 'agent_model_request':
      await onAgentModelRequest?.(event.data)
      break
    case 'done':
      onDone?.(event.data)
      break
    case 'error':
      onError?.(event.data)
      break
    default:
      break
  }
}
