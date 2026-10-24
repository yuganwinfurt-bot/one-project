<template>
  <div class="page-container staff-message-center" v-loading="loading">
    <section class="content-card staff-inbox">
      <aside class="staff-inbox__sidebar">
        <div class="staff-inbox__title"><span>消息 <small v-if="unreadCount">{{ unreadCount }} 条未读</small></span><el-button v-if="unreadCount" text size="small" :loading="markingAllRead" @click="markAllEventsRead">全部已读</el-button></div>
        <div class="staff-inbox__list">
          <button v-for="event in events" :key="event.id" type="button" class="staff-inbox__row" :class="{'is-selected': selectedEventId === event.id, 'is-unread': !event.is_read}" @click="selectEvent(event)">
            <span class="staff-inbox__avatar"><el-icon><component :is="eventIcon(event.event_type)" /></el-icon></span>
            <span class="staff-inbox__row-main"><span class="staff-inbox__row-heading"><strong>{{ event.title }}</strong><time>{{ shortTime(event.create_time) }}</time></span><span class="staff-inbox__row-preview">{{ event.content }}</span></span>
            <i v-if="!event.is_read" class="staff-inbox__unread-dot" />
          </button>
          <el-empty v-if="!events.length" :image-size="76" description="暂无消息" />
        </div>
      </aside>
      <main class="staff-inbox__main">
        <div v-if="activeEvent" class="staff-event-detail">
          <span class="staff-event-detail__icon"><el-icon :size="26"><component :is="eventIcon(activeEvent.event_type)" /></el-icon></span>
          <div class="staff-event-detail__body">
            <span class="staff-event-detail__type">{{ eventTypeLabel(activeEvent.event_type) }}</span><h2>{{ activeEvent.title }}</h2><time>{{ activeEvent.create_time || '时间未知' }}</time><p>{{ activeEvent.content }}</p>
            <el-button v-if="activeEvent.event_type === 'order_paid'" type="primary" @click="openOrder">查看订单并处理发货</el-button>
            <el-button v-else-if="activeEvent.event_type === 'review_reply'" type="primary" @click="router.push({path: `/manager/products/${activeEvent.product_id}`, query: {review_id: activeEvent.review_id}})">查看评论</el-button>
            <el-button v-else-if="['diagnosis_report', 'alert'].includes(activeEvent.event_type)" type="primary" @click="openReport">{{ activeEvent.event_type === 'alert' ? '查看预警' : '查看诊断报告' }}</el-button>
            <el-button v-else-if="['after_sale_request', 'human_support'].includes(activeEvent.event_type)" type="primary" @click="openEventConversation">打开售后工单</el-button>
          </div>
        </div>
        <div v-else class="staff-inbox__placeholder"><el-icon :size="42"><Bell /></el-icon><strong>选择一条消息查看详情</strong><span>人工接待提醒会出现在这里，点击通知可前往对应售后工单。</span></div>
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Bell, Document, Service, Tickets } from '@element-plus/icons-vue'
import { readReviewNotification } from '@/api/community'
import { getStaffMessageCenter, markAllStaffMessageEventsRead, markStaffMessageEventRead } from '@/api/ecommerce'
import { openSupportTickets } from '@/utils/supportPortal'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const markingAllRead = ref(false)
const events = ref([])
const selectedEventId = ref(null)
const unreadCount = ref(0)
const activeEvent = computed(() => events.value.find(item => item.id === selectedEventId.value))
let refreshTimer = null
let disposed = false
let requesting = false
function shortTime(value) { return String(value || '').slice(5, 16) }
function eventIcon(type) { return type === 'order_paid' ? Tickets : type === 'diagnosis_report' ? Document : ['after_sale_request', 'human_support'].includes(type) ? Service : Bell }
function eventTypeLabel(type) { return ({order_paid: '订单发货提醒', review_reply: '评价回复', diagnosis_report: '诊断报告', after_sale_request: '售后事件', human_support: '人工接待提醒', alert: '风险预警'})[type] || '系统通知' }
function notifyUnread() { window.dispatchEvent(new CustomEvent('staff-message-center-updated', {detail: unreadCount.value})) }
async function loadCenter(showLoading = false) {
  if (requesting || disposed) return
  requesting = true
  if (showLoading) loading.value = true
  try {
    const response = await getStaffMessageCenter()
    if (disposed) return
    events.value = response.data?.events || []
    unreadCount.value = Number(response.data?.unread_count || 0)
    notifyUnread()
  } catch (error) { if (showLoading) ElMessage.error(error?.message || '加载消息中心失败') }
  finally { loading.value = false; requesting = false }
}
async function selectEvent(event) {
  selectedEventId.value = event.id
  if (event.is_read) return
  try {
    if (event.event_type === 'review_reply') await readReviewNotification(event.notification_id)
    else await markStaffMessageEventRead(event.id)
    event.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    notifyUnread()
  } catch (error) { ElMessage.error(error?.message || '标记消息失败') }
}
async function markAllEventsRead() {
  if (markingAllRead.value) return
  markingAllRead.value = true
  try {
    await markAllStaffMessageEventsRead()
    events.value = events.value.map(item => ({...item, is_read: true}))
    unreadCount.value = 0
    notifyUnread()
    ElMessage.success('通知已全部读完')
  } catch (error) { ElMessage.error(error?.message || '标记通知失败') }
  finally { markingAllRead.value = false }
}
function openReport() { router.push({path: '/manager/reports', query: activeEvent.value?.event_type === 'alert' ? {tab: 'alerts'} : {tab: 'reports', reportId: String(activeEvent.value?.target_id || '')}}) }
function openEventConversation() { openSupportTickets(activeEvent.value?.event_type === 'human_support' ? {supportConversationId: activeEvent.value.target_id} : {afterSaleId: activeEvent.value?.target_id}) }
function openOrder() { if (activeEvent.value?.target_id) router.push({path: '/manager/orders', query: {orderId: String(activeEvent.value.target_id)}}) }
onMounted(async () => {
  if (route.query.tab || route.query.conversationId || route.query.afterSaleId) router.replace({path: route.path, query: {}})
  await loadCenter(true)
  refreshTimer = setInterval(() => { if (document.visibilityState === 'visible') loadCenter(false) }, 5000)
})
onBeforeUnmount(() => { disposed = true; if (refreshTimer) clearInterval(refreshTimer) })
</script>

