<template>
  <el-container class="layout layout--admin layout--theme-classic">
    <el-aside :width="effectiveSidebarCollapsed ? '54px' : '210px'" class="sidebar" :class="{ 'sidebar--collapsed': effectiveSidebarCollapsed }">
      <div class="brand">
        <div ref="brandSwitcherRef" class="brand-switcher">
          <button
            ref="brandToggleRef"
            class="brand-icon brand-switcher-toggle"
            type="button"
            aria-label="打开项目菜单"
            aria-controls="brand-switcher-menu"
            :aria-expanded="brandMenuOpen"
            @click.stop="brandMenuOpen = !brandMenuOpen"
          >
            <svg
              viewBox="0 0 24 24"
              width="20"
              height="20"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              aria-hidden="true"
            >
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <Teleport to="body">
          <nav
            ref="brandMenuRef"
            :style="brandMenuStyle"
            id="brand-switcher-menu"
            class="brand-switcher-menu"
            aria-label="项目入口"
            :hidden="!brandMenuOpen"
          >
            <span class="brand-switcher-heading">项目入口</span>
            <span class="brand-switcher-current">电商分析平台 <small>当前页面</small></span>
            <a class="brand-switcher-link" :href="customerServiceUrl" @click="closeBrandMenu">
              售后工单系统 <span aria-hidden="true">→</span>
            </a>
            <a class="brand-switcher-link" :href="agentUrl" @click="closeBrandMenu">
              Agent 控制台 <span aria-hidden="true">→</span>
            </a>
            <a class="brand-switcher-link" :href="ragUrl" @click="closeBrandMenu">
              RAG 知识库 <span aria-hidden="true">→</span>
            </a>
            <a class="brand-switcher-link" :href="projectHomeUrl" @click="closeBrandMenu">
              项目主页 <span aria-hidden="true">→</span>
            </a>
          </nav>
          </Teleport>
        </div>
        <span class="brand-text">电商分析平台</span>
      </div>
      <CommerceSidebar :active="activeMenu" :collapsed="effectiveSidebarCollapsed" :user="userInfo" :customer-unread="customerMessageUnread" :staff-unread="staffMessageUnread" />
    </el-aside>

    <el-container class="main-wrap">
      <el-header class="topbar" height="50px">
        <div class="topbar-left">
          <button class="sidebar-fold" type="button" :aria-label="effectiveSidebarCollapsed ? '展开侧栏' : '收起侧栏'" :aria-expanded="!effectiveSidebarCollapsed" @click="toggleSidebar"><Transition name="sidebar-fold-icon"><el-icon :key="effectiveSidebarCollapsed ? 'expand' : 'fold'" :size="20"><Expand v-if="effectiveSidebarCollapsed" /><Fold v-else /></el-icon></Transition></button>
          <div class="breadcrumb-container" aria-label="当前位置">
            <button class="breadcrumb-home" type="button" @click="router.push('/manager/home')">首页</button>
            <template v-if="currentSection">
              <span class="breadcrumb-separator">/</span>
              <span>{{ currentSection }}</span>
            </template>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-current">{{ currentTitle }}</span>
          </div>
        </div>
        <div class="topbar-right">
          <!-- 铃铛统一进入消息列表，未读数按当前账号类型显示。 -->
          <button
            type="button"
            class="topbar-bell"
            :title="userInfo?.role === 'customer' ? '我的消息' : '消息中心'"
            :aria-label="userInfo?.role === 'customer' ? '打开我的消息' : '打开消息中心'"
            @click="openMessageCenter"
          >
            <el-badge :value="topbarMessageUnread" :hidden="!topbarMessageUnread" :max="99">
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
          </button>
          <button class="topbar-mini-store" type="button" aria-label="打开小程序商城" title="打开小程序商城" @click="router.push('/mini-store')">
            <el-icon><Shop /></el-icon>
            <span>小程序</span>
          </button>
          <span class="topbar-user">{{ userInfo?.name || userInfo?.username }}</span>
          <el-dropdown trigger="click" placement="bottom-end" @command="handleCommand">
            <span class="topbar-dropdown-trigger">
              <el-avatar :size="36" class="topbar-avatar" :src="userInfo?.avatar || undefined">
                {{ avatarLetter }}
              </el-avatar>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><UserFilled /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item v-if="userInfo?.role !== 'admin'" command="password">
                  <el-icon><Lock /></el-icon>
                  修改密码
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <nav class="tags-view-container" aria-label="已打开页面" role="tablist">
        <div class="tags-view-scroll">
          <div v-for="tab in visitedTabs" :key="tab.path" class="tags-view-item" :class="{ active: route.path === tab.path }">
            <button class="tags-view-link" type="button" role="tab" :aria-selected="route.path === tab.path" @click="router.push(tab.fullPath)">
              <span v-if="route.path === tab.path" class="tags-view-dot" aria-hidden="true"></span>{{ tab.label }}
            </button>
            <button v-if="!tab.fixed" class="tags-view-close" type="button" :aria-label="`关闭${tab.label}标签`" @click.stop="closeVisitedTab(tab)">×</button>
          </div>
        </div>
      </nav>
      <el-main class="main-content">
        <!-- 仅缓存对话页：切换菜单后会话不丢失；其他页面保持每次进入重新加载 -->
        <router-view v-slot="{ Component }">
          <keep-alive include="Chat">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>

  </el-container>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import CommerceSidebar from '@/components/CommerceSidebar.vue'
