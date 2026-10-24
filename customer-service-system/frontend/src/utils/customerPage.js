import router from '@/router'
import { loginAsUserApi } from '@/api/user'

export function isCustomerPageCommand(question) {
  const text = String(question || '').trim()
  if (text.length > 120 || /为什么|怎么|如何|不能|无法|失败|忘记|密码|不要|不想|别给|注册|创建.*(?:账号|用户)|新增.*(?:账号|用户)|删除|修改|重置|然后|并且|分析|查询|是否|能不能/.test(text)) return false
  return /^(?:请|帮我|给我|麻烦|我想要|我想|我要|请你|再|新)*\s*(?:(?:打开|新开|开一个|开个|进入).*(?:用户端|买家端|客户端|(?:用户|买家|客户).*(?:页|界面|账号|账户))|(?:登录|登陆|切换到?).*(?:用户|买家|客户)|(?:打开|新开|进入).*(?:用户|买家|客户))/.test(text)
}

function waitForMessage(popup, type) {
  return new Promise((resolve,reject)=>{
    const cleanup = () => { window.removeEventListener('message',receive); clearTimeout(timer) }
    const receive = event => {
      if (event.origin !== window.location.origin || event.source !== popup) return
      if (event.data?.type === 'account-switch-error') { cleanup(); reject(new Error(event.data.message || '用户页面打开失败')) }
      else if (event.data?.type === type) { cleanup(); resolve(event.data) }
    }
    const timer = setTimeout(()=>{ cleanup(); reject(new Error('新页面响应超时，请重试')) },15000)
    window.addEventListener('message',receive)
  })
}

export async function openCustomerPage(entry, reservedPopup) {
  const popup = reservedPopup || window.open('about:blank','_blank')
  if (!popup) throw new Error('浏览器拦截了新标签页，请点击下方“打开用户页面”重试')
  try {
    if (entry.action === 'login_page') {
      popup.location.replace(router.resolve({path:'/login',query:{mode:'user',isolated:'1'}}).href)
      return {label:'用户登录页面', loggedIn:false}
    }
    if (entry.action !== 'login_as' || !Number.isInteger(entry.user?.id) || entry.user.role !== 'customer') throw new Error('用户页面信息无效')
    const ready = waitForMessage(popup,'account-switch-ready')
    popup.location.replace(router.resolve({name:'SwitchAccount'}).href)
    await ready
    const result = await loginAsUserApi(entry.user.id)
    if (popup.closed) throw new Error('新标签页已关闭，请重试')
    const completed = waitForMessage(popup,'account-switch-complete')
    popup.postMessage({type:'account-switch-session',data:result.data},window.location.origin)
    await completed
    return {label:entry.label, loggedIn:true}
  } catch (error) { if (!popup.closed) popup.close(); throw error }
}
