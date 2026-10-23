<template>
  <div class="page-container customer-message-center" v-loading="loading">
    <section class="content-card customer-message-center__heading">
      <div>
        <h1>我的消息 <small v-if="unreadCount">{{ unreadCount }} 条未读</small></h1>
        <p>查看私聊、售后会话、评论回复和订单通知。</p>
      </div>
      <el-button v-if="unreadCount" text @click="markAllRead">全部标为已读</el-button>
    </section>

    <section class="customer-message-center__body">
      <aside class="content-card customer-message-list">
        <nav class="customer-message-list__filters" aria-label="消息类型">
          <button
            v-for="filter in filters"
            :key="filter.key"
            type="button"
            :class="{ 'is-active': activeFilter === filter.key }"
            @click="setFilter(filter.key)"
          >
            {{ filter.label }}
            <span>{{ filter.count }}</span>
          </button>
        </nav>

        <div v-if="filteredMessages.length" class="customer-message-list__items">
          <button
            v-for="message in filteredMessages"
            :key="message.id"
            type="button"
            class="customer-message-row"
            :class="{
              'is-active': selectedMessageId === message.id,
              'is-unread': messageUnreadCount(message) > 0
            }"
            @click="selectMessage(message)"
          >
            <span class="customer-message-row__icon" :class="`is-${message.type}`">
              <el-icon :size="20"><component :is="messageIcon(message.type)" /></el-icon>
            </span>
            <span class="customer-message-row__body">
              <span class="customer-message-row__topline">
                <strong>{{ messageTitle(message) }}</strong>
                <time>{{ shortTime(message.create_time) }}</time>
              </span>
              <span class="customer-message-row__subtitle">{{ messageSubtitle(message) }}</span>
              <span class="customer-message-row__preview">{{ messagePreview(message) }}</span>
            </span>
            <span v-if="messageUnreadCount(message)" class="customer-message-row__badge">
              {{ messageUnreadCount(message) > 99 ? '99+' : messageUnreadCount(message) }}
            </span>
          </button>
        </div>
        <el-empty v-else description="这个分类还没有消息" :image-size="72" />
      </aside>

      <main class="content-card customer-message-detail">
        <DirectConversationPanel v-if="activeMessage?.type === 'direct_chat'" :conversation-id="activeMessage.conversation_id" :peer="activeMessage" @updated="load(true)" />
        <template v-else-if="activeMessage?.type === 'after_sale_chat'">
          <header class="customer-message-detail__header">
            <span class="customer-message-detail__avatar"><el-icon :size="23"><ChatDotRound /></el-icon></span>
            <div>
              <h2>售后保障</h2>
              <p>订单 {{ activeMessage.order_no }} · {{ activeMessage.product_name }}</p>
            </div>
            <el-tag size="small" effect="light" round :type="applicationStatusTone(afterSaleApplication?.status)">{{ afterSaleApplication ? applicationStatusLabel(afterSaleApplication) : '售后会话' }}</el-tag>
          </header>

          <div ref="chatListRef" class="customer-chat__messages" v-loading="chatLoading">
            <el-empty
              v-if="!chatLoading && !afterSaleApplication && !chatMessages.length"
              description="还没有消息，发送一条消息开始沟通"
              :image-size="82"
            />
            <article v-if="afterSaleApplication" class="customer-chat-application">
              <span class="customer-chat-application__sender">我提交了售后申请</span>
              <div class="customer-chat-application__card">
                <div class="customer-chat-application__product">
                  <img v-if="afterSaleApplication.image_url" :src="afterSaleApplication.image_url" :alt="afterSaleApplication.product_name">
                  <span v-else class="customer-chat-application__image-placeholder">商品</span>
                  <div>
                    <strong>{{ afterSaleApplication.product_name }}</strong>
                    <span>订单 {{ afterSaleApplication.order_no }}</span>
                  </div>
                </div>
                <div class="customer-chat-application__details">
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
                <el-button
                  v-if="canConfirmExchangeReceived(afterSaleApplication)"
                  type="primary"
                  :loading="confirmingReceipt"
                  @click="confirmExchangeReceipt"
                >确认收到换货商品</el-button>
                <div
                  v-if="canSubmitReturnShipment"
                  class="customer-chat-application__shipment-form"
                >
                  <el-input
                    v-model="returnTrackingDraft"
                    maxlength="100"
                    placeholder="商家已同意，请填写寄回物流单号"
                  />
                  <el-button
                    type="primary"
                    :loading="returnShipmentSubmitting"
                    :disabled="!returnTrackingDraft.trim()"
                    @click="submitReturnShipment"
                  >
                    提交寄回物流
                  </el-button>
                </div>
                <p v-if="afterSaleApplication.admin_note" class="customer-chat-application__reply">
                  <span>商家说明：</span>{{ afterSaleApplication.admin_note }}
                </p>
              </div>
              <time>{{ afterSaleApplication.create_time }}</time>
            </article>
            <div
              v-for="message in visibleChatMessages"
              :key="message.id"
              class="customer-chat-message"
              :class="{ 'is-mine': message.sender_role === 'customer' }"
            >
              <div class="customer-chat-message__content">
                <span class="customer-chat-message__sender">
                  {{ message.sender_role === 'customer' ? '我' : message.sender_name || '售后客服' }}
                </span>
                <div class="customer-chat-message__bubble">{{ message.content }}</div>
                <time>{{ message.create_time }}</time>
              </div>
            </div>
          </div>

          <section v-if="isAfterSaleClosed(afterSaleApplication)" class="customer-chat__closed">
            <div class="customer-chat__closed-copy">
              <strong>{{ afterSaleApplication.status === 'rejected' ? '售后已拒绝 · 服务评价' : '售后服务评价' }}</strong>
              <span>沟通通道已关闭，对话记录仍可查看。请评价本次售后服务。</span>
            </div>
            <template v-if="afterSaleApplication.service_rating == null">
              <el-rate v-model="serviceRatingDraft" show-text :texts="serviceRatingTexts" />
              <el-input
                v-model="serviceFeedbackDraft"
                type="textarea"
                :rows="2"
                maxlength="1000"
                resize="none"
                placeholder="可以补充评价内容（选填）"
              />
              <el-button
                class="customer-chat__rating-submit"
                type="primary"
                :loading="ratingSubmitting"
                :disabled="!serviceRatingDraft"
                @click="submitServiceRating"
              >
                提交评价
              </el-button>
            </template>
            <div v-else class="customer-chat__rating-done">
              感谢评价，本次售后服务评分：{{ afterSaleApplication.service_rating }} / 5
              <p v-if="afterSaleApplication.service_feedback">{{ afterSaleApplication.service_feedback }}</p>
            </div>
          </section>
          <form v-else class="customer-chat__compose" @submit.prevent="sendMessage">
            <el-input
              v-model="draft"
              type="textarea"
              :rows="3"
              maxlength="2000"
              resize="none"
              placeholder="输入消息，按 Ctrl + Enter 发送"
              @keydown.ctrl.enter.prevent="sendMessage"
            />
            <div class="customer-chat__actions">
              <span>售后客服会在消息中心回复你</span>
              <el-button type="primary" :loading="sending" :disabled="!draft.trim() || chatLoading" native-type="submit">
                发送
              </el-button>
            </div>
          </form>
        </template>

        <template v-else-if="activeMessage">
          <header class="customer-message-detail__header">
            <span class="customer-message-detail__avatar" :class="`is-${activeMessage.type}`">
              <el-icon :size="23"><component :is="messageIcon(activeMessage.type)" /></el-icon>
            </span>
            <div>
              <h2>{{ messageTitle(activeMessage) }}</h2>
              <p>{{ messageSubtitle(activeMessage) }}</p>
            </div>
            <time>{{ activeMessage.create_time || '时间未知' }}</time>
          </header>

          <section class="customer-notice">
            <div class="customer-notice__intro">
              <span class="customer-notice__label">消息通知</span>
              <h3>{{ messageTitle(activeMessage) }}</h3>
              <p>{{ messagePreview(activeMessage) }}</p>
            </div>

            <div class="customer-notice__facts">
              <div class="customer-notice__fact">
                <span>关联商品</span>
                <strong>{{ activeMessage.product_name || '—' }}</strong>
              </div>
              <div v-if="activeMessage.type === 'shipment'" class="customer-notice__fact">
                <span>订单编号</span>
                <strong>{{ activeMessage.order_no || '—' }}</strong>
              </div>
              <template v-else-if="activeMessage.type === 'price_drop'">
                <div class="customer-notice__fact">
                  <span>降价前</span>
                  <strong class="customer-notice__old-price">¥{{ money(activeMessage.previous_price) }}</strong>
                </div>
                <div class="customer-notice__fact">
                  <span>当前价格</span>
                  <strong class="customer-notice__current-price">¥{{ money(activeMessage.current_price) }}</strong>
                </div>
              </template>
              <div v-else-if="activeMessage.type === 'review_reply'" class="customer-notice__fact"><span>被回复的评价</span><strong>{{ activeMessage.review_content }}</strong></div>
              <div v-else-if="activeMessage.type === 'restock'" class="customer-notice__fact"><span>通知时库存</span><strong>{{ activeMessage.stock }} 件</strong></div>
            </div>

            <div class="customer-notice__footer">
              <span>{{ activeMessage.type === 'review_reply' ? '点击查看完整评论与回复。' : activeMessage.type === 'restock' ? '商品已恢复有货，最新库存以商品页为准。' : activeMessage.type === 'shipment' ? '物流进度会继续在这里提醒。' : '收藏商品有新的价格变化时会在这里提醒。' }}</span>
              <el-button type="primary" plain @click="openMessageTarget(activeMessage)">
                {{ activeMessage.type === 'review_reply' ? '查看评论' : activeMessage.type === 'shipment' ? '查看订单' : '查看商品' }}
                <el-icon class="el-icon--right"><ArrowRight /></el-icon>
              </el-button>
            </div>
          </section>
        </template>

        <el-empty v-else description="选择一条消息查看详情" :image-size="100" />
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight, ChatDotRound, PriceTag, Van } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import DirectConversationPanel from '@/components/DirectConversationPanel.vue'
import {
  getCustomerAfterSaleMessages,
  getCustomerMessages,
  markCustomerMessageRead,
  markCustomerMessagesRead,
  sendCustomerAfterSaleMessage,
  submitCustomerAfterSaleServiceRating,
  submitAfterSaleReturnShipment,
  confirmOrderReceived
} from '@/api/customer'
import {
  applicationStatusLabel, applicationStatusTone, serviceTypeLabel, serviceTypeTone,
  isAfterSaleClosed, canConfirmExchangeReceived, canSubmitReturnShipment as canReturnShipment,
  returnShipmentLabel, returnTrackingLabel
} from '@/utils/afterSale'

