<template>

<div class="m-view"><MiniHeader :title="title" /><div class="m-scroll" v-loading="loading">
<template v-if="mode==='offers'"><section><h2 class="m-section-label">优惠券</h2><article v-for="coupon in coupons" :key="coupon.id" class="m-coupon"><div><strong>¥{{ coupon.discount }}</strong><small>满 {{ coupon.min_amount }} 元可用</small></div><section><h3>{{ coupon.name }}</h3><p>有效期至 {{ coupon.ends_at?.slice(0,10) }}</p><button class="m-primary" :disabled="Boolean(coupon.claim_id) || !coupon.available || coupon.claimed>=coupon.quantity" @click="claim(coupon)">{{ coupon.used_at ? '已使用' : coupon.reserved ? '订单占用' : coupon.claim_id ? '已领取' : !coupon.available ? '已失效' : '立即领取' }}</button></section></article><p v-if="!coupons.length" class="m-empty">暂无可领取优惠券</p></section><section><h2 class="m-section-label">一起拼团</h2><article v-for="rule in rules" :key="rule.id" class="m-card"><span class="m-pill">{{ rule.target_size }} 人团 · {{ rule.hours }} 小时</span><h3 class="m-group-name">{{ rule.name }}</h3><div class="m-row"><strong class="m-price">¥{{ Number(rule.price).toFixed(2) }}</strong><button class="m-primary" @click="prepareGroup(rule)">发起拼团</button></div><button class="m-quiet" @click="router.push(`/manager/store/products/${rule.product_id}`)">查看商品 ›</button></article><article v-for="group in groups" :key="group.id" class="m-card"><h3>{{ group.product_name }}</h3><p class="m-muted">团号 {{ group.id }} · {{ group.member_count }}/{{ group.target_size }} 人<br/>截止 {{ group.expires_at }}</p><div class="m-actions"><span class="m-pill">{{ ({forming:'组团中',completed:'已成团',expired:'已到期取消'})[group.status] }}</span><button v-if="group.status==='forming' && rules.some(r=>r.id===group.rule_id)" class="m-primary" @click="prepareGroup(rules.find(r=>r.id===group.rule_id),group)">参加此团</button></div></article></section></template>
<template v-else-if="mode==='help'"><section class="m-card"><h2>{{ portal.shop?.name || '商城公告' }}</h2><p class="m-service-text">{{ portal.shop?.description }}</p><details v-for="notice in portal.notices || []" :key="notice.id" class="m-faq"><summary>{{ notice.name }}</summary><p class="m-service-text">{{ notice.content }}</p></details><p v-if="!portal.notices?.length" class="m-muted">暂无公告</p></section><section class="m-card"><h2>常见问题</h2><details v-for="faq in portal.faqs || []" :key="faq.id" class="m-faq"><summary>{{ faq.name }}</summary><p class="m-service-text">{{ faq.answer }}</p></details></section><section class="m-card"><h2>联系我们</h2><p class="m-muted">{{ portal.shop?.phone }} {{ portal.shop?.email }}</p><button class="m-primary" @click="router.push({path:'/manager/messages',query:{tab:'support'}})">在线客服</button></section></template>
<template v-else><section class="m-card"><h2>告诉我们你的建议</h2><label class="m-field">主题<input class="m-native-input" v-model="feedback.name" maxlength="120" placeholder="想反馈什么问题？" /></label><label class="m-field">详细描述<textarea class="m-native-input" v-model="feedback.content" maxlength="5000" placeholder="描述你遇到的问题或建议" /></label><label class="m-field">联系方式（选填）<input class="m-native-input" v-model="feedback.contact" maxlength="100" placeholder="邮箱或手机号" /></label><button class="m-primary" :disabled="saving" style="width:100%" @click="submitFeedback">{{ saving ? '提交中…' : '提交反馈' }}</button></section><h2 class="m-section-label">我的反馈</h2><article v-for="item in feedbacks" :key="item.id" class="m-card"><h3>{{ item.name }}</h3><p class="m-service-text">{{ item.content }}</p><div v-if="item.reply" class="m-feedback-reply">商家回复：{{ item.reply }}</div><small class="m-muted">{{ item.create_time }}</small></article><p v-if="!feedbacks.length" class="m-empty">暂无反馈记录</p></template>
</div><MiniSheet v-model="groupDialog" :title="selectedGroup ? '参加拼团' : '发起拼团'"><p class="m-muted">购买 1 件，团购价 ¥{{ Number(selectedGroup?.price ?? selectedRule?.price ?? 0).toFixed(2) }}。</p><select v-model="addressId" class="m-native-select"><option :value="null">选择收货地址</option><option v-for="address in addresses" :key="address.id" :value="address.id">{{ address.receiver_name }} {{ address.phone }} {{ address.detail }}</option></select><button v-if="!addresses.length" class="m-quiet" @click="router.push('/manager/addresses')">添加收货地址 ›</button><template #footer><button class="m-primary" :disabled="!addressId || saving" @click="submitGroup">{{ saving ? '提交中…' : '确认参团' }}</button></template></MiniSheet></div>
</template>
<script setup>
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
import { useCustomerMall } from '@/composables/customer/CustomerMall'

const {
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
} = useCustomerMall()


</script>
<style scoped>
.m-section-label{font-size:14px;font-weight:600;margin:8px 4px 14px}.m-coupon{display:flex;gap:16px;margin-bottom:12px;border-radius:14px;background:#fff;overflow:hidden}.m-coupon>div{width:116px;flex:none;background:#fff0e8;display:grid;align-content:center;justify-items:center;gap:8px;padding:14px 8px;color:#e46e54}.m-coupon>div strong{font-size:26px}.m-coupon>div small{font-size:10px}.m-coupon>section{padding:16px 12px 16px 0;flex:1;min-width:0}.m-coupon h3{font-size:13px;margin:0}.m-coupon p{font-size:10px;color:#a5afb8;margin:7px 0}.m-coupon .m-primary{font-size:11px;min-height:30px;padding:5px 15px}.m-group-name{margin-top:12px}.m-service-text{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;line-height:1.9;color:#788b98}.m-faq{padding:14px 0;border-top:1px solid #f1f3f5}.m-faq summary{font-size:13px;line-height:1.7;cursor:pointer}.m-feedback-reply{font-size:12px;padding:12px;background:#fff5ef;border-radius:8px;line-height:1.8;color:#c28e78;margin-bottom:12px}
</style>
