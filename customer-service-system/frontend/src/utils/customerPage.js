import router from '@/router'
import { loginAsUserApi } from '@/api/user'

export function isCustomerPageCommand(question) {
  const text = String(question || '').trim()
  if (!text || text.length > 120 || /为什么|怎么|如何|无法|失败|忘记|密码|不要|不想|不需要|不用|别|注册|创建|新增|新建|删除|修改|编辑|更新|重置|权限|资料|信息|然后|并且|分析|查询|是否/.test(text)) return false
  // Courtesy words and "随便/随机" are still requests to open an existing buyer.
  // Only this navigation path bypasses the model; account mutations stay blocked.
  const command = text.replace(/^(?:(?:请你|请|帮我|给我|为我|麻烦你|麻烦|我想要|我想|我要|可以|能不能|能否|随便|随机|任意|随意|再)\s*)+/, '')
  return /^(?:(?:打开|新开|开一个|开个|进入).*(?:用户|买家|客户)|(?:登录|登陆|切换到?).*(?:用户|买家|客户))/.test(command)
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