const router = useRouter()
const route = useRoute()
const messages = ref([])
const unreadCount = ref(0)
const loading = ref(false)
const chatLoading = ref(false)
const sending = ref(false)
const ratingSubmitting = ref(false)
const draft = ref('')
const serviceRatingDraft = ref(0)
const serviceFeedbackDraft = ref('')
const serviceRatingTexts = ['很不满意', '不满意', '一般', '满意', '非常满意']
const activeFilter = ref('all')
const selectedMessageId = ref(null)
const chatMessages = ref([])
const visibleChatMessages = computed(() => chatMessages.value.filter((message) =>
  !isAfterSaleShipmentNotice(message.content)
))
const afterSaleApplication = ref(null)
const returnTrackingDraft = ref('')
const returnShipmentSubmitting = ref(false)
const confirmingReceipt = ref(false)
const chatListRef = ref(null)
let inboxTimer = null
let chatTimer = null
let conversationRequestId = 0
let inboxRequestId = 0

const filteredMessages = computed(() => messages.value.filter((message) => {
  if (activeFilter.value === 'conversations') return message.type === 'after_sale_chat'
  if (activeFilter.value === 'private') return message.type === 'direct_chat'
  if (activeFilter.value === 'notices') return !['after_sale_chat', 'direct_chat'].includes(message.type)
  return true
}))
const activeMessage = computed(() =>
  messages.value.find((message) => message.id === selectedMessageId.value) || null
)
const filters = computed(() => [
  { key: 'all', label: '全部', count: messages.value.length },
  { key: 'conversations', label: '售后', count: messages.value.filter((item) => item.type === 'after_sale_chat').length },
  { key: 'private', label: '私聊', count: messages.value.filter((item) => item.type === 'direct_chat').length },
  { key: 'notices', label: '通知', count: messages.value.filter((item) => !['after_sale_chat', 'direct_chat'].includes(item.type)).length }
])
const canSubmitReturnShipment = computed(() =>
  canReturnShipment(afterSaleApplication.value)
)