import { mallGroups, mallTitles } from '@/utils/mallNavigation'
import { Expand, Fold } from '@element-plus/icons-vue'
import {
  Menu as IconMenu,
  User,
  ChatDotRound,
  Clock,
  UserFilled,
  Lock,
  SwitchButton,
  Goods,
  Shop,
  List,
  ChatLineSquare,
  Document,
  TrendCharts,
  Search,
  Bell,
  Memo,
  ShoppingCart,
  Star,
  Tickets,
  Location,
  Service
} from '@element-plus/icons-vue'
import router from '@/router'
import { ElNotification } from 'element-plus'
import { getStaffMessageCenter, markStaffMessageEventRead } from '@/api/ecommerce'
import { getCustomerMessages } from '@/api/customer'
import { sendUserHeartbeat, sendUserLogout } from '@/api/user'
import { getToken, logout } from '@/utils/auth'
import { clearChatMessages } from '@/utils/chatCache'
import { apiUrl } from '@/utils/apiBase'
import { useUser } from '@/utils/user'

const route = useRoute()
function storedSidebarState() { try { return localStorage.getItem('ecom.sidebar-collapsed') === '1' } catch { return false } }
const sidebarCollapsed = ref(storedSidebarState())
const narrowSidebar = ref(window.innerWidth <= 900)
const effectiveSidebarCollapsed = computed(() => sidebarCollapsed.value || narrowSidebar.value)
function resizeSidebar() { narrowSidebar.value = window.innerWidth <= 900 }
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  // 窄屏也允许手动展开，下一次窗口尺寸变化时再按屏宽调整。
  if (narrowSidebar.value) { narrowSidebar.value = false; sidebarCollapsed.value = false }
  try { localStorage.setItem('ecom.sidebar-collapsed', sidebarCollapsed.value ? '1' : '0') } catch {}
}
const { userInfo } = useUser()
const customerMessageUnread = ref(0)
let customerMessageTimer = null
const staffMessageUnread = ref(0)
let staffMessageTimer = null
let staffMessageRefreshing = false
let orderNoticeBaselineReady = false
let layoutDisposed = false
const observedOrderNotices = new Set()
const orderNoticePopups = new Set()
const topbarMessageUnread = computed(() =>
  userInfo.value?.role === 'customer' ? customerMessageUnread.value : staffMessageUnread.value
)
const LAYOUT_LOCK_CLASS = 'admin-layout-lock'
const brandMenuOpen = ref(false)
const brandSwitcherRef = ref(null)
const brandToggleRef = ref(null)
const brandMenuRef = ref(null)
const brandMenuStyle = ref({})

function positionBrandMenu() {
  if (!brandMenuOpen.value || !brandToggleRef.value) return
  const anchor = brandToggleRef.value.getBoundingClientRect()
  const width = Math.min(235, window.innerWidth - 16)
  const height = brandMenuRef.value?.offsetHeight || 260
  brandMenuStyle.value = {
    width: `${width}px`,
    left: `${Math.max(8, Math.min(anchor.left, window.innerWidth - width - 8))}px`,
    top: `${Math.max(8, Math.min(anchor.bottom + 10, window.innerHeight - height - 8))}px`,
  }
}
watch([brandMenuOpen, effectiveSidebarCollapsed], async () => {
  await nextTick()
  positionBrandMenu()
}, { flush: 'post' })

const projectHomeUrl = new URL('/', window.location.href)
const agentUrl = new URL('/', window.location.href)
const ragUrl = new URL('/', window.location.href)
const customerServiceUrl = new URL('http://127.0.0.1:3000/tickets')
if (['127.0.0.1', 'localhost', '[::1]'].includes(window.location.hostname)) {
  projectHomeUrl.port = '8030'
  agentUrl.port = '8020'
  ragUrl.port = '4173'
} else {
  agentUrl.pathname = '/agent/'
  ragUrl.pathname = '/rag/'
}

function closeBrandMenu() {
  brandMenuOpen.value = false
}

function handleBrandMenuPointer(event) {
  if (!brandSwitcherRef.value?.contains(event.target) && !brandMenuRef.value?.contains(event.target)) closeBrandMenu()
}

function handleBrandMenuKeydown(event) {
  if (event.key === 'Escape' && brandMenuOpen.value) {
    closeBrandMenu()
    brandToggleRef.value?.focus()
  }
}

function openMessageCenter() {
  router.push(userInfo.value?.role === 'customer'
    ? '/manager/messages'
    : { path: '/manager/message-center', query: { tab: 'events' } })
}

function handleVisibilityChange() {
  // 切回标签页时立刻对一次，避免看到过期的角标
  if (document.visibilityState === 'visible') {
    if (userInfo.value?.role === 'customer') refreshCustomerMessageUnread()
    else refreshStaffMessageUnread()
    sendUserHeartbeat().catch(() => {})
  }
}

