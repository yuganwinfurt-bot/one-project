import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { createContext, SourceTextModule } from 'node:vm'

async function createService(fetch) {
  const source = await readFile(new URL('../src/utils/agentModel.js', import.meta.url), 'utf8')
  const module = new SourceTextModule(source, {
    context: createContext({ fetch, URL, AbortSignal, window: { location: {
      hostname: 'www.yuganwinfurt.top', href: 'https://www.yuganwinfurt.top/ecommerce/manager/chat'
    } } }),
    initializeImportMeta(meta) { meta.env = {} }
  })
  await module.link(() => { throw new Error('Unexpected import') })
  await module.evaluate()
  return module.namespace.getSupportModelStatus
}

test('check service readiness through Agent without reading or sending model credentials', async () => {
  const status = await createService(async (url, options) => {
    assert.equal(url.href, 'https://www.yuganwinfurt.top/agent/api/support-model/status')
    assert.equal(options.method, 'GET')
    assert.equal(options.credentials, 'omit')
    assert.equal(options.cache, 'no-store')
    assert.equal(options.body, undefined)
    assert.equal(options.headers, undefined)
    return {ok:true,json:async()=>({available:true,name:'客服模型'})}
  })
  assert.deepEqual(await status(), {available:true,name:'客服模型'})
})

test('an unavailable service remains unavailable in the readiness result', async () => {
  const status = await createService(async () => ({ok:true,json:async()=>({available:false,name:null})}))
  assert.equal((await status()).available, false)
})

test('a failed status request is not treated as an enabled model', async () => {
  const status = await createService(async () => ({ok:false,status:502}))
  await assert.rejects(status(), /无法读取客服模型状态/)
})
