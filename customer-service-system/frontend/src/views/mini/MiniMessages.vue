<template>
<div class="m-view m-messages">
<CustomerSupportPanel v-if="supportOpen" mobile :conversation-id="Number(route.query.supportConversationId) || undefined" @back="miniBack" />
<template v-else-if="miniInbox"><MiniHeader title="我的消息"><template #right><button class="m-quiet" v-if="unreadCount" @click="markAllRead">全已读</button></template></MiniHeader><nav class="m-tabs"><button v-for="filter in filters" :key="filter.key" :class="{active:activeFilter===filter.key}" @click="activeFilter=filter.key">{{ filter.label }} <small v-if="filter.count">{{ filter.count }}</small></button></nav><div class="m-scroll m-inbox-scroll" v-loading="loading"><button class="m-contact-entry" @click="router.replace({path:route.path,query:{tab:'support'}})"><span class="m-message-avatar m-message-service">♧</span><div><strong>联系客服</strong><p>AI 在线解答 · 可申请人工协助</p></div><b>›</b></button><button v-for="message in filteredMessages" :key="message.id" class="m-message-row" @click="miniOpen(message)"><span class="m-message-avatar">{{ message.type==='shipment' ? '▣' : message.type==='review_reply' ? '☆' : '◌' }}<i v-if="messageUnreadCount(message)">{{ messageUnreadCount(message) }}</i></span><div><header><strong>{{ messageTitle(message) }}</strong><time>{{ shortTime(message.create_time) }}</time></header><p>{{ messagePreview(message) }}</p></div></button><div v-if="!filteredMessages.length && !loading" class="m-empty"><span>◌</span><p>暂无消息</p></div></div></template>
<template v-else-if="miniAfterSale"><header class="m-header"><button class="m-icon-button" @click="miniBack" aria-label="返回消息列表">‹</button><h1>售后沟通</h1><button class="m-quiet" @click="miniProgress=true">进度</button></header><div class="m-after-sale-bar"><div><strong>{{ afterSaleApplication?.product_name || activeMessage?.product_name || '售后服务' }}</strong><p>{{ miniChatClosed ? '会话已结束，记录已保留' : afterSaleApplication?.handling_mode==='human' ? '人工客服已接入' : afterSaleApplication?.handling_mode==='human_requested' ? '等待人工接待' : 'AI 客服接待中' }}</p></div><button v-if="afterSaleApplication && !miniChatClosed && afterSaleApplication.handling_mode==='ai'" @click="requestAfterSaleHuman">申请人工</button><button v-else-if="afterSaleApplication && !miniChatClosed" :disabled="miniClosing" @click="miniEndHuman">结束人工</button></div><div ref="chatListRef" class="m-scroll m-after-chat" v-loading="chatLoading" role="log" aria-live="polite"><article v-for="message in visibleChatMessages" :key="message.id" class="m-chat-message" :class="{mine:message.sender_role==='customer',system:message.sender_role==='system'}"><small>{{ message.sender_role==='customer' ? '我' : message.sender_name }}</small><p>{{ message.content }}</p><time>{{ message.create_time?.replace('T',' ').slice(0,19) }}</time></article><p v-if="afterSaleAIThinking" class="m-muted">AI 客服正在回复…</p></div><form v-if="afterSaleApplication && !miniChatClosed" class="m-mobile-composer" @submit.prevent="sendMessage"><textarea v-model="draft" rows="2" maxlength="2000" placeholder="输入消息…" enterkeyhint="send" @keydown="miniSendKey" /><button class="m-primary" :disabled="sending || !draft.trim()" type="submit">发送</button></form><div v-else class="m-footer"><span class="m-muted">人工会话已结束</span><button class="m-primary" @click="router.replace({path:route.path,query:{tab:'support'}})">新咨询</button></div>
<MiniSheet v-model="miniProgress" title="售后进度"><template v-if="afterSaleApplication"><span class="m-pill">{{ applicationStatusLabel(afterSaleApplication) }}</span><div class="m-detail-line"><span>订单号</span><span>{{ afterSaleApplication.order_no }}</span></div><div class="m-detail-line"><span>申请类型</span><span>{{ serviceTypeLabel(afterSaleApplication.service_type) }}</span></div><div class="m-detail-line"><span>原因</span><span>{{ afterSaleApplication.reason }}</span></div><div class="m-detail-line"><span>处理说明</span><span>{{ afterSaleApplication.admin_note || '暂无' }}</span></div><div class="m-detail-line"><span>寄回物流</span><span>{{ returnTrackingLabel(afterSaleApplication) }}</span></div><div v-if="afterSaleApplication.exchange_tracking_no" class="m-detail-line"><span>换货物流</span><span>{{ afterSaleApplication.exchange_tracking_no }}</span></div><label v-if="canReturnShipment(afterSaleApplication)" class="m-field">寄回物流单号<input v-model="returnTrackingDraft" class="m-native-input" maxlength="100" /><button class="m-primary" :disabled="returnShipmentSubmitting || !returnTrackingDraft.trim()" @click="submitReturnShipment">提交物流单号</button></label><button v-if="canConfirmExchangeReceived(afterSaleApplication)" class="m-primary" :disabled="confirmingReceipt" @click="confirmExchangeReceipt">确认换货收货</button><section v-if="isAfterSaleClosed(afterSaleApplication)" class="m-service-rating"><h3>评价本次售后服务</h3><el-rate v-model="serviceRatingDraft" :disabled="afterSaleApplication.service_rating!=null" /><textarea class="m-native-input" v-model="serviceFeedbackDraft" maxlength="1000" placeholder="说说你的服务体验" :disabled="afterSaleApplication.service_rating!=null" /><button v-if="afterSaleApplication.service_rating==null" class="m-primary" :disabled="!serviceRatingDraft || ratingSubmitting" @click="submitServiceRating">提交评价</button></section></template></MiniSheet></template>
<template v-else-if="miniPrivate"><header class="m-header"><button class="m-icon-button" @click="miniBack">‹</button><h1>{{ activeMessage?.peer_name || '私聊' }}</h1><span class="m-header-spacer"></span></header><div class="m-private"><DirectConversationPanel v-if="activeMessage" :conversation-id="activeMessage.conversation_id" :peer="activeMessage" @updated="load(true)" /></div></template>
<template v-else><header class="m-header"><button class="m-icon-button" @click="miniBack">‹</button><h1>消息详情</h1><span class="m-header-spacer"></span></header><div class="m-scroll"><article class="m-card m-notice"><span class="m-pill">{{ messageSubtitle(miniNotice) }}</span><h2>{{ messageTitle(miniNotice) }}</h2><p>{{ miniNotice.content || messagePreview(miniNotice) }}</p><small class="m-muted">{{ miniNotice.create_time }}</small><button class="m-primary" @click="openMessageTarget(miniNotice)">查看详情</button></article></div></template>
</div>
</template>
<script setup>
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
import { useCustomerMessages } from '@/composables/customer/CustomerMessages'

