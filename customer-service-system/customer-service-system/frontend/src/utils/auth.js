//  存储token、存储用户信息、获取token、用户信息，删除token、用户信息这些作用
const TOKEN_KEY = 'token'
const USER_KEY = 'userInfo'
const SESSION_AUTH_OVERRIDE_KEY = 'sessionAuthOverride'

function authStorage() {
  return sessionStorage.getItem(SESSION_AUTH_OVERRIDE_KEY) === '1' ? sessionStorage : localStorage
}

export function beginSessionAuthOverride() {
  sessionStorage.setItem(SESSION_AUTH_OVERRIDE_KEY, '1')
}

export function getToken() {
  return authStorage().getItem(TOKEN_KEY)
}

export function setToken(token) {
  authStorage().setItem(TOKEN_KEY, token)
}

export function removeToken() {
  authStorage().removeItem(TOKEN_KEY)
}

export function getUserInfo() {
  const str = authStorage().getItem(USER_KEY)
  return str ? JSON.parse(str) : null
}

export function setUserInfo(userInfo) {
  authStorage().setItem(USER_KEY, JSON.stringify(userInfo))
}

export function removeUserInfo() {
  authStorage().removeItem(USER_KEY)
}

// 登出
export function logout() {
  removeToken()
  removeUserInfo()
}
