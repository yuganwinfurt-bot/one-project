<template>
  <div class="auth-page">
    <div class="auth-panel auth-panel--brand">
      <div class="brand-content">
        <div class="brand-logo">
          <el-icon :size="36"><DataAnalysis /></el-icon>
        </div>
        <h1>电商分析平台</h1>
        <p>
          自然语言提问 · 结构化 / 语义检索 · 多智能体协作<br />
          FastAPI · Vue 3 · Element Plus · LangGraph
        </p>
      </div>
    </div>
    <div class="auth-panel auth-panel--form">
      <el-card class="auth-card" shadow="never">
        <div class="login-modes" role="tablist" aria-label="登录入口">
          <button
            type="button"
            role="tab"
            class="login-mode"
            :class="{ 'is-active': loginMode === 'backend' }"
            :aria-selected="loginMode === 'backend'"
            @click="setLoginMode('backend')"
          >后台登录</button>
          <button
            type="button"
            role="tab"
            class="login-mode"
            :class="{ 'is-active': loginMode === 'user' }"
            :aria-selected="loginMode === 'user'"
            @click="setLoginMode('user')"
          >用户登录</button>
        </div>
        <h2 class="title">{{ loginMode === 'backend' ? '后台登录' : '用户登录' }}</h2>
        <p class="subtitle">
          {{ loginMode === 'backend' ? '管理员和运营账号登录后台' : '用户登录后可浏览商品并管理个人资料' }}
        </p>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="0"
          size="large"
          @keyup.enter="login"
        >
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="submit-btn" :loading="loadingValue" @click="login">
              登录
            </el-button>
          </el-form-item>
          <div class="footer-link">
            <template v-if="loginMode === 'user'">
              还没有账号？<router-link to="/register">立即注册</router-link>
            </template>
            <template v-else>选择下方演示账号即可体验后台功能</template>
          </div>
        </el-form>
        <LoginDemoAccounts :mode="loginMode" @select="fillDemoAccount" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { User, Lock, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useRoute } from 'vue-router'
import { loginApi } from '@/api/auth'
import { useUser } from '@/utils/user'
import LoginDemoAccounts from './LoginDemoAccounts.vue'

const { saveLoginData } = useUser()
const route = useRoute()

const formRef = ref()
const loginMode = ref(route.query.mode === 'user' ? 'user' : 'backend')
const form = reactive({
  username: '',
  password: ''
})
const loadingValue = ref(false)

function fillDemoAccount(account) {
  form.username = account.username
  form.password = account.password
  formRef.value?.clearValidate()
}

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

watch(
  () => route.query.mode,
  (mode) => {
    loginMode.value = mode === 'user' ? 'user' : 'backend'
  }
)

function setLoginMode(mode) {
  if (loginMode.value === mode) return
  loginMode.value = mode
  form.username = ''
  form.password = ''
  formRef.value?.clearValidate()
  router.replace({ path: '/login', query: mode === 'user' ? { mode: 'user' } : {} })
}

const login = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loadingValue.value = true
  try {
    const res = await loginApi({ ...form, login_type: loginMode.value })
    if (res.code === 200) {
      saveLoginData(res.data)
      ElMessage.success('登录成功')
      const redirect = route.query.redirect
      const safeRedirect = typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')
        ? redirect
        : null
      await router.push(loginMode.value === 'user' ? (safeRedirect || '/manager/store') : '/manager/home')
    }
  } finally {
    loadingValue.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
}

.auth-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-panel--brand {
  background: linear-gradient(145deg, #0f172a 0%, var(--app-primary-dark) 50%, var(--app-primary) 100%);
  color: #fff;
  padding: 48px;
}

.brand-content {
  max-width: 400px;
}

.brand-logo {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  backdrop-filter: blur(8px);
}

.brand-content h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
}

.brand-content p {
  font-size: 15px;
  line-height: 1.8;
  opacity: 0.85;
}

.auth-panel--form {
  background: var(--app-bg);
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius);
  padding: 8px 4px 4px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: var(--app-text);
}

.subtitle {
  margin: 8px 0 28px;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.login-modes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  margin: 0 0 24px;
  padding: 4px;
  border-radius: 10px;
  background: #f1f5f4;
}

.login-mode {
  min-height: 38px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--app-text-secondary);
  font: inherit;
  cursor: pointer;
}

.login-mode.is-active {
  background: #fff;
  color: var(--app-primary-dark);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(15, 35, 54, 0.12);
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
}

.footer-link {
  text-align: center;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.footer-link a {
  color: var(--app-primary);
  text-decoration: none;
  font-weight: 500;
}

.footer-link a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .auth-panel--brand {
    display: none;
  }
}
</style>
