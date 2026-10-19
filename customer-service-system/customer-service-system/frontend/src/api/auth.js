import request from '@/utils/request'
import { apiUrl } from '@/utils/apiBase'

/** 登录页公开的演示账号；不带登录令牌，也不缓存过期凭据。 */
export async function getDemoAccountsApi(mode, signal) {
  const response = await fetch(`${apiUrl('/api/auth/demo-accounts')}?mode=${encodeURIComponent(mode)}`, {
    cache: 'no-store',
    signal
  })
  const payload = await response.json()
  if (!response.ok || payload.code !== 200) {
    throw new Error(payload.message || '暂时无法读取演示账号')
  }
  return payload.data || []
}

/**
 * 登录请求
 */
export function loginApi(data) {
  return request({
    url: '/api/auth/login',
    method: 'post',
    data
  })
}

/**
 * 注册请求
 */
export function registerApi(data) {
  return request({
    url: '/api/auth/register',
    method: 'post',
    data
  })
}
