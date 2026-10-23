<template>
  <div class="page-container staff-message-center" v-loading="loading">
    <section class="content-card staff-message-center__heading">
      <div>
        <h1>消息中心</h1>
        <p>查看新订单发货提醒，处理用户私聊、售后申请和评论回复。</p>
      </div>
      <el-button
        v-if="unreadEventCount"
        text
        :loading="markingAllRead"
        @click="markAllEventsRead"
      >
        通知全部已读
      </el-button>
    </section>

    <section class="content-card staff-inbox">
      <aside class="staff-inbox__sidebar">
        <div class="staff-inbox__tabs">
          <button
            type="button"
            :class="{ 'is-active': activeTab === 'conversations' }"
            @click="selectTab('conversations')"
          >
            售后会话 <span>{{ conversations.length }}</span>
          </button>
          <button
            type="button"
            :class="{ 'is-active': activeTab === 'private' }"
            @click="selectTab('private')"
          >私聊 <span>{{ directConversations.length }}</span></button>
          <button
            type="button"
            :class="{ 'is-active': activeTab === 'events' }"
            @click="selectTab('events')"
          >
            通知 <span v-if="unreadEventCount" class="staff-inbox__tab-badge">{{ unreadEventCount }}</span>
          </button>
        </div>

        <div v-if="activeTab === 'conversations'" class="staff-inbox__list">
          <button
            v-for="conversation in conversations"
            :key="conversation.after_sale_id"
            type="button"
            class="staff-inbox__row"
            :class="{ 'is-selected': selectedAfterSaleId === conversation.after_sale_id }"
            title="左键打开售后会话，右键完成售后"
            @click="selectConversation(conversation.after_sale_id)"
            @contextmenu.prevent="openConversationContextMenu($event, conversation)"
          >
            <span class="staff-inbox__avatar">{{ firstLetter(conversation.user_name || conversation.username) }}</span>
            <span class="staff-inbox__row-main">
              <span class="staff-inbox__row-heading">
                <strong>{{ conversation.user_name || conversation.username }}</strong>
                <time>{{ shortTime(conversation.create_time) }}</time>
              </span>
              <span class="staff-inbox__row-context">{{ conversation.product_name }} · {{ conversation.order_no }}</span>
              <span class="staff-inbox__row-preview">{{ conversationPreview(conversation.preview) }}</span>
            </span>
            <span v-if="conversation.unread_count" class="staff-inbox__unread">
              {{ conversation.unread_count > 99 ? '99+' : conversation.unread_count }}
            </span>
          </button>
          <el-empty v-if="!conversations.length" :image-size="76" description="暂无售后会话" />
        </div>

        <div v-else-if="activeTab === 'events'" class="staff-inbox__list">
          <button
            v-for="event in events"
            :key="event.id"
            type="button"
            class="staff-inbox__row staff-inbox__event-row"
            :class="{
              'is-selected': selectedEventId === event.id,
              'is-unread': !event.is_read
            }"
            @click="selectEvent(event)"
          >
            <span class="staff-inbox__avatar staff-inbox__avatar--event">
              <el-icon><component :is="eventIcon(event.event_type)" /></el-icon>
            </span>
            <span class="staff-inbox__row-main">
              <span class="staff-inbox__row-heading">
                <strong>{{ event.title }}</strong>
                <time>{{ shortTime(event.create_time) }}</time>
              </span>
              <span class="staff-inbox__row-preview">{{ event.content }}</span>
            </span>
            <i v-if="!event.is_read" class="staff-inbox__unread-dot" />
          </button>
          <el-empty v-if="!events.length" :image-size="76" description="暂无新事件" />
        </div>
        <div v-else class="staff-inbox__list">
          <button v-for="conversation in directConversations" :key="conversation.id" type="button" class="staff-inbox__row"
            :class="{ 'is-selected': selectedDirectConversationId === conversation.conversation_id }"
            @click="selectPrivateConversation(conversation.conversation_id)">
            <el-avatar :src="conversation.peer_avatar || undefined">{{ firstLetter(conversation.peer_name) }}</el-avatar>
            <span class="staff-inbox__row-main"><span class="staff-inbox__row-heading"><strong>{{ conversation.peer_name }}</strong><time>{{ shortTime(conversation.create_time) }}</time></span><span class="staff-inbox__row-preview">{{ conversation.preview }}</span></span>
            <span v-if="conversation.unread_count" class="staff-inbox__unread">{{ conversation.unread_count }}</span>
          </button>
          <el-empty v-if="!directConversations.length" :image-size="76" description="暂无私聊，点击订单或售后中的用户即可发起" />
        </div>
      </aside>

      <main class="staff-inbox__main">
        <DirectConversationPanel v-if="activeTab === 'private' && activeDirectConversation" :conversation-id="selectedDirectConversationId" :peer="activeDirectConversation" @updated="loadCenter(false)" />
        <template v-else-if="activeTab === 'conversations' && activeConversation">
          <header class="staff-chat__header">
            <span class="staff-inbox__avatar">{{ firstLetter(activeConversation.user_name || activeConversation.username) }}</span>
            <div>
              <strong>{{ activeConversation.user_name || activeConversation.username }}</strong>
              <span>{{ activeConversation.product_name }} · {{ activeConversation.order_no }}</span>
            </div>
            <el-tag :type="statusTone(activeConversation.status)" effect="light" round>
              {{ applicationStatusLabel(activeConversation) }}
            </el-tag>
            <el-button
              v-if="canCompleteActiveAfterSale"
              type="primary"
              :loading="processingAfterSale"
              :disabled="chatLoading"
              @click="confirmCompletion(afterSaleApplication)"
            >{{ completionActionLabel(afterSaleApplication) }}</el-button>
          </header>

          <div
            ref="messageListRef"
            class="staff-chat__messages"
            @contextmenu.prevent="openConversationContextMenu($event, activeConversation)"
          >
            <el-empty v-if="!afterSaleApplication && !chatMessages.length && !chatLoading" :image-size="90" description="发送第一条消息，开始沟通" />
            <article
              v-if="afterSaleApplication"
              class="staff-chat-application"
              title="右键可完成售后"
            >
              <span class="staff-chat-application__sender">{{ afterSaleApplication.user_name || afterSaleApplication.username }} 提交了售后申请</span>
              <div class="staff-chat-application__card">
                <div class="staff-chat-application__product">
                  <img v-if="afterSaleApplication.image_url" :src="afterSaleApplication.image_url" :alt="afterSaleApplication.product_name">
                  <span v-else class="staff-chat-application__image-placeholder">商品</span>
                  <div>
                    <strong>{{ afterSaleApplication.product_name }}</strong>
                    <span>订单 {{ afterSaleApplication.order_no }}</span>
                  </div>
                </div>
                <div class="staff-chat-application__details">
                  <span>售后类型</span>
                  <el-tag :type="serviceTypeTone(afterSaleApplication.service_type)" effect="light" round>
                    {{ serviceTypeLabel(afterSaleApplication.service_type) }}
                  </el-tag>
                  <el-tag :type="applicationStatusTone(afterSaleApplication.status)" effect="light" round>
                    {{ applicationStatusLabel(afterSaleApplication) }}
                  </el-tag>
                </div>
                <p><span>申请原因：</span>{{ afterSaleApplication.reason }}</p>
                <p v-if="afterSaleApplication.description"><span>补充说明：</span>{{ afterSaleApplication.description }}</p>
                <template v-if="afterSaleApplication.service_type !== 'refund' && ['approved', 'completed'].includes(afterSaleApplication.status)">
                  <p><span>商品寄回：</span>{{ returnShipmentLabel(afterSaleApplication) }}</p>
                  <p><span>寄回物流单号：</span>{{ returnTrackingLabel(afterSaleApplication) }}</p>
                </template>
                <p v-if="afterSaleApplication.exchange_shipping_address"><span>换货收货地址：</span>{{ afterSaleApplication.exchange_shipping_address }}</p>
                <p v-if="afterSaleApplication.exchange_tracking_no"><span>商家发货物流单号：</span>{{ afterSaleApplication.exchange_tracking_no }}</p>
                <div v-if="canCompleteActiveAfterSale" class="staff-chat-application__actions staff-chat-application__completion">
                  <span>{{ afterSaleApplication.service_type === 'return' ? '买家已提交寄回物流，请核对收到的退货。' : '核对处理结果后，确认完成本次售后。' }}</span>
                  <el-button
                    type="primary"
                    :loading="processingAfterSale"
                    :disabled="chatLoading"
                    @click="confirmCompletion(afterSaleApplication)"
                  >{{ completionActionLabel(afterSaleApplication) }}</el-button>
                </div>
                <p v-if="afterSaleApplication.service_rating"><span>售后服务评分：</span>{{ afterSaleApplication.service_rating }} / 5{{ afterSaleApplication.service_feedback ? ` · ${afterSaleApplication.service_feedback}` : '' }}</p>
                <p v-if="afterSaleApplication.admin_note" class="staff-chat-application__reply">
                  <span>处理说明：</span>{{ afterSaleApplication.admin_note }}
                </p>
                <div v-if="canSubmitExchangeShipment" class="staff-chat-application__shipment-form">
                  <label for="exchange-shipment-tracking">商家发货物流单号</label>
                  <el-input
                    id="exchange-shipment-tracking"
                    v-model="exchangeTrackingDraft"
                    maxlength="100"
                    placeholder="用户寄回后，填写换货商品的物流单号"
                  />
                  <el-button
                    type="primary"
                    :loading="exchangeShipmentSubmitting"
                    :disabled="!exchangeTrackingDraft.trim()"
                    @click="submitExchangeShipment"
                  >
                    提交发货单号
                  </el-button>
                </div>
                <div v-if="afterSaleApplication.status === 'pending'" class="staff-chat-application__actions">
                  <span>请审核这条售后申请</span>
                  <div>
                    <el-button
                      type="success"
                      :loading="processingAfterSale"
                      :disabled="processingAfterSale"
                      @click="handleAfterSale('approve')"
                    >
                      同意
                    </el-button>
                    <el-button
                      type="danger"
                      plain
                      :disabled="processingAfterSale"
                      @click="openRejectDialog"
                    >
                      拒绝
                    </el-button>
                  </div>
                </div>
              </div>
              <time>{{ afterSaleApplication.create_time }}</time>
            </article>
            <article
              v-for="message in visibleChatMessages"
              :key="message.id"
              class="staff-chat__message"
              :class="{ 'staff-chat__message--mine': isMine(message) }"
            >
              <span class="staff-chat__message-name">{{ message.sender_name || (message.sender_role === 'customer' ? activeConversation.user_name : '售后客服') }}</span>
              <div class="staff-chat__bubble">{{ message.content }}</div>
              <time>{{ message.create_time || '刚刚' }}</time>
            </article>
          </div>

          <div v-if="isAfterSaleClosed(afterSaleApplication || activeConversation)" class="staff-chat__closed">
            <strong>{{ (afterSaleApplication || activeConversation).status === 'rejected' ? '售后已拒绝' : '售后已完成' }}</strong>
            <span>消息通道已关闭，对话记录仍可查看。</span>
          </div>
          <form v-else class="staff-chat__composer" @submit.prevent="sendMessage">
            <el-input
              v-model="draft"
              type="textarea"
              :rows="2"
              maxlength="2000"
              resize="none"
              placeholder="输入售后沟通内容，按发送与用户沟通"
              @keydown.ctrl.enter.prevent="sendMessage"
            />
            <el-button type="primary" :loading="sending" :disabled="!draft.trim() || chatLoading" native-type="submit">
              发送
            </el-button>
          </form>
        </template>

        <template v-else-if="activeTab === 'events' && activeEvent">
          <div class="staff-event-detail">
            <span class="staff-event-detail__icon">
              <el-icon :size="26"><component :is="eventIcon(activeEvent.event_type)" /></el-icon>
            </span>
            <div class="staff-event-detail__body">
              <span class="staff-event-detail__type">{{ eventTypeLabel(activeEvent.event_type) }}</span>
              <h2>{{ activeEvent.title }}</h2>
              <time>{{ activeEvent.create_time || '时间未知' }}</time>
              <p>{{ activeEvent.content }}</p>
              <el-button
                v-if="activeEvent.event_type === 'order_paid'"
                type="primary"
                @click="openOrder"
              >查看订单并处理发货</el-button>
              <el-button
                v-else-if="activeEvent.event_type === 'review_reply'"
                type="primary"
                @click="router.push({ path: `/manager/products/${activeEvent.product_id}`, query: { review_id: activeEvent.review_id } })"
              >查看评论</el-button>
              <el-button
                v-if="['diagnosis_report', 'alert'].includes(activeEvent.event_type)"
                type="primary"
                @click="openReport"
              >
                {{ activeEvent.event_type === 'alert' ? '查看预警' : '查看诊断报告' }}
              </el-button>
              <el-button
                v-else-if="activeEvent.event_type === 'after_sale_request'"
                type="primary"
                @click="openEventConversation"
              >
                打开售后会话
              </el-button>
            </div>
          </div>
        </template>

        <div v-else class="staff-inbox__placeholder">
          <el-icon :size="42"><ChatDotRound /></el-icon>
          <strong>{{ activeTab === 'conversations' ? '选择一个会话开始沟通' : '选择一条通知查看详情' }}</strong>
          <span>{{ activeTab === 'conversations' ? '售后中心的“沟通”会直接打开对应用户会话。' : '新订单待发货、售后申请和风险提醒会显示在通知列表。' }}</span>
        </div>
      </main>
    </section>

    <div
      v-if="conversationContextMenu"
      class="staff-conversation-menu__backdrop"
      @click="closeConversationContextMenu"
      @contextmenu.prevent="closeConversationContextMenu"
    />
    <div
      v-if="conversationContextMenu"
      class="staff-conversation-menu"
      :style="{ left: `${conversationContextMenu.x}px`, top: `${conversationContextMenu.y}px` }"
      @click.stop
    >
      <button
        type="button"
        class="staff-conversation-menu__action"
        :disabled="Boolean(contextCompletionBlockedReason)"
        @click="completeContextConversation"
      >
        {{ contextCompletionLabel }}
      </button>
      <span v-if="contextCompletionBlockedReason" class="staff-conversation-menu__hint">
        {{ contextCompletionBlockedReason }}
      </span>
    </div>

    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝售后申请"
      width="480px"
      :close-on-click-modal="false"
    >
      <p class="staff-reject-dialog__tip">请填写拒绝原因，用户会在售后消息中收到说明。</p>
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="4"
        maxlength="2000"
        show-word-limit
        placeholder="请说明拒绝原因"
      />
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button
          type="danger"
          :loading="processingAfterSale"
          :disabled="!rejectReason.trim()"
          @click="confirmReject"
        >
          确认拒绝
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell, ChatDotRound, Document, Service, Tickets } from '@element-plus/icons-vue'
import DirectConversationPanel from '@/components/DirectConversationPanel.vue'
import { readReviewNotification } from '@/api/community'
import {
  staffApplicationStatusLabel as applicationStatusLabel, applicationStatusTone, serviceTypeLabel, serviceTypeTone,
  isAfterSaleClosed, completionBlockedReason, completionActionLabel,
  canSubmitExchangeShipment as canShipExchange, returnShipmentLabel, returnTrackingLabel
} from '@/utils/afterSale'
import {
  getAfterSaleMessages,
  getStaffMessageCenter,
  markAllStaffMessageEventsRead,
  markStaffMessageEventRead,
  processAfterSale,
  submitAfterSaleExchangeShipment,
  sendAfterSaleMessage
} from '@/api/ecommerce'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const markingAllRead = ref(false)
const chatLoading = ref(false)
const sending = ref(false)
const processingAfterSale = ref(false)
const rejectDialogVisible = ref(false)
const rejectReason = ref('')
const rejectTargetAfterSaleId = ref(null)
const conversationContextMenu = ref(null)
const events = ref([])
const conversations = ref([])
const directConversations = ref([])
const selectedDirectConversationId = ref(null)
const activeDirectConversation = computed(() => directConversations.value.find(item => item.conversation_id === selectedDirectConversationId.value))
const unreadCount = ref(0)
const activeTab = ref(route.query.tab === 'events' ? 'events' : 'conversations')
const selectedAfterSaleId = ref(null)
const selectedEventId = ref(null)
const chatMessages = ref([])
const visibleChatMessages = computed(() => chatMessages.value.filter((message) =>
  !isAfterSaleShipmentNotice(message.content)
))
const afterSaleApplication = ref(null)
const draft = ref('')
const exchangeTrackingDraft = ref('')
const exchangeShipmentSubmitting = ref(false)
const messageListRef = ref(null)
let refreshTimer = null
let conversationRequestId = 0
let centerRequestId = 0