function money(value) {
  return Number(value || 0).toFixed(2)
}

function shortTime(value) {
  if (!value) return ''
  const text = String(value)
  return text.length > 10 ? text.slice(5, 16) : text
}

function messageIcon(type) {
  return { after_sale_chat: ChatDotRound, shipment: Van, restock: Van, price_drop: PriceTag }[type] || ChatDotRound
}

function messageTitle(message) {
  if (message.type === 'direct_chat') return message.peer_name
  if (message.type === 'review_reply') return `${message.actor_name}回复了你`
  return { after_sale_chat: '售后保障', shipment: '服务提醒', price_drop: '降价通知', restock: '收藏商品到货提醒' }[message.type] || '消息'
}

function messageSubtitle(message) {
  if (message.type === 'direct_chat') return '商家私聊'
  if (message.type === 'after_sale_chat') return `订单 ${message.order_no} · ${message.product_name}`
  if (message.type === 'shipment') return `订单 ${message.order_no} · ${message.product_name}`
  return message.product_name || '收藏商品'
}

function messagePreview(message) {
  if (message.type === 'direct_chat') return message.preview || '点击开始私聊'
  if (message.type === 'review_reply') return message.content
  if (message.type === 'restock') return `你收藏的“${message.product_name}”已补货，可以前往商品页查看。`
  if (message.type === 'after_sale_chat') {
    if (isAfterSaleShipmentNotice(message.preview)) return '物流信息已更新，详见售后卡片。'
    return message.preview || '点击查看售后沟通'
  }
  if (message.type === 'shipment') return `订单已发货，${message.product_name}正在配送，请留意收货。`
  return `${message.product_name}降价了，现价 ¥${money(message.current_price)}，快去看看吧。`
}

