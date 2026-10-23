import request from '@/utils/request'

/** 分页查询平台修改日志。 */
export function listPlatformLogs(params) {
  return request({
    url: '/api/platform-logs',
    method: 'get',
    params
  })
}

/** 回退一条支持回退的平台修改日志。 */
export function rollbackPlatformLog(id) {
  return request({
    url: `/api/platform-logs/${id}/rollback`,
    method: 'post'
  })
}
