<template>
  <main class="switch-account-page">
    <div class="switch-account-card">
      <div class="switch-account-mark">E</div>
      <h1>正在切换账号</h1>
      <p>{{ message }}</p>
    </div>
  </main>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { beginSessionAuthOverride } from '@/utils/auth'
import { useUser } from '@/utils/user'

const router = useRouter()
const { saveLoginData } = useUser()
const message = ref('正在等待管理员授权…')
let handoffTimeout = null

const handleHandoff = async (event) => {
  if (event.origin !== window.location.origin || event.source !== window.opener) return
  if (event.data?.type !== 'account-switch-session') return

  const loginData = event.data.data
  if (!loginData?.token || !loginData?.user) {
    message.value = '账号会话无效，请关闭此页后重试。'
    window.opener?.postMessage({ type: 'account-switch-error', message: message.value }, window.location.origin)
    return
  }

  window.removeEventListener('message', handleHandoff)
  if (handoffTimeout) clearTimeout(handoffTimeout)

  beginSessionAuthOverride()
  saveLoginData(loginData)
  message.value = `已登录为 ${loginData.user.name || loginData.user.username}，正在进入账号页面…`
  window.opener.postMessage(
    { type: 'account-switch-complete', username: loginData.user.username },
    window.location.origin
  )
  await router.replace('/manager/home')
}

onMounted(() => {
  if (!window.opener || window.opener.closed) {
    message.value = '未检测到发起切换的管理页面，请从用户管理中重新点击“登录”。'
    return
  }

  window.addEventListener('message', handleHandoff)
  window.opener.postMessage({ type: 'account-switch-ready' }, window.location.origin)
  handoffTimeout = setTimeout(() => {
    message.value = '等待管理员授权超时，请关闭此页后重试。'
  }, 15000)
})

onUnmounted(() => {
  window.removeEventListener('message', handleHandoff)
  if (handoffTimeout) clearTimeout(handoffTimeout)
})
</script>

<style scoped>
.switch-account-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: #f5f8f7;
  color: #102237;
}

.switch-account-card {
  width: min(100%, 420px);
  padding: 40px 32px;
  border: 1px solid #d9e5e1;
  border-radius: 20px;
  background: #fff;
  text-align: center;
  box-shadow: 0 18px 48px rgb(16 34 55 / 8%);
}

.switch-account-mark {
  display: grid;
  width: 52px;
  height: 52px;
  place-items: center;
  margin: 0 auto 20px;
  border-radius: 16px;
  background: #102237;
  color: #fff;
  font-size: 22px;
  font-weight: 700;
}

h1 {
  margin: 0;
  font-size: 22px;
}

p {
  margin: 12px 0 0;
  color: #718396;
  line-height: 1.7;
}
</style>