function handlePageHide() {
  const token = getToken()
  if (!token) return
  fetch(apiUrl('/api/user/logout'), {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    keepalive: true
  }).catch(() => {})
}

const USER_HEARTBEAT_POLL_MS = 30000
let userHeartbeatTimer = null

const TITLE_MAP = {
  '/manager/home': '系统首页',
  '/manager/platform-logs': '平台日志',
  '/manager/store': '商品首页',
  '/manager/cart': '购物车',
  '/manager/favorites': '我的收藏',
  '/manager/messages': '我的消息',
  '/manager/my-orders': '订单记录',
  '/manager/addresses': '我的地址',
  '/manager/chat': '智能运营助手',
  '/manager/history': '运行历史',
  '/manager/metrics': '观测看板',
  '/manager/products': '商品列表',
  '/manager/product-listing': '商品上架',
  '/manager/orders': '订单数据',
  '/manager/after-sales': '售后工单',
  '/manager/message-center': '消息中心',
  '/manager/reviews': '评价数据',
  '/manager/reports': '诊断报告',
  '/manager/semantic': '语义检索',
  '/manager/user': '用户管理',
  '/manager/profile': '个人资料',
  '/manager/password': '修改密码'
}

const activeMenu = computed(() => {
  if (route.path.startsWith('/manager/password')) {
    return ''
  }
  if (route.path.startsWith('/manager/store/products/')) return '/manager/store'
  if (route.path.startsWith('/manager/product-listing')) return '/manager/product-listing'
  if (route.path.startsWith('/manager/products/')) return '/manager/products'
  return route.path
})

const currentTitle = computed(() =>
  route.path.startsWith('/manager/product-listing')
    ? (route.params.id ? '编辑商品' : '商品上架')
    : route.path.startsWith('/manager/products/') || route.path.startsWith('/manager/store/products/')
      ? '商品详情'
      : mallTitles[route.params.resource] || ({ '/manager/offers': '优惠与团购', '/manager/help': '公告与帮助', '/manager/feedback': '意见反馈' })[route.path] || TITLE_MAP[route.path] || '电商分析平台'
)
const currentSection = computed(() => {
  const resource = String(route.params.resource || '')
  const mallGroup = mallGroups.find(group => group.items.some(([key]) => key === resource))
  if (mallGroup) return mallGroup.title
  if (['/manager/orders', '/manager/after-sales'].includes(route.path)) return '商场管理'
  if (route.path.startsWith('/manager/product-listing') || ['/manager/products', '/manager/reviews'].includes(route.path)) return '商品管理'
  if (['/manager/history', '/manager/reports', '/manager/metrics', '/manager/semantic'].includes(route.path)) return '智能分析'
  if (['/manager/user', '/manager/profile', '/manager/password', '/manager/platform-logs', '/manager/message-center', '/manager/messages'].includes(route.path)) return '系统管理'
  if (['/manager/cart', '/manager/favorites', '/manager/my-orders', '/manager/addresses'].includes(route.path)) return '我的购物'
  return ''
})
const visitedTabs = ref([{ path: '/manager/home', fullPath: '/manager/home', label: '首页', fixed: true }])
function addVisitedTab() {
  if (!route.path.startsWith('/manager/')) return
  const existing = visitedTabs.value.find(tab => tab.path === route.path)
  if (existing) {
    existing.fullPath = route.fullPath
    existing.label = currentTitle.value === '系统首页' ? '首页' : currentTitle.value
    return
  }
  visitedTabs.value.push({ path: route.path, fullPath: route.fullPath, label: currentTitle.value, fixed: false })
}
function closeVisitedTab(tab) {
  if (tab.fixed) return
  const index = visitedTabs.value.findIndex(item => item.path === tab.path)
  if (index < 0) return
  visitedTabs.value.splice(index, 1)
  if (route.path === tab.path) {
    const next = visitedTabs.value[Math.min(index, visitedTabs.value.length - 1)] || visitedTabs.value[0]
    router.push(next?.fullPath || '/manager/home')
  }
}
watch(() => route.fullPath, addVisitedTab, { immediate: true })
const avatarLetter = computed(() => {
  const name = userInfo.value?.name || userInfo.value?.username || '?'
  return String(name).slice(0, 1).toUpperCase()
})

