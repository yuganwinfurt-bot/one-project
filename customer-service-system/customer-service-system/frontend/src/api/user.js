import request from '@/utils/request'

/**
 * 获取当前登录用户
 */
export function getUserInfo() {
  return request({
    url: '/api/user/me',
    method: 'get'
  })
}

/** 更新当前用户在线心跳 */
export function sendUserHeartbeat() {
  return request({
    url: '/api/user/heartbeat',
    method: 'post'
  })
}

/** 主动退出时清除在线心跳 */
export function sendUserLogout() {
  return request({
    url: '/api/user/logout',
    method: 'post'
  })
}

/**
 * 修改当前登录用户的个人信息
 */
export function updateUserInfo(data) {
  return request({
    url: '/api/user/me',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 */
export function updatePassword(data) {
  return request({
    url: '/api/user/password',
    method: 'put',
    data
  })
}

/**
 * 分页模糊查询用户列表
 */
export function getUserPageList(params) {
  return request({
    url: '/api/user/list',
    method: 'get',
    params
  })
}

/** 平台管理员以运营账号身份开启独立会话 */
export function loginAsUserApi(userId) {
  return request({
    url: `/api/user/${userId}/login-as`,
    method: 'post'
  })
}

/**
 * 新增用户
 */
export function createUserApi(data) {
  return request({
    url: '/api/user',
    method: 'post',
    data
  })
}

/** 仅管理员可为运营账号更新资料和密码 */
export function updateManagedUserApi(userId, data) {
  return request({
    url: `/api/user/${userId}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户
 */
export function deleteUserApi(userId) {
  return request({
    url: `/api/user/${userId}`,
    method: 'delete'
  })
}
