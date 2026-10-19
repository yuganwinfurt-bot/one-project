<template>
  <div class="page-container dashboard">
    <div class="content-card dash-head">
      <div class="dash-head__text">
        <div class="dash-head__title">
          你好，{{ userInfo?.name || userInfo?.username || '同学' }}
        </div>
        <div class="dash-head__sub">
          这里是脚手架底座的工作台；后续业务模块（Agent 对话、数据看板等）可直接按此版式扩展。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUser } from '@/utils/user'

defineOptions({ name: 'Home' })

const { userInfo } = useUser()
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-gap);
}

.dash-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.dash-head__title {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.dash-head__sub {
  margin-top: 4px;
  font-size: 13px;
  color: var(--app-text-secondary);
}
</style>
