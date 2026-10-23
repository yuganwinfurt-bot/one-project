// 本地开发走 Vite 代理；子目录部署时与页面使用同一个前缀。
// 例如 BASE_URL=/ecommerce/，则接口为 /ecommerce/api/...。
export const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.BASE_URL || '/')
  .replace(/\/+$/, '')

export function apiUrl(path) {
  return `${apiBaseUrl}/${path.replace(/^\/+/, '')}`
}
