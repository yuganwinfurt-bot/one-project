<template>
  <el-dialog
    :model-value="modelValue"
    :title="dialogTitle"
    width="620px"
    :close-on-click-modal="false"
    class="after-sale-conversation-dialog"
    @update:model-value="emit('update:modelValue', $event)"
    @closed="emit('closed')"
  >
    <div v-if="afterSale" class="conversation-context">
      <strong>{{ afterSale.product_name || '售后沟通' }}</strong>
      <span>订单 {{ afterSale.order_no || `#${afterSale.order_id || ''}` }}</span>
    </div>

    <div ref="listRef" class="conversation-messages" v-loading="loading">
      <el-empty v-if="!loading && !messages.length" description="还没有消息，发一条消息开始沟通" :image-size="72" />
      <div
        v-for="message in messages"
        :key="message.id"
        class="conversation-message"
        :class="{ 'conversation-message--mine': isMine(message) }"
      >
        <div class="conversation-message__content">
          <span class="conversation-message__name">{{ isMine(message) ? '我' : message.sender_name }}</span>
          <div class="conversation-message__bubble">{{ message.content }}</div>
          <time>{{ message.create_time }}</time>
        </div>
      </div>
    </div>

    <div class="conversation-compose">
      <el-input
        v-model="draft"
        type="textarea"
        :rows="3"
        maxlength="2000"
        resize="none"
        placeholder="输入消息，按 Ctrl + Enter 发送"
        @keydown.ctrl.enter.prevent="sendMessage"
      />
      <el-button type="primary" :loading="sending" :disabled="!draft.trim()" @click="sendMessage">
        发送
      </el-button>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getCustomerAfterSaleMessages,
  sendCustomerAfterSaleMessage
} from '@/api/customer'
import { getAfterSaleMessages, sendAfterSaleMessage } from '@/api/ecommerce'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  afterSale: { type: Object, default: null },
  audience: { type: String, default: 'staff' }
})
const emit = defineEmits(['update:modelValue', 'closed', 'read', 'sent'])

const messages = ref([])
const loading = ref(false)
const sending = ref(false)
const draft = ref('')
const listRef = ref(null)
let pollTimer = null

const dialogTitle = computed(() =>
  props.audience === 'customer'
    ? '售后保障'
    : `联系用户${props.afterSale?.user_name || props.afterSale?.username ? ` · ${props.afterSale.user_name || props.afterSale.username}` : ''}`
)

function isMine(message) {
  if (message.sender_role === 'system') return false
  return props.audience === 'customer'
    ? message.sender_role === 'customer'
    : message.sender_role !== 'customer'
}

async function scrollToBottom() {
  await nextTick()
  if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
}

async function loadMessages(showLoading = false) {
  const afterSaleId = props.afterSale?.id
  if (!afterSaleId || loading.value) return
  if (showLoading) loading.value = true
  try {
    const response = props.audience === 'customer'
      ? await getCustomerAfterSaleMessages(afterSaleId)
      : await getAfterSaleMessages(afterSaleId)
    const data = response.data || {}
    const shouldScroll = !messages.value.length || messages.value.at(-1)?.id !== data.messages?.at(-1)?.id
    messages.value = data.messages || []
    if (props.audience === 'customer' && data.unread_count) emit('read', data.unread_count)
    if (shouldScroll) await scrollToBottom()
  } catch (error) {
    if (showLoading) ElMessage.error(error?.message || '加载沟通消息失败')
  } finally {
    if (showLoading) loading.value = false
  }
}

async function sendMessage() {
  const content = draft.value.trim()
  const afterSaleId = props.afterSale?.id
  if (!content || !afterSaleId || sending.value) return
  sending.value = true
  try {
    const response = props.audience === 'customer'
      ? await sendCustomerAfterSaleMessage(afterSaleId, content)
      : await sendAfterSaleMessage(afterSaleId, content)
    messages.value.push(response.data)
    draft.value = ''
    emit('sent', response.data)
    await scrollToBottom()
  } catch (error) {
    ElMessage.error(error?.message || '发送消息失败')
  } finally {
    sending.value = false
  }
}

watch(
  () => [props.modelValue, props.afterSale?.id, props.audience],
  ([visible, afterSaleId]) => {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
    messages.value = []
    draft.value = ''
    if (visible && afterSaleId) {
      loadMessages(true)
      pollTimer = setInterval(() => loadMessages(false), 5000)
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.conversation-context { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; color: #718296; font-size: 13px; }
.conversation-context strong { color: #17324b; font-size: 14px; }
.conversation-messages { display: flex; min-height: 180px; max-height: 340px; flex-direction: column; gap: 14px; overflow-y: auto; padding: 14px; border: 1px solid #e8eeec; border-radius: 12px; background: #f7faf8; }
.conversation-message { display: flex; justify-content: flex-start; }
.conversation-message--mine { justify-content: flex-end; }
.conversation-message__content { display: grid; max-width: min(82%, 420px); gap: 5px; }
.conversation-message--mine .conversation-message__content { justify-items: end; }
.conversation-message__name, .conversation-message time { color: #82919f; font-size: 11px; }
.conversation-message__bubble { padding: 10px 13px; border: 1px solid #e2e9e6; border-radius: 4px 14px 14px; background: #fff; color: #263f55; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere; }
.conversation-message--mine .conversation-message__bubble { border-color: #cde9df; border-radius: 14px 4px 14px 14px; background: #e7f5ef; }
.conversation-compose { display: flex; align-items: flex-end; gap: 12px; margin-top: 14px; }
.conversation-compose .el-input { flex: 1; }
@media (max-width: 600px) { .conversation-compose { align-items: stretch; flex-direction: column; } .conversation-compose .el-button { align-self: flex-end; } }
</style>
