<template>
  <div class="page-container chat-page">
    <!-- 消息列表 -->
    <div class="content-card chat-page__messages" ref="messagesRef" @scroll="handleMessagesScroll">
      <div v-if="!messages.length" class="chat-page__empty">
        <p class="chat-page__empty-text">分析商品和订单，也可以新建多规格商品、维护价格库存、处理售后和修改后台配置；账号及角色权限不可修改。</p>
        <div class="chat-page__examples">
          <span class="chat-page__examples-label">可以试试：</span>
          <el-button
            v-for="question in exampleQuestions"
            :key="question"
            size="small"
            round
            @click="handleSend(question)"
          >
            {{ question }}
          </el-button>
        </div>
      </div>

      <div
        v-for="msg in messages"
        :key="msg.id"
        class="chat-page__message"
        :class="`chat-page__message--${msg.role}`"
      >
        <!-- 用户消息 -->
        <div v-if="msg.role === 'user'" class="chat-page__bubble">
          <div class="chat-page__role">我</div>
          <div class="chat-page__content chat-page__content--plain">{{ msg.content }}</div>
        </div>

        <!-- 助手消息：处理过程（可折叠、执行中滚动）+ 结果 -->
        <div v-else class="chat-page__assistant">
          <div v-if="msg.runState === 'running' || msg.steps.length" class="chat-page__process">
            <button
              type="button"
              class="chat-page__process-head"
              :aria-expanded="msg.processOpen"
              @click="toggleProcess(msg)"
            >
              <span
                v-if="msg.runState === 'running'"
                class="chat-page__process-spinner"
                aria-hidden="true"
              ></span>
              <span v-else class="chat-page__process-dot" aria-hidden="true"></span>
              <span class="chat-page__process-title">{{ processTitle(msg) }}</span>
              <span class="chat-page__process-toggle">{{ msg.processOpen ? '收起' : '展开' }}</span>
            </button>
            <ul
              v-show="msg.processOpen"
              class="chat-page__process-list"
              :ref="(el) => setProcessRef(msg.id, el)"
            >
              <li
                v-for="(step, stepIndex) in msg.steps"
                :key="stepIndex"
                class="chat-page__process-item"
              >
                <span
                  v-if="step.agentLabel"
                  class="chat-page__process-agent"
                  :data-agent="step.agent || ''"
                  >{{ step.agentLabel }}</span
                >
                <span class="chat-page__process-stage">{{ step.stage }}</span>
                <span class="chat-page__process-message">{{ step.message }}</span>
                <!-- 结构化查询这一步带上本次生成的 SQL：学员可对照数据库核对 -->
                <pre v-if="step.sql" class="chat-page__process-sql">{{ step.sql }}</pre>
              </li>
            </ul>
          </div>

          <!-- 结果：执行过程结束后才出现 -->
          <div v-if="msg.content || msg.meta || msg.runId" class="chat-page__bubble">
            <div class="chat-page__role">助手</div>
            <div class="chat-page__content" v-html="renderMarkdown(msg.content)"></div>
            <div v-if="msg.meta" class="chat-page__meta">{{ msg.meta }}</div>
            <div
              v-if="msg.runId || msg.content || msg.runState === 'error'"
              class="chat-page__feedback"
            >
              <template v-if="msg.runId && msg.runState !== 'running'">
                <el-tooltip content="有用（评价会记录到运行历史，可随时修改）" placement="top">
                  <el-button
                    size="small"
                    text
                    :icon="Select"
                    :type="msg.feedback === 1 ? 'primary' : ''"
                    aria-label="有用"
                    @click="handleFeedback(msg, 1)"
                  />
                </el-tooltip>
                <el-tooltip content="没用（评价会记录到运行历史，可随时修改）" placement="top">
                  <el-button
                    size="small"
                    text
                    :icon="Close"
                    :type="msg.feedback === -1 ? 'danger' : ''"
                    aria-label="没用"
                    @click="handleFeedback(msg, -1)"
                  />
                </el-tooltip>
              </template>
              <el-tooltip v-if="msg.content" content="复制回答" placement="top">
                <el-button
                  size="small"
                  text
                  :icon="DocumentCopy"
                  aria-label="复制回答"
                  @click="handleCopy(msg)"
                />
              </el-tooltip>
              <el-button
                v-if="msg.runId && msg.content && ['done', 'awaiting'].includes(msg.runState)"
                size="small" text type="primary"
                :loading="savingReportId === msg.runId"
                :disabled="loading"
                @click="handleSaveReport(msg)"
              >{{ msg.reportId ? '查看诊断报告' : '保存诊断报告' }}</el-button>
              <el-button
                v-if="msg.runId && ['interrupted', 'error'].includes(msg.runState)"
                size="small"
                text
                type="primary"
                :icon="RefreshRight"
                :disabled="loading"
                @click="resumeMessage(msg)"
              >
                继续生成回答
              </el-button>
              <el-tooltip v-if="msg.runState === 'error'" content="重新提问" placement="top">
                <el-button
                  size="small"
                  text
                  type="primary"
                  :icon="RefreshRight"
                  aria-label="重新提问"
                  :disabled="loading"
                  @click="retryMessage(msg)"
                />
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 商品复核或后台配置在核对差异后确认执行 -->
    <div class="content-card chat-page__pending" v-if="pendingAction">
      <div class="chat-page__pending-title">{{ configurationPending ? '确认后台业务操作' : '确认商品复核' }}</div>
      <p class="chat-page__pending-msg">{{ pendingAction.message }}</p>
      <p class="chat-page__pending-reason" v-if="pendingAction.reason">
        {{ pendingAction.reason }}
      </p>
      <ul class="chat-page__pending-list">
        <li v-for="(act, idx) in pendingAction.actions || []" :key="idx">
          <strong>{{ act.title || act.type }}</strong>
          <div v-for="change in act.changes || []" :key="change.key" class="chat-page__configuration-diff">
            {{ change.label }}：<span>{{ change.before }}</span> → <strong>{{ change.after }}</strong>
          </div>
          <small v-if="act.notice" class="chat-page__configuration-note">{{ act.notice }}</small>
        </li>
      </ul>
      <div class="chat-page__pending-actions">
        <el-button :disabled="confirming || loading" @click="handleRejectActions">取消</el-button>
        <el-button type="primary" :loading="confirming" :disabled="loading" @click="handleApproveActions">
          {{ configurationPending ? '确认执行操作' : '确认标记待复核' }}
        </el-button>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="content-card chat-page__composer">
      <el-input
        v-model="input"
        type="textarea"
        :rows="3"
        maxlength="1000"
        show-word-limit
        aria-label="分析问题"
        placeholder="例如：创建一个含 256GB / 512GB 规格的商品，或调整库存、满减和订单配置…"
        :disabled="loading || Boolean(pendingCloudApproval)"
        @keydown.enter.exact="handleInputEnter"
      />
      <div v-if="pendingCloudApproval" class="chat-page__cloud-consent" role="status" aria-live="polite">
        <div class="chat-page__cloud-consent-copy">
          <strong>确认本次云端模型调用</strong>
          <span>
            本次问题及分析上下文（可能包含商品、订单或评价信息）将发送给
            {{ pendingCloudApproval.profile.vendor || pendingCloudApproval.profile.provider || '云端服务' }}
            的 {{ pendingCloudApproval.profile.name || pendingCloudApproval.profile.model }}。
          </span>
        </div>
        <div class="chat-page__cloud-consent-actions">
          <el-button size="small" @click="cancelCloudApproval">取消</el-button>
          <el-button size="small" @click="confirmCloudApproval(false)">
            仅本次同意
          </el-button>
          <el-button size="small" type="primary" @click="confirmCloudApproval(true)">
            同意并记住，以后免询问
          </el-button>
        </div>
      </div>
      <div class="chat-page__actions">
        <div class="chat-page__action-notes">
          <span class="chat-page__hint">Enter 发送 · Shift + Enter 换行</span>
          <a
            class="chat-page__settings-link"
            :href="agentModelSettingsUrl"
            target="_blank"
            rel="noopener noreferrer"
          >
            ⚙ 前往设置模型 ↗
          </a>
          <span v-if="rememberedCloudConsentKey" class="chat-page__consent-status">
            已记住一个云端模型授权（切换模型会重新确认）
            <el-button link size="small" @click="forgetCloudConsent">撤销记住</el-button>
          </span>
        </div>
        <div class="chat-page__buttons">
          <el-button @click="handleClear" :disabled="loading || Boolean(pendingCloudApproval)">清空</el-button>
          <el-button v-if="loading" @click="handleStop">停止生成</el-button>
          <el-button
            type="primary"
            :loading="loading"
            :disabled="loading || Boolean(pendingCloudApproval) || !input.trim()"
            @click="handleSend()"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onActivated, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close, DocumentCopy, RefreshRight, Select } from '@element-plus/icons-vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { useRoute, useRouter } from 'vue-router'
