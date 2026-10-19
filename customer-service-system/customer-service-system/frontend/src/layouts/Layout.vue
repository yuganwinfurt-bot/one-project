<template>
  <el-container class="layout layout--admin">
    <el-aside width="256px" class="sidebar">
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
          <nav
            id="brand-switcher-menu"
            class="brand-switcher-menu"
            aria-label="项目入口"
            :hidden="!brandMenuOpen"
          >
            <span class="brand-switcher-heading">项目入口</span>
            <span class="brand-switcher-current">电商分析平台 <small>当前页面</small></span>
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
        </div>
        <span class="brand-text">电商分析平台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        background-color="transparent"
        text-color="#566477"
        active-text-color="#102237"
      >
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>数据分析对话</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/home">
          <el-icon><icon-menu /></el-icon>
          <span>系统首页</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/platform-logs">
          <el-icon><Memo /></el-icon>
          <span>平台日志</span>
        </el-menu-item>
        <el-menu-item index="/manager/store">
          <el-icon><Shop /></el-icon>
          <span>商品首页</span>
        </el-menu-item>
        <el-menu-item v-if="userInfo?.role === 'customer'" index="/manager/cart">
          <el-icon><ShoppingCart /></el-icon>
          <span>购物车</span>
        </el-menu-item>
        <el-menu-item v-if="userInfo?.role === 'customer'" index="/manager/favorites">
          <el-icon><Star /></el-icon>
          <span>我的收藏</span>
        </el-menu-item>
        <el-menu-item v-if="userInfo?.role === 'customer'" index="/manager/messages">
          <el-icon><Bell /></el-icon>
          <span class="sidebar-menu-label">
            我的消息
            <span v-if="customerMessageUnread" class="sidebar-menu-badge">
              {{ customerMessageUnread > 99 ? '99+' : customerMessageUnread }}
            </span>
          </span>
        </el-menu-item>
        <el-menu-item v-if="userInfo?.role === 'customer'" index="/manager/my-orders">
          <el-icon><Tickets /></el-icon>
          <span>订单记录</span>
        </el-menu-item>
        <el-menu-item v-if="userInfo?.role === 'customer'" index="/manager/addresses">
          <el-icon><Location /></el-icon>
          <span>我的地址</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/history">
          <el-icon><Clock /></el-icon>
          <span>运行历史</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/reports">
          <el-icon><Document /></el-icon>
          <span>诊断报告</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/metrics">
          <el-icon><TrendCharts /></el-icon>
          <span>观测看板</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/products">
          <el-icon><Goods /></el-icon>
          <span>商品数据</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/orders">
          <el-icon><List /></el-icon>
          <span>订单数据</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/after-sales">
          <el-icon><Service /></el-icon>
          <span>售后中心</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/message-center">
          <el-icon><ChatDotRound /></el-icon>
          <span class="sidebar-menu-label">
            消息中心
            <span v-if="staffMessageUnread" class="sidebar-menu-badge">
              {{ staffMessageUnread > 99 ? '99+' : staffMessageUnread }}
            </span>
          </span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/reviews">
          <el-icon><ChatLineSquare /></el-icon>
          <span>评价数据</span>
        </el-menu-item>
        <el-menu-item v-if="['admin', 'user'].includes(userInfo?.role)" index="/manager/semantic">
          <el-icon><Search /></el-icon>
          <span>语义检索</span>
        </el-menu-item>
        <el-menu-item v-if="['user', 'customer'].includes(userInfo?.role)" index="/manager/profile">
          <el-icon><UserFilled /></el-icon>
          <span>个人资料</span>
        </el-menu-item>
        <el-menu-item v-if="userInfo?.role === 'admin'" index="/manager/user">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-wrap">
      <el-header class="topbar" height="72px">
        <div class="topbar-left">
          <span class="topbar-title">{{ currentTitle }}</span>
        </div>
        <div class="topbar-right">
          <button
            type="button"
            class="server-identity-control"
            :class="{
              'is-admin': serverIdentity.available && serverIdentity.role === 'admin',
              'is-unavailable': !serverIdentity.available && !serverIdentity.loading
            }"
            :disabled="serverIdentity.loading"
            :aria-label="serverIdentityLabel"
            aria-live="polite"
            @click="handleServerIdentityClick"
          >
            <span class="server-identity-dot" aria-hidden="true"></span>
            <span>{{ serverIdentityLabel }}</span>
          </button>
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
                <el-dropdown-item command="password">
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
      <el-main class="main-content">
        <!-- 仅缓存对话页：切换菜单后会话不丢失；其他页面保持每次进入重新加载 -->
        <router-view v-slot="{ Component }">
          <keep-alive include="Chat">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>

    <div
      v-if="serverLoginVisible"
      class="server-login-backdrop"
      @click.self="closeServerLogin"
      @keydown.esc.stop.prevent="closeServerLogin"
    >
      <section
        class="server-login-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="server-login-title"
      >
        <button
          class="server-login-close"
          type="button"
          aria-label="关闭登录框"
          :disabled="serverLoginBusy"
          @click="closeServerLogin"
        >
          ×
        </button>
        <p class="server-login-kicker">ADMINISTRATOR ACCESS</p>
        <h2 id="server-login-title">管理员登录</h2>
        <p class="server-login-description">登录后可管理服务器级管理员账号和角色。</p>
        <form class="server-login-form" @submit.prevent="submitServerAdminLogin">
          <label for="server-admin-username">账号</label>
          <input
            id="server-admin-username"
            ref="serverLoginUsernameInput"
            v-model="serverLoginUsername"
            type="text"
            autocomplete="username"
            maxlength="80"
            required
          />
          <label for="server-admin-password">密码</label>
          <input
            id="server-admin-password"
            v-model="serverLoginPassword"
            type="password"
            autocomplete="current-password"
            maxlength="512"
            required
          />
          <p v-if="serverLoginError" class="server-login-error" role="alert">
            {{ serverLoginError }}
          </p>
          <div class="server-login-actions">
            <button class="server-login-secondary" type="button" :disabled="serverLoginBusy" @click="closeServerLogin">
              取消
            </button>
            <button class="server-login-primary" type="submit" :disabled="serverLoginBusy">
              {{ serverLoginBusy ? '正在登录…' : '登录' }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </el-container>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
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
import { ElMessage } from 'element-plus'
import { getStaffMessageCenter } from '@/api/ecommerce'
import { getCustomerMessages } from '@/api/customer'
import { sendUserHeartbeat, sendUserLogout } from '@/api/user'
import { getToken, logout } from '@/utils/auth'
import { clearChatMessages } from '@/utils/chatCache'
import { apiUrl } from '@/utils/apiBase'
import { useUser } from '@/utils/user'

const route = useRoute()
const { userInfo } = useUser()
const customerMessageUnread = ref(0)
let customerMessageTimer = null
const staffMessageUnread = ref(0)
let staffMessageTimer = null
const topbarMessageUnread = computed(() =>
  userInfo.value?.role === 'customer' ? customerMessageUnread.value : staffMessageUnread.value
)
const LAYOUT_LOCK_CLASS = 'admin-layout-lock'
const brandMenuOpen = ref(false)
const brandSwitcherRef = ref(null)
const brandToggleRef = ref(null)

const isLocalProjectHost = ['127.0.0.1', 'localhost', '[::1]'].includes(window.location.hostname)
const projectHomeUrl = new URL('/', window.location.href)
const agentUrl = new URL('/', window.location.href)
const ragUrl = new URL('/', window.location.href)
if (isLocalProjectHost) {
  projectHomeUrl.port = '8030'
  agentUrl.port = '8020'
  ragUrl.port = '4173'
} else {
  agentUrl.pathname = '/agent/'
  ragUrl.pathname = '/rag/'
}

const serverIdentity = ref({
  role: 'guest',
  available: false,
  loading: true,
  loginConfigured: false
})
const serverLoginVisible = ref(false)
const serverLoginUsernameInput = ref(null)
const serverLoginUsername = ref('')
const serverLoginPassword = ref('')
const serverLoginError = ref('')
const serverLoginBusy = ref(false)

const serverIdentityLabel = computed(() => {
  if (serverIdentity.value.loading) return '正在读取身份…'
  if (!serverIdentity.value.available) return '身份状态未知 · 重试'
  return serverIdentity.value.role === 'admin'
    ? '服务器管理员 · 退出'
    : '游客 · 登录'
})

function serverAuthEndpoint(action) {
  const url = new URL(window.location.origin)
  if (isLocalProjectHost) {
    url.port = '8020'
    url.pathname = `/api/auth/${action}`
  } else {
    url.pathname = `/agent/api/auth/${action}`
  }
  url.search = ''
  url.hash = ''
  return url.href
}

async function refreshServerIdentity() {
  serverIdentity.value = { ...serverIdentity.value, loading: true }
  try {
    const response = await fetch(serverAuthEndpoint('status'), { credentials: 'include' })
    if (!response.ok) throw new Error(`身份服务返回 HTTP ${response.status}`)
    const result = await response.json()
    serverIdentity.value = {
      role: result.role === 'admin' ? 'admin' : 'guest',
      available: true,
      loading: false,
      loginConfigured: Boolean(result.login_configured)
    }
  } catch {
    serverIdentity.value = {
      ...serverIdentity.value,
      available: false,
      loading: false
    }
  }
}

async function handleServerIdentityClick() {
  if (serverIdentity.value.loading) return
  if (!serverIdentity.value.available) {
    await refreshServerIdentity()
    return
  }

  if (serverIdentity.value.role === 'admin') {
    try {
      const response = await fetch(serverAuthEndpoint('logout'), {
        method: 'POST',
        credentials: 'include'
      })
      if (!response.ok) throw new Error(`退出失败：HTTP ${response.status}`)
      await refreshServerIdentity()
      ElMessage.success('已退出服务器管理员身份')
    } catch (error) {
      ElMessage.error(error.message || '服务器管理员退出失败')
    }
    return
  }

  if (!serverIdentity.value.loginConfigured) {
    ElMessage.warning('服务器管理员登录尚未配置')
    return
  }
  serverLoginUsername.value = ''
  serverLoginPassword.value = ''
  serverLoginError.value = ''
  serverLoginVisible.value = true
  await nextTick()
  serverLoginUsernameInput.value?.focus()
}

function closeServerLogin() {
  if (serverLoginBusy.value) return
  serverLoginVisible.value = false
  serverLoginPassword.value = ''
  serverLoginError.value = ''
}

async function submitServerAdminLogin() {
  if (serverLoginBusy.value) return
  if (!serverLoginUsername.value.trim() || !serverLoginPassword.value) {
    serverLoginError.value = '请输入账号和密码'
    return
  }
  serverLoginBusy.value = true
  serverLoginError.value = ''
  try {
    const response = await fetch(serverAuthEndpoint('login'), {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: serverLoginUsername.value.trim(),
        password: serverLoginPassword.value
      })
    })
    const result = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(result.detail || '登录失败，请检查账号和密码')
    await refreshServerIdentity()
    if (!serverIdentity.value.available || serverIdentity.value.role !== 'admin') {
      throw new Error('登录已提交，但身份状态未能确认，请稍后重试')
    }
    serverLoginVisible.value = false
    serverLoginPassword.value = ''
    ElMessage.success('服务器管理员登录成功')
  } catch (error) {
    serverLoginError.value = error.message || '登录服务暂不可用，请稍后重试'
  } finally {
    serverLoginBusy.value = false
  }
}