const {
useCustomerRouter,
computed,
nextTick,
onBeforeUnmount,
onMounted,
ref,
watch,
ElMessage,
ElMessageBox,
ArrowRight,
ChatDotRound,
PriceTag,
Van,
useRoute,
DirectConversationPanel,
CustomerSupportPanel,
request,
getCustomerAfterSaleMessages,
getCustomerMessages,
markCustomerMessageRead,
markCustomerMessagesRead,
sendCustomerAfterSaleMessage,
submitCustomerAfterSaleServiceRating,
submitAfterSaleReturnShipment,
confirmOrderReceived,
applicationStatusLabel,
applicationStatusTone,
serviceTypeLabel,
serviceTypeTone,
isAfterSaleClosed,
canConfirmExchangeReceived,
canReturnShipment,
returnShipmentLabel,
returnTrackingLabel,
router,
route,
supportOpen,
afterSaleAIThinking,
toggleSupport,
messages,
unreadCount,
loading,
chatLoading,
sending,
ratingSubmitting,
draft,
serviceRatingDraft,
serviceFeedbackDraft,
serviceRatingTexts,
activeFilter,
selectedMessageId,
chatMessages,
visibleChatMessages,
afterSaleApplication,
returnTrackingDraft,
returnShipmentSubmitting,
confirmingReceipt,
chatListRef,
inboxTimer,
chatTimer,
conversationRequestId,
inboxRequestId,
filteredMessages,
activeMessage,
filters,
canSubmitReturnShipment,
money,
shortTime,
messageIcon,
messageTitle,
messageSubtitle,
messagePreview,
isAfterSaleShipmentNotice,
messageUnreadCount,
setFilter,
selectMessage,
markNoticeRead,
loadConversation,
submitReturnShipment,
scrollToBottom,
openMessageTarget,
sendMessage,
confirmExchangeReceipt,
submitServiceRating,
load,
markAllRead,
requestAfterSaleHuman
} = useCustomerMessages()