import { getUserInfo } from '@/utils/auth'
import { streamChat, confirmActions, getRunAnswerContext, submitModelResult, saveRunReport } from '@/api/chat'
import { submitFeedback, updateRunAnswer } from '@/api/observability'
import { clearChatMessages, loadChatMessages, saveChatMessages } from '@/utils/chatCache'
import {
  completeWithAgentModel,
  getAgentModelSettingsUrl,
  getActiveAgentModel,
  isCloudAgentModel
} from '@/utils/agentModel'

// 组件名用于 Layout 中 keep-alive 的 include 匹配：切换菜单时保留会话
defineOptions({ name: 'Chat' })

const savingReportId = ref(null)

async function handleSaveReport(msg) {
  if (savingReportId.value) return
  if (!msg.reportId) {
    savingReportId.value = msg.runId
    try {
      await updateRunAnswer(msg.runId, msg.content)
      const response = await saveRunReport(msg.runId)
      msg.reportId = response.data?.report_id
      ElMessage.success(response.data?.reused ? '这次分析已保存过报告' : '诊断报告已保存')
    } finally { savingReportId.value = null }
  }
  if (msg.reportId) router.push({ path: '/manager/reports', query: { tab: 'reports', reportId: msg.reportId } })
}

// 空状态示例问题：点击直接发送（措辞会影响路由，示例覆盖结构化/语义/高风险三条路径）
const exampleQuestions = [
  '静音蓝牙耳机的差评有哪些？',
  '查看当前订单和运费配置',
  '帮我生成一个多规格商品上架方案',
  'AI 可以帮我操作哪些后台功能？',
  '轻云运动跑鞋的差评有点多，帮我看看并处理'
]

