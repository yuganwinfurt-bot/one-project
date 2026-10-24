import { useCustomerRouter } from '@/utils/customerRouter'
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
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

export function useCustomerOrders() {
const router = useCustomerRouter()
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
return {
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
};
}