const activeConversation = computed(() =>
  conversations.value.find((item) => item.after_sale_id === selectedAfterSaleId.value) || null
)
const activeEvent = computed(() => events.value.find((item) => item.id === selectedEventId.value) || null)
const contextConversation = computed(() =>
  conversations.value.find((item) => item.after_sale_id === conversationContextMenu.value?.afterSaleId) || null
)
const contextApplication = computed(() => afterSaleApplication.value?.id === contextConversation.value?.after_sale_id
  ? afterSaleApplication.value : contextConversation.value)
const contextCompletionBlockedReason = computed(() => chatLoading.value ? '正在加载最新售后状态' : completionBlockedReason(contextApplication.value))
const contextCompletionLabel = computed(() => completionActionLabel(contextApplication.value))
const unreadEventCount = computed(() => events.value.filter((item) => !item.is_read).length)
const canSubmitExchangeShipment = computed(() =>
  canShipExchange(afterSaleApplication.value)
)
const canCompleteActiveAfterSale = computed(() =>
  afterSaleApplication.value?.id === selectedAfterSaleId.value &&
  afterSaleApplication.value?.status === 'approved' &&
  !completionBlockedReason(afterSaleApplication.value)
)

function isAfterSaleShipmentNotice(content = '') {
  return content.startsWith('我已寄回商品，物流单号：') ||
    content.startsWith('已提交寄回物流信息，详见售后卡片。') ||
    content.startsWith('商家已提交换货发货物流信息，详见售后卡片。')
}

