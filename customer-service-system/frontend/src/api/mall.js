import request from '@/utils/request'

export const mallPermissions = () => request.get('/api/mall/permissions', { silentError: true })
export const mallMeta = (resource) => request.get(`/api/mall/admin/meta/${resource}`)
export const mallList = (resource, params = {}) => request.get(`/api/mall/admin/${resource}`, { params })
export const mallSave = (resource, id, data) => id
  ? request.put(`/api/mall/admin/${resource}/${id}`, data)
  : request.post(`/api/mall/admin/${resource}`, data)
export const mallDelete = (resource, id) => request.delete(`/api/mall/admin/${resource}/${id}`)
export const mallSettings = (key) => request.get(`/api/mall/admin/settings/${key}`)
export const saveMallSettings = (key, data) => request.put(`/api/mall/admin/settings/${key}`, data)
export const mallStatistics = (dimension, params) => request.get(`/api/mall/admin/statistics/${dimension}`, { params })
export const mallPortal = () => request.get('/api/mall/portal')
export const mallRegionChildren = (parent_id = 0) => request.get('/api/mall/regions', { params: { parent_id } })
export const mallTopicProducts = (id) => request.get(`/api/mall/topics/${id}/products`)
export const mallActivity = (data) => request.post('/api/mall/activities', data, { silentError: true })
export const customerCoupons = () => request.get('/api/mall/my/coupons')
export const claimCoupon = (id) => request.post(`/api/mall/my/coupons/${id}/claim`)
export const customerFeedback = () => request.get('/api/mall/my/feedback')
export const sendFeedback = (data) => request.post('/api/mall/my/feedback', data)
export const customerGroups = () => request.get('/api/mall/my/groups')
export const joinGroup = (data) => request.post('/api/mall/my/groups', data)

export function downloadRows(rows, columns, name) {
  const escape = (value) => {
    let text = String(value ?? '')
    if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`
    return `"${text.replaceAll('"', '""')}"`
  }
  const content = [columns.map(c => escape(c.label)).join(','), ...rows.map(row => columns.map(c => escape(row[c.key])).join(','))].join('\r\n')
  const url = URL.createObjectURL(new Blob(['\uFEFF', content], { type: 'text/csv;charset=utf-8' }))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${name}.csv`
  anchor.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
