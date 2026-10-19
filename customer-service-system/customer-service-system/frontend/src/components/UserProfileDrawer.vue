<template>
  <el-drawer :model-value="modelValue" title="用户资料" size="420px" @update:model-value="$emit('update:modelValue', $event)">
    <div v-loading="loading" class="customer-profile">
      <template v-if="profile">
        <el-avatar :size="64" :src="profile.avatar || undefined">{{ profile.name?.slice(0, 1) }}</el-avatar>
        <h2>{{ profile.name }}</h2>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="账号">{{ profile.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ profile.email || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ profile.phone || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ profile.create_time }}</el-descriptions-item>
          <el-descriptions-item label="账号状态">{{ profile.status === 1 ? '正常' : '已停用' }} · {{ profile.online ? '在线' : '离线' }}</el-descriptions-item>
          <el-descriptions-item label="有效订单">{{ profile.order_count }} 笔</el-descriptions-item>
          <el-descriptions-item label="订单实付总额">¥{{ Number(profile.order_amount).toFixed(2) }}</el-descriptions-item>
        </el-descriptions>
        <el-button type="primary" :loading="starting" :disabled="profile.status !== 1" @click="startPrivate">私聊</el-button>
      </template>
      <el-empty v-else-if="!loading" :description="userId ? error || '资料暂不可用' : `${displayName || '该买家'}为历史订单中的买家记录，尚未关联注册账号，无法发起私聊。`" />
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createDirectConversation, getCustomerProfile } from '@/api/community'
const props = defineProps({ modelValue: Boolean, userId: Number, displayName: String })
const emit = defineEmits(['update:modelValue'])
const router = useRouter()
const profile = ref(null)
const loading = ref(false)
const starting = ref(false)
const error = ref('')
let requestId = 0
watch(() => [props.modelValue, props.userId], async ([visible, id]) => {
  const current = ++requestId
  profile.value = null
  loading.value = false
  error.value = ''
  if (!visible || !id) return
  loading.value = true
  try {
    const response = await getCustomerProfile(id)
    if (current === requestId) profile.value = response.data
  } catch (e) { if (current === requestId) error.value = e.message || '加载用户资料失败' }
  finally { if (current === requestId) loading.value = false }
})
async function startPrivate() {
  if (!profile.value || starting.value) return
  starting.value = true
  try {
    const response = await createDirectConversation(profile.value.id)
    emit('update:modelValue', false)
    await router.push({ path: '/manager/message-center', query: { conversationId: String(response.data.conversation_id) } })
  } catch (e) { ElMessage.error(e.message || '无法发起私聊') }
  finally { starting.value = false }
}
</script>

<style scoped>
.customer-profile { display: grid; justify-items: start; gap: 18px; min-height: 220px; }
.customer-profile h2 { margin: 0; }
.customer-profile :deep(.el-descriptions) { width: 100%; }
</style>