const SERVER_IDENTITY_POLL_MS = 60000
let serverIdentityTimer = null

function refreshServerIdentityWhenVisible() {
  if (document.visibilityState === 'visible') refreshServerIdentity()
}

function closeBrandMenu() {
  brandMenuOpen.value = false
}

function handleBrandMenuPointer(event) {
  if (!brandSwitcherRef.value?.contains(event.target)) closeBrandMenu()
}

function handleBrandMenuKeydown(event) {
  if (event.key === 'Escape' && brandMenuOpen.value) {
    closeBrandMenu()
    brandToggleRef.value?.focus()
  }
}

function openMessageCenter() {
  router.push(userInfo.value?.role === 'customer' ? '/manager/messages' : '/manager/message-center')
}

function handleVisibilityChange() {
  // 切回标签页时立刻对一次，避免看到过期的角标
  if (document.visibilityState === 'visible') {
    if (userInfo.value?.role === 'customer') refreshCustomerMessageUnread()
    else refreshStaffMessageUnread()
    refreshServerIdentity()
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
  '/manager/chat': '数据分析对话',
  '/manager/history': '运行历史',
  '/manager/metrics': '观测看板',
  '/manager/products': '商品数据',
  '/manager/orders': '订单数据',
  '/manager/after-sales': '售后中心',
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
  if (route.path.startsWith('/manager/products/')) return '/manager/products'
  return route.path
})