const miniNotice=ref(null),miniProgress=ref(false),miniClosing=ref(false)
const miniAfterSale=computed(()=>!!route.query.afterSaleId)
const miniPrivate=computed(()=>!!route.query.conversationId)
const miniChatClosed=computed(()=>!!afterSaleApplication.value?.conversation_closed || isAfterSaleClosed(afterSaleApplication.value))
const miniInbox=computed(()=>!supportOpen.value&&!miniAfterSale.value&&!miniPrivate.value&&!miniNotice.value)
function miniBack(){miniNotice.value=null;router.replace({path:route.path,query:{tab:'inbox'}})}
async function miniOpen(message){miniNotice.value=['after_sale_chat','support_chat','direct_chat'].includes(message.type)?null:message;await selectMessage(message)}
async function miniEndHuman(){const id=afterSaleApplication.value?.support_conversation_id;if(!id||miniClosing.value)return;try{await ElMessageBox.confirm('结束人工接待后，聊天记录仍会保留，退款或换货继续按原流程处理。','结束人工服务',{confirmButtonText:'结束服务',cancelButtonText:'继续沟通'});miniClosing.value=true;await request.post(`/api/customer/support/conversations/${id}/close`,{reason:'问题已解决或不再需要人工服务'});await loadConversation(activeMessage.value.after_sale_id,true);window.dispatchEvent(new Event('customer-messages-updated'))}catch(e){if(e!=='cancel'&&e!=='close')ElMessage.error(e.message || '结束失败')}finally{miniClosing.value=false}}
function miniSendKey(event){if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing&&event.keyCode!==229){event.preventDefault();sendMessage()}}

</script>
<style scoped>

.m-inbox-scroll{padding:0;background:#fff}.m-message-row,.m-contact-entry{display:flex;gap:13px;align-items:center;width:100%;padding:18px 16px;border:0;border-bottom:1px solid #f4f5f7;background:#fff;text-align:left}.m-message-avatar{position:relative;display:grid;place-items:center;flex:none;width:44px;height:44px;border-radius:14px;background:#f0edf6;color:#b0a4bc;font-size:23px}.m-message-service{background:#fff0e5;color:#deac85}.m-message-avatar i{position:absolute;right:-4px;top:-4px;padding:1px 5px;border-radius:10px;background:#ed6957;color:#fff;font-size:10px;font-style:normal}.m-message-row>div,.m-contact-entry>div{flex:1;min-width:0}.m-message-row header{display:flex;justify-content:space-between;gap:10px}.m-message-row strong,.m-contact-entry strong{font-size:13px;font-weight:500}.m-message-row time{font-size:9px;color:#bdc4cb;flex:none}.m-message-row p,.m-contact-entry p{font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#a4aeb8;margin:7px 0 0}.m-contact-entry>b{color:#bdc5ce;font-size:22px}.m-after-sale-bar{display:flex;align-items:center;gap:10px;flex:none;padding:12px 16px;background:#fff8f0;border-bottom:1px solid #f5eadf}.m-after-sale-bar>div{flex:1;min-width:0}.m-after-sale-bar strong{display:block;font-size:12px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.m-after-sale-bar p{font-size:10px;color:#c0a890;margin:5px 0 0}.m-after-sale-bar>button{flex:none;min-height:34px;padding:5px 10px;border:1px solid #eedbc9;background:#fffaf4;border-radius:18px;font-size:11px;color:#bf9877}.m-after-chat{padding:16px 14px 24px;overflow-anchor:none}.m-chat-message{width:max-content;max-width:84%;margin-bottom:20px}.m-chat-message small{font-size:10px;color:#a2adb6}.m-chat-message p{margin:5px 0;padding:10px 13px;border-radius:3px 12px 12px;background:#fff;font-size:14px;line-height:1.8;white-space:pre-wrap;overflow-wrap:anywhere;color:#536875}.m-chat-message time{font-size:9px;color:#b5bec6}.m-chat-message.mine{margin-left:auto;text-align:right}.m-chat-message.mine p{background:#ffede3;border-radius:12px 3px 12px 12px;text-align:left}.m-chat-message.system{margin-left:auto;margin-right:auto;max-width:95%;text-align:center}.m-chat-message.system p{padding:6px 10px;font-size:10px;color:#a2aeb9;background:#eaeef2}.m-chat-message.system small,.m-chat-message.system time{display:none}.m-mobile-composer{display:flex;align-items:flex-end;gap:9px;flex:none;padding:10px 12px calc(10px + env(safe-area-inset-bottom));border-top:1px solid #e8edf1;background:#fff}.m-mobile-composer>textarea{flex:1;width:0;height:62px;resize:none;padding:10px;border:1px solid #e5ebef;border-radius:10px;background:#f9fafb;font-size:16px;line-height:1.6;outline:none}.m-mobile-composer>.m-primary{min-width:62px;padding:8px 12px}.m-private{display:flex;flex:1;min-height:0;overflow:hidden}.m-private :deep(>*){flex:1;min-height:0}.m-notice h2{font-size:17px;margin-top:16px}.m-notice>p{white-space:pre-wrap;line-height:1.9;font-size:14px}.m-notice>.m-primary{display:block;margin:20px auto 0}.m-service-rating{display:grid;gap:14px;margin-top:20px}.m-service-rating h3{font-size:14px;margin:0}

</style>