const input = ref('')
const route = useRoute()
const router = useRouter()
const loading = ref(false)
const confirming = ref(false)
const pendingCloudApproval = ref(null)
const agentModelSettingsUrl = getAgentModelSettingsUrl()
const CLOUD_CONSENT_STORAGE_KEY = 'ecom-analysis-agent.cloud-model-consent.v1'
const rememberedCloudConsentKey = ref(readRememberedCloudConsent())
const messagesRef = ref(null)
const pendingAction = ref(null)
const configurationPending = computed(() => pendingAction.value?.actions?.some(action => ['update_mall_setting', 'update_coupon', 'manage_business'].includes(action.type)))
// 是否跟随到底部：用户主动上滑阅读时不再强行拉回
const stickToBottom = ref(true)
// 过程区列表的 DOM 引用表：messageId -> <ul> 元素
const processRefs = new Map()
// 当前处于“等待人工确认”的助手消息（确认/取消后往它上面追加执行步骤）
let pendingOwner = null

// 页面刷新会断开流，待确认操作从运行历史重新读取，避免展示失效的内存状态。
const restoredMessages = loadChatMessages().map((msg) => {
  if (msg?.role !== 'assistant') return msg
  const wasRunning = msg.runState === 'running'
  const wasAwaiting = msg.runState === 'awaiting'
  return {
    ...msg,
    processOpen: false,
    runState: wasRunning || wasAwaiting ? 'interrupted' : msg.runState,
    meta: wasAwaiting || wasRunning ? '页面连接已断开，可继续已保存的分析' : msg.meta
  }
})
const messages = ref(restoredMessages)

// 从失效的历史确认记录重新分析时，先把原问题带入输入框，不自动提交。
watch(
  () => route.query.prefill,
  (question) => {
    if (typeof question !== 'string') return
    input.value = question
    const query = { ...route.query }
    delete query.prefill
    router.replace({ path: route.path, query })
  },
  { immediate: true }
)

// 消息自增 id：用于过程区列表的 DOM 引用与滚动定位
let messageSeq = restoredMessages.reduce((max, msg) => Math.max(max, msg.id || 0), 0)

// 会话写回本地缓存（节流，避免流式输出期间频繁写入）
let saveTimer = null
watch(
  messages,
  () => {
    if (saveTimer) return
    saveTimer = setTimeout(() => {
      saveTimer = null
      saveChatMessages(messages.value)
    }, 400)
  },
  { deep: true }
)

// 运行中每秒刷新一次，用于过程区显示“已用 N 秒”（长步骤期间也能看出没卡住）
const nowTick = ref(Date.now())
let tickTimer = null
watch(loading, (running) => {
  if (running) {
    nowTick.value = Date.now()
    if (!tickTimer) {
      tickTimer = setInterval(() => {
        nowTick.value = Date.now()
      }, 1000)
    }
  } else if (tickTimer) {
    clearInterval(tickTimer)
    tickTimer = null
  }
})

onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer)
  saveChatMessages(messages.value)
  abortController?.abort(new DOMException('page_unmounted', 'AbortError'))
  if (tickTimer) {
    clearInterval(tickTimer)
    tickTimer = null
  }
})

function handleInputEnter(event) {
  // 中文输入法选词时的 Enter 不触发提交；Shift + Enter 由浏览器默认插入换行
  if (event.isComposing) return
  event.preventDefault()
  handleSend()
}

let abortController = null
let resumePreparationId = 0

function renderMarkdown(text) {
  const html = marked.parse(text || '', { async: false })
  return DOMPurify.sanitize(html)
}

async function scrollToBottom(force = false) {
  await nextTick()
  if (!force && !stickToBottom.value) return
  const el = messagesRef.value
  if (el) {
    el.scrollTop = el.scrollHeight
    stickToBottom.value = true
  }
}

function handleMessagesScroll() {
  const el = messagesRef.value
  if (!el) return
  stickToBottom.value = el.scrollTop + el.clientHeight >= el.scrollHeight - 60
}

// 回到会话最新位置：消息列表贴底，展开着的处理过程也贴底
function restoreBottom() {
  stickToBottom.value = true
  scrollToBottom(true)
  for (const msg of messages.value) {
    if (msg.processOpen) scrollProcessList(msg)
  }
}

// 刷新后恢复会话时，直接定位到最新一条
onMounted(() => {
  if (messages.value.length) {
    restoreBottom()
  }
})

// keep-alive 切走时内部滚动容器会被摘出文档，浏览器把 scrollTop 归零；
// 切回来要重新贴底，否则每次从别的页面回来都停在最上面
onActivated(() => {
  if (!messages.value.length) return
  restoreBottom()
  // 首帧高度可能还没稳定，下一帧再补一次
  requestAnimationFrame(() => restoreBottom())
})

function setProcessRef(messageId, el) {
  if (el) {
    processRefs.set(messageId, el)
  } else {
    processRefs.delete(messageId)
  }
}

