import axios from 'axios'
import { getToken, logout } from './auth'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { apiBaseUrl } from './apiBase'

const service = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000 //30s
})

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
      ElMessage.error(data.message || '请求失败')
      if (data.code === 401) {
        logout()
        router.push('/login')
      }
      // HTTP 200 也可能是业务失败，让页面的 catch 保留待办和重试入口。
      return Promise.reject(data)
    }
    return data
  },
  (err) => {
    if (err.response) {
      const httpStatusCode = err.response.status
      if (httpStatusCode === 401) {
        ElMessage.error('登录状态已失效，请重新登录')
        logout()
        router.push('/login')
      } else {
        ElMessage.error(err.response.data?.message || '请求失败')
      }
    } else {
      // 后端没启动，网络异常了
      ElMessage.error('网络异常，请检查后端服务')
    }
    return Promise.reject(err)
  }
)

export default service
