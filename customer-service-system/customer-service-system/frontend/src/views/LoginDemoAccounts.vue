<template>
  <div class="demo-hint">
    <span class="demo-hint__title">体验账号（仅开发环境显示）</span>
    <template v-if="mode === 'backend'">
      <div class="demo-account"><b>后台管理员</b><span>账号：<code>admin</code></span><span>密码：<code>admin</code></span></div>
      <div class="demo-account"><b>运营账号 1</b><span>账号：<code>aaa</code></span><span>密码：<code>123</code></span></div>
      <div class="demo-account"><b>运营账号 2</b><span>账号：<code>bbb</code></span><span>密码：<code>123</code></span></div>
    </template>
    <div v-else class="demo-account demo-account--note">普通用户账号请注册后登录</div>
  </div>
</template>

<script setup>
defineProps({ mode: { type: String, required: true } })
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
  grid-template-columns: 82px 1fr 1fr;
  align-items: center;
  gap: 6px;
  padding: 3px 0;
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
  padding: 2px 8px;
  background: #eef3f0;
  border-radius: 4px;
  font-family: ui-monospace, monospace;
  color: var(--app-primary-dark);
}
</style>