function scrollProcessList(msg) {
  if (!msg?.processOpen) return
  const el = processRefs.get(msg.id)
  if (el) {
    el.scrollTop = el.scrollHeight
  }
}

// 过程区标题：执行中（带步数）/ 已完成（步数、耗时）/ 等待确认 / 失败 / 已停止
function processTitle(msg) {
  switch (msg.runState) {
    case 'running': {
      const stepText = msg.steps.length ? ` · 已 ${msg.steps.length} 步` : ''
      const seconds = msg.startedAt
        ? Math.max(0, Math.floor((nowTick.value - msg.startedAt) / 1000))
        : 0
      return `正在处理…${stepText} · ${seconds} 秒`
    }
    case 'awaiting':
      return `已处理 · ${msg.steps.length} 步 · 等待人工确认`
    case 'done': {
      const seconds = msg.elapsedMs != null ? ` · ${(msg.elapsedMs / 1000).toFixed(1)} 秒` : ''
      return `已处理 · ${msg.steps.length} 步${seconds}`
    }
    case 'error':
      return `处理失败 · ${msg.steps.length} 步`
    case 'interrupted':
      return `回答待继续 · ${msg.steps.length} 步`
    case 'stopped':
      return `已停止 · ${msg.steps.length} 步`
    default:
      return '处理过程'
  }
}

// 过程项的字段只在这里组装：agent_step 与 status 两条事件走同一个映射，
// 避免出现「某个字段只在一个分支里取、另一个分支丢掉」的问题（SQL 就踩过）
function toStep(data, fallbackStage) {
  return {
    stage: data.stage || data.node || fallbackStage,
    message: data.message || '',
    agent: data.agent || '',
    agentLabel: data.agent_label || '',
    sql: data.sql || ''
  }
}

function pushStep(msg, step) {
  if (!msg) return
  msg.steps.push(step)
  nextTick(() => {
    scrollProcessList(msg)
    scrollToBottom()
  })
}

function toggleProcess(msg) {
  msg.processOpen = !msg.processOpen
  if (msg.processOpen) {
    nextTick(() => scrollProcessList(msg))
  }
}

function createAssistantMessage(question) {
  return {
    id: ++messageSeq,
    role: 'assistant',
    content: '',
    meta: '',
    runId: null,
    feedback: null,
    steps: [],
    runState: 'running',
    elapsedMs: null,
    processOpen: true,
    startedAt: Date.now(),
    question
  }
}

// 取最近几轮对话带上后端：多轮指代消解要用（「看下它的评价」里的「它」）
function buildHistory(endIndex) {
  return messages.value
    .slice(0, endIndex)
    .filter((msg) => msg.content)
    .slice(-6)
    .map((msg) => ({ role: msg.role, content: msg.content.slice(0, 500) }))
}

async function loadAgentModel() {
  try {
    return await getActiveAgentModel()
  } catch (error) {
    ElMessage.error(error.message || '读取 Agent 当前模型失败')
    return null
  }
}

function cancelCloudApproval() {
  const pending = pendingCloudApproval.value
  if (pending && !pending.retryMessage && !input.value.trim()) {
    input.value = pending.question
  }
  pendingCloudApproval.value = null
}

function readRememberedCloudConsent() {
  try {
    return window.localStorage.getItem(cloudConsentStorageKey()) || ''
  } catch {
    return ''
  }
}

function cloudConsentStorageKey() {
  const user = getUserInfo()
  const owner = user?.id ?? user?.username ?? 'anonymous'
  return `${CLOUD_CONSENT_STORAGE_KEY}:${owner}`
}

function cloudConsentKey(profile) {
  return JSON.stringify([
    profile?.provider || profile?.vendor || '',
    profile?.endpoint || '',
    profile?.model || ''
  ])
}

function hasRememberedCloudConsent(profile) {
  return rememberedCloudConsentKey.value === cloudConsentKey(profile)
}

function rememberCloudConsent(profile) {
  const key = cloudConsentKey(profile)
  try {
    window.localStorage.setItem(cloudConsentStorageKey(), key)
    rememberedCloudConsentKey.value = key
  } catch {
    ElMessage.warning('浏览器无法记住授权；本次仍会继续发送')
  }
}

function forgetCloudConsent() {
  try {
    window.localStorage.removeItem(cloudConsentStorageKey())
  } catch {
    // 即使浏览器存储不可用，也立即在当前页面撤销记忆状态。
  }
  rememberedCloudConsentKey.value = ''
  ElMessage.success('已撤销记住的云端模型授权')
}

