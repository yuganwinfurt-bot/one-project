/**
 * 巡检 API：系统触发的一次 Agent 跑动（用固定问题）
 */
import request from '@/utils/request'

/** 当前巡检使用的固定问题 */
export function getPatrolQuestion() {
  return request.get('/api/patrol/question')
}

/** 执行一次巡检（同步跑完，约 30~60 秒，超时放宽到 3 分钟） */
export function runPatrol() {
  return request.post('/api/patrol/run', null, { timeout: 180000 })
}
