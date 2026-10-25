import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { SourceTextModule, SyntheticModule } from 'node:vm'

const source = await readFile(new URL('../src/utils/customerPage.js', import.meta.url), 'utf8')
const module = new SourceTextModule(source)
await module.link(specifier => new SyntheticModule(
  specifier === '@/router' ? ['default'] : ['loginAsUserApi'],
  function () { this.setExport(specifier === '@/router' ? 'default' : 'loginAsUserApi', () => {}) },
))
await module.evaluate()
const { isCustomerPageCommand } = module.namespace

for (const command of [
  '随便登录一个用户', '给我登录一个用户', '帮我随便登录一个用户',
  '请随机打开一个买家页面', '可以帮我登录用户123123吗', '能不能帮我打开用户端',
  '登录一个用户的账号', '请新开一个客户界面', '切换到买家账号',
]) {
  test(`用户页面指令：${command}`, () => assert.equal(isCustomerPageCommand(command), true))
}

for (const command of [
  '修改用户密码', '登录用户然后修改密码', '打开用户权限', '创建用户',
  '登录客服管理员', '为什么不能登录用户', '不要登录用户', '我不想打开用户页面',
  '打开用户页面并编辑个人资料', '打开客户页面删除用户', '查询用户订单',
]) {
  test(`保留限制：${command}`, () => assert.equal(isCustomerPageCommand(command), false))
}