const currentTitle = computed(() =>
  route.path.startsWith('/manager/products/') || route.path.startsWith('/manager/store/products/')
    ? '商品详情'
    : TITLE_MAP[route.path] || '电商分析平台'
)

const avatarLetter = computed(() => {
  const name = userInfo.value?.name || userInfo.value?.username || '?'
  return String(name).slice(0, 1).toUpperCase()
})

onMounted(() => {
  document.documentElement.classList.add(LAYOUT_LOCK_CLASS)
  refreshServerIdentity()
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
  serverIdentityTimer = setInterval(() => {
    if (document.visibilityState === 'visible') refreshServerIdentity()
  }, SERVER_IDENTITY_POLL_MS)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('pagehide', handlePageHide)
  window.addEventListener('focus', refreshServerIdentityWhenVisible)
  document.addEventListener('mousedown', handleBrandMenuPointer)
  document.addEventListener('keydown', handleBrandMenuKeydown)
})

onUnmounted(() => {
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
  if (serverIdentityTimer) {
    clearInterval(serverIdentityTimer)
    serverIdentityTimer = null
  }
  if (userHeartbeatTimer) {
    clearInterval(userHeartbeatTimer)
    userHeartbeatTimer = null
  }
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('pagehide', handlePageHide)
  window.removeEventListener('focus', refreshServerIdentityWhenVisible)
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
  try {
    const response = await getStaffMessageCenter()
    staffMessageUnread.value = Number(response.data?.unread_count || 0)
  } catch {
    // 消息角标不影响其他页面导航。
  }
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
  position: absolute;
  top: calc(100% + 10px);
  left: 0;
  z-index: 30;
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

.server-identity-control {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 0 15px;
  border: 1px solid #dbe4e1;
  border-radius: 999px;
  background: #fff;
  color: #102237;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
}

.server-identity-control:hover:not(:disabled) {
  border-color: #a9d4c7;
  background: #fbfcf9;
  box-shadow: 0 2px 8px rgba(16, 34, 55, 0.05);
}

.server-identity-control:focus-visible {
  outline: 3px solid rgba(26, 156, 129, 0.24);
  outline-offset: 2px;
}

.server-identity-control:disabled {
  cursor: wait;
  opacity: 0.8;
}

.server-login-backdrop {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: grid;
  place-items: center;
  padding: 14px;
  background: #10223780;
  backdrop-filter: blur(3px);
}

.server-login-panel {
  position: relative;
  width: min(440px, 100%);
  padding: 31px;
  border: 1px solid #dbe4e1;
  border-radius: 17px;
  background: #fff;
  color: #102237;
  box-shadow: 0 24px 70px rgba(16, 34, 55, 0.2);
}

.server-login-kicker {
  margin: 0 0 10px;
  color: #188c77;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.16em;
}

.server-login-panel h2 {
  margin: 0;
  color: #102237;
  font-size: 23px;
}

.server-login-description {
  margin: 9px 0 22px;
  color: #687984;
  font-size: 13px;
  line-height: 1.6;
}

.server-login-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 34px;
  height: 34px;
  border: 1px solid #dbe4e1;
  border-radius: 8px;
  background: #fff;
  color: #536473;
  font: inherit;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.server-login-close:hover:not(:disabled) {
  background: #eef5f0;
  color: #102237;
}

.server-login-form {
  display: grid;
  gap: 8px;
}

.server-login-form label {
  margin-top: 6px;
  color: #536473;
  font-size: 12px;
  font-weight: 600;
}

.server-login-form input {
  width: 100%;
  height: 42px;
  padding: 0 11px;
  border: 1px solid #c6d8ce;
  border-radius: 8px;
  background: #fbfcf9;
  color: #102237;
  font: inherit;
  font-size: 13px;
  outline: none;
}

.server-login-form input:focus {
  border-color: #1a9c81;
  box-shadow: 0 0 0 3px rgba(26, 156, 129, 0.11);
}

.server-login-error {
  margin: 5px 0 0;
  color: #b44943;
  font-size: 12px;
  line-height: 1.6;
}

.server-login-actions {
  display: flex;
  justify-content: flex-end;
  gap: 9px;
  margin-top: 13px;
}

.server-login-actions button {
  min-height: 38px;
  padding: 0 14px;
  border-radius: 8px;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.server-login-secondary {
  border: 1px solid #dbe4e1;
  background: #fff;
  color: #536473;
}

.server-login-primary {
  border: 1px solid #102237;
  background: #102237;
  color: #fff;
}

.server-login-actions button:disabled,
.server-login-close:disabled {
  cursor: wait;
  opacity: 0.65;
}

@media (max-width: 500px) {
  .server-login-panel {
    padding: 27px 22px;
  }
}

.server-identity-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 8px;
  border-radius: 50%;
  background: #d9a441;
}

.server-identity-control.is-admin .server-identity-dot {
  background: #1a9c81;
}

.server-identity-control.is-unavailable .server-identity-dot {
  background: #d99a43;
}

.topbar-dropdown-trigger {
  display: inline-flex;
  align-items: center;
  outline: none;
  cursor: pointer;
}

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
  .sidebar {
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
  .brand-text {
    display: none;
  }
  .sidebar-menu {
    padding: 12px 8px;
  }
  .sidebar-menu :deep(.el-menu-item) {
    justify-content: center;
    padding: 0 !important;
  }
  .sidebar-menu :deep(.el-menu-item .el-icon) {
    margin-right: 0;
  }
  .sidebar-menu :deep(.el-menu-item > span) {
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
  .server-identity-control {
    min-height: 34px;
    gap: 6px;
    padding: 0 9px;
    font-size: 10px;
  }
  .server-identity-dot {
    width: 6px;
    height: 6px;
    flex-basis: 6px;
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
</style>