function conversationPreview(content = '') {
  return isAfterSaleShipmentNotice(content) ? '物流信息已更新，详见售后卡片。' : content
}

function eventIcon(type) {
  return type === 'order_paid' ? Tickets : type === 'diagnosis_report' ? Document : type === 'after_sale_request' ? Service : Bell
}

function eventTypeLabel(type) {
  return type === 'order_paid' ? '订单发货提醒' : type === 'review_reply' ? '评价回复' : type === 'diagnosis_report' ? '诊断报告' : type === 'after_sale_request' ? '售后事件' : type === 'alert' ? '风险预警' : '系统通知'
}

function statusTone(status) {
  return applicationStatusTone(status)
}

function completionConfirmationText(conversation) {
  if (conversation?.service_type === 'return') {
    return '确认已收到买家退回的商品并办理演示退款？确认后会标记为已退货退款，关闭售后会话并邀请买家评价服务。本系统尚未接入支付渠道，此操作不会实际划款。'
  }
  if (conversation?.service_type === 'refund') {
    return '请确认已完成退款。确认后系统会关闭售后会话，并邀请用户评价服务。'
  }
  return '请确认换货流程已完成。确认后系统会关闭售后会话，并邀请用户评价服务。'
}

function firstLetter(value) {
  return String(value || '?').slice(0, 1).toUpperCase()
}

