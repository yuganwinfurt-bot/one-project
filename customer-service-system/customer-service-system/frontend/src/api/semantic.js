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
  return request.post('/api/semantic/sync', {}, { timeout: 600000 })
}
