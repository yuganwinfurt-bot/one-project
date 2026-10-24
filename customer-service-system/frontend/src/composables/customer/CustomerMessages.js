import { useCustomerRouter } from '@/utils/customerRouter'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight, ChatDotRound, PriceTag, Van } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import DirectConversationPanel from '@/components/DirectConversationPanel.vue'
import CustomerSupportPanel from '@/components/CustomerSupportPanel.vue'
import request from '@/utils/request'
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

export function useCustomerMessages() {
const router = useCustomerRouter()
const route = useRoute()
const supportOpen = computed(() => route.query.tab === 'support')
const afterSaleAIThinking = ref(false)
function toggleSupport() {
  router.replace({ path: route.path, query: supportOpen.value ? { tab: 'inbox' } : { tab: 'support' } })
}
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
let disposed = false
const filteredMessages = computed(() => messages.value.filter((message) => {
  if (activeFilter.value === 'conversations') return ['after_sale_chat', 'support_chat'].includes(message.type)
  if (activeFilter.value === 'private') return message.type === 'direct_chat'
  if (activeFilter.value === 'notices') return !['after_sale_chat', 'support_chat', 'direct_chat'].includes(message.type)
  return true
}))
const activeMessage = computed(() =>
  messages.value.find((message) => message.id === selectedMessageId.value) || null
)
const filters = computed(() => [
  { key: 'all', label: '全部', count: messages.value.length },
  { key: 'conversations', label: '售后', count: messages.value.filter((item) => ['after_sale_chat', 'support_chat'].includes(item.type)).length },
  { key: 'private', label: '私聊', count: messages.value.filter((item) => item.type === 'direct_chat').length },
  { key: 'notices', label: '通知', count: messages.value.filter((item) => !['after_sale_chat', 'support_chat', 'direct_chat'].includes(item.type)).length }
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
  if (message.type === 'support_chat') return '售后客服'
  if (message.type === 'direct_chat') return message.peer_name
  if (message.type === 'review_reply') return `${message.actor_name}回复了你`
  return { after_sale_chat: '售后保障', shipment: '服务提醒', price_drop: '降价通知', restock: '收藏商品到货提醒' }[message.type] || '消息'
}
function messageSubtitle(message) {
  if (message.type === 'support_chat') return message.title || '客服咨询'
  if (message.type === 'direct_chat') return '商家私聊'
  if (message.type === 'after_sale_chat') return `订单 ${message.order_no} · ${message.product_name}`
  if (message.type === 'shipment') return `订单 ${message.order_no} · ${message.product_name}`
  return message.product_name || '收藏商品'
}
function messagePreview(message) {
  if (message.type === 'support_chat') return message.preview || '点击查看客服咨询'
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
  if (['after_sale_chat', 'support_chat', 'direct_chat'].includes(message.type)) return Number(message.unread_count || 0)
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
  if (message.type === 'support_chat') { await router.replace({path: route.path, query: {tab: 'support', supportConversationId: String(message.support_conversation_id)}}); return }
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
    afterSaleAIThinking.value = !!data.application?.ai_pending
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
  if (!content || !afterSaleId || sending.value || chatLoading.value || (isAfterSaleClosed(afterSaleApplication.value) || afterSaleApplication.value?.conversation_closed)) return
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
    afterSaleAIThinking.value = !!response.data?.ai_pending
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
  const requestedView = route.fullPath
  try {
    const response = await getCustomerMessages()
    if (requestId !== inboxRequestId || requestedView !== route.fullPath) return
    messages.value = response.data?.list || []
    const unread = Number(response.data?.unread_count || 0)
    const unreadChanged = unread !== unreadCount.value
    unreadCount.value = unread
    if (unreadChanged) window.dispatchEvent(new Event('customer-messages-updated'))
    if (supportOpen.value) return
    const requestedPrivateId = Number(route.query.conversationId)
    const requestedPrivate = requestedPrivateId ? messages.value.find(item => item.type === 'direct_chat' && item.conversation_id === requestedPrivateId) : null
    if (requestedPrivate) {
      activeFilter.value = 'all'
      if (selectedMessageId.value !== requestedPrivate.id) await selectMessage(requestedPrivate)
      return
    }
    const requestedAfterSaleId = Number(route.query.afterSaleId)
    const requestedConversation = requestedAfterSaleId
      ? messages.value.find((item) => ['after_sale_chat', 'support_chat'].includes(item.type) && Number(item.after_sale_id) === requestedAfterSaleId)
      : null
    if (requestedConversation) {
      activeFilter.value = 'all'
      if (selectedMessageId.value !== requestedConversation.id) await selectMessage(requestedConversation, true)
      return
    }
    if (route.path.startsWith('/mini-store')) return
    const selectedStillExists = filteredMessages.value.some((item) => item.id === selectedMessageId.value)
    if (!selectedStillExists) {
      const nextMessage = filteredMessages.value.find(item => item.type !== 'support_chat')
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
watch(() => [route.query.afterSaleId, route.query.conversationId, route.query.tab], () => load(true))
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
  if (disposed) return
  inboxTimer = setInterval(() => {
    if (document.visibilityState === 'visible') load(true)
  }, 5000)
  chatTimer = setInterval(() => {
    const message = activeMessage.value
    if (!supportOpen.value && document.visibilityState === 'visible' && message?.type === 'after_sale_chat') {
      loadConversation(message.after_sale_id, false)
    }
  }, 5000)
})
onBeforeUnmount(() => {
  disposed = true
  inboxRequestId += 1
  conversationRequestId += 1
  if (inboxTimer) clearInterval(inboxTimer)
  if (chatTimer) clearInterval(chatTimer)
})
async function requestAfterSaleHuman() {
  const id = afterSaleApplication.value?.support_conversation_id
  if (!id) return
  try {
    await request.post(`/api/customer/support/conversations/${id}/human`, {reason: '对AI回答不满意，希望人工客服协助'})
    afterSaleAIThinking.value = false
    await loadConversation(activeMessage.value.after_sale_id)
    ElMessage.success('已申请人工，两边后台已收到提醒')
  } catch (error) { ElMessage.error(error.message || '申请人工失败') }
}
return {
useCustomerRouter,
computed,
nextTick,
onBeforeUnmount,
onMounted,
ref,
watch,
ElMessage,
ElMessageBox,
ArrowRight,
ChatDotRound,
PriceTag,
Van,
useRoute,
DirectConversationPanel,
CustomerSupportPanel,
request,
getCustomerAfterSaleMessages,
getCustomerMessages,
markCustomerMessageRead,
markCustomerMessagesRead,
sendCustomerAfterSaleMessage,
submitCustomerAfterSaleServiceRating,
submitAfterSaleReturnShipment,
confirmOrderReceived,
applicationStatusLabel,
applicationStatusTone,
serviceTypeLabel,
serviceTypeTone,
isAfterSaleClosed,
canConfirmExchangeReceived,
canReturnShipment,
returnShipmentLabel,
returnTrackingLabel,
router,
route,
supportOpen,
afterSaleAIThinking,
toggleSupport,
messages,
unreadCount,
loading,
chatLoading,
sending,
ratingSubmitting,
draft,
serviceRatingDraft,
serviceFeedbackDraft,
serviceRatingTexts,
activeFilter,
selectedMessageId,
chatMessages,
visibleChatMessages,
afterSaleApplication,
returnTrackingDraft,
returnShipmentSubmitting,
confirmingReceipt,
chatListRef,
inboxTimer,
chatTimer,
conversationRequestId,
inboxRequestId,
filteredMessages,
activeMessage,
filters,
canSubmitReturnShipment,
money,
shortTime,
messageIcon,
messageTitle,
messageSubtitle,
messagePreview,
isAfterSaleShipmentNotice,
messageUnreadCount,
setFilter,
selectMessage,
markNoticeRead,
loadConversation,
submitReturnShipment,
scrollToBottom,
openMessageTarget,
sendMessage,
confirmExchangeReceipt,
submitServiceRating,
load,
markAllRead,
requestAfterSaleHuman
};
}
