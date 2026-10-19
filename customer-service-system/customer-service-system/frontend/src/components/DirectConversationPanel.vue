<template>
  <section class="direct-panel">
    <header class="direct-panel__header"><el-avatar :src="peer?.peer_avatar || undefined">{{ peer?.peer_name?.slice(0, 1) }}</el-avatar><div><strong>{{ peer?.peer_name || '私聊' }}</strong><span>{{ peer?.peer_role === 'customer' ? '用户私聊' : '商家私聊' }}</span></div></header>
    <div ref="listRef" class="direct-panel__messages" v-loading="loading">
      <el-empty v-if="!messages.length && !loading" description="还没有消息，发送第一条消息开始私聊" />
      <article v-for="message in messages" :key="message.id" class="direct-message" :class="{ 'is-mine': message.sender_id === userInfo?.id }">
        <span>{{ message.sender_name }}</span><p>{{ message.content }}</p><time>{{ message.create_time }}</time>
      </article>
    </div>
    <form class="direct-panel__composer" @submit.prevent="send">
      <el-input v-model="draft" type="textarea" :rows="2" maxlength="2000" placeholder="输入私聊消息，Ctrl + Enter 发送" @keydown.ctrl.enter.prevent="send" />
      <el-button type="primary" :disabled="!draft.trim() || loading" :loading="sending" native-type="submit">发送</el-button>
    </form>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getDirectMessages, sendDirectMessage } from '@/api/community'
import { useUser } from '@/utils/user'
const props = defineProps({ conversationId: Number, peer: Object })
const emit = defineEmits(['updated'])
const { userInfo } = useUser()
const messages = ref([]), draft = ref(''), loading = ref(false), sending = ref(false), listRef = ref(null)
let requestId = 0, timer
async function load(initial = false) {
  const id = props.conversationId
  if (!id || (loading.value && !initial)) return
  const current = ++requestId
  if (initial) loading.value = true
  try {
    const response = await getDirectMessages(id)
    if (current !== requestId || props.conversationId !== id) return
    const rows = response.data?.list || []
    const changed = rows.at(-1)?.id !== messages.value.at(-1)?.id
    const nearBottom = !listRef.value || listRef.value.scrollHeight - listRef.value.scrollTop - listRef.value.clientHeight < 80
    messages.value = rows
    if (initial || (changed && nearBottom)) {
      await nextTick()
      if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
    }
    if (response.data?.unread_count) emit('updated')
  } catch (e) { if (initial && current === requestId) ElMessage.error(e.message || '加载私聊失败') }
  finally { if (current === requestId) loading.value = false }
}
watch(() => props.conversationId, () => { messages.value = []; draft.value = ''; load(true) }, { immediate: true })
timer = setInterval(() => { if (document.visibilityState === 'visible') load() }, 4000)
async function send() {
  const id = props.conversationId, content = draft.value.trim()
  if (!id || !content || sending.value || loading.value) return
  sending.value = true
  try {
    await sendDirectMessage(id, content)
    if (props.conversationId === id) { draft.value = ''; await load(true) }
    emit('updated')
  } catch (e) { ElMessage.error(e.message || '发送私聊失败') }
  finally { sending.value = false }
}
onBeforeUnmount(() => { requestId++; clearInterval(timer) })
</script>

<style scoped>
.direct-panel { display: flex; flex: 1; flex-direction: column; min-height: 0; min-width: 0; height: 100%; background: #f8faf9; }
.direct-panel__header { display: flex; gap: 12px; align-items: center; padding: 16px 20px; background: white; border-bottom: 1px solid #e5ece8; }
.direct-panel__header > div { display: grid; gap: 4px; }
.direct-panel__header span { font-size: 12px; color: #7b8b9b; }
.direct-panel__messages { display: flex; flex: 1; min-height: 0; overflow-y: auto; flex-direction: column; gap: 16px; padding: 20px; }
.direct-message { max-width: 76%; align-self: flex-start; }
.direct-message.is-mine { align-self: flex-end; }
.direct-message > span, .direct-message time { color: #82919f; font-size: 12px; }
.direct-message p { margin: 5px 0; padding: 10px 14px; background: white; border: 1px solid #e1e9e5; border-radius: 10px; white-space: pre-wrap; overflow-wrap: anywhere; }
.direct-message.is-mine p { background: #e8f6f0; }
.direct-panel__composer { display: flex; align-items: end; gap: 12px; padding: 16px; background: white; border-top: 1px solid #e5ece8; }
</style>
