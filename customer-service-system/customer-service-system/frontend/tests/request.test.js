import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { SourceTextModule, SyntheticModule } from 'node:vm'
import axios from 'axios'

// 加载真实拦截器，仅替代浏览器存储、提示和路由；响应由 Axios adapter 提供。
async function createRequest(data) {
  const notifications = []
  const navigations = []
  let loggedOut = false
  const modules = {
    axios: { default: axios },
    './auth': { getToken: () => null, logout: () => { loggedOut = true } },
    'element-plus': { ElMessage: { error: message => notifications.push(message) } },
    '@/router': { default: { push: path => navigations.push(path) } }
  }
  const source = await readFile(new URL('../src/utils/request.js', import.meta.url), 'utf8')
  const module = new SourceTextModule(source, {
    initializeImportMeta(meta) { meta.env = {} }
  })
  await module.link(specifier => {
    const exports = modules[specifier]
    return new SyntheticModule(Object.keys(exports), function () {
      for (const [name, value] of Object.entries(exports)) this.setExport(name, value)
    })
  })
  await module.evaluate()
  const request = module.namespace.default
  request.defaults.adapter = async config => ({
    status: 200, statusText: 'OK', headers: {}, config, data
  })
  return { request, notifications, navigations, isLoggedOut: () => loggedOut }
}

for (const code of [403, 500]) {
  test(`业务错误 ${code} 拒绝 Promise，页面不会清除待办`, async () => {
    const response = { code, message: '确认失败', data: null }
    const { request, notifications } = await createRequest(response)
    let pending = true
    await assert.rejects(async () => {
      await request.post('/api/chat/actions/confirm')
      pending = false
    }, error => error === response)
    assert.equal(pending, true)
    assert.deepEqual(notifications, ['确认失败'])
  })
}

test('业务 401 拒绝请求并退出登录', async () => {
  const state = await createRequest({ code: 401, message: '过期' })
  await assert.rejects(state.request.get('/api/user/me'))
  assert.equal(state.isLoggedOut(), true)
  assert.deepEqual(state.navigations, ['/login'])
})

test('成功响应继续返回业务数据', async () => {
  const response = { code: 200, data: { approved: true } }
  const state = await createRequest(response)
  assert.deepEqual(await state.request.post('/api/chat/actions/confirm'), response)
  assert.deepEqual(state.notifications, [])
})