onMounted(() => {
  window.addEventListener('resize', resizeSidebar)
  window.addEventListener('resize', positionBrandMenu)
  document.addEventListener('scroll', positionBrandMenu, true)
  document.addEventListener('transitionend', positionBrandMenu)
  document.documentElement.classList.add(LAYOUT_LOCK_CLASS)
  refreshCustomerMessageUnread()
  customerMessageTimer = setInterval(() => {
    if (document.visibilityState === 'visible') refreshCustomerMessageUnread()
  }, 5000)
  window.addEventListener('customer-messages-read', clearCustomerMessageUnread)
  window.addEventListener('customer-messages-updated', refreshCustomerMessageUnread)
  sendUserHeartbeat().catch(() => {})
  userHeartbeatTimer = setInterval(() => {
    if (document.visibilityState === 'visible') sendUserHeartbeat().catch(() => {})
  }, USER_HEARTBEAT_POLL_MS)
  if (userInfo.value?.role !== 'customer') {
    refreshStaffMessageUnread()
    staffMessageTimer = setInterval(() => {
      if (document.visibilityState === 'visible') refreshStaffMessageUnread()
    }, 5000)
  }
  window.addEventListener('staff-message-center-updated', handleStaffMessageCenterUpdated)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('pagehide', handlePageHide)
  document.addEventListener('mousedown', handleBrandMenuPointer)
  document.addEventListener('keydown', handleBrandMenuKeydown)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeSidebar)
  window.removeEventListener('resize', positionBrandMenu)
  document.removeEventListener('scroll', positionBrandMenu, true)
  document.removeEventListener('transitionend', positionBrandMenu)
  layoutDisposed = true
  for (const popup of orderNoticePopups) popup.close()
  orderNoticePopups.clear()
  document.documentElement.classList.remove(LAYOUT_LOCK_CLASS)
  if (customerMessageTimer) {
    clearInterval(customerMessageTimer)
    customerMessageTimer = null
  }
  if (staffMessageTimer) {
    clearInterval(staffMessageTimer)
    staffMessageTimer = null
  }
  window.removeEventListener('staff-message-center-updated', handleStaffMessageCenterUpdated)
  window.removeEventListener('customer-messages-read', clearCustomerMessageUnread)
  window.removeEventListener('customer-messages-updated', refreshCustomerMessageUnread)
  if (userHeartbeatTimer) {
    clearInterval(userHeartbeatTimer)
    userHeartbeatTimer = null
  }
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('pagehide', handlePageHide)
  document.removeEventListener('mousedown', handleBrandMenuPointer)
  document.removeEventListener('keydown', handleBrandMenuKeydown)
})

async function refreshCustomerMessageUnread() {
  if (userInfo.value?.role !== 'customer') {
    customerMessageUnread.value = 0
    return
  }
  try {
    const response = await getCustomerMessages()
    customerMessageUnread.value = Number(response.data?.unread_count || 0)
  } catch {
    // 消息数量属于辅助信息；接口暂不可用时不影响页面导航。
  }
}

async function refreshStaffMessageUnread() {
  if (userInfo.value?.role === 'customer') {
    staffMessageUnread.value = 0
    return
  }
  if (layoutDisposed || staffMessageRefreshing) return
  staffMessageRefreshing = true
  try {
    const response = await getStaffMessageCenter()
    if (layoutDisposed) return
    staffMessageUnread.value = Number(response.data?.unread_count || 0)
    const humanEvents = (response.data?.events || []).filter(event => event.event_type === 'human_support')
    for (const event of humanEvents) {
      const key = `human:${event.id}`
      if (!event.is_read && !observedOrderNotices.has(key)) {
        ElNotification({title: '买家申请人工客服', message: event.content, type: 'warning', duration: 8000,
          onClick: () => router.push({path: '/manager/message-center', query: {tab: 'events'}})})
      }
      observedOrderNotices.add(key)
    }
    const orderEvents = (response.data?.events || []).filter(event => event.event_type === 'order_paid')
    const newOrders = orderEvents.filter(event => !event.is_read && !observedOrderNotices.has(event.id))
    for (const event of orderEvents) observedOrderNotices.add(event.id)
    // 首次进入只恢复未读角标；之后只弹出新收到的订单，轮询不重复弹窗。
    if (orderNoticeBaselineReady && newOrders.length) showNewOrderNotice(newOrders)
    orderNoticeBaselineReady = true
  } catch {
    // 消息角标不影响其他页面导航。
  } finally {
    staffMessageRefreshing = false
  }
}

function showNewOrderNotice(events) {
  const single = events.length === 1 ? events[0] : null
  let popup
  popup = ElNotification({
    title: single ? '新订单待发货' : `${events.length} 笔新订单待发货`,
    message: single ? single.content : '买家已提交新的演示订单，请进入消息中心查看并安排发货。',
    type: 'success',
    duration: 8000,
    customClass: 'order-paid-popup',
    onClick: () => {
      popup.close()
      if (single) void openPaidOrderNotice(single)
      else router.push({ path: '/manager/message-center', query: { tab: 'events' } })
    },
    onClose: () => orderNoticePopups.delete(popup)
  })
  orderNoticePopups.add(popup)
}

async function openPaidOrderNotice(event) {
  try {
    await markStaffMessageEventRead(event.id)
    window.dispatchEvent(new CustomEvent('staff-message-center-updated'))
  } catch {
    // 标记暂时失败时仍允许处理订单，提醒会在发货事务内再次置为已读。
  }
  if (!layoutDisposed) router.push({ path: '/manager/orders', query: { orderId: String(event.target_id) } })
}

function handleStaffMessageCenterUpdated(event) {
  if (typeof event.detail === 'number') staffMessageUnread.value = event.detail
  else refreshStaffMessageUnread()
}

