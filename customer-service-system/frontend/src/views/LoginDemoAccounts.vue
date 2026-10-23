<template>
  <div class="demo-hint">
    <span class="demo-hint__title">演示账号 · 点击填入</span>
    <div class="demo-accounts">
      <div v-if="loadError" class="demo-account--note">
        演示账号暂时无法更新，<button type="button" class="demo-retry" @click="refreshAccounts">点击重试</button>
      </div>
      <div v-else-if="loading && !accounts.length" class="demo-account--note">正在读取演示账号…</div>
      <button
        v-for="account in accounts"
        :key="account.id"
        type="button"
        class="demo-account"
        :disabled="!account.password"
        :aria-label="`填入${account.label}演示账号`"
        @click="emit('select', account)"
      >
        <b>{{ account.label }}</b>
        <span>账号：<code>{{ account.username }}</code></span>
        <span>密码：<code>{{ account.password || '待补齐' }}</code></span>
      </button>
      <div v-if="mode === 'backend' && !loading && !loadError && !accounts.some(account => account.role === 'user')" class="demo-account--note">
        暂无启用的运营账号，可在后台用户管理中新建。
      </div>
      <div v-if="accounts.some(account => !account.password)" class="demo-account--note">
        待补齐的账号成功登录一次或重新设置密码后，即可在这里点击体验。
      </div>
      <div v-if="mode === 'user' && !loading && !loadError && !accounts.length" class="demo-account--note">暂无可用的演示用户。</div>
      <div v-if="accounts.length" class="demo-account--note demo-rule">{{ mode === 'backend' ? '显示最早创建的两个启用运营账号，修改后自动更新。' : '体验浏览商品、购物车、下单与售后流程。' }}</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { getDemoAccountsApi } from '@/api/auth'

const props = defineProps({ mode: { type: String, required: true } })
const emit = defineEmits(['select'])
const accounts = ref([])
const loading = ref(false)
const loadError = ref(false)
let interval = null
let controller = null
let requestNumber = 0

async function refreshAccounts(force = false) {
  if ((loading.value && force !== true) || document.hidden) return
  const requestId = ++requestNumber
  const requestedMode = props.mode
  controller?.abort()
  loading.value = true
  const requestController = new AbortController()
  controller = requestController
  const timeout = setTimeout(() => requestController.abort(), 10000)
  try {
    const result = await getDemoAccountsApi(requestedMode, requestController.signal)
    if (requestId !== requestNumber || requestedMode !== props.mode) return
    accounts.value = result
    loadError.value = false
  } catch {
    if (requestId !== requestNumber || requestedMode !== props.mode) return
    accounts.value = []
    loadError.value = true
  } finally {
    clearTimeout(timeout)
    if (requestId === requestNumber) loading.value = false
  }
}

watch(() => props.mode, () => {
  accounts.value = []
  loadError.value = false
  void refreshAccounts(true)
})
onMounted(() => {
  void refreshAccounts()
  interval = setInterval(() => { void refreshAccounts() }, 10000)
  window.addEventListener('focus', refreshAccounts)
  document.addEventListener('visibilitychange', refreshAccounts)
})
onUnmounted(() => {
  requestNumber += 1
  clearInterval(interval)
  controller?.abort()
  window.removeEventListener('focus', refreshAccounts)
  document.removeEventListener('visibilitychange', refreshAccounts)
})
</script>

<style scoped>
.demo-hint {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px dashed var(--app-border);
  font-size: 13px;
  color: var(--app-text-secondary);
}

.demo-hint__title {
  display: block;
  margin-bottom: 8px;
  text-align: center;
}

.demo-account {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr) minmax(0, 1fr);
  align-items: center;
  gap: 6px;
  padding: 3px 0;
}

.demo-account > span { min-width: 0; overflow-wrap: anywhere; }

button.demo-account {
  width: 100%;
  border: 0;
  border-radius: 6px;
  background: transparent;
  text-align: left;
  color: inherit;
  font: inherit;
  cursor: pointer;
}

button.demo-account:hover,
button.demo-account:focus-visible {
  background: #eef3f0;
}

button.demo-account:disabled {
  cursor: default;
  opacity: 0.65;
}

.demo-retry {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--app-primary);
  font: inherit;
  cursor: pointer;
}

.demo-rule {
  margin-top: 8px;
  font-size: 12px;
}

.demo-account b {
  color: var(--app-text-secondary);
  font-size: 12px;
  font-weight: 500;
}

.demo-account--note {
  display: block;
  text-align: center;
  color: var(--app-text-secondary);
}

.demo-account code {
  display: inline-block;
  box-sizing: border-box;
  max-width: 100%;
  overflow-wrap: anywhere;
  padding: 2px 8px;
  background: #eef3f0;
  border-radius: 4px;
  font-family: ui-monospace, monospace;
  color: var(--app-primary-dark);
}
</style>