function isAfterSaleShipmentNotice(content = '') {
  return content.startsWith('我已寄回商品，物流单号：') ||
    content.startsWith('已提交寄回物流信息，详见售后卡片。') ||
    content.startsWith('商家已提交换货发货物流信息，详见售后卡片。')
}

function messageUnreadCount(message) {
  if (['after_sale_chat', 'direct_chat'].includes(message.type)) return Number(message.unread_count || 0)
  return message.is_read ? 0 : 1
}

function setFilter(filter) {
  activeFilter.value = filter
  const first = filteredMessages.value[0]
  if (first) selectMessage(first)
  else {
    selectedMessageId.value = null
    chatMessages.value = []
    conversationRequestId += 1
  }
}

async function selectMessage(message, scroll = true) {
  conversationRequestId += 1
  selectedMessageId.value = message.id
  draft.value = ''
  returnTrackingDraft.value = ''
  serviceRatingDraft.value = 0
  serviceFeedbackDraft.value = ''
  if (message.type === 'after_sale_chat') {
    chatMessages.value = []
    afterSaleApplication.value = null
    await router.replace({ path: route.path, query: { afterSaleId: String(message.after_sale_id) } })
    await loadConversation(message.after_sale_id, scroll)
    return
  }
  conversationRequestId += 1
  chatMessages.value = []
  afterSaleApplication.value = null
  chatLoading.value = false
  await router.replace({ path: route.path, query: message.type === 'direct_chat' ? { conversationId: String(message.conversation_id) } : {} })
  await markNoticeRead(message)
}

async function markNoticeRead(message) {
  if (message.is_read || !['shipment', 'price_drop', 'review_reply', 'restock'].includes(message.type)) return
  const messageId = Number(String(message.id).split('-').at(-1))
  try {
    await markCustomerMessageRead(message.type, messageId)
    message.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    window.dispatchEvent(new Event('customer-messages-updated'))
  } catch (error) {
    ElMessage.error(error?.message || '标记消息已读失败')
  }
}

async function loadConversation(afterSaleId, scroll = true) {
  if (!afterSaleId) return
  if (chatLoading.value && !scroll) return
  const requestId = ++conversationRequestId
  chatLoading.value = true
  try {
    const response = await getCustomerAfterSaleMessages(afterSaleId)
    if (requestId !== conversationRequestId || activeMessage.value?.after_sale_id !== afterSaleId) return
    const data = response.data || {}
    const nextMessages = data.messages || []
    afterSaleApplication.value = data.application || null
    if (data.application?.service_rating != null) {
      serviceRatingDraft.value = Number(data.application.service_rating)
      serviceFeedbackDraft.value = data.application.service_feedback || ''
    }
    const hasNewMessage = nextMessages.at(-1)?.id !== chatMessages.value.at(-1)?.id
    const nearBottom = !chatListRef.value ||
      chatListRef.value.scrollHeight - chatListRef.value.scrollTop - chatListRef.value.clientHeight < 80
    chatMessages.value = nextMessages
    const newlyReadCount = Number(data.unread_count || 0)
    if (newlyReadCount) {
      unreadCount.value = Math.max(0, unreadCount.value - newlyReadCount)
      messages.value = messages.value.map((item) => item.after_sale_id === afterSaleId
        ? { ...item, unread_count: 0, is_read: true }
        : item)
      window.dispatchEvent(new Event('customer-messages-updated'))
    }
    if (hasNewMessage && (scroll || nearBottom)) await scrollToBottom()
  } catch (error) {
    if (requestId === conversationRequestId) ElMessage.error(error?.message || '加载售后会话失败')
  } finally {
    if (requestId === conversationRequestId) chatLoading.value = false
  }
}

