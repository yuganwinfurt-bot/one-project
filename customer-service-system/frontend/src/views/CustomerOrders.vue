<template>
  <div class="page-container customer-page" v-loading="loading">
    <section class="content-card customer-page__heading">
      <div>
        <h1>订单记录</h1>
        <p>这里显示当前账号提交的订单。</p>
      </div>
      <el-button @click="router.push('/manager/store')">继续逛商品</el-button>
    </section>

    <section v-if="orders.length" class="order-list">
      <article v-for="order in orders" :key="order.id" class="content-card order-card">
        <header class="order-card__header">
          <div class="order-card__meta">
            <strong>订单号 {{ order.order_no }}</strong>
            <time>{{ order.create_time || '时间未知' }}</time>
          </div>
          <el-tag :type="statusTone(order)" effect="light" round>
            {{ statusLabel(order) }}
          </el-tag>
        </header>
        <div class="order-card__body">
          <div class="order-card__product">
            <div class="order-card__image">
              <el-image v-if="order.image_url" :src="order.image_url" fit="cover" />
              <el-icon v-else><Picture /></el-icon>
            </div>
            <div>
              <strong>{{ order.product_name || `商品 #${order.product_id}` }}</strong>
              <span v-if="order.variant_name">{{ order.variant_name }}</span>
              <span>数量：{{ order.quantity }}</span>
              <span v-if="order.status === 'unpaid'">付款截止：{{ order.payment_deadline_at }} · 超时自动取消</span>
              <span v-if="order.review_deadline_at && order.status === 'completed' && !order.reviewed">评价截止：{{ order.review_deadline_at }}</span>
              <span v-if="order.discount || order.shipping_fee">优惠：¥{{ Number(order.discount || 0).toFixed(2) }} · 运费：¥{{ Number(order.shipping_fee || 0).toFixed(2) }}</span>
              <span v-if="order.shipping_address">收货信息：{{ order.shipping_address }}</span>
              <span v-if="order.tracking_no || (['shipped', 'completed'].includes(order.status) && !order.after_sale?.exchange_tracking_no)">
                发货物流单号：{{ order.tracking_no || '未录入' }}
              </span>
              <span v-if="order.after_sale?.service_type === 'exchange' && order.after_sale.exchange_tracking_no">
                换货物流单号：{{ order.after_sale.exchange_tracking_no }}
              </span>
              <span v-if="['return', 'exchange'].includes(order.after_sale?.service_type) && order.after_sale?.return_tracking_no">
                寄回物流单号：{{ order.after_sale.return_tracking_no }}
              </span>
            </div>
          </div>
          <div class="order-card__amount">
            <span>{{ order.status === 'unpaid' ? '应付金额' : '实付金额' }}</span>
            <strong>¥{{ Number(order.amount).toFixed(2) }}</strong>
            <template v-if="order.status === 'unpaid'">
              <el-button type="primary" @click="openPayment(order)">去付款</el-button>
              <el-button link type="info" :loading="cancellingOrderId === order.id" @click="cancelUnpaid(order)">取消订单</el-button>
            </template>
            <el-button
              v-if="canConfirmExchangeReceived(order.after_sale) || (order.status === 'shipped' && (!order.after_sale || order.after_sale.status === 'rejected'))"
              type="success"
              plain
              :loading="receivingOrderId === order.id"
              @click="confirmReceipt(order)"
            >
              {{ canConfirmExchangeReceived(order.after_sale) ? '确认换货收货' : '确认收货' }}
            </el-button>
            <el-button v-if="canReview(order)" type="primary" plain @click="openReview(order)">
              写评价
            </el-button>
            <el-tag v-else-if="order.review_expired" type="info" effect="light" round>评价期限已过</el-tag>
            <el-tag v-else-if="order.reviewed" type="success" effect="light" round>已评价</el-tag>
            <el-button v-if="canSubmitReturnShipment(order)" type="primary" plain @click="openReturnShipment(order)">
              填写寄回物流
            </el-button>
            <el-button v-else-if="order.after_sale && !isAfterSaleClosed(order.after_sale)" type="primary" plain @click="openReturnShipment(order)">查看售后</el-button>
            <el-dropdown v-if="isAfterSaleClosed(order.after_sale) || canApplyAfterSale(order)" trigger="click" placement="bottom-end">
              <button class="order-card__more" type="button" aria-label="更多订单操作">更多</button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="isAfterSaleClosed(order.after_sale)" @click="openReturnShipment(order)">查看售后</el-dropdown-item>
                  <el-dropdown-item v-if="canApplyAfterSale(order)" @click="openAfterSale(order)">
                    {{ order.after_sale?.status === 'completed' ? '再次申请售后' : order.after_sale?.status === 'rejected' ? '重新申请售后' : '申请售后' }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </article>
    </section>

    <section v-else-if="!loading" class="content-card customer-empty">
      <el-empty description="暂时没有订单记录">
        <el-button type="primary" @click="router.push('/manager/store')">去商品首页</el-button>
      </el-empty>
    </section>

    <el-dialog v-model="paymentVisible" title="订单付款" width="min(560px, 94vw)" :close-on-click-modal="false">
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
    </el-dialog>

    <el-dialog v-model="reviewVisible" title="评价商品" width="520px" :close-on-click-modal="false">
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
    </el-dialog>

    <el-dialog v-model="afterSaleVisible" title="申请售后" width="560px" :close-on-click-modal="false">
      <div v-if="afterSaleTarget" class="after-sale-form">
        <div class="review-form__product">
          {{ afterSaleTarget.product_name || `商品 #${afterSaleTarget.product_id}` }}
          <span>· 订单 {{ afterSaleTarget.order_no }}</span>
        </div>
        <el-form label-width="90px">
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
    </el-dialog>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { Picture } from '@element-plus/icons-vue'
import {
  confirmOrderReceived,
  createOrderAfterSale,
  createOrderReview,
  getCustomerOrders,
  payCustomerOrder,
  cancelCustomerOrder,
  getAddresses
} from '@/api/customer'
import { orderStatusLabel as statusLabel, isAfterSaleClosed, canConfirmExchangeReceived, canSubmitReturnShipment as canReturnShipment } from '@/utils/afterSale'
import { useVisibleRefresh } from '@/utils/visibleRefresh'

const router = useRouter()
const route = useRoute()
const orders = ref([])
const loading = ref(false)
const reviewVisible = ref(false)
const reviewSubmitting = ref(false)
const reviewTarget = ref(null)
const reviewForm = ref({ rating: 5, content: '' })
const receivingOrderId = ref(null)
const afterSaleVisible = ref(false)
const afterSaleSubmitting = ref(false)
const afterSaleTarget = ref(null)
const afterSaleForm = ref({
  service_type: 'refund',
  reason: '',
  description: '',
  exchange_address_id: null
})
const addresses = ref([])
const paymentVisible = ref(false), paying = ref(false), paymentOrderId = ref(null), cancellingOrderId = ref(null)
let autoPaymentShown = false
const paymentOrder = computed(() => orders.value.find(order => order.id === paymentOrderId.value))
const paymentOrders = computed(() => paymentOrder.value ? orders.value.filter(order => paymentOrder.value.checkout_id ? order.checkout_id === paymentOrder.value.checkout_id : order.id === paymentOrder.value.id) : [])
const paymentTotal = computed(() => Math.round(paymentOrders.value.reduce((total, order) => total + Number(order.amount), 0) * 100) / 100)

function openPayment(order) {
  paymentOrderId.value = order.id
  paymentVisible.value = true
}

async function submitPayment() {
  if (!paymentOrder.value || paying.value || paymentOrder.value.status !== 'unpaid') return
  paying.value = true
  try {
    const response = await payCustomerOrder(paymentOrder.value.id)
    paymentVisible.value = false
    ElMessage.success(response.message)
  } catch {} finally { paying.value = false; await load(true) }
}

async function cancelUnpaid(order) {
  try {
    await ElMessageBox.confirm('确定取消本次结算的待付款订单吗？库存和优惠券会返还，同次结算的商品将一起取消。', '取消订单', { type: 'warning', confirmButtonText: '取消订单', cancelButtonText: '保留订单' })
    cancellingOrderId.value = order.id
    const response = await cancelCustomerOrder(order.id)
    ElMessage.success(response.message)
    await load(true)
  } catch {} finally { cancellingOrderId.value = null }
}

function canSubmitReturnShipment(order) {
  return canReturnShipment(order.after_sale)
}

function openReturnShipment(order) {
  const afterSaleId = order.after_sale?.id
  if (!afterSaleId) {
    ElMessage.error('未找到对应的售后申请')
    return
  }
  router.push({ path: '/manager/messages', query: { afterSaleId: String(afterSaleId) } })
}

function statusTone(order) {
  const afterSaleTones = { pending: 'warning', approved: 'warning', rejected: 'danger', completed: 'success' }
  return afterSaleTones[order.after_sale?.status] ||
    ({ unpaid: 'warning', paid: '', shipped: 'warning', completed: 'success', cancelled: 'info' }[order.status] || 'info')
}

function canReview(order) {
  return !order.reviewed && !order.review_expired && order.status === 'completed'
}

function canApplyAfterSale(order) {
  if (order.after_sale_options) return Object.values(order.after_sale_options).some(option => option.enabled)
  return ['paid', 'shipped', 'completed'].includes(order.status) &&
    (!order.after_sale || order.after_sale.status === 'rejected' || (order.after_sale.status === 'completed' && order.after_sale.service_type === 'exchange' && order.status === 'completed'))
}

function afterSaleChoice(type) {
  const order = afterSaleTarget.value
  if (order?.after_sale_options?.[type]) return order.after_sale_options[type]
  const enabled = type === 'refund' || order?.status !== 'paid'
  return { enabled, reason: enabled ? '' : '订单尚未发货，请选择仅退款，无需寄回商品' }
}

function addressLabel(address) {
  const area = `${address.province}${address.city}${address.district}${address.detail}`
  return `${address.receiver_name} · ${address.phone} · ${area}${address.is_default ? '（默认）' : ''}`
}

async function openAfterSale(order) {
  afterSaleTarget.value = order
  afterSaleForm.value = {
    service_type: 'refund',
    reason: '',
    description: '',
    exchange_address_id: null
  }
  try {
    const response = await getAddresses()
    addresses.value = response.data?.list || []
  } catch (error) {
    addresses.value = []
    ElMessage.error(error?.message || '读取收货地址失败')
  }
  afterSaleVisible.value = true
}

function changeAfterSaleType(type) {
  if (type === 'exchange') {
    afterSaleForm.value.exchange_address_id = addresses.value.find((address) => address.is_default)?.id || addresses.value[0]?.id || null
  } else {
    afterSaleForm.value.exchange_address_id = null
  }
}

function goManageAddresses() {
  afterSaleVisible.value = false
  router.push('/manager/addresses')
}

async function submitAfterSale() {
  const reason = afterSaleForm.value.reason.trim()
  if (!afterSaleTarget.value) return
  if (!reason) {
    ElMessage.warning('请填写申请原因')
    return
  }
  if (afterSaleForm.value.service_type === 'exchange' && !afterSaleForm.value.exchange_address_id) {
    ElMessage.warning('换货申请请选择新的收货地址')
    return
  }

  afterSaleSubmitting.value = true
  try {
    const response = await createOrderAfterSale(afterSaleTarget.value.id, {
      ...afterSaleForm.value,
      reason,
      description: afterSaleForm.value.description.trim() || null
    })
    afterSaleTarget.value.after_sale = response.data
    afterSaleVisible.value = false
    ElMessage.success('售后申请已提交')
    await load(true)
  } catch (error) {
    ElMessage.error(error?.message || '提交售后申请失败')
  } finally {
    afterSaleSubmitting.value = false
  }
}

async function confirmReceipt(order) {
  receivingOrderId.value = order.id
  try {
    const response = await confirmOrderReceived(order.id)
    order.status = 'completed'
    if (order.after_sale) order.after_sale.order_status = 'completed'
    ElMessage.success(response.message || '已确认收货，现在可以评价商品')
    await load(true)
  } catch (error) {
    ElMessage.error(error?.message || '确认收货失败')
  } finally {
    receivingOrderId.value = null
  }
}

function openReview(order) {
  reviewTarget.value = order
  reviewForm.value = { rating: 5, content: '' }
  reviewVisible.value = true
}

async function submitReview() {
  const content = reviewForm.value.content.trim()
  if (!reviewTarget.value) return
  if (!content) {
    ElMessage.warning('请填写评价内容')
    return
  }

  reviewSubmitting.value = true
  try {
    await createOrderReview(reviewTarget.value.id, {
      rating: reviewForm.value.rating,
      content
    })
    reviewTarget.value.reviewed = true
    reviewVisible.value = false
    ElMessage.success('评价已提交')
    await load(true)
  } catch (error) {
    ElMessage.error(error?.message || '提交评价失败')
  } finally {
    reviewSubmitting.value = false
  }
}

let orderRequestId = 0
async function load(silent = false) {
  const requestId = ++orderRequestId
  if (silent !== true) loading.value = true
  try {
    const response = await getCustomerOrders()
    if (requestId !== orderRequestId) return
    orders.value = response.data?.list || []
    if (!autoPaymentShown && route.query.pay) {
      const target = orders.value.find(order => order.id === Number(route.query.pay))
      if (target) { autoPaymentShown = true; if (target.status === 'unpaid') openPayment(target) }
    }
  } catch (error) {
    if (silent !== true) ElMessage.error(error?.message || '加载订单失败')
  } finally {
    if (requestId === orderRequestId) loading.value = false
  }
}

onMounted(load)
useVisibleRefresh(() => load(true))
</script>

<style scoped>
.customer-page { display: grid; gap: 18px; }
.customer-page__heading { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.customer-page__heading h1 { margin: 0; color: #102237; font-size: 22px; }
.customer-page__heading p { margin: 6px 0 0; color: #728396; font-size: 14px; }
.order-list { display: grid; gap: 14px; }
.order-card { padding: 0 22px; }
.order-card__header { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 18px 0; border-bottom: 1px solid #e8eeec; }
.order-card__meta { display: flex; flex-wrap: wrap; align-items: center; gap: 18px; color: #17324b; }
.order-card__meta time { color: #82919f; font-size: 13px; }
.order-card__body { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 18px 0; }
.order-card__product { display: flex; align-items: center; gap: 16px; min-width: 0; }
.order-card__image { display: grid; width: 84px; height: 84px; flex: 0 0 84px; place-items: center; overflow: hidden; border-radius: 12px; background: #eff4f1; color: #82929c; }
.order-card__image :deep(.el-image), .order-card__image :deep(img) { width: 100%; height: 100%; }
.order-card__product > div:last-child { display: grid; gap: 8px; min-width: 0; color: #708194; font-size: 13px; }
.order-card__product strong { overflow: hidden; color: #17324b; font-size: 15px; text-overflow: ellipsis; white-space: nowrap; }
.order-card__amount { display: grid; justify-items: end; gap: 8px; color: #82919f; font-size: 13px; white-space: nowrap; }
.order-card__amount strong { color: #e94b42; font-size: 20px; }
.order-card__amount :deep(.el-button), .order-card__amount :deep(.el-tag) { justify-self: end; }
.order-card__more { justify-self: end; padding: 0; border: 0; background: transparent; color: #82919f; font: inherit; font-size: 12px; line-height: 1.4; cursor: pointer; }
.order-card__more:hover { color: #d98932; }
.order-card__more:focus-visible { outline: 2px solid #d98932; outline-offset: 3px; border-radius: 2px; }
.review-form { display: grid; gap: 12px; }
.payment-panel { display: grid; gap: 14px; }
.payment-panel > p { margin: 0; color: var(--app-text-secondary); font-size: 13px; }
.payment-product { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding-bottom: 14px; border-bottom: 1px solid var(--app-border); }
.payment-product > div { display: grid; gap: 6px; }
.payment-product span { color: var(--app-text-secondary); font-size: 13px; }
.payment-total { display: flex; justify-content: space-between; align-items: center; gap: 14px; padding: 14px; background: var(--app-bg); }
.payment-total strong { color: #e94b42; font-size: 23px; }
.review-form__product { color: #17324b; font-size: 16px; font-weight: 650; }
.review-form__label { margin-top: 4px; color: #586d80; font-size: 14px; }
.after-sale-form { display: grid; gap: 12px; }
.after-sale-form__control { width: 100%; }
.after-sale-form__address { display: flex; width: 100%; min-width: 0; flex-direction: column; gap: 8px; }
.after-sale-form__no-address { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; color: #bd6e21; font-size: 13px; }
.after-sale-form__inline-hint { margin: 0; color: #82919f; font-size: 13px; line-height: 1.6; }
.after-sale-form__hint { margin: 0; color: #82919f; font-size: 13px; }
.customer-empty { padding: 40px 20px; }
@media (max-width: 700px) { .customer-page__heading, .order-card__body { align-items: flex-start; flex-direction: column; } .order-card__amount { justify-items: start; } }
</style>