function shortTime(value) {
  if (!value) return ''
  const text = String(value)
  return text.length > 10 ? text.slice(5, 16) : text
}

function isMine(message) {
  return message.sender_role !== 'customer' && message.sender_role !== 'system'
}

async function loadCenter(showLoading = false) {
  if (loading.value) return
  if (showLoading) loading.value = true
  const requestId = ++centerRequestId
  try {
    const response = await getStaffMessageCenter()
    if (requestId !== centerRequestId) return
    events.value = response.data?.events || []
    conversations.value = response.data?.conversations || []
    directConversations.value = response.data?.direct_conversations || []
    unreadCount.value = Number(response.data?.unread_count || 0)
    window.dispatchEvent(new CustomEvent('staff-message-center-updated', { detail: unreadCount.value }))
    const privateId = Number(route.query.conversationId)
    if (privateId && directConversations.value.some(item => item.conversation_id === privateId)) {
      activeTab.value = 'private'
      selectedDirectConversationId.value = privateId
      selectedAfterSaleId.value = null
      return
    }
    const queryId = Number(route.query.afterSaleId)
    if (queryId && queryId !== selectedAfterSaleId.value && conversations.value.some((item) => item.after_sale_id === queryId)) {
      activeTab.value = 'conversations'
      selectedAfterSaleId.value = queryId
      await loadConversation(queryId, chatMessages.value.length === 0)
    }
  } catch (error) {
    if (showLoading) ElMessage.error(error?.message || '加载消息中心失败')
  } finally {
    if (showLoading) loading.value = false
  }
}