async function runStream(question, assistantMsg, history, modelProfile) {
  const controller = new AbortController()
  abortController = controller
  try {
    await streamChat(question, {
      signal: controller.signal,
      history,
      useAgentModel: true,
      onAgentStep(data) {
        pushStep(assistantMsg, toStep(data, 'agent'))
      },
      onStatus(data) {
        if (data.run_id) assistantMsg.runId = data.run_id
        // agent_step 已覆盖带角色的过程；这里只补裸 status（如 answering）
        if (data.agent_label) return
        pushStep(assistantMsg, toStep(data, 'status'))
      },
      onRoute(data) {
        const label = {
          structured: '结构化查询', semantic: '语义检索', conversation: '模型对话', management: '后台业务'
        }[data.route] || '查询规划'
        pushStep(assistantMsg, {
          stage: 'route',
          message: `路由 → ${label}：${data.reason || ''}`,
          agent: data.agent || 'analysis',
          agentLabel: data.agent_label || '查询分析 Agent'
        })
      },
      onToken(data) {
        assistantMsg.content += data.content || ''
        scrollToBottom()
      },
      async onAgentModelRequest(data) {
        const label = modelProfile.name || modelProfile.model
        assistantMsg.agentModelLabel = label
        assistantMsg.runId = data.run_id || assistantMsg.runId
        pushStep(assistantMsg, { stage: 'model', message: `使用「${label}」${data.purpose}`, agentLabel: '当前模型' })
        let requestMessages = data.messages || []
        const startedAt = Date.now()
        try {
          for (let attempt = 0; attempt < 2; attempt += 1) {
            const remaining = (data.timeout_ms || 120000) - (Date.now() - startedAt) - 1000
            if (remaining <= 0) throw new Error('当前模型规划超时，请重试')
            const content = await completeWithAgentModel(modelProfile, requestMessages, controller.signal, {
              maxTokens: 4096, timeoutMs: remaining
            })
            const response = await submitModelResult(data.run_id, data.request_id, content)
            const result = response.data || {}
            if (result.accepted) return
            if (result.expired || attempt === 1) throw new Error(result.error || '模型查询规划校验失败')
            pushStep(assistantMsg, { stage: 'model_validation', message: '模型结果未通过查询校验，正在修正一次', agentLabel: '当前模型' })
            requestMessages = [
              ...requestMessages,
              { role: 'assistant', content },
              { role: 'user', content: `校验未通过：${result.error}。保留原问题全部条件，修正后按要求重新输出。` }
            ]
          }
        } catch (error) {
          try { await submitModelResult(data.run_id, data.request_id, '', error.message || '模型请求已停止', controller.signal.aborted) } catch { /* 已失效请求无需重复提交 */ }
          throw error
        }
      },
      async onAgentModelContext(data) {
        const modelLabel = modelProfile.name || modelProfile.model
        assistantMsg.agentModelLabel = modelLabel
        assistantMsg.runId = data.run_id || assistantMsg.runId
        pushStep(assistantMsg, {
          stage: 'answering',
          message: `正在使用 Agent 控制台模型「${modelLabel}」生成回答`,
          agent: 'analysis',
          agentLabel: 'Agent 模型'
        })
        assistantMsg.content = await completeWithAgentModel(
          modelProfile,
          data.messages || [],
          controller.signal
        )
        if (data.run_id) {
          try {
            await updateRunAnswer(data.run_id, assistantMsg.content)
          } catch {
            ElMessage.warning('回答已生成，但运行历史摘要保存失败')
          }
        }
        scrollToBottom()
      },
      onActionPending(data) {
        pendingAction.value = data
        pendingOwner = assistantMsg
        assistantMsg.runState = 'awaiting'
        pushStep(assistantMsg, {
          stage: 'action_pending',
          message: data.message || '等待人工确认动作',
          agent: 'decision',
          agentLabel: '报告决策 Agent'
        })
      },
      onDone(data) {
        const parts = []
        if (data.route === 'structured') parts.push('结构化查询')
        if (data.route === 'semantic') parts.push('语义检索')
        if (data.route === 'conversation') parts.push('模型对话')
        if (assistantMsg.agentModelLabel) parts.push(`Agent 模型：${assistantMsg.agentModelLabel}`)
        assistantMsg.meta = parts.join(' · ')
        if (data.elapsed_ms != null) {
          assistantMsg.elapsedMs = data.elapsed_ms
        }
        assistantMsg.runState = data.awaiting_confirmation ? 'awaiting' : 'done'
        // 处理完成自动收起，点击标题可展开查看完整过程
        assistantMsg.processOpen = false
        if (data.run_id) {
          assistantMsg.runId = data.run_id
        }
        scrollToBottom()
      },
      onError(data) {
        const msg = data.message || '对话失败'
        if (!assistantMsg.content) {
          assistantMsg.content = msg
        } else {
          ElMessage.error(msg)
        }
        assistantMsg.meta = '出错'
        assistantMsg.runState = 'error'
        assistantMsg.processOpen = false
        if (data.run_id) {
          assistantMsg.runId = data.run_id
        }
        scrollToBottom()
      }
    })
  } catch (err) {
    if (controller.signal.aborted && controller.signal.reason?.message === 'user_stop') {
      assistantMsg.meta = '你已停止本次回答'
      assistantMsg.runState = 'stopped'
    } else {
      assistantMsg.meta = controller.signal.aborted
        ? '页面连接已断开，可继续已保存的分析'
        : err.message || '连接异常，回答尚未完成'
      assistantMsg.runState = assistantMsg.runId ? 'interrupted' : 'error'
      assistantMsg.processOpen = false
    }
  } finally {
    if (abortController === controller) {
      loading.value = false
      abortController = null
    }
    await scrollToBottom()
  }
}