async function submitReturnShipment() {
  const afterSaleId = afterSaleApplication.value?.id
  const trackingNo = returnTrackingDraft.value.trim()
  if (!afterSaleId || !trackingNo || returnShipmentSubmitting.value) return
  returnShipmentSubmitting.value = true
  try {
    await submitAfterSaleReturnShipment(afterSaleId, trackingNo)
    if (activeMessage.value?.after_sale_id === afterSaleId) returnTrackingDraft.value = ''
    ElMessage.success('寄回物流已提交，商家会在售后消息中收到提醒')
    if (activeMessage.value?.after_sale_id === afterSaleId) await loadConversation(afterSaleId)
    await load(true)
  } catch (error) {
    ElMessage.error(error?.message || '提交寄回物流失败')
  } finally {
    returnShipmentSubmitting.value = false
  }
}

async function scrollToBottom() {
  await nextTick()
  if (chatListRef.value) chatListRef.value.scrollTop = chatListRef.value.scrollHeight
}

function openMessageTarget(message) {
  if (message.type === 'review_reply') {
    router.push({ path: `/manager/store/products/${message.product_id}`, query: { review_id: String(message.review_id) } })
    return
  }
  router.push(message.type === 'shipment'
    ? '/manager/my-orders'
    : `/manager/store/products/${message.product_id}`)
}

async function sendMessage() {
  const content = draft.value.trim()
  const afterSaleId = activeMessage.value?.after_sale_id
  if (!content || !afterSaleId || sending.value || chatLoading.value || isAfterSaleClosed(afterSaleApplication.value)) return
  sending.value = true
  try {
    const response = await sendCustomerAfterSaleMessage(afterSaleId, content)
    if (activeMessage.value?.after_sale_id === afterSaleId) chatMessages.value.push(response.data)
    messages.value = messages.value.map((item) => item.after_sale_id === afterSaleId
      ? { ...item, preview: content, create_time: response.data?.create_time || item.create_time }
      : item)
    if (activeMessage.value?.after_sale_id === afterSaleId) {
      draft.value = ''
      await scrollToBottom()
    }
    await load(true)
  } catch (error) {
    ElMessage.error(error?.message || '发送消息失败')
  } finally {
    sending.value = false
  }
}

async function confirmExchangeReceipt() {
  const application = afterSaleApplication.value
  if (!canConfirmExchangeReceived(application) || confirmingReceipt.value) return
  try {
    await ElMessageBox.confirm('确认已收到换货商品？确认后通知商家完成售后。', '确认换货收货', {
      confirmButtonText: '已收到', cancelButtonText: '取消', type: 'warning'
    })
  } catch { return }
  confirmingReceipt.value = true
  try {
    const response = await confirmOrderReceived(application.order_id)
    if (activeMessage.value?.after_sale_id === application.id) await loadConversation(application.id)
    await load(true)
    ElMessage.success(response.message || '已确认收到换货商品')
  } catch (error) {
    ElMessage.error(error?.message || '确认换货收货失败')
  } finally {
    confirmingReceipt.value = false
  }
}

async function submitServiceRating() {
  const afterSaleId = afterSaleApplication.value?.id
  if (!afterSaleId || !serviceRatingDraft.value || ratingSubmitting.value || afterSaleApplication.value?.service_rating != null) return
  ratingSubmitting.value = true
  try {
    const response = await submitCustomerAfterSaleServiceRating(
      afterSaleId,
      serviceRatingDraft.value,
      serviceFeedbackDraft.value.trim() || null
    )
    if (activeMessage.value?.after_sale_id === afterSaleId) afterSaleApplication.value = { ...afterSaleApplication.value, ...(response.data || {}) }
    ElMessage.success('感谢评价售后服务')
    await load(true)
  } catch (error) {
    ElMessage.error(error?.message || '提交售后服务评价失败')
  } finally {
    ratingSubmitting.value = false
  }
}