async function loadConversation(afterSaleId, scroll = true) {
  if (!afterSaleId) return
  if (chatLoading.value && !scroll) return
  const requestId = ++conversationRequestId
  chatLoading.value = true
  try {
    const response = await getAfterSaleMessages(afterSaleId)
    if (requestId !== conversationRequestId || selectedAfterSaleId.value !== afterSaleId) return
    const nextMessages = response.data?.messages || []
    const changed = nextMessages.at(-1)?.id !== chatMessages.value.at(-1)?.id
    afterSaleApplication.value = response.data?.application || null
    chatMessages.value = nextMessages
    conversations.value = conversations.value.map((item) =>
      item.after_sale_id === afterSaleId ? { ...item, ...afterSaleApplication.value, unread_count: 0 } : item
    )
    const readCount = Number(response.data?.unread_count || 0)
    if (readCount) {
      unreadCount.value = Math.max(0, unreadCount.value - readCount)
      window.dispatchEvent(new CustomEvent('staff-message-center-updated', { detail: unreadCount.value }))
    }
    if (scroll && changed) await scrollToBottom()
  } catch (error) {
    if (requestId === conversationRequestId) ElMessage.error(error?.message || '加载售后会话失败')
  } finally {
    if (requestId === conversationRequestId) chatLoading.value = false
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messageListRef.value) messageListRef.value.scrollTop = messageListRef.value.scrollHeight
}

async function selectConversation(afterSaleId) {
  closeConversationContextMenu()
  activeTab.value = 'conversations'
  selectedEventId.value = null
  selectedAfterSaleId.value = afterSaleId
  conversationRequestId += 1
  draft.value = ''
  exchangeTrackingDraft.value = ''
  chatMessages.value = []
  afterSaleApplication.value = null
  await router.replace({
    path: '/manager/message-center',
    query: { afterSaleId: String(afterSaleId) }
  })
  await loadConversation(afterSaleId)
}

function openConversationContextMenu(event, conversation) {
  const afterSaleId = conversation.after_sale_id
  if (activeTab.value !== 'conversations' || selectedAfterSaleId.value !== afterSaleId) {
    selectConversation(afterSaleId)
  }
  const menuWidth = 200
  const menuHeight = 92
  conversationContextMenu.value = {
    afterSaleId: conversation.after_sale_id,
    x: Math.max(8, Math.min(event.clientX, Math.max(8, window.innerWidth - menuWidth - 8))),
    y: Math.max(8, Math.min(event.clientY, Math.max(8, window.innerHeight - menuHeight - 8)))
  }
}

function closeConversationContextMenu() {
  conversationContextMenu.value = null
}

async function completeContextConversation() {
  const conversation = contextApplication.value
  closeConversationContextMenu()
  await confirmCompletion(conversation)
}

async function confirmCompletion(conversation) {
  if (processingAfterSale.value || chatLoading.value) return
  const afterSaleId = conversation?.after_sale_id || conversation?.id
  const blockedReason = completionBlockedReason(conversation)
  if (blockedReason) {
    ElMessage.info(blockedReason)
    return
  }
  try {
    await ElMessageBox.confirm(
      completionConfirmationText(conversation),
      completionActionLabel(conversation),
      { confirmButtonText: completionActionLabel(conversation), cancelButtonText: '再检查一下', type: 'warning' }
    )
  } catch {
    return
  }
  if (selectedAfterSaleId.value !== afterSaleId) await selectConversation(afterSaleId)
  await handleAfterSale('complete', null, afterSaleId)
}

function selectTab(tab) {
  closeConversationContextMenu()
  if (tab === 'private') {
    conversationRequestId += 1
    selectedAfterSaleId.value = null
    afterSaleApplication.value = null
    chatLoading.value = false
    activeTab.value = 'private'
    const id = selectedDirectConversationId.value || directConversations.value[0]?.conversation_id
    if (id) selectPrivateConversation(id)
    else router.replace({ path: '/manager/message-center', query: {} })
    return
  }
  activeTab.value = tab
  if (tab === 'events') {
    conversationRequestId += 1
    chatLoading.value = false
    selectedAfterSaleId.value = null
    selectedEventId.value = null
    chatMessages.value = []
    afterSaleApplication.value = null
    router.replace({ path: '/manager/message-center', query: {} })
  } else {
    selectedEventId.value = null
    const id = conversations.value[0]?.after_sale_id
    if (id) selectConversation(id)
    else router.replace({ path: '/manager/message-center', query: {} })
  }
}

function selectPrivateConversation(id) {
  closeConversationContextMenu()
  conversationRequestId += 1
  selectedAfterSaleId.value = null
  afterSaleApplication.value = null
  chatLoading.value = false
  activeTab.value = 'private'
  selectedDirectConversationId.value = id
  router.replace({ path: '/manager/message-center', query: { conversationId: String(id) } })
}