function restoreSavedRun(msg, data) {
  if (data.answer) {
    msg.content = data.answer
    msg.meta = '已恢复保存的回答'
    msg.runState = 'done'
  }
  if (data.pending_action && (data.answer || msg.content)) {
    pendingAction.value = data.pending_action
    pendingOwner = msg
    msg.runState = 'awaiting'
  }
  return Boolean(data.answer)
}

async function resumeMessage(msg) {
  if (loading.value || !msg.runId) return
  const preparationId = ++resumePreparationId
  loading.value = true
  try {
    const response = await getRunAnswerContext(msg.runId)
    if (preparationId !== resumePreparationId) return
    const data = response.data || {}
    if (restoreSavedRun(msg, data)) return
    if (!data.messages?.length) {
      msg.meta = data.status === 'running'
        ? '后台还在分析，稍后可点击继续获取结果'
        : '这条旧记录没有保存回答上下文，请重新提问一次；新记录支持继续回答'
      return
    }
    const profile = await loadAgentModel()
    if (preparationId !== resumePreparationId) return
    if (!profile) return
    if (isCloudAgentModel(profile) && !hasRememberedCloudConsent(profile)) {
      pendingCloudApproval.value = { question: msg.question, profile, resumeMessage: msg }
      return
    }
    await startResume(msg, profile, data)
  } finally {
    if (preparationId === resumePreparationId && !abortController) loading.value = false
  }
}

async function startResume(msg, profile, savedData = null) {
  loading.value = true
  const controller = new AbortController()
  abortController = controller
  msg.runState = 'running'
  msg.meta = ''
  msg.startedAt = Date.now()
  try {
    const data = savedData || (await getRunAnswerContext(msg.runId)).data || {}
    if (restoreSavedRun(msg, data)) return
    if (!data.messages?.length) throw new Error('分析上下文暂不可用，请稍后继续')
    msg.runState = 'running'
    pushStep(msg, { stage: 'answering', message: '使用已保存的分析继续生成回答', agent: 'analysis', agentLabel: 'Agent 模型' })
    const answer = await completeWithAgentModel(profile, data.messages, controller.signal)
    msg.content = answer
    await updateRunAnswer(msg.runId, answer)
    msg.meta = `已根据保存的分析完成回答 · ${profile.name || profile.model}`
    if (data.pending_action) {
      pendingAction.value = data.pending_action
      pendingOwner = msg
    }
    msg.runState = data.pending_action ? 'awaiting' : 'done'
    msg.processOpen = false
  } catch (error) {
    const stoppedByUser = controller.signal.aborted && controller.signal.reason?.message === 'user_stop'
    msg.meta = stoppedByUser ? '你已停止本次回答' : '回答尚未完成，可继续：' + (error.message || '连接已断开')
    msg.runState = stoppedByUser ? 'stopped' : 'interrupted'
  } finally {
    if (abortController === controller) {
      abortController = null
      loading.value = false
    }
  }
}

onMounted(async () => {
  const unfinished = messages.value.filter((msg) => msg.role === 'assistant' && msg.runId && msg.runState === 'interrupted').slice(-5)
  await Promise.allSettled(unfinished.map(async (msg) => {
    const response = await getRunAnswerContext(msg.runId)
    if (!loading.value && msg.runState === 'interrupted') {
      const data = response.data || {}
      if (msg !== messages.value[messages.value.length - 1]) data.pending_action = null
      restoreSavedRun(msg, data)
    }
  }))
})

async function handleSend(presetQuestion) {
  const question = (presetQuestion ?? input.value).trim()
  if (!question) {
    ElMessage.warning('请输入问题')
    return
  }
  if (loading.value) return

  loading.value = true
  const modelProfile = await loadAgentModel()
  if (!modelProfile) {
    loading.value = false
    return
  }
  const history = buildHistory(messages.value.length)
  if (isCloudAgentModel(modelProfile) && !hasRememberedCloudConsent(modelProfile)) {
    pendingCloudApproval.value = { question, history, profile: modelProfile }
    loading.value = false
    return
  }
  await startNewQuestion(question, modelProfile, history)
}

async function startNewQuestion(question, modelProfile, history) {
  loading.value = true
  pendingCloudApproval.value = null
  pendingAction.value = null
  pendingOwner = null
  input.value = ''
  messages.value.push({ id: ++messageSeq, role: 'user', content: question })
  const assistantMsg = createAssistantMessage(question)
  messages.value.push(assistantMsg)
  await scrollToBottom(true)

  await runStream(question, assistantMsg, history, modelProfile)
}

// 失败重试：重置该轮助手消息后按原问题重新执行
async function retryMessage(msg) {
  if (loading.value || !msg?.question) return
  loading.value = true
  const modelProfile = await loadAgentModel()
  if (!modelProfile) {
    loading.value = false
    return
  }
  const history = buildHistory(messages.value.indexOf(msg))
  if (isCloudAgentModel(modelProfile) && !hasRememberedCloudConsent(modelProfile)) {
    pendingCloudApproval.value = { question: msg.question, history, profile: modelProfile, retryMessage: msg }
    loading.value = false
    return
  }
  await startRetry(msg, modelProfile, history)
}

