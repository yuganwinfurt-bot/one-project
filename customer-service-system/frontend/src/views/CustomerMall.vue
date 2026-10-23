<template>
  <div class="page-container customer-mall" v-loading="loading">
    <section class="content-card page-heading"><div><p class="eyebrow">{{ mode === 'offers' ? 'MEMBER BENEFITS' : 'CUSTOMER SERVICE' }}</p><h1>{{ title }}</h1><p>{{ subtitle }}</p></div><el-button @click="load">刷新</el-button></section>

    <template v-if="mode === 'offers'">
      <section class="content-card"><h2>领券中心</h2><p class="muted">每张优惠券每人限领一次，可在立即购买或购物车结算时使用。待付款订单取消或超时后释放优惠券，已付款订单退款不返还已核销的券。</p><div class="coupon-grid"><article v-for="coupon in coupons" :key="coupon.id" class="coupon"><div><strong>¥{{ coupon.discount }}</strong><span>满 ¥{{ coupon.min_amount }} 可用</span></div><section><h3>{{ coupon.name }}</h3><p>{{ coupon.starts_at }} 至 {{ coupon.ends_at }}</p><el-button :disabled="Boolean(coupon.claim_id) || !coupon.available || coupon.claimed >= coupon.quantity" type="primary" size="small" @click="claim(coupon)">{{ coupon.used_at ? '已使用' : coupon.reserved ? '待付款订单占用' : !coupon.available ? '已失效' : coupon.claim_id ? '已领取' : coupon.claimed >= coupon.quantity ? '已领完' : '立即领取' }}</el-button></section></article></div><el-empty v-if="!coupons.length" description="暂无优惠券" /></section>
      <section class="content-card"><h2>团购活动</h2><p class="muted">每次参团购买 1 件，团购价含运费且不叠加优惠券。成团后可发货；到期未成团自动取消演示订单并返还库存。</p><div class="group-grid"><article v-for="rule in rules" :key="rule.id"><h3>{{ rule.name }}</h3><p>商品 ID：{{ rule.product_id }} · {{ rule.target_size }} 人成团 · 限时 {{ rule.hours }} 小时</p><strong>¥{{ Number(rule.price).toFixed(2) }}</strong><el-button type="primary" @click="prepareGroup(rule)">发起拼团</el-button><el-button link @click="router.push(`/manager/store/products/${rule.product_id}`)">查看商品</el-button></article></div><el-empty v-if="!rules.length" description="暂无开放的团购活动" />
        <el-table v-if="groups.length" :data="groups" style="margin-top:24px"><el-table-column prop="id" label="团号" width="75" /><el-table-column prop="product_name" label="商品" min-width="150" /><el-table-column prop="leader" label="团长" /><el-table-column label="人数"><template #default="{row}">{{ row.member_count }} / {{ row.target_size }}</template></el-table-column><el-table-column prop="expires_at" label="截止时间" min-width="170" /><el-table-column label="状态"><template #default="{row}">{{ ({ forming:'组团中', completed:'已成团', expired:'已到期取消' })[row.status] }}</template></el-table-column><el-table-column label="操作" width="90"><template #default="{row}"><el-button v-if="row.status === 'forming' && rules.some(r => r.id === row.rule_id)" link type="primary" @click="prepareGroup(rules.find(r => r.id === row.rule_id), row)">参团</el-button></template></el-table-column></el-table>
      </section>
    </template>

    <template v-else-if="mode === 'help'">
      <section class="content-card"><h2>{{ portal.shop?.name || '商城公告' }}</h2><p class="plain-text">{{ portal.shop?.description }}</p><p v-if="portal.shop?.phone || portal.shop?.email">联系商家：{{ portal.shop.phone }} {{ portal.shop.email }}</p><el-collapse><el-collapse-item v-for="notice in portal.notices" :key="notice.id" :title="notice.name" :name="notice.id"><p class="plain-text">{{ notice.content }}</p><small>{{ notice.starts_at || notice.create_time }}</small></el-collapse-item></el-collapse><el-empty v-if="!portal.notices?.length" description="暂无公告" /></section>
      <section class="content-card"><h2>常见问题</h2><el-collapse><el-collapse-item v-for="faq in portal.faqs" :key="faq.id" :name="faq.id" :title="faq.name"><p class="plain-text">{{ faq.answer }}</p></el-collapse-item></el-collapse><el-empty v-if="!portal.faqs?.length" description="暂无常见问题" /></section>
    </template>

    <template v-else>
      <section class="content-card feedback-form"><el-form label-position="top"><el-form-item label="主题" required><el-input v-model="feedback.name" maxlength="120" /></el-form-item><el-form-item label="反馈内容" required><el-input v-model="feedback.content" type="textarea" :rows="5" maxlength="5000" show-word-limit /></el-form-item><el-form-item label="联系方式（选填）"><el-input v-model="feedback.contact" maxlength="120" /></el-form-item></el-form><el-button type="primary" :loading="saving" @click="submitFeedback">提交反馈</el-button></section>
      <section class="content-card"><h2>我的反馈</h2><article v-for="record in feedbacks" :key="record.id" class="feedback-record"><h3>{{ record.name }} <el-tag size="small" :type="record.reply ? 'success' : 'info'">{{ record.reply ? '已回复' : '待回复' }}</el-tag></h3><p class="plain-text">{{ record.content }}</p><blockquote v-if="record.reply">商家回复：{{ record.reply }}</blockquote><small>{{ record.create_time }}</small></article><el-empty v-if="!feedbacks.length" description="暂无反馈记录" /></section>
    </template>

    <el-dialog v-model="groupDialog" :title="selectedGroup ? `参加 ${selectedGroup.id} 号团` : '发起拼团'" width="min(520px,94vw)" :close-on-click-modal="false"><p>本次创建演示订单，购买 1 件，团购价 ¥{{ Number(selectedGroup?.price ?? selectedRule?.price ?? 0).toFixed(2) }}。</p><el-select v-model="addressId" placeholder="选择收货地址" style="width:100%"><el-option v-for="address in addresses" :key="address.id" :value="address.id" :label="`${address.receiver_name} · ${address.phone} · ${address.detail}`" /></el-select><el-button v-if="!addresses.length" style="margin-top:14px" @click="router.push('/manager/addresses')">先添加收货地址</el-button><template #footer><el-button @click="groupDialog=false">取消</el-button><el-button type="primary" :disabled="!addressId" :loading="saving" @click="submitGroup">确认参团</el-button></template></el-dialog>
  </div>
