/**
 * 可观测性 / 历史记录 API
 */
import request from '@/utils/request'

/** 分页查询运行列表 */
export function listRuns(params = {}) {
  return request.get('/api/observability/runs', { params })
}

/** 观测看板统计（成功率 / 耗时 / 路由分布 / 反馈） */
export function getStats(params = {}) {
  return request.get('/api/observability/stats', { params })
}

/** 查看某次运行详情（含步骤） */
export function getRunDetail(runId) {
  return request.get(`/api/observability/runs/${runId}`)
}

/** 点赞 / 点踩 */
export function submitFeedback(runId, rating, comment) {
  return request.post(`/api/observability/runs/${runId}/feedback`, {
    rating,
    comment: comment || null
  })
}

/** 保存浏览器侧 Agent 模型生成的回答摘要 */
export function updateRunAnswer(runId, answer) {
  return request.put(`/api/observability/runs/${runId}/answer`, { answer })
}