<style scoped>
.staff-message-center { display:grid; grid-template-rows:minmax(0,1fr); height:100%; gap:0; min-height:520px; }
.staff-message-center__heading { display:flex; align-items:center; justify-content:space-between; gap:18px; }
.staff-message-center__heading h1 { margin:0; color:#102237; font-size:22px; }
.staff-message-center__heading p { margin:6px 0 0; color:#728396; font-size:14px; }
.staff-inbox { display:grid; grid-template-columns:minmax(300px,360px) minmax(0,1fr); min-height:0; overflow:hidden; padding:0; }
.staff-inbox__sidebar { display:flex; min-height:0; flex-direction:column; border-right:1px solid #e5ece8; }
.staff-inbox__title { display:flex; align-items:center; justify-content:space-between; padding:18px; border-bottom:1px solid #e9efec; font-weight:600; color:#102237; }
.staff-inbox__title small { color:#ed6b28; font-size:12px; font-weight:400; }
.staff-inbox__list { min-height:0; flex:1; overflow:auto; }
.staff-inbox__row { display:flex; width:100%; align-items:center; gap:12px; padding:15px 14px; border:0; border-bottom:1px solid #f0f3f1; color:inherit; background:#fff; cursor:pointer; text-align:left; }
.staff-inbox__row:hover,.staff-inbox__row.is-selected { background:#f2f8f5; }
.staff-inbox__row-main { display:grid; min-width:0; flex:1; gap:5px; }
.staff-inbox__row-heading { display:flex; min-width:0; align-items:center; justify-content:space-between; gap:8px; }
.staff-inbox__row-heading strong { overflow:hidden; color:#102237; font-size:14px; text-overflow:ellipsis; white-space:nowrap; }
.staff-inbox__row-heading time { flex:none; color:#9aa7b3; font-size:11px; }
.staff-inbox__row-preview { overflow:hidden; color:#82919f; font-size:12px; text-overflow:ellipsis; white-space:nowrap; }
.staff-inbox__unread-dot { width:7px; height:7px; flex:none; border-radius:50%; background:#ed6b28; }
.staff-inbox__avatar { display:grid; width:38px; height:38px; flex:none; place-items:center; border-radius:12px; color:#087e70; background:#e4f2ed; }
.staff-inbox__main { display:flex; min-width:0; min-height:0; overflow:auto; background:#f7f9f8; }
.staff-event-detail { display:flex; gap:18px; padding:clamp(24px,5vw,64px); }
.staff-event-detail__icon { display:grid; width:54px; height:54px; flex:none; place-items:center; border-radius:16px; color:#087e70; background:#e4f2ed; }
.staff-event-detail__body { min-width:0; }
.staff-event-detail__type { color:#159b83; font-size:12px; font-weight:700; }
.staff-event-detail h2 { margin:7px 0; color:#102237; font-size:21px; }
.staff-event-detail time { color:#8a98a6; font-size:12px; }
.staff-event-detail p { max-width:760px; margin:22px 0; color:#53687b; line-height:1.8; white-space:pre-wrap; overflow-wrap:anywhere; }
.staff-inbox__placeholder { display:grid; flex:1; align-content:center; justify-items:center; gap:12px; padding:30px; color:#91a0ad; text-align:center; }
.staff-inbox__placeholder strong { color:#506276; font-size:15px; }
.staff-inbox__placeholder span { font-size:13px; }
@media(max-width:900px) { .staff-inbox { grid-template-columns:minmax(250px,300px) minmax(0,1fr); } }
@media(max-width:640px) { .staff-inbox { grid-template-columns:1fr; grid-template-rows:240px minmax(280px,1fr); } .staff-inbox__sidebar { border-right:0; border-bottom:1px solid #e5ece8; } .staff-event-detail { padding:20px; } }
</style>