async function load(silent = false) {
  if (loading.value) return
  if (!silent) loading.value = true
  const requestId = ++inboxRequestId
  try {
    const response = await getCustomerMessages()
    if (requestId !== inboxRequestId) return
    messages.value = response.data?.list || []
    const unread = Number(response.data?.unread_count || 0)
    const unreadChanged = unread !== unreadCount.value
    unreadCount.value = unread
    if (unreadChanged) window.dispatchEvent(new Event('customer-messages-updated'))
    const requestedPrivateId = Number(route.query.conversationId)
    const requestedPrivate = requestedPrivateId ? messages.value.find(item => item.type === 'direct_chat' && item.conversation_id === requestedPrivateId) : null
    if (requestedPrivate) {
      activeFilter.value = 'all'
      if (selectedMessageId.value !== requestedPrivate.id) await selectMessage(requestedPrivate)
      return
    }
    const requestedAfterSaleId = Number(route.query.afterSaleId)
    const requestedConversation = requestedAfterSaleId
      ? messages.value.find((item) => item.type === 'after_sale_chat' && Number(item.after_sale_id) === requestedAfterSaleId)
      : null
    if (requestedConversation) {
      activeFilter.value = 'all'
      if (selectedMessageId.value !== requestedConversation.id) await selectMessage(requestedConversation, true)
      return
    }
    const selectedStillExists = filteredMessages.value.some((item) => item.id === selectedMessageId.value)
    if (!selectedStillExists) {
      const nextMessage = filteredMessages.value[0]
      if (nextMessage) await selectMessage(nextMessage, true)
      else {
        selectedMessageId.value = null
        chatMessages.value = []
        afterSaleApplication.value = null
      }
    }
  } catch (error) {
    if (!silent) ElMessage.error(error?.message || '加载消息失败')
  } finally {
    if (!silent) loading.value = false
  }
}

watch(() => [route.query.afterSaleId, route.query.conversationId], () => load(true))

async function markAllRead() {
  try {
    await markCustomerMessagesRead()
    messages.value = messages.value.map((message) => ({ ...message, is_read: true, unread_count: 0 }))
    unreadCount.value = 0
    window.dispatchEvent(new Event('customer-messages-read'))
    ElMessage.success('消息已全部标为已读')
  } catch (error) {
    ElMessage.error(error?.message || '标记消息失败')
  }
}

onMounted(async () => {
  await load()
  inboxTimer = setInterval(() => {
    if (document.visibilityState === 'visible') load(true)
  }, 5000)
  chatTimer = setInterval(() => {
    const message = activeMessage.value
    if (document.visibilityState === 'visible' && message?.type === 'after_sale_chat') {
      loadConversation(message.after_sale_id, false)
    }
  }, 5000)
})

onBeforeUnmount(() => {
  inboxRequestId += 1
  conversationRequestId += 1
  if (inboxTimer) clearInterval(inboxTimer)
  if (chatTimer) clearInterval(chatTimer)
})
</script>

