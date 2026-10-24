import axios from 'axios'
import { getToken, logout } from './auth'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useUser } from './user'
import { apiBaseUrl } from './apiBase'

const service = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000 //30s
})

function redirectToLogin() {
  useUser().reloadUser()
  const current = router.currentRoute.value
  router.replace(current.path.startsWith('/mini-store')
    ? {path:'/mini-store',query:{tab:'login',next:current.fullPath}}
    : '/login')
}

function isAuthRequest(config) {
  const url = String(config?.url || '').split('?')[0]
  return url === '/api/auth/login' || url === '/api/auth/register'
}

// 请求拦截器的配置
service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (err) => Promise.reject(err)
)

// 返回的拦截器配置
service.interceptors.response.use(
  (res) => {
    const data = res.data
    if (data.code !== 200) {
      const authRequest = isAuthRequest(res.config)
      if (!res.config.silentError || (data.code === 401 && !authRequest)) ElMessage.error(data.message || '请求失败')
      if (data.code === 401 && !authRequest) {
        logout()
        redirectToLogin()
      }
      // HTTP 200 也可能是业务失败，让页面的 catch 保留待办和重试入口。
      return Promise.reject(data)
    }
    return data
  },
  (err) => {
    const status = err.response?.status
    const detail = err.response?.data?.message || err.response?.data?.detail
    let message = typeof detail === 'string' ? detail : '请求失败，请稍后重试'
    if (status === 504) message = '服务器处理超时；后台同步任务可能仍在运行，请刷新进度'
    else if (status === 502 || status === 503) message = typeof detail === 'string' ? detail : '后端服务暂时不可用，请稍后重试'
    else if (!err.response) {
      message = ['ECONNABORTED', 'ETIMEDOUT'].includes(err.code)
        ? '请求等待超时；若已提交同步，任务可能仍在运行，请刷新进度'
        : '网络连接中断，请检查网络后重试'
    }
    err.userMessage = message
    if (err.response) {
      const httpStatusCode = err.response.status
      if (httpStatusCode === 401) {
        if (isAuthRequest(err.config)) {
          if (!err.config?.silentError) ElMessage.error(detail || '账号或密码错误')
        } else {
          ElMessage.error('登录状态已失效，请重新登录')
          logout()
          redirectToLogin()
        }
      } else if (!err.config?.silentError) {
        ElMessage.error(message)
      }
    } else if (!err.config?.silentError) {
      ElMessage.error(message)
    }
    return Promise.reject(err)
  }
)

export default service