async function selectEvent(event) {
  conversationRequestId += 1
  chatLoading.value = false
  afterSaleApplication.value = null
  activeTab.value = 'events'
  selectedAfterSaleId.value = null
  selectedEventId.value = event.id
  chatMessages.value = []
  if (event.is_read) return
  try {
    if (event.event_type === 'review_reply') await readReviewNotification(event.notification_id)
    else await markStaffMessageEventRead(event.id)
    event.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    window.dispatchEvent(new CustomEvent('staff-message-center-updated', { detail: unreadCount.value }))
  } catch (error) {
    ElMessage.error(error?.message || '标记消息失败')
  }
}

async function markAllEventsRead() {
  if (markingAllRead.value) return
  markingAllRead.value = true
  try {
    await markAllStaffMessageEventsRead()
    events.value = events.value.map((item) => ({ ...item, is_read: true }))
    unreadCount.value = [...conversations.value, ...directConversations.value].reduce((sum, item) => sum + Number(item.unread_count || 0), 0)
    window.dispatchEvent(new CustomEvent('staff-message-center-updated', { detail: unreadCount.value }))
    ElMessage.success('通知已全部读完')
  } catch (error) {
    ElMessage.error(error?.message || '标记通知失败')
  } finally {
    markingAllRead.value = false
  }
}

async function sendMessage() {
  const content = draft.value.trim()
  const afterSaleId = activeConversation.value?.after_sale_id
  if (!content || !afterSaleId || sending.value || chatLoading.value || isAfterSaleClosed(afterSaleApplication.value || activeConversation.value)) return
  sending.value = true
  try {
    const response = await sendAfterSaleMessage(afterSaleId, content)
    if (selectedAfterSaleId.value === afterSaleId) {
      chatMessages.value.push(response.data)
      draft.value = ''
      await scrollToBottom()
    }
    await loadCenter(false)
  } catch (error) {
    ElMessage.error(error?.message || '发送售后消息失败')
  } finally {
    sending.value = false
  }
}

async function submitExchangeShipment() {
  const afterSaleId = afterSaleApplication.value?.id
  const trackingNo = exchangeTrackingDraft.value.trim()
  if (!afterSaleId || !trackingNo || exchangeShipmentSubmitting.value) return
  exchangeShipmentSubmitting.value = true
  try {
    await submitAfterSaleExchangeShipment(afterSaleId, trackingNo)
    if (selectedAfterSaleId.value === afterSaleId) exchangeTrackingDraft.value = ''
    ElMessage.success('换货商品发货单号已提交，用户可在消息中心查看')
    await loadCenter(false)
    if (selectedAfterSaleId.value === afterSaleId) await loadConversation(afterSaleId, false)
  } catch (error) {
    ElMessage.error(error?.message || '提交换货发货单号失败')
  } finally {
    exchangeShipmentSubmitting.value = false
  }
}

function openRejectDialog() {
  rejectReason.value = ''
  rejectTargetAfterSaleId.value = afterSaleApplication.value?.id || null
  rejectDialogVisible.value = true
}

async function confirmReject() {
  const reason = rejectReason.value.trim()
  if (!reason) {
    ElMessage.warning('请填写拒绝原因')
    return
  }
  await handleAfterSale('reject', reason, rejectTargetAfterSaleId.value)
}

async function handleAfterSale(action, note = null, targetAfterSaleId = null) {
  const afterSaleId = targetAfterSaleId || afterSaleApplication.value?.id
  if (!afterSaleId || processingAfterSale.value) return
  processingAfterSale.value = true
  try {
    const response = await processAfterSale(afterSaleId, action, note)
    const updated = response.data || {}
    const resultText = {
      approve: '已同意售后申请',
      reject: '已拒绝售后申请',
      complete: '售后已完成，消息通道已关闭'
    }[action]
    conversations.value = conversations.value.map((item) =>
      item.after_sale_id === afterSaleId
        ? { ...item, ...updated, preview: resultText, create_time: updated.processed_at || item.create_time }
        : item
    )
    if (selectedAfterSaleId.value === afterSaleId) await loadConversation(afterSaleId)
    rejectDialogVisible.value = false
    rejectTargetAfterSaleId.value = null
    ElMessage.success(resultText)
    await loadCenter(false)
  } catch (error) {
    ElMessage.error(error?.message || '处理售后申请失败')
  } finally {
    processingAfterSale.value = false
  }
}

function openReport() {
  router.push({
    path: '/manager/reports',
    query: activeEvent.value?.event_type === 'alert'
      ? { tab: 'alerts' }
      : { tab: 'reports', reportId: String(activeEvent.value?.target_id || '') }
  })
}

function openEventConversation() {
  const afterSaleId = activeEvent.value?.target_id
  if (afterSaleId) selectConversation(afterSaleId)
}

function openOrder() {
  const orderId = activeEvent.value?.target_id
  if (orderId) router.push({ path: '/manager/orders', query: { orderId: String(orderId) } })
}

watch(() => route.query.tab, tab => {
  if (tab === 'events' && activeTab.value !== 'events') selectTab('events')
})

watch(
  () => route.query.afterSaleId,
  (id) => {
    const afterSaleId = Number(id)
    if (afterSaleId && afterSaleId !== selectedAfterSaleId.value) {
      selectConversation(afterSaleId)
    }
  }
)
watch(() => route.query.conversationId, id => {
  if (id && (Number(id) !== selectedDirectConversationId.value || activeTab.value !== 'private')) {
    selectPrivateConversation(Number(id))
    loadCenter(false)
  }
})