</template>

<script setup>
import { computed, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { customerCoupons, claimCoupon, customerGroups, joinGroup, mallPortal, customerFeedback, sendFeedback } from '@/api/mall'
import { getAddresses } from '@/api/customer'
const route = useRoute(), router = useRouter()
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
</script>

<style scoped>
.customer-mall { display:grid;gap:18px; }.page-heading { display:flex;align-items:center;justify-content:space-between;gap:20px; }.page-heading h1 { font-size:23px;margin:4px 0 10px;color:#102237; }.page-heading p,.muted { font-size:13px;color:#788b95;line-height:1.7; }.eyebrow { font-size:10px!important;letter-spacing:2px;color:#1a9c81!important; }.content-card h2 { font-size:18px;color:#102237;margin-top:0; }.coupon-grid,.group-grid { display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:16px; }.coupon { display:flex;gap:18px;border:1px solid #d5e9dd;border-radius:12px;overflow:hidden; }.coupon>div { min-width:100px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#e9f5ed;padding:15px;gap:10px; }.coupon strong { color:#118c71;font-size:29px; }.coupon span { font-size:12px;color:#6c8c7d; }.coupon section { padding:8px 15px 18px 0; }.coupon h3,.group-grid h3 { font-size:16px; }.coupon p,.group-grid p { font-size:12px;color:#7b8e96;line-height:1.8; }.group-grid>article { padding:20px;border:1px solid #dfeae3;border-radius:12px;background:#fcfdfb; }.group-grid strong { font-size:25px;color:#cb6a43;display:block;margin:15px 0; }.plain-text,blockquote { white-space:pre-wrap;line-height:1.85; }.feedback-form { max-width:800px; }.feedback-record { padding:12px 0 22px;border-bottom:1px solid #e8efea; }.feedback-record h3 { font-size:15px; }.feedback-record blockquote { margin:15px 0;padding:12px 18px;background:#edf7f0;border-left:3px solid #1b9f80; }.feedback-record small { color:#899996; }
</style>
