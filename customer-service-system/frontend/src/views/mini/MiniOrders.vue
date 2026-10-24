<template>

<div class="m-view"><MiniHeader title="我的订单"><template #right><button class="m-quiet" @click="load()">刷新</button></template></MiniHeader><nav class="m-tabs"><button v-for="entry in [['all','全部'],['unpaid','待付款'],['paid','待发货'],['shipped','待收货'],['review','待评价'],['completed','已完成'],['after_sale','售后']]" :key="entry[0]" :class="{active:miniStatus===entry[0]}" @click="miniStatus=entry[0]">{{ entry[1] }}</button></nav>
<div class="m-scroll" v-loading="loading"><article v-for="order in miniOrders" :key="order.id" class="m-card"><div class="m-order-top"><span>订单 {{ order.order_no }}</span><b>{{ statusLabel(order) }}</b></div><div class="m-item" @click="router.push(`/manager/store/products/${order.product_id}`)"><img v-if="order.image_url" :src="order.image_url" class="m-item-image" /><span v-else class="m-item-fallback">商品</span><div><h3>{{ order.product_name }}</h3><p>{{ order.variant_name || '默认规格' }} · ×{{ order.quantity }}</p><strong>¥{{ Number(order.amount).toFixed(2) }}</strong></div></div><p v-if="order.status==='unpaid'" class="m-muted">付款截止 {{ order.payment_deadline_at }}</p><details class="m-order-details"><summary>订单详情与物流</summary><div class="m-detail-line"><span>下单时间</span><span>{{ order.create_time }}</span></div><div class="m-detail-line"><span>收货地址</span><span>{{ order.shipping_address || '暂无' }}</span></div><div class="m-detail-line"><span>物流单号</span><span>{{ order.after_sale?.exchange_tracking_no || order.tracking_no || '尚未发货' }}</span></div><div class="m-detail-line"><span>运费 / 优惠</span><span>¥{{ order.shipping_fee || 0 }} / ¥{{ order.discount || 0 }}</span></div><div v-if="order.after_sale" class="m-detail-line"><span>售后</span><span>{{ order.after_sale.reason }} · {{ order.after_sale.admin_note || '以处理进度为准' }}</span></div></details><div class="m-actions"><button v-if="order.status==='unpaid'" class="m-secondary" :disabled="cancellingOrderId===order.id" @click="cancelUnpaid(order)">取消订单</button><button v-if="order.status==='unpaid'" class="m-primary" @click="openPayment(order)">去付款</button><button v-if="canConfirmExchangeReceived(order.after_sale) || (order.status==='shipped' && (!order.after_sale || order.after_sale.status==='rejected'))" class="m-primary" :disabled="receivingOrderId===order.id" @click="confirmReceipt(order)">确认收货</button><button v-if="canReview(order)" class="m-primary" @click="openReview(order)">评价商品</button><span v-else-if="order.reviewed" class="m-muted">已评价</span><button v-if="order.after_sale" class="m-secondary" @click="openReturnShipment(order)">查看售后</button><button v-if="canApplyAfterSale(order)" class="m-secondary" @click="openAfterSale(order)">申请售后</button></div></article><div v-if="!loading && !miniOrders.length" class="m-empty"><span>▤</span><p>这里还没有订单</p><button class="m-primary" @click="router.push('/manager/store')">去挑选好物</button></div></div>
    <MiniSheet v-model="paymentVisible" title="订单付款" :close-on-click-modal="false">
      <div v-if="paymentOrder" class="payment-panel">
        <el-alert title="当前为本地模拟付款，不会产生真实扣款。" type="info" :closable="false" />
        <div v-for="order in paymentOrders" :key="order.id" class="payment-product">
          <div><strong>{{ order.product_name }}</strong><span>{{ order.variant_name || '默认规格' }} × {{ order.quantity }}</span></div>
          <strong>¥{{ Number(order.amount).toFixed(2) }}</strong>
        </div>
        <p>付款截止：{{ paymentOrder.payment_deadline_at }}</p>
        <p v-if="paymentOrders.length > 1">本次结算包含 {{ paymentOrders.length }} 笔商品订单，将一并完成付款。</p>
        <div class="payment-total"><span>合计应付（含优惠和运费）</span><strong>¥{{ paymentTotal.toFixed(2) }}</strong></div>
        <el-alert v-if="paymentOrder.status !== 'unpaid'" title="订单状态已更新，请关闭后查看订单记录。" type="warning" :closable="false" />
      </div>
      <template #footer><el-button :disabled="paying" @click="paymentVisible = false">稍后付款</el-button><el-button type="primary" :loading="paying" :disabled="paymentOrder?.status !== 'unpaid'" @click="submitPayment">确认模拟付款</el-button></template>
    </MiniSheet>

    <MiniSheet v-model="reviewVisible" title="评价商品" :close-on-click-modal="false">
      <div v-if="reviewTarget" class="review-form">
        <div class="review-form__product">{{ reviewTarget.product_name || `商品 #${reviewTarget.product_id}` }}</div>
        <label class="review-form__label">商品评分</label>
        <el-rate v-model="reviewForm.rating" show-text />
        <label class="review-form__label" for="customer-order-review">评价内容</label>
        <el-input
          id="customer-order-review"
          v-model="reviewForm.content"
          type="textarea"
          :rows="5"
          maxlength="2000"
          show-word-limit
          placeholder="分享一下这件商品的使用感受"
        />
      </div>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" :loading="reviewSubmitting" @click="submitReview">提交评价</el-button>
      </template>
    </MiniSheet>

    <MiniSheet v-model="afterSaleVisible" title="申请售后" :close-on-click-modal="false">
      <div v-if="afterSaleTarget" class="after-sale-form">
        <div class="review-form__product">
          {{ afterSaleTarget.product_name || `商品 #${afterSaleTarget.product_id}` }}
          <span>· 订单 {{ afterSaleTarget.order_no }}</span>
        </div>
        <el-form label-position="top">
          <el-form-item label="售后类型">
            <el-select v-model="afterSaleForm.service_type" class="after-sale-form__control" @change="changeAfterSaleType">
              <el-option label="仅退款" value="refund" :disabled="!afterSaleChoice('refund').enabled" />
              <el-option label="退货退款" value="return" :disabled="!afterSaleChoice('return').enabled" />
              <el-option label="换货" value="exchange" :disabled="!afterSaleChoice('exchange').enabled" />
            </el-select>
            <p v-if="!afterSaleChoice('exchange').enabled" class="after-sale-form__inline-hint">{{ afterSaleChoice('exchange').reason }}</p>
          </el-form-item>
          <el-form-item v-if="afterSaleForm.service_type === 'exchange'" label="换货收货地址">
            <div class="after-sale-form__address">
              <el-select
                v-if="addresses.length"
                v-model="afterSaleForm.exchange_address_id"
                class="after-sale-form__control"
                placeholder="选择替换商品寄达的收货地址"
              >
                <el-option
                  v-for="address in addresses"
                  :key="address.id"
                  :label="addressLabel(address)"
                  :value="address.id"
                />
              </el-select>
              <div v-else class="after-sale-form__no-address">
                <span>还没有收货地址，换货需要重新选择收货地址</span>
                <el-button link type="primary" @click="goManageAddresses">去添加地址</el-button>
              </div>
              <span class="after-sale-form__inline-hint">这是商家寄出替换商品时使用的收货地址；退回商品寄到哪里，商家同意后会在消息中告知。</span>
            </div>
          </el-form-item>
          <el-form-item label="申请原因">
            <el-input
              v-model="afterSaleForm.reason"
              maxlength="200"
              placeholder="请简要说明申请原因"
            />
          </el-form-item>
          <el-form-item label="补充说明">
            <el-input
              v-model="afterSaleForm.description"
              type="textarea"
              :rows="4"
              maxlength="2000"
              show-word-limit
              placeholder="可补充问题描述或希望的处理方式（选填）"
            />
          </el-form-item>
        </el-form>
        <p class="after-sale-form__hint">提交后由后台售后中心审核。退货/换货申请获商家同意后，可在我的消息中填写寄回物流单号。</p>
      </div>
      <template #footer>
        <el-button @click="afterSaleVisible = false">取消</el-button>
        <el-button type="primary" :loading="afterSaleSubmitting" @click="submitAfterSale">
          提交申请
        </el-button>
      </template>
    </MiniSheet>