async function confirmCloudApproval(remember = false) {
  const pending = pendingCloudApproval.value
  if (!pending || loading.value) return
  if (remember) rememberCloudConsent(pending.profile)
  pendingCloudApproval.value = null
  if (pending.resumeMessage) {
    await startResume(pending.resumeMessage, pending.profile)
  } else if (pending.retryMessage) {
    await startRetry(pending.retryMessage, pending.profile, pending.history)
  } else {
    await startNewQuestion(pending.question, pending.profile, pending.history)
  }
}

async function startRetry(msg, modelProfile, history) {
  loading.value = true
  pendingCloudApproval.value = null
  pendingAction.value = null
  pendingOwner = null
  Object.assign(msg, {
    content: '',
    meta: '',
    agentModelLabel: '',
    runId: null,
    feedback: null,
    steps: [],
    runState: 'running',
    elapsedMs: null,
    processOpen: true
  })
  await runStream(msg.question, msg, history, modelProfile)
}

// 确认/取消后：把执行结果追加到待确认的那轮对话，过程区收尾
function finishPendingRun(message, isError = false, answer = null) {
  const msg = pendingOwner || messages.value[messages.value.length - 1]
  if (!msg || msg.role !== 'assistant') return
  if (answer) msg.content = answer
  else if (configurationPending.value) msg.content = `${msg.content || ''}\n\n**配置执行结果**\n\n${message}`
  pushStep(msg, {
    stage: 'executing',
    message,
    agent: 'decision',
    agentLabel: '报告决策 Agent'
  })
  msg.runState = isError ? 'error' : 'done'
  msg.processOpen = false
  pendingOwner = null
}

async function handleApproveActions() {
  if (!pendingAction.value?.thread_id || confirming.value) return
  confirming.value = true
  try {
    const res = await confirmActions(pendingAction.value.thread_id, true)
    const executed = res.data?.actions_executed || []
    ElMessage.success(res.data?.status_message || `已执行 ${executed.length} 个动作`)
    finishPendingRun(res.data?.status_message || `已确认并执行 ${executed.length} 个动作`, false, res.data?.answer)
    window.dispatchEvent(new Event('mall-settings-updated'))
    pendingAction.value = null
  } catch (e) {
    finishPendingRun(e?.message || '确认失败，请重新提问后核对配置', true)
  } finally {
    confirming.value = false
  }
}

async function handleRejectActions() {
  if (!pendingAction.value?.thread_id || confirming.value) return
  confirming.value = true
  try {
    const res = await confirmActions(pendingAction.value.thread_id, false)
    ElMessage.info(res.data?.status_message || '已取消执行')
    finishPendingRun(res.data?.status_message || '用户取消，未执行动作', false, res.data?.answer)
    pendingAction.value = null
  } catch (e) {
    finishPendingRun('取消失败：任务可能已失效，请重新提问后再试', true)
  } finally {
    confirming.value = false
  }
}

function handleStop() {
  resumePreparationId += 1
  if (abortController) {
    abortController.abort(new DOMException('user_stop', 'AbortError'))
    abortController = null
  }
  loading.value = false
  const last = messages.value[messages.value.length - 1]
  if (last?.role === 'assistant' && !last.meta) {
    last.meta = '已停止'
    last.runState = 'stopped'
  }
}

async function handleClear() {
  if (!messages.value.length) return
  try {
    await ElMessageBox.confirm('确定清空当前对话吗？本地缓存也会一并删除。', '提示', {
      type: 'warning',
      confirmButtonText: '清空',
      cancelButtonText: '取消'
    })
  } catch (e) {
    return
  }
  handleStop()
  messages.value = []
  pendingAction.value = null
  pendingOwner = null
  processRefs.clear()
  clearChatMessages()
  input.value = ''
}

async function handleCopy(msg) {
  if (!msg?.content) return
  try {
    await navigator.clipboard.writeText(msg.content)
    ElMessage.success('已复制')
  } catch (e) {
    ElMessage.error('复制失败，请手动选择文本')
  }
}

async function handleFeedback(msg, rating) {
  // 允许修改评分：点同一个按钮不重复提交，换一个按钮覆盖为最新评价
  if (!msg?.runId || msg.feedback === rating) return
  try {
    await submitFeedback(msg.runId, rating)
    msg.feedback = rating
    ElMessage.success(rating === 1 ? '已标记有用' : '已标记没用')
  } catch (e) {
    ElMessage.error('反馈提交失败')
  }
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-gap);
  height: 100%;
  min-height: 480px;
}

/* ---------- 处理过程（可折叠） ---------- */

.chat-page__process {
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #f8fafc;
  overflow: hidden;
}

.chat-page__process-head {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: var(--app-text-secondary);
  text-align: left;
}

.chat-page__process-head:hover {
  background: rgba(15, 23, 42, 0.04);
}

.chat-page__process-title {
  flex: 1;
  min-width: 0;
}

.chat-page__process-toggle {
  flex: 0 0 auto;
  font-size: 12px;
  color: var(--el-color-primary);
}

.chat-page__process-spinner {
  flex: 0 0 auto;
  width: 12px;
  height: 12px;
  border: 2px solid var(--el-color-primary-light-7);
  border-top-color: var(--el-color-primary);
  border-radius: 50%;
  animation: chat-spin 0.8s linear infinite;
}

.chat-page__process-dot {
  flex: 0 0 auto;
  width: 6px;
  height: 6px;
  margin: 0 3px;
  border-radius: 50%;
  background: var(--app-text-secondary);
}

