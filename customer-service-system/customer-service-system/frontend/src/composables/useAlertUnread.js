/**
 * 预警未读数的单一数据源。
 *
 * 未读数要在三个地方显示（顶栏铃铛、诊断报告页签角标、首页指标卡），
 * 各自去取很容易出现数字不一致；这里用模块级 ref 共享，任何地方
 * 标记已读后调一次 refresh()，三处同时更新。
 */
import { ref } from 'vue'
import { getAlertSummary } from '@/api/ecommerce'

const unread = ref(0)
let inflight = null

export function useAlertUnread() {
  async function refresh({ force = false } = {}) {
    // 并发调用合并成一次请求（铃铛轮询与页面刷新可能同时触发）
    if (inflight) {
      if (!force) return inflight
      // 写入已读后，不能复用写入前发出的统计请求。
      await inflight
      return refresh()
    }
    inflight = getAlertSummary()
      .then((res) => {
        unread.value = res.data?.unread || 0
      })
      .catch(() => {
        // 静默失败：未读数不是关键路径，不打扰用户
      })
      .finally(() => {
        inflight = null
      })
    return inflight
  }

  return { unread, refresh }
}