onMounted(async () => {
  await loadCenter(true)
  refreshTimer = setInterval(async () => {
    if (document.visibilityState === 'visible') {
      await loadCenter(false)
      if (activeConversation.value) loadConversation(activeConversation.value.after_sale_id, false)
    }
  }, 5000)
})

onBeforeUnmount(() => {
  conversationRequestId += 1
  centerRequestId += 1
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.staff-message-center { display: grid; grid-template-rows: auto minmax(0, 1fr); height: 100%; gap: 18px; min-height: 520px; }
.staff-message-center__heading { display: flex; align-items: center; justify-content: space-between; gap: 18px; }
.staff-message-center__heading h1 { margin: 0; color: #102237; font-size: 22px; }
.staff-message-center__heading p { margin: 6px 0 0; color: #728396; font-size: 14px; }
.staff-inbox { display: grid; grid-template-columns: minmax(300px, 360px) minmax(0, 1fr); min-height: 0; overflow: hidden; padding: 0; }
.staff-inbox__sidebar { display: flex; min-height: 0; flex-direction: column; border-right: 1px solid #e5ece8; }
.staff-inbox__tabs { display: grid; grid-template-columns: repeat(3, 1fr); border-bottom: 1px solid #e9efec; }
.staff-inbox__tabs button { display: flex; justify-content: center; align-items: center; gap: 8px; padding: 18px 12px; border: 0; border-bottom: 2px solid transparent; color: #718194; background: transparent; cursor: pointer; font: inherit; }
.staff-inbox__tabs button.is-active { border-bottom-color: #159b83; color: #102237; font-weight: 700; }
.staff-inbox__tabs button span { color: #82919f; font-size: 12px; }
.staff-inbox__tabs button .staff-inbox__tab-badge { min-width: 19px; padding: 2px 6px; border-radius: 999px; color: #fff; background: #ed6b28; }
.staff-inbox__list { min-height: 0; flex: 1; overflow: auto; }
.staff-inbox__row { display: flex; width: 100%; align-items: center; gap: 12px; padding: 15px 14px; border: 0; border-bottom: 1px solid #f0f3f1; color: inherit; background: #fff; cursor: pointer; text-align: left; }
.staff-inbox__row:hover, .staff-inbox__row.is-selected { background: #f2f8f5; }
.staff-inbox__row-main { display: grid; min-width: 0; flex: 1; gap: 5px; }
.staff-inbox__row-heading { display: flex; min-width: 0; align-items: center; justify-content: space-between; gap: 8px; }
.staff-inbox__row-heading strong { overflow: hidden; color: #102237; font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.staff-inbox__row-heading time { flex: none; color: #8a98a6; font-size: 11px; }
.staff-inbox__row-context, .staff-inbox__row-preview { overflow: hidden; color: #77889a; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.staff-inbox__row-preview { color: #627487; }
.staff-inbox__avatar { display: grid; width: 42px; height: 42px; flex: none; place-items: center; border-radius: 50%; color: #087e70; background: #e4f2ed; font-size: 17px; font-weight: 700; }
.staff-inbox__avatar--event { color: #fff; background: #159b83; }
.staff-inbox__event-row.is-unread .staff-inbox__row-heading strong { color: #102237; }
.staff-inbox__unread { display: grid; min-width: 20px; height: 20px; flex: none; place-items: center; padding: 0 5px; border-radius: 999px; color: #fff; background: #ed6b28; font-size: 11px; }
.staff-inbox__unread-dot { width: 8px; height: 8px; flex: none; border-radius: 50%; background: #ed6b28; }
.staff-inbox__main { display: flex; min-width: 0; min-height: 0; flex-direction: column; background: #f8faf9; }
.staff-chat__header { display: flex; align-items: center; gap: 12px; padding: 16px 22px; border-bottom: 1px solid #e5ece8; background: #fff; }
.staff-chat__header > div { display: grid; flex: 1; gap: 4px; }
.staff-chat__header strong { color: #102237; font-size: 15px; }
.staff-chat__header span:not(.staff-inbox__avatar) { color: #7b8b9b; font-size: 12px; }
.staff-chat__messages { display: flex; min-height: 0; flex: 1; flex-direction: column; gap: 14px; overflow: auto; padding: 22px; }
.staff-chat__message { display: flex; max-width: min(76%, 680px); flex-direction: column; align-items: flex-start; gap: 5px; }
.staff-chat__message--mine { align-self: flex-end; align-items: flex-end; }
.staff-chat__message-name, .staff-chat__message time { color: #8997a5; font-size: 11px; }
.staff-chat__bubble { padding: 10px 14px; border: 1px solid #e6ece9; border-radius: 4px 14px 14px; color: #26384b; background: #fff; line-height: 1.65; white-space: pre-wrap; overflow-wrap: anywhere; }
.staff-chat__message--mine .staff-chat__bubble { border-color: #cae8df; border-radius: 14px 4px 14px 14px; background: #e8f6f0; }
.staff-chat-application { display: grid; width: min(82%, 620px); align-self: flex-start; justify-items: start; gap: 5px; }
.staff-chat-application__sender, .staff-chat-application > time { color: #8997a5; font-size: 11px; }
.staff-chat-application__card { display: grid; width: 100%; gap: 12px; padding: 14px; border: 1px solid #e1e9e5; border-radius: 4px 14px 14px; background: #fff; }
.staff-chat-application__product { display: flex; min-width: 0; align-items: center; gap: 12px; }
.staff-chat-application__product img, .staff-chat-application__image-placeholder { display: grid; width: 64px; height: 64px; flex: 0 0 64px; place-items: center; border-radius: 10px; background: #f0f5f2; object-fit: cover; color: #82919f; font-size: 12px; }
.staff-chat-application__product > div { display: grid; min-width: 0; gap: 6px; }
.staff-chat-application__product strong { overflow: hidden; color: #263f55; font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.staff-chat-application__product span { color: #82919f; font-size: 12px; }
.staff-chat-application__details { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: 8px; padding-top: 10px; border-top: 1px solid #edf1ef; }
.staff-chat-application__details > span, .staff-chat-application__card p > span { color: #82919f; font-size: 12px; }
.staff-chat-application__details > strong { min-width: 0; color: #263f55; font-size: 13px; }
.staff-chat-application__card p { margin: 0; color: #53687b; font-size: 13px; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere; }
.staff-chat-application__card p.staff-chat-application__reply { padding: 9px 10px; border-radius: 8px; background: #f7f9f8; }
.staff-chat-application__shipment-form { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 8px; padding-top: 12px; border-top: 1px solid #edf1ef; }
.staff-chat-application__shipment-form label { grid-column: 1 / -1; color: #53687b; font-size: 13px; }
.staff-chat-application__shipment-form :deep(.el-input) { min-width: 0; }
.staff-chat-application__actions { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding-top: 12px; border-top: 1px solid #edf1ef; }
.staff-chat-application__actions > span, .staff-reject-dialog__tip { color: #82919f; font-size: 13px; }
.staff-chat-application__actions > div { display: flex; gap: 8px; }
.staff-chat-application__completion { flex-wrap: wrap; }
.staff-reject-dialog__tip { margin: 0 0 12px; line-height: 1.6; }
.staff-chat__composer { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 12px; padding: 14px 18px; border-top: 1px solid #e5ece8; background: #fff; }
.staff-chat__composer .el-button { min-width: 76px; }
.staff-chat__closed { display: grid; gap: 5px; padding: 14px 20px; border-top: 1px solid #e5ece8; background: #fff; }
.staff-chat__closed strong { color: #087e70; font-size: 13px; }
.staff-chat__closed span { color: #82919f; font-size: 12px; }
.staff-conversation-menu__backdrop { position: fixed; z-index: 4000; inset: 0; }
.staff-conversation-menu { position: fixed; z-index: 4001; display: grid; width: 190px; gap: 5px; padding: 7px; border: 1px solid #e2e9e6; border-radius: 10px; background: #fff; box-shadow: 0 12px 32px rgba(16, 34, 55, .18); }
.staff-conversation-menu__action { padding: 9px 10px; border: 0; border-radius: 7px; color: #102237; background: #fff; cursor: pointer; font: inherit; text-align: left; }
.staff-conversation-menu__action:hover:not(:disabled) { color: #087e70; background: #f1f8f5; }
.staff-conversation-menu__action:disabled { color: #a2adb6; cursor: not-allowed; }
.staff-conversation-menu__hint { padding: 0 10px 5px; color: #99a5af; font-size: 11px; line-height: 1.45; }
.staff-event-detail { display: flex; gap: 18px; padding: clamp(24px, 5vw, 64px); }
.staff-event-detail__icon { display: grid; width: 54px; height: 54px; flex: none; place-items: center; border-radius: 16px; color: #087e70; background: #e4f2ed; }
.staff-event-detail__body { min-width: 0; }
.staff-event-detail__type { color: #159b83; font-size: 12px; font-weight: 700; }
.staff-event-detail h2 { margin: 7px 0; color: #102237; font-size: 21px; }
.staff-event-detail time { color: #8a98a6; font-size: 12px; }
.staff-event-detail p { max-width: 760px; margin: 22px 0; color: #53687b; line-height: 1.8; white-space: pre-wrap; overflow-wrap: anywhere; }
.staff-inbox__placeholder { display: grid; flex: 1; align-content: center; justify-items: center; gap: 12px; padding: 30px; color: #91a0ad; text-align: center; }
.staff-inbox__placeholder strong { color: #506276; font-size: 15px; }
.staff-inbox__placeholder span { font-size: 13px; }
@media (max-width: 900px) {
  .staff-inbox { grid-template-columns: minmax(245px, 32%) minmax(0, 1fr); }
  .staff-inbox__row { gap: 9px; padding-inline: 10px; }
}
@media (max-width: 680px) {
  .staff-inbox { grid-template-columns: 1fr; min-height: 70vh; }
  .staff-inbox__sidebar { max-height: 32vh; border-right: 0; border-bottom: 1px solid #e5ece8; }
  .staff-inbox__main { min-height: 38vh; }
  .staff-chat__message { max-width: 90%; }
  .staff-chat-application { width: min(96%, 620px); }
  .staff-chat-application__card { padding: 11px; }
  .staff-chat-application__details { grid-template-columns: auto minmax(0, 1fr); }
  .staff-chat-application__details :deep(.el-tag) { grid-column: 1 / -1; justify-self: start; }
}
</style>
