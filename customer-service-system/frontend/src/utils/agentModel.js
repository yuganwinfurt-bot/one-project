const localHosts = new Set(['127.0.0.1', 'localhost', '[::1]'])

function getAgentUrl() {
  const local = localHosts.has(window.location.hostname)
  const configured = import.meta.env.VITE_AGENT_URL
  const url = new URL(configured || (local ? '/' : '/agent/'), window.location.href)
  if (local && !configured) url.port = '8020'
  if (!url.pathname.endsWith('/')) url.pathname += '/'
  return url
}

/** 返回 Agent 控制台的模型设置直达地址。 */
export function getAgentModelSettingsUrl() {
  const url = getAgentUrl()
  url.searchParams.set('view', 'settings')
  return url.href
}

/** Read shared customer-service readiness without sending credentials. */
export async function getSupportModelStatus() {
  const response = await fetch(new URL('api/support-model/status', getAgentUrl()), {
    method: 'GET', cache: 'no-store', credentials: 'omit',
    signal: AbortSignal.timeout(5000)
  })
  if (!response.ok) throw new Error('无法读取客服模型状态')
  return response.json()
}

/** 从同源 Agent 页面桥接读取控制台当前选中的模型配置。 */
export function getActiveAgentModel() {
  const agentUrl = getAgentUrl()
  const nonce = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`
  const bridgeUrl = new URL(`static/model-bridge.html#${nonce}`, agentUrl)
  const iframe = document.createElement('iframe')
  iframe.title = 'Agent 模型连接'
  iframe.setAttribute('aria-hidden', 'true')
  Object.assign(iframe.style, {
    position: 'fixed',
    width: '1px',
    height: '1px',
    opacity: '0',
    pointerEvents: 'none',
    border: '0'
  })
  iframe.src = bridgeUrl.href

  return new Promise((resolve, reject) => {
    let settled = false
    let attempts = 0
    let retryTimer = null
    let timeoutTimer = null
    const cleanup = () => {
      clearInterval(retryTimer)
      clearTimeout(timeoutTimer)
      window.removeEventListener('message', onMessage)
      iframe.remove()
    }
    const finish = (error, profile) => {
      if (settled) return
      settled = true
      cleanup()
      if (error) reject(error)
      else resolve(profile)
    }
    const onMessage = (event) => {
      if (event.source !== iframe.contentWindow || event.origin !== agentUrl.origin) return
      if (event.data?.nonce !== nonce) return
      if (event.data.type === 'yugan-active-model-error') {
        finish(new Error(event.data.message || '读取 Agent 当前模型失败'))
      } else if (event.data.type === 'yugan-active-model') {
        if (!event.data.profile?.model || !event.data.profile?.endpoint) {
          finish(new Error('Agent 当前模型配置不完整'))
          return
        }
        finish(null, event.data.profile)
      }
    }
    window.addEventListener('message', onMessage)
    document.body.appendChild(iframe)

    retryTimer = setInterval(() => {
      attempts += 1
      iframe.contentWindow?.postMessage(
        { type: 'yugan-request-active-model', nonce },
        agentUrl.origin
      )
      if (attempts >= 40) finish(new Error('连接 Agent 超时，请确认 Agent 控制台已启动并登录'))
    }, 250)
    timeoutTimer = setTimeout(
      () => finish(new Error('连接 Agent 超时，请确认 Agent 控制台已启动并登录')),
      11000
    )
  })
}

/** 在浏览器中调用 Agent 当前模型，云端 API Key 不经过电商后端。 */
export async function completeWithAgentModel(profile, messages, abortSignal, options = {}) {
  let response
  let requestUrl
  let headers = { 'Content-Type': 'application/json' }
  let body

  if (profile.mode === 'server') {
    requestUrl = new URL('api/models/server-ollama/chat/completions', getAgentUrl())
    headers = {
      ...headers,
      ...(profile.api_token ? { Authorization: `Bearer ${profile.api_token}` } : {})
    }
    body = { model: profile.model, messages, max_tokens: options.maxTokens || 2048 }
  } else {
    const anthropic = profile.provider === 'anthropic' || profile.vendor === 'Claude'
    const endpoint = String(profile.endpoint || '').replace(/\/+$/, '')
    if (!endpoint) throw new Error('Agent 模型没有配置接口地址')
    requestUrl = anthropic
      ? `${endpoint.endsWith('/v1') ? endpoint : `${endpoint}/v1`}/messages`
      : `${endpoint}/chat/completions`

    if (anthropic) {
      headers['x-api-key'] = profile.api_key || ''
      headers['anthropic-version'] = '2023-06-01'
      headers['anthropic-dangerous-direct-browser-access'] = 'true'
      body = {
        model: profile.model,
        max_tokens: options.maxTokens || 4096,
        system: messages
          .filter((item) => item.role === 'system')
          .map((item) => item.content)
          .join('\n\n'),
        messages: messages.filter((item) => item.role !== 'system')
      }
    } else {
      if (profile.mode !== 'local') headers.Authorization = `Bearer ${profile.api_key || ''}`
      body = { model: profile.model, messages, stream: false }
      if (options.maxTokens) body.max_tokens = options.maxTokens
    }
  }

  const timeoutSignal = AbortSignal.timeout(options.timeoutMs || (profile.mode === 'server' ? 300000 : 120000))
  const signal = abortSignal ? AbortSignal.any([abortSignal, timeoutSignal]) : timeoutSignal
  try {
    response = await fetch(requestUrl, {
      method: 'POST',
      credentials: profile.mode === 'server' ? 'include' : 'omit',
      headers,
      body: JSON.stringify(body),
      signal
    })
  } catch (error) {
    if (timeoutSignal.aborted && !abortSignal?.aborted) throw new Error('Agent 模型响应超时，可继续已保存的分析')
    if (error instanceof TypeError) {
      throw new Error('无法连接 Agent 模型接口；请检查模型地址及接口的跨域设置')
    }
    throw error
  }

  let raw
  try {
    raw = await response.text()
  } catch (error) {
    if (timeoutSignal.aborted && !abortSignal?.aborted) throw new Error('Agent 模型响应超时，可继续已保存的分析')
    throw error
  }
  let payload
  try {
    payload = JSON.parse(raw)
  } catch {
    payload = {}
  }
  if (!response.ok) {
    throw new Error(
      payload.detail || payload.error?.message || payload.message || `模型接口返回 HTTP ${response.status}`
    )
  }
  const answer =
    profile.provider === 'anthropic' || profile.vendor === 'Claude'
      ? (payload.content || [])
          .filter((item) => item.type === 'text')
          .map((item) => item.text)
          .join('')
      : payload.choices?.[0]?.message?.content
  if (typeof answer !== 'string' || !answer.trim()) throw new Error('Agent 模型没有返回文本回答')
  return answer
}

/** 云端配置统一在发起数据分析前确认；本机和 Agent 服务端模型不弹窗。 */
export function isCloudAgentModel(profile) {
  if (profile?.mode === 'server') return false
  if (profile?.mode !== 'local') return true
  try {
    return !localHosts.has(new URL(profile.endpoint).hostname)
  } catch {
    return true
  }
}
