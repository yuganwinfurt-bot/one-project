/**
 * 语义检索调试 API（对应 lesson-04 的检索链路）
 */
import request from '@/utils/request'

/** 模糊主题 → 向量检索，返回 top_k 命中与距离 */
export function searchSemantic(query, topK = 5) {
  return request.post('/api/semantic/search', { query, top_k: topK })
}

/** 将后台业务数据及功能规则脱敏同步到“电商分析平台”知识库 */
export function syncSemanticData() {
  return request.post('/api/semantic/sync', {}, { timeout: 45000, silentError: true })
}

/** 刷新页面时读最新任务；轮询时按任务编号读取，不重复提交快照。 */
export function getSemanticSyncStatus(jobId = '') {
  return request.get(`/api/semantic/sync${jobId ? `/${encodeURIComponent(jobId)}` : ''}`, {
    timeout: 15000, silentError: true
  })
}