function clearCustomerMessageUnread() {
  customerMessageUnread.value = 0
}

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/manager/profile')
  } else if (command === 'password') {
    router.push('/manager/password')
  } else if (command === 'logout') {
    const loginRoute = userInfo.value?.role === 'customer'
      ? { path: '/login', query: { mode: 'user' } }
      : '/login'
    try {
      await sendUserLogout()
    } catch {}
    logout()
    clearChatMessages()
    router.push(loginRoute)
  }
}
</script>

<style scoped>
.sidebar--collapsed .brand-text { display: none; }
.sidebar--collapsed { padding-left: 4px; padding-right: 4px; }
.sidebar--collapsed .brand { justify-content: center; padding-left: 0; padding-right: 0; }
.sidebar-fold { display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; width: 34px; height: 34px; padding: 0; border: 1px solid #dce7df; border-radius: 8px; background: transparent; color: #536d61; cursor: pointer; }
.sidebar-fold:hover { background: #e5f2e9; }
.breadcrumb-container { display:flex; align-items:center; gap:8px; min-width:0; overflow:hidden; color:#606266; font-size:14px; white-space:nowrap; }
.breadcrumb-home { border:0; padding:0; background:transparent; color:#909399; font:inherit; cursor:pointer; }
.breadcrumb-home:hover { color:#409eff; }
.breadcrumb-separator { color:#c0c4cc; }
.breadcrumb-current { color:#606266; }
.tags-view-container { flex:0 0 34px; height:34px; min-width:0; overflow:hidden; background:#fff; border-bottom:1px solid #d8dce5; box-shadow:0 1px 3px rgba(0,0,0,.08); }
.tags-view-scroll { display:flex; align-items:center; gap:5px; width:100%; height:33px; overflow-x:auto; padding:0 8px; }
.tags-view-item { position:relative; display:inline-flex; flex:0 0 auto; align-items:center; height:26px; margin-top:1px; border:1px solid #d8dce5; background:#fff; color:#495060; font-size:12px; }
.tags-view-link { display:inline-flex; align-items:center; gap:4px; height:24px; border:0; padding:0 8px; background:transparent; color:inherit; font:inherit; cursor:pointer; }
.tags-view-item.active { border-color:#42b983; background:#42b983; color:#fff; }
.tags-view-dot { width:8px; height:8px; border-radius:50%; background:#fff; }
.tags-view-close { width:17px; height:17px; margin-right:3px; border:0; border-radius:50%; background:transparent; color:inherit; line-height:15px; cursor:pointer; }
.tags-view-close:hover { background:rgba(0,0,0,.16); color:#fff; }
.layout {
  width: 100%;
  max-width: 100vw;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  background: var(--app-bg);
}

.sidebar {
  padding: 20px 14px 14px;
  background: var(--app-sidebar-bg);
  border-right: 1px solid #c6d8ce;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.brand {
  min-height: 63px;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 2px 9px 23px;
}

.brand-icon {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: #102237;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.brand-switcher {
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}

.brand-switcher-toggle {
  border: 0;
  padding: 0;
  cursor: pointer;
  transition: filter 0.2s, box-shadow 0.2s;
}

.brand-switcher-toggle:hover,
.brand-switcher-toggle[aria-expanded='true'] {
  background: #1d4255;
}

.brand-switcher-toggle:focus-visible {
  outline: 3px solid rgba(26, 156, 129, 0.34);
  outline-offset: 3px;
}

.brand-switcher-menu {
  position: fixed;
  z-index: 3000;
  box-sizing: border-box;
  max-height: calc(100vh - 16px);
  overflow-y: auto;
  display: grid;
  gap: 5px;
  width: 215px;
  padding: 10px;
  border: 1px solid #dbe4e1;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 16px 40px rgba(16, 34, 55, 0.15);
}

.brand-switcher-menu[hidden] {
  display: none;
}

.brand-switcher-heading {
  padding: 4px 8px 6px;
  color: #71858e;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
}

.brand-switcher-link,
.brand-switcher-current {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 38px;
  padding: 8px 10px;
  border-radius: 8px;
  color: #102237;
  font-size: 13px;
  text-decoration: none;
  white-space: nowrap;
}

.brand-switcher-link:hover,
.brand-switcher-link:focus-visible {
  background: #e9f1ed;
  color: #147c69;
}

.brand-switcher-link span {
  color: #1a9c81;
}

.brand-switcher-current {
  background: #e9f1ed;
  color: #102237;
  font-weight: 600;
}

.brand-switcher-current small {
  margin: 0;
  color: #71858e;
  font-size: 10px;
  letter-spacing: 0;
}

.brand-text {
  font-size: 16px;
  font-weight: 600;
  color: #102237;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  padding: 12px 10px;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
}

.sidebar-menu :deep(.el-menu-item) {
  position: relative;
}

.sidebar-menu-label {
  display: inline-flex;
  min-width: 0;
  align-items: center;
  gap: 7px;
}

.sidebar-menu-badge {
  display: inline-flex;
  min-width: 16px;
  height: 16px;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border-radius: 9px;
  background: #f56c6c;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  line-height: 16px;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  min-height: 32px;
  flex: 0 1 44px;
  line-height: normal;
  margin-bottom: 0;
  border-radius: var(--app-radius-sm);
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: var(--app-sidebar-hover) !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: var(--app-sidebar-active) !important;
  border: 1px solid #c6d8ce;
  color: #102237 !important;
  font-weight: 600;
}

.sidebar-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #1a9c81;
}

.main-wrap {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  flex-shrink: 0;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--app-space-page);
  background: #fbfcf9;
  border-bottom: 1px solid var(--app-border);
  box-shadow: none;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  flex: 1;
  overflow: hidden;
}

.topbar-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.topbar-dropdown-trigger {
  display: inline-flex;
  align-items: center;
  outline: none;
  cursor: pointer;
}

.topbar-mini-store {
  min-height:36px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:7px;
  padding:0 11px;
  border:1px solid var(--app-border);
  border-radius:8px;
  background:#fff;
  color:var(--app-text-secondary);
  font:inherit;
  font-size:12px;
  cursor:pointer;
  transition:color .2s,border-color .2s,background-color .2s;
}
.topbar-mini-store:hover { border-color:var(--app-primary); color:var(--app-primary); }
.topbar-bell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border: 0;
  background: transparent;
  color: var(--app-text-secondary);
  cursor: pointer;
  outline: none;
  font: inherit;
  transition: color 0.2s;
}

.topbar-bell:hover {
  color: var(--app-primary);
}

.alert-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--app-border);
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text);
}

.alert-panel__unread {
  font-size: 12px;
  font-weight: 400;
  color: #ef4444;
}

.alert-panel__list {
  margin: 0;
  padding: 0;
  list-style: none;
  max-height: 260px;
  overflow-y: auto;
}

.alert-panel__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--app-border);
  cursor: pointer;
}

.alert-panel__item:last-child {
  border-bottom: none;
}

.alert-panel__item:hover .alert-panel__content {
  color: var(--app-primary);
}

.alert-panel__content {
  flex: 1;
  font-size: 13px;
  color: var(--app-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alert-panel__time {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.alert-panel__empty {
  padding: 14px 0;
  text-align: center;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.alert-panel__foot {
  padding-top: 8px;
  border-top: 1px solid var(--app-border);
  text-align: right;
}

.topbar-user {
  font-size: 14px;
  color: var(--app-text-secondary);
}

.topbar-avatar {
  background: #102237;
  color: #fff;
  font-weight: 600;
}

.main-content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  --el-main-padding: 0;
  padding: var(--app-space-page);
  overflow: hidden;
}

/* 窄屏保留图标导航，为分析内容和输入框留出空间。 */
@media (max-width: 900px) {
  .sidebar.sidebar--collapsed {
    width: 72px !important;
    padding-right: 4px;
    padding-left: 4px;
    position: relative;
    z-index: 10;
    overflow: visible;
  }
  .brand {
    padding: 2px 0 23px;
    justify-content: center;
  }
  .sidebar--collapsed .brand-text {
    display: none;
  }
  .sidebar--collapsed .sidebar-menu {
    padding: 12px 8px;
  }
  .sidebar--collapsed .sidebar-menu :deep(.el-menu-item) {
    justify-content: center;
    padding: 0 !important;
  }
  .sidebar--collapsed .sidebar-menu :deep(.el-menu-item .el-icon) {
    margin-right: 0;
  }
  .sidebar--collapsed .sidebar-menu :deep(.el-menu-item > span) {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
  }
  .topbar {
    padding: 0 16px;
  }
}
@media (max-width: 500px) {
  .topbar-user {
    display: none;
  }
  .topbar-right {
    gap: 8px;
  }
  .topbar-mini-store {
    width:36px;
    min-width:36px;
    padding:0;
  }
  .topbar-mini-store span {
    display:none;
  }
}
</style>

<style>
html.admin-layout-lock,
html.admin-layout-lock body,
html.admin-layout-lock #app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

html.admin-layout-lock .layout--admin .main-content {
  overflow-x: hidden;
  overflow-y: auto;
}
.layout--admin.layout--theme-classic {
  --app-primary: #409eff;
  --app-primary-light: #66b1ff;
  --app-primary-dark: #1f2d3d;
  --app-sidebar-bg: #1f2d3d;
  --app-sidebar-hover: #263445;
  --app-sidebar-active: #409eff;
  --app-bg: #f0f2f5;
  --app-card-bg: #fff;
  --app-text: #303133;
  --app-text-secondary: #606266;
  --app-border: #dcdfe6;
  --app-radius: 4px;
  --app-radius-sm: 4px;
  --app-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  --app-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12);
  --el-color-primary: #409eff;
  --el-color-primary-light-3: #79bbff;
  --el-color-primary-light-5: #a0cfff;
  --el-color-primary-light-7: #c6e2ff;
  --el-color-primary-light-8: #d9ecff;
  --el-color-primary-light-9: #ecf5ff;
  --el-color-primary-dark-2: #337ecc;
  --el-text-color-primary: #303133;
  --el-text-color-regular: #606266;
  --el-text-color-secondary: #909399;
  --el-border-color: #dcdfe6;
  --el-border-color-light: #e4e7ed;
  --el-border-color-lighter: #ebeef5;
  --el-fill-color-light: #f5f7fa;
  --el-fill-color-lighter: #fafafa;
  --el-bg-color-page: #f0f2f5;
  --el-table-header-bg-color: #f5f7fa;
  --el-table-border-color: #ebeef5;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-current-row-bg-color: #ecf5ff;
  --el-border-radius-base: 4px;
}

.layout--admin.layout--theme-classic .sidebar {
  border-right-color: #1f2d3d;
}
.layout--admin.layout--theme-classic .brand-text {
  color: #fff;
}
.layout--admin.layout--theme-classic .brand-icon {
  border-radius: 4px;
  background: #409eff;
}
.layout--admin.layout--theme-classic .sidebar-menu {
  gap: 0 !important;
  padding: 0 0 12px !important;
  background: #1f2d3d !important;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-sub-menu__title,
.layout--admin.layout--theme-classic .sidebar-menu .el-menu-item {
  box-sizing: border-box;
  width: 100%;
  min-height: 52px;
  height: 52px;
  margin: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  color: #bfcbd9 !important;
  line-height: 52px;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-sub-menu > .el-sub-menu__title {
  padding-right: 20px !important;
  background: #34495e !important;
  color: #dbe5ee !important;
  font-weight: 500;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-sub-menu > .el-sub-menu__title:hover,
.layout--admin.layout--theme-classic .sidebar-menu > .el-sub-menu.is-opened > .el-sub-menu__title,
.layout--admin.layout--theme-classic .sidebar-menu > .el-sub-menu.is-active > .el-sub-menu__title {
  background: #3a5169 !important;
  color: #fff !important;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-menu--inline {
  padding: 0 !important;
  background: #1f2d3d !important;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-menu--inline > .el-menu-item {
  min-height: 48px;
  height: 48px;
  padding-left: 50px !important;
  background: #1f2d3d !important;
  color: #bfcbd9 !important;
  line-height: 48px;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-menu--inline > .el-menu-item:hover {
  background: #263445 !important;
  color: #fff !important;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-menu--inline > .el-menu-item.is-active {
  background: #1f2d3d !important;
  color: #409eff !important;
  font-weight: 600;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-menu-item:hover {
  background: #263445 !important;
  color: #fff !important;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-menu-item.is-active {
  background: #34495e !important;
  color: #409eff !important;
  font-weight: 600;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-sub-menu__title .el-icon,
.layout--admin.layout--theme-classic .sidebar-menu .el-sub-menu__icon-arrow {
  color: #aebac8;
}
.layout--admin.layout--theme-classic .sidebar-menu .external-service-item a {
  border-radius: 0;
  color: #bfcbd9;
}
.layout--admin.layout--theme-classic .sidebar-menu .external-service-item a:hover {
  background: #263445;
  color: #fff;
}
.layout--admin.layout--theme-classic .topbar {
  background: #fff;
  border-bottom-color: #dcdfe6;
}
.layout--admin.layout--theme-classic .topbar-title {
  color: #303133;
}
.layout--admin.layout--theme-classic .sidebar-fold {
  border-color: #dcdfe6;
  border-radius: 4px;
  color: #606266;
}
.layout--admin.layout--theme-classic .sidebar-fold:hover {
  background: #ecf5ff;
  color: #409eff;
}
.layout--admin.layout--theme-classic .main-content {
  background: #f0f2f5;
}
.layout--admin.layout--theme-classic .content-card,
.layout--admin.layout--theme-classic .el-card {
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.layout--admin.layout--theme-classic .el-table {
  --el-table-header-bg-color: #f5f7fa;
  --el-table-border-color: #ebeef5;
  --el-table-row-hover-bg-color: #f5f7fa;
}
.layout--admin.layout--theme-classic {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
}
.layout--admin.layout--theme-classic .sidebar {
  padding: 0;
  background: #304156;
  border-right: 0;
}
.layout--admin.layout--theme-classic .brand {
  min-height: 50px;
  padding: 0 14px;
  gap: 10px;
}
.layout--admin.layout--theme-classic .brand-icon {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  background: #409eff;
}
.layout--admin.layout--theme-classic .brand-text {
  color: #fff;
  font-size: 15px;
}
.layout--admin.layout--theme-classic .sidebar-menu {
  gap: 0 !important;
  padding: 0 0 12px !important;
  background: #304156 !important;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-sub-menu__title,
.layout--admin.layout--theme-classic .sidebar-menu .el-menu-item {
  box-sizing: border-box;
  width: 100%;
  min-height: 50px;
  height: 50px;
  margin: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  color: #bfcbd9 !important;
  line-height: 50px;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-sub-menu > .el-sub-menu__title {
  padding-right: 20px !important;
  background: #34495e !important;
  color: #dbe5ee !important;
  font-weight: 500;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-sub-menu > .el-sub-menu__title:hover,
.layout--admin.layout--theme-classic .sidebar-menu > .el-sub-menu.is-opened > .el-sub-menu__title,
.layout--admin.layout--theme-classic .sidebar-menu > .el-sub-menu.is-active > .el-sub-menu__title {
  background: #3a5169 !important;
  color: #fff !important;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-menu--inline {
  padding: 0 !important;
  background: #1f2d3d !important;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-menu--inline > .el-menu-item {
  min-height: 48px;
  height: 48px;
  padding-left: 50px !important;
  background: #1f2d3d !important;
  color: #bfcbd9 !important;
  line-height: 48px;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-menu--inline > .el-menu-item:hover {
  background: #263445 !important;
  color: #fff !important;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-menu--inline > .el-menu-item.is-active {
  background: #1f2d3d !important;
  color: #409eff !important;
  font-weight: 600;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-menu-item {
  background: #304156 !important;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-menu-item:hover {
  background: #263445 !important;
  color: #fff !important;
}
.layout--admin.layout--theme-classic .sidebar-menu > .el-menu-item.is-active {
  background: #304156 !important;
  color: #409eff !important;
  font-weight: 600;
}
.layout--admin.layout--theme-classic .sidebar-menu .el-sub-menu__title .el-icon,
.layout--admin.layout--theme-classic .sidebar-menu .el-sub-menu__icon-arrow {
  color: #aebac8;
}
.layout--admin.layout--theme-classic .sidebar-menu .external-service-item a {
  min-height: 48px;
  border-radius: 0;
  color: #bfcbd9;
}
.layout--admin.layout--theme-classic .sidebar-menu .external-service-item a:hover {
  background: #263445;
  color: #fff;
}
.layout--admin.layout--theme-classic .topbar {
  height: 50px;
  flex: 0 0 50px;
  padding: 0 15px;
  background: #fff;
  border-bottom-color: #d8dce5;
}
.layout--admin.layout--theme-classic .sidebar-fold {
  width: 34px;
  height: 34px;
  border-color: transparent;
  border-radius: 0;
  color: #303133;
}
.layout--admin.layout--theme-classic .sidebar-fold:hover {
  background: #f5f7fa;
  color: #409eff;
}
.layout--admin.layout--theme-classic .breadcrumb-container {
  color: #606266;
}
.layout--admin.layout--theme-classic .breadcrumb-home {
  color: #303133;
}
.layout--admin.layout--theme-classic .breadcrumb-current {
  color: #909399;
}
.layout--admin.layout--theme-classic .main-content {
  padding: 0;
  background: #fff;
}
.layout--admin.layout--theme-classic .main-content > .page-container {
  padding: clamp(10px, 1vw, 20px);
}
.layout--admin.layout--theme-classic .content-card {
  min-width: 0;
  max-width: 100%;
  padding: clamp(12px, 0.85vw, 16px);
}
.layout--admin.layout--theme-classic .el-card {
  min-width: 0;
  max-width: 100%;
  border-color: #dfe6ec;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.layout--admin.layout--theme-classic .el-table {
  --el-table-header-bg-color: #f5f7fa;
  --el-table-border-color: #ebeef5;
  --el-table-row-hover-bg-color: #f5f7fa;
  color: #606266;
}
.layout--admin.layout--theme-classic .el-table th.el-table__cell {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
}
.layout--admin.layout--theme-classic .el-table td.el-table__cell {
  border-bottom-color: #ebeef5;
}
.layout--admin.layout--theme-classic .el-table .el-table__row--striped td.el-table__cell {
  background: #fafafa;
}
.layout--admin.layout--theme-classic .el-table--border .el-table__cell {
  border-right-color: #ebeef5;
}
.layout--admin.layout--theme-classic .el-button,
.layout--admin.layout--theme-classic .el-input__wrapper,
.layout--admin.layout--theme-classic .el-select__wrapper,
.layout--admin.layout--theme-classic .el-textarea__inner,
.layout--admin.layout--theme-classic .el-date-editor,
.layout--admin.layout--theme-classic .el-dialog,
.layout--admin.layout--theme-classic .el-pagination button,
.layout--admin.layout--theme-classic .el-pager li {
  border-radius: 4px;
}
.layout--admin.layout--theme-classic .el-button {
  font-weight: 400;
}
.layout--admin.layout--theme-classic .el-pagination {
  margin-top: 20px;
  color: #606266;
}
.layout--admin.layout--theme-classic .mall-heading {
  min-height: 0;
  justify-content: flex-end;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
.layout--admin.layout--theme-classic .mall-heading > div:first-child {
  display: none;
}
.layout--admin.layout--theme-classic .mall-content {
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
.layout--admin.layout--theme-classic .mall-toolbar {
  margin-bottom: 18px;
}
.layout--admin.layout--theme-classic .mall-summary article {
  border-radius: 4px;
  border-color: #dfe6ec;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.layout--admin .sidebar { transition: width 240ms cubic-bezier(.2, .8, .2, 1), flex-basis 240ms cubic-bezier(.2, .8, .2, 1), padding 240ms ease; }
.sidebar-fold-icon-enter-active,
.sidebar-fold-icon-leave-active { transition: opacity 160ms ease, transform 160ms ease; }
.sidebar-fold-icon-enter-from { opacity: 0; transform: rotate(-90deg) scale(.82); }
.sidebar-fold-icon-leave-to { opacity: 0; transform: rotate(90deg) scale(.82); }
</style>
