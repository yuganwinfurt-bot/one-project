import { onBeforeUnmount, onMounted } from 'vue'

// 页面重新获得焦点时立即同步；后台标签页暂停轮询。
export function useVisibleRefresh(refresh, interval = 5000) {
  let timer
  let refreshing = false
  const run = async () => {
    if (document.visibilityState !== 'visible' || refreshing) return
    refreshing = true
    try { await refresh() } catch {
      // 临时断线留给下次刷新重试，避免轮询产生未处理的 Promise 错误。
    } finally { refreshing = false }
  }
  onMounted(() => {
    timer = setInterval(run, interval)
    window.addEventListener('focus', run)
    document.addEventListener('visibilitychange', run)
  })
  onBeforeUnmount(() => {
    clearInterval(timer)
    window.removeEventListener('focus', run)
    document.removeEventListener('visibilitychange', run)
  })
}
