<template>
  <el-container class="layout layout--admin">
    <el-aside width="240px" class="sidebar">
      <div class="brand">
        <div class="brand-icon">
          <el-icon :size="22"><DataAnalysis /></el-icon>
        </div>
        <span class="brand-text">智能系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        background-color="transparent"
        text-color="#94a3b8"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/manager/home">
          <el-icon><icon-menu /></el-icon>
          <span>系统首页</span>
        </el-menu-item>
        <el-menu-item v-if="userInfo?.role === 'admin'" index="/manager/user">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-wrap">
      <el-header class="topbar" height="60px">
        <div class="topbar-left">
          <span class="topbar-title">{{ currentTitle }}</span>
        </div>
        <div class="topbar-right">
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
                  个人信息
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
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  Menu as IconMenu,
  User,
  DataAnalysis,
  UserFilled,
  Lock,
  SwitchButton
} from '@element-plus/icons-vue'
import router from '@/router'
import { logout } from '@/utils/auth'
import { useUser } from '@/utils/user'

const route = useRoute()
const { userInfo } = useUser()
const LAYOUT_LOCK_CLASS = 'admin-layout-lock'

const TITLE_MAP = {
  '/manager/home': '系统首页',
  '/manager/user': '用户管理',
  '/manager/profile': '个人信息',
  '/manager/password': '修改密码'
}

const activeMenu = computed(() => {
  if (route.path.startsWith('/manager/profile') || route.path.startsWith('/manager/password')) {
    return ''
  }
  return route.path
})

const currentTitle = computed(() => TITLE_MAP[route.path] || '智能系统')

const avatarLetter = computed(() => {
  const name = userInfo.value?.name || userInfo.value?.username || '?'
  return String(name).slice(0, 1).toUpperCase()
})

onMounted(() => {
  document.documentElement.classList.add(LAYOUT_LOCK_CLASS)
})

onUnmounted(() => {
  document.documentElement.classList.remove(LAYOUT_LOCK_CLASS)
})

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/manager/profile')
  } else if (command === 'password') {
    router.push('/manager/password')
  } else if (command === 'logout') {
    logout()
    router.push('/login')
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
  background: var(--app-sidebar-bg);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.brand {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--app-primary-light), var(--app-primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.brand-text {
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  padding: 12px 10px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin-bottom: 4px;
  border-radius: var(--app-radius-sm);
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: var(--app-sidebar-hover) !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: var(--app-sidebar-active) !important;
  font-weight: 500;
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
  background: var(--app-card-bg);
  border-bottom: 1px solid var(--app-border);
  box-shadow: var(--app-shadow);
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

.topbar-dropdown-trigger {
  display: inline-flex;
  align-items: center;
  outline: none;
  cursor: pointer;
}

.topbar-user {
  font-size: 14px;
  color: var(--app-text-secondary);
}

.topbar-avatar {
  background: linear-gradient(135deg, var(--app-primary-light), var(--app-primary-dark));
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

/* 窄屏保留图标导航 */
@media (max-width: 900px) {
  .sidebar {
    width: 72px !important;
  }
  .brand {
    padding: 0;
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