<style scoped>
.customer-message-center { display: grid; grid-template-rows: auto minmax(0, 1fr); height: 100%; gap: 18px; min-height: 560px; }
.customer-message-center__heading { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.customer-message-center__heading h1 { margin: 0; color: #102237; font-size: 22px; }
.customer-message-center__heading h1 small { margin-left: 8px; color: #ed6b28; font-size: 13px; font-weight: 500; }
.customer-message-center__heading p { margin-top: 6px; color: #728396; font-size: 14px; }
.customer-message-center__body { display: grid; min-height: 0; grid-template-columns: minmax(270px, 330px) minmax(0, 1fr); gap: 16px; }
.customer-message-list, .customer-message-detail { min-width: 0; min-height: 0; overflow: hidden; padding: 0; }
.customer-message-list { display: flex; flex-direction: column; }
.customer-message-list__filters { display: flex; flex: 0 0 auto; gap: 4px; padding: 12px; border-bottom: 1px solid #edf0f2; }
.customer-message-list__filters button { display: inline-flex; min-height: 34px; align-items: center; gap: 6px; padding: 0 10px; border: 0; border-radius: 8px; background: transparent; color: #728396; font: inherit; cursor: pointer; }
.customer-message-list__filters button.is-active { background: #eaf3ef; color: #126e61; font-weight: 600; }
.customer-message-list__filters button span { color: #98a5af; font-size: 12px; }
.customer-message-list__items { min-height: 0; overflow-y: auto; }
.customer-message-row { display: grid; width: 100%; min-height: 82px; grid-template-columns: 42px minmax(0, 1fr) auto; align-items: center; gap: 11px; padding: 12px 14px; border: 0; border-bottom: 1px solid #edf0f2; background: #fff; color: inherit; text-align: left; cursor: pointer; }
.customer-message-row:hover { background: #f8faf9; }
.customer-message-row.is-active { background: #eef6f2; }
.customer-message-row__icon, .customer-message-detail__avatar { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 12px; background: #edf6fb; color: #2698d7; }
.customer-message-row__icon.is-shipment, .customer-message-detail__avatar.is-shipment { background: #edf7ff; color: #2797d5; }
.customer-message-row__icon.is-price_drop, .customer-message-detail__avatar.is-price_drop { background: #fff5e8; color: #ed9a19; }
.customer-message-row__body { display: grid; min-width: 0; gap: 4px; }
.customer-message-row__topline { display: flex; min-width: 0; align-items: center; justify-content: space-between; gap: 8px; }
.customer-message-row__topline strong { overflow: hidden; color: #24384c; font-size: 14px; font-weight: 650; text-overflow: ellipsis; white-space: nowrap; }
.customer-message-row__topline time { flex: 0 0 auto; color: #98a5af; font-size: 11px; }
.customer-message-row__subtitle, .customer-message-row__preview { overflow: hidden; color: #81909e; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.customer-message-row__badge { display: grid; min-width: 18px; height: 18px; place-items: center; padding: 0 5px; border-radius: 10px; background: #ed6b19; color: #fff; font-size: 11px; line-height: 1; }
.customer-message-detail { display: flex; flex-direction: column; }
.customer-message-detail__header { display: flex; min-height: 70px; flex: 0 0 auto; align-items: center; gap: 12px; padding: 14px 20px; border-bottom: 1px solid #edf0f2; }
.customer-message-detail__avatar { width: 44px; height: 44px; flex: 0 0 44px; }
.customer-message-detail__header > div { min-width: 0; flex: 1; }
.customer-message-detail__header h2 { overflow: hidden; margin: 0; color: #17324b; font-size: 16px; text-overflow: ellipsis; white-space: nowrap; }
.customer-message-detail__header p { overflow: hidden; margin: 4px 0 0; color: #81909e; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.customer-message-detail__header > time { flex: 0 0 auto; color: #98a5af; font-size: 12px; }
.customer-chat__messages { display: flex; min-height: 0; flex: 1; flex-direction: column; gap: 14px; overflow-y: auto; padding: 20px; background: #f8faf9; }
.customer-chat-message { display: flex; justify-content: flex-start; }
.customer-chat-message.is-mine { justify-content: flex-end; }
.customer-chat-message__content { display: grid; max-width: min(78%, 520px); gap: 5px; }
.customer-chat-message.is-mine .customer-chat-message__content { justify-items: end; }
.customer-chat-message__sender, .customer-chat-message time { color: #82919f; font-size: 11px; }
.customer-chat-message__bubble { padding: 10px 13px; border: 1px solid #e2e9e6; border-radius: 4px 14px 14px; background: #fff; color: #263f55; line-height: 1.65; white-space: pre-wrap; overflow-wrap: anywhere; }
.customer-chat-message.is-mine .customer-chat-message__bubble { border-color: #cde9df; border-radius: 14px 4px 14px 14px; background: #e7f5ef; }
.customer-chat-application { display: grid; width: min(82%, 620px); align-self: flex-end; justify-items: end; gap: 5px; }
.customer-chat-application__sender, .customer-chat-application > time { color: #82919f; font-size: 11px; }
.customer-chat-application__card { display: grid; width: 100%; gap: 12px; padding: 14px; border: 1px solid #cde9df; border-radius: 14px 4px 14px 14px; background: #fff; }
.customer-chat-application__product { display: flex; min-width: 0; align-items: center; gap: 12px; }
.customer-chat-application__product img, .customer-chat-application__image-placeholder { display: grid; width: 64px; height: 64px; flex: 0 0 64px; place-items: center; border-radius: 10px; background: #f0f5f2; object-fit: cover; color: #82919f; font-size: 12px; }
.customer-chat-application__product > div { display: grid; min-width: 0; gap: 6px; }
.customer-chat-application__product strong { overflow: hidden; color: #263f55; font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.customer-chat-application__product span { color: #82919f; font-size: 12px; }
.customer-chat-application__details { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: 8px; padding-top: 10px; border-top: 1px solid #edf1ef; }
.customer-chat-application__details > span, .customer-chat-application__card p > span { color: #82919f; font-size: 12px; }
.customer-chat-application__details > strong { min-width: 0; color: #263f55; font-size: 13px; }
.customer-chat-application__card p { margin: 0; color: #53687b; font-size: 13px; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere; }
.customer-chat-application__card p.customer-chat-application__reply { padding: 9px 10px; border-radius: 8px; background: #f7f9f8; }
.customer-chat-application__shipment-form { display: flex; align-items: flex-start; gap: 8px; padding-top: 10px; border-top: 1px solid #edf1ef; }
.customer-chat-application__shipment-form :deep(.el-input) { min-width: 0; flex: 1; }
.customer-chat__compose { flex: 0 0 auto; padding: 14px 18px 16px; border-top: 1px solid #edf0f2; }
.customer-chat__actions { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 10px; }
.customer-chat__actions > span { color: #9aa6af; font-size: 12px; }
.customer-chat__closed { display: grid; flex: 0 0 auto; gap: 10px; padding: 14px 18px 16px; border-top: 1px solid #edf0f2; background: #fff; }
.customer-chat__closed-copy { display: grid; gap: 4px; }
.customer-chat__closed-copy strong { color: #17324b; font-size: 14px; }
.customer-chat__closed-copy span { color: #81909e; font-size: 12px; }
.customer-chat__closed :deep(.el-rate) { min-height: 24px; }
.customer-chat__rating-submit { justify-self: end; }
.customer-chat__rating-done { color: #087e70; font-size: 13px; }
.customer-chat__rating-done p { margin: 5px 0 0; color: #607488; white-space: pre-wrap; overflow-wrap: anywhere; }
.customer-notice { display: flex; min-height: 0; flex: 1; flex-direction: column; padding: 30px 34px; background: linear-gradient(135deg, #fbfdfc 0%, #f5f9f7 100%); }
.customer-notice__intro { max-width: 900px; }
.customer-notice__label { color: #8493a0; font-size: 12px; }
.customer-notice h3 { margin: 12px 0 8px; color: #17324b; font-size: 24px; }
.customer-notice p { max-width: 760px; margin: 0; color: #607488; font-size: 16px; line-height: 1.8; }
.customer-notice__facts { display: grid; max-width: 900px; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 30px; }
.customer-notice__fact { display: grid; min-height: 92px; align-content: center; gap: 8px; padding: 16px 18px; border: 1px solid #e5ece8; border-radius: 12px; background: #fff; }
.customer-notice__fact > span { color: #82919f; font-size: 12px; }
.customer-notice__fact strong { overflow-wrap: anywhere; color: #263f55; font-size: 15px; }
.customer-notice__old-price { color: #8d9aa5 !important; text-decoration: line-through; }
.customer-notice__fact .customer-notice__current-price { color: #e65b4a; font-size: 20px; }
.customer-notice__footer { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: auto; padding-top: 22px; color: #98a5af; font-size: 13px; }
.customer-message-detail :deep(.el-empty) { margin: auto; }
@media (max-width: 900px) {
  .customer-message-center__body { height: auto; min-height: 0; grid-template-columns: 1fr; }
  .customer-message-list { min-height: 250px; max-height: 340px; }
  .customer-message-detail { min-height: 520px; }
}
@media (max-width: 600px) {
  .customer-message-center__heading { align-items: flex-start; }
  .customer-message-center__heading h1 { font-size: 19px; }
  .customer-message-center__heading p { max-width: 250px; line-height: 1.5; }
  .customer-message-list__filters { padding: 10px; }
  .customer-message-row { grid-template-columns: 38px minmax(0, 1fr) auto; gap: 9px; padding: 11px 10px; }
  .customer-message-row__icon { width: 38px; height: 38px; }
  .customer-message-row__topline { align-items: flex-start; }
  .customer-message-row__topline time { font-size: 10px; }
  .customer-message-detail { min-height: 470px; }
  .customer-message-detail__header { padding: 12px; }
  .customer-chat__messages { padding: 14px 12px; }
  .customer-chat__compose { padding: 11px; }
  .customer-chat__actions > span { max-width: 170px; line-height: 1.4; }
  .customer-chat-application { width: min(96%, 560px); }
  .customer-chat-application__card { padding: 11px; }
  .customer-chat-application__details { grid-template-columns: auto minmax(0, 1fr); }
  .customer-chat-application__details :deep(.el-tag) { grid-column: 1 / -1; justify-self: start; }
  .customer-notice { padding: 22px 16px; }
  .customer-notice h3 { font-size: 21px; }
  .customer-notice p { font-size: 14px; }
  .customer-notice__facts { grid-template-columns: 1fr; gap: 9px; margin-top: 20px; }
  .customer-notice__fact { min-height: 72px; }
  .customer-notice__footer { align-items: flex-start; flex-direction: column; }
}
</style>