</div>
</template>
<script setup>
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
import { useCustomerOrders } from '@/composables/customer/CustomerOrders'

const {
useCustomerRouter,
computed,
onMounted,
ref,
ElMessage,
ElMessageBox,
useRoute,
Picture,
confirmOrderReceived,
createOrderAfterSale,
createOrderReview,
getCustomerOrders,
payCustomerOrder,
cancelCustomerOrder,
getAddresses,
statusLabel,
isAfterSaleClosed,
canConfirmExchangeReceived,
canReturnShipment,
useVisibleRefresh,
router,
route,
orders,
loading,
reviewVisible,
reviewSubmitting,
reviewTarget,
reviewForm,
receivingOrderId,
afterSaleVisible,
afterSaleSubmitting,
afterSaleTarget,
afterSaleForm,
addresses,
paymentVisible,
paying,
paymentOrderId,
cancellingOrderId,
autoPaymentShown,
paymentOrder,
paymentOrders,
paymentTotal,
openPayment,
submitPayment,
cancelUnpaid,
canSubmitReturnShipment,
openReturnShipment,
statusTone,
canReview,
canApplyAfterSale,
afterSaleChoice,
addressLabel,
openAfterSale,
changeAfterSaleType,
goManageAddresses,
submitAfterSale,
confirmReceipt,
openReview,
submitReview,
orderRequestId,
load
} = useCustomerOrders()

const miniStatus=ref(route.query.status || 'all')
const miniOrders=computed(()=>orders.value.filter(order=>miniStatus.value==='all' || (miniStatus.value==='after_sale' ? !!order.after_sale : miniStatus.value==='review' ? canReview(order) : order.status===miniStatus.value)))
</script>
<style scoped>
.m-order-top{display:flex;gap:8px;align-items:center;justify-content:space-between;margin-bottom:14px;font-size:10px;color:#a0aab4}.m-order-top b{color:#e77e60;font-size:12px;font-weight:500;white-space:nowrap}.m-order-details{margin-top:14px;padding-top:10px;border-top:1px solid #f2f4f6}.m-order-details summary{font-size:12px;color:#9aa6b0;cursor:pointer}.m-item>div:last-child>strong{display:block;text-align:right;font-size:15px}
</style>
