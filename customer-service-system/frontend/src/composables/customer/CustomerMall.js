import { useCustomerRouter } from '@/utils/customerRouter'
import { computed, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { customerCoupons, claimCoupon, customerGroups, joinGroup, mallPortal, customerFeedback, sendFeedback } from '@/api/mall'
import { getAddresses } from '@/api/customer'

export function useCustomerMall() {
const route = useRoute(), router = useCustomerRouter()
const mode = computed(() => route.meta.mallMode)
const title = computed(() => ({ offers:'优惠与团购', help:'公告与帮助', feedback:'意见反馈' })[mode.value])
const subtitle = computed(() => mode.value === 'offers' ? '查看优惠券和团购，优惠金额以提交订单时的结果为准。' : mode.value === 'help' ? '查看商城通知、联系方式和常见问题。' : '描述你遇到的问题，商家回复会显示在本页。')
const loading = ref(false), saving = ref(false), coupons = ref([]), rules = ref([]), groups = ref([]), portal = ref({}), feedbacks = ref([])
const feedback = reactive({ name:'',content:'',contact:'' })
const groupDialog = ref(false), selectedGroup = ref(null), selectedRule = ref(null), addresses = ref([]), addressId = ref(null)
let version = 0
async function load() {
  const current = ++version, target = mode.value
  loading.value = true
  try {
    if (target === 'offers') {
      const [c,g] = await Promise.all([customerCoupons(),customerGroups()])
      if (current !== version) return
      coupons.value = c.data.list
      rules.value = g.data.rules
      groups.value = g.data.groups
    } else if (target === 'help') {
      const res = await mallPortal()
      if (current === version) portal.value = res.data
    } else {
      const res = await customerFeedback()
      if (current === version) feedbacks.value = res.data.list
    }
  } catch {} finally { if (current === version) loading.value = false }
}
async function claim(coupon) { try { await claimCoupon(coupon.id); ElMessage.success('已领取，可到购物车使用'); await load() } catch {} }
async function prepareGroup(rule, group = null) {
  if (!rule) return
  selectedRule.value = rule
  selectedGroup.value = group
  try { addresses.value = (await getAddresses()).data.list; addressId.value = addresses.value.find(a => a.is_default)?.id || addresses.value[0]?.id; groupDialog.value = true } catch {}
}
async function submitGroup() {
  if (saving.value) return
  saving.value = true
  try { await joinGroup({ rule_id:selectedRule.value.id, group_id:selectedGroup.value?.id || null, address_id:addressId.value }); groupDialog.value = false; ElMessage.success('参团成功，可在订单记录查看进度'); await load() } catch {} finally { saving.value = false }
}
async function submitFeedback() {
  if (saving.value) return
  if (!feedback.name.trim() || !feedback.content.trim()) { ElMessage.warning('请填写主题和反馈内容'); return }
  saving.value = true
  try { await sendFeedback({ ...feedback }); Object.assign(feedback,{ name:'',content:'',contact:'' }); ElMessage.success('反馈已提交'); await load() } catch {} finally { saving.value = false }
}
const timer = setInterval(() => { if (mode.value === 'offers' && document.visibilityState === 'visible' && !groupDialog.value && !saving.value) load() }, 60000)
onUnmounted(() => { version++; clearInterval(timer) })
watch(mode, load, { immediate:true })
return {
useCustomerRouter,
computed,
onUnmounted,
reactive,
ref,
watch,
useRoute,
ElMessage,
customerCoupons,
claimCoupon,
customerGroups,
joinGroup,
mallPortal,
customerFeedback,
sendFeedback,
getAddresses,
route,
router,
mode,
title,
subtitle,
loading,
saving,
coupons,
rules,
groups,
portal,
feedbacks,
feedback,
groupDialog,
selectedGroup,
selectedRule,
addresses,
addressId,
version,
load,
claim,
prepareGroup,
submitGroup,
submitFeedback,
timer
};
}