@keyframes chat-spin {
  to {
    transform: rotate(360deg);
  }
}

.chat-page__process-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 220px;
  overflow-y: auto;
  padding: 8px 12px 10px;
  border-top: 1px solid var(--app-border);
}

.chat-page__process-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
  line-height: 1.5;
  flex-wrap: wrap;
}

/* 过程里的 SQL：整行分段显示，等宽字体便于逐句讲解 */
.chat-page__process-sql {
  width: 100%;
  margin: 2px 0 4px;
  padding: 6px 8px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #f8fafc;
  font-family: Consolas, Menlo, monospace;
  font-size: 12px;
  line-height: 1.6;
  color: var(--app-text);
  white-space: pre-wrap;
  word-break: break-all;
}

.chat-page__process-agent {
  flex: 0 0 auto;
  font-weight: 600;
  color: var(--el-color-primary);
}

.chat-page__process-agent[data-agent='scheduler'] {
  color: var(--el-color-info);
}

.chat-page__process-agent[data-agent='decision'] {
  color: var(--el-color-warning);
}

.chat-page__process-stage {
  flex: 0 0 auto;
  color: var(--app-text-secondary);
}

/* ---------- 消息 ---------- */

.chat-page__messages {
  flex: 1;
  min-height: 280px;
  overflow-y: auto;
}

.chat-page__empty {
  padding: var(--app-space-card) 0;
  text-align: center;
  color: var(--app-text-secondary);
}

.chat-page__empty-text {
  margin: 0 0 12px;
}

.chat-page__examples {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.chat-page__examples-label {
  font-size: 13px;
}

.chat-page__message {
  display: flex;
  margin-bottom: 12px;
}

.chat-page__message--user {
  justify-content: flex-end;
}

.chat-page__message--assistant {
  justify-content: flex-start;
}

.chat-page__assistant {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 85%;
  min-width: 0;
}

.chat-page__bubble {
  padding: 10px 12px;
  border-radius: var(--app-radius-sm);
  border: 1px solid var(--app-border);
  background: #f8fafc;
}

.chat-page__message--user .chat-page__bubble {
  max-width: 80%;
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
}

.chat-page__role {
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.chat-page__content {
  line-height: 1.6;
  word-break: break-word;
  color: var(--app-text);
}

.chat-page__content--plain {
  white-space: pre-wrap;
}

.chat-page__content :deep(p) {
  margin: 0 0 0.5em;
}

.chat-page__content :deep(p:last-child) {
  margin-bottom: 0;
}

.chat-page__content :deep(ul),
.chat-page__content :deep(ol) {
  padding-left: 1.2em;
  margin: 0.4em 0;
  list-style: disc;
}

.chat-page__meta {
  margin-top: 6px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.chat-page__feedback {
  margin-top: 8px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.chat-page__pending {
  border-style: dashed;
  border-color: var(--el-color-warning);
  background: var(--el-color-warning-light-9);
}

.chat-page__pending-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--app-text);
}

.chat-page__pending-msg,
.chat-page__pending-reason {
  font-size: 13px;
  margin-bottom: 6px;
  line-height: 1.5;
  color: var(--app-text-secondary);
}

.chat-page__pending-list {
  margin: 0 0 10px;
  padding-left: 1.2em;
  list-style: disc;
  font-size: 13px;
}

.chat-page__configuration-diff { margin-top: 8px; font-size: 13px; line-height: 1.6; }
.chat-page__configuration-diff span { color: var(--app-text-secondary); }
.chat-page__configuration-diff strong { color: var(--app-primary); }
.chat-page__configuration-note { display: block; margin-top: 8px; color: var(--app-text-secondary); line-height: 1.6; }

.chat-page__pending-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.chat-page__composer {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-gap);
}

.chat-page__cloud-consent {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 14px;
  border: 1px solid var(--el-color-warning-light-5);
  border-radius: var(--app-radius-sm);
  background: var(--el-color-warning-light-9);
}

.chat-page__cloud-consent-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  color: var(--app-text-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.chat-page__cloud-consent-copy strong {
  color: var(--app-text);
}

.chat-page__cloud-consent-actions {
  display: flex;
  flex: 0 0 auto;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

@media (max-width: 640px) {
  .chat-page__cloud-consent {
    align-items: flex-start;
    flex-direction: column;
  }
}

.chat-page__actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.chat-page__action-notes {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 12px;
  min-width: 0;
}

.chat-page__settings-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 9px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #fff;
  color: var(--app-text);
  font-size: 12px;
  text-decoration: none;
}

.chat-page__settings-link:hover {
  border-color: var(--el-color-primary-light-5);
  color: var(--el-color-primary);
}

.chat-page__consent-status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.chat-page__hint {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.chat-page__buttons {
  display: flex;
  gap: 8px;
}

.chat-page__actions .el-button + .el-button,
.chat-page__pending-actions .el-button + .el-button {
  margin-left: 0;
}

.chat-page__content :deep(table) {
  display: block;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
}

.chat-page__content :deep(th),
.chat-page__content :deep(td) {
  border: 1px solid var(--app-border);
  padding: 8px;
}
</style>
