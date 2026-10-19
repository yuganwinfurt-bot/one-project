/**
 * 对话会话的本地缓存。
 * 页面内切换菜单由 Layout 的 keep-alive 保持；
 * 刷新 / 重新打开页面时从这里恢复；退出登录时清除。
 */

const STORAGE_KEY = 'ecom_chat_messages'
// 最多保留的消息条数，避免长期使用后占用过大
const MAX_MESSAGES = 100

export function loadChatMessages() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const list = JSON.parse(raw)
    return Array.isArray(list) ? list : []
  } catch (e) {
    return []
  }
}

export function saveChatMessages(messages) {
  try {
    if (!messages || !messages.length) {
      localStorage.removeItem(STORAGE_KEY)
      return
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_MESSAGES)))
  } catch (e) {
    // 存储不可用或超限时不影响正常对话
  }
}

export function clearChatMessages() {
  localStorage.removeItem(STORAGE_KEY)
}
