import { useCustomerRouter } from '@/utils/customerRouter'
import { computed, onMounted, ref, watch } from 'vue'
import { customerCoupons, mallPortal } from '@/api/mall'
import { checkoutTotals, couponLabel } from '@/utils/checkout'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Picture } from '@element-plus/icons-vue'
import SkuSelectionDialog from '@/components/SkuSelectionDialog.vue'
import {
  checkoutCart,
  changeCartVariant,
  deleteCartItem,
  getAddresses,
  getCart,
  updateCartItem
} from '@/api/customer'

export function useCustomerCart(props,emit) {
const router = useCustomerRouter()
const items = ref([])
const addresses = ref([])
const selectedItemIds = ref([])
const addressId = ref(null)
const loading = ref(false)
const checkoutBusy = ref(false)
const busyItemId = ref(null)
const variantDialogVisible = ref(false)
const variantDialogItem = ref(null)
const variantDialogKey = ref('')
const coupons = ref([]), couponClaimId = ref(null), shipping = ref({ base_fee:0, free_over:0 })
const orderSettings = ref({ checkout_enabled: true, max_quantity: 99, unpaid_timeout_minutes: 30 })
const usableCoupons = computed(() => coupons.value.filter(c => c.available && c.claim_id && !c.used_at && !c.reserved && Number(c.min_amount) <= selectedTotal.value))
const selectedCoupon = computed(() => usableCoupons.value.find(c => c.claim_id === couponClaimId.value))
const totals = computed(() => checkoutTotals(selectedTotal.value, selectedCoupon.value, shipping.value))
const couponDiscount = computed(() => totals.value.discount)
const shippingFee = computed(() => totals.value.shipping)
const payableTotal = computed(() => totals.value.payable)
const selectedItems = computed(() => items.value.filter((item) => selectedItemIds.value.includes(item.id)))
const selectedTotal = computed(() =>
  selectedItems.value.reduce((sum, item) => sum + cartPrice(item) * item.quantity, 0)
)
watch(usableCoupons, coupons => {
  if (couponClaimId.value && !coupons.some(coupon => coupon.claim_id === couponClaimId.value)) couponClaimId.value = null
})
const allSelected = computed({
  get: () => items.value.some(cartAvailable) && selectedItems.value.length === items.value.filter(cartAvailable).length,
  set: (checked) => {
    selectedItemIds.value = checked ? items.value.filter(cartAvailable).map((item) => item.id) : []
  }
})
function money(value) {
  return `¥${Number(value || 0).toFixed(2)}`
}
function cartPrice(item) {
  return Number(item.product.selected_variant?.price ?? item.product.price)
}
function cartStock(item) {
  if (item.product.needs_variant_selection) return 0
  return Number(item.product.selected_variant?.stock ?? item.product.stock)
}
function cartAvailable(item) {
  return item.product.shelf_status === 'on_sale' && item.product.review_status === 'normal' && cartStock(item) >= item.quantity && item.quantity <= Math.min(99, orderSettings.value.max_quantity || 99)
}
async function changeVariant(item, variantKey) {
  busyItemId.value = item.id
  try {
    await changeCartVariant(item.id, variantKey)
    await load()
    ElMessage.success('商品规格已更换，价格和库存已更新')
    return true
  } catch (error) {
    ElMessage.error(error?.message || '更换商品规格失败')
    return false
  } finally { busyItemId.value = null }
}
function openVariantDialog(item) {
  variantDialogItem.value = item
  const currentKey = item.product.selected_variant?.key || ''
  variantDialogKey.value = item.product.needs_variant_selection ? '' : currentKey
  variantDialogVisible.value = true
}
async function confirmVariantChange() {
  const item = variantDialogItem.value
  if (!item || !variantDialogKey.value || busyItemId.value === item.id) return
  if (await changeVariant(item, variantDialogKey.value)) variantDialogVisible.value = false
}
function openProduct(productId) {
  if (props.embedded) emit('open-product', productId)
  else router.push(`/manager/store/products/${productId}`)
}
function continueShopping() {
  if (props.embedded) emit('continue-shopping')
  else router.push('/manager/store')
}
function manageAddresses() {
  if (props.embedded) emit('manage-addresses')
  else router.push('/manager/addresses')
}
function goGetCoupons() {
  if (props.embedded) emit('show-coupons')
  else router.push('/manager/offers')
}
async function load() {
  loading.value = true
  try {
    const [cartResponse, addressResponse, couponResponse, portalResponse] = await Promise.all([getCart(), getAddresses(), customerCoupons(), mallPortal()])
    coupons.value = couponResponse.data.list
    shipping.value = portalResponse.data.shipping
    orderSettings.value = portalResponse.data.order
    items.value = cartResponse.data?.list || []
    emit('cart-updated', items.value)
    addresses.value = addressResponse.data?.list || []
    selectedItemIds.value = items.value.filter(cartAvailable).map((item) => item.id)
    addressId.value = addresses.value.find((address) => address.is_default)?.id || addresses.value[0]?.id || null
  } catch (error) {
    ElMessage.error(error?.message || '加载购物车失败')
  } finally {
    loading.value = false
  }
}
async function changeQuantity(item, quantity) {
  if (!quantity || quantity === item.quantity) return
  busyItemId.value = item.id
  try {
    await updateCartItem(item.id, quantity)
    item.quantity = quantity
    emit('cart-updated', items.value)
  } catch (error) {
    ElMessage.error(error?.message || '更新商品数量失败')
  } finally {
    busyItemId.value = null
  }
}
async function removeItem(item) {
  try {
    await ElMessageBox.confirm(`确定将“${item.product.name}”移出购物车吗？`, '移除商品', {
      type: 'warning'
    })
    await deleteCartItem(item.id)
    items.value = items.value.filter((entry) => entry.id !== item.id)
    selectedItemIds.value = selectedItemIds.value.filter((id) => id !== item.id)
    emit('cart-updated', items.value)
    ElMessage.success('已移出购物车')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(error?.message || '移除失败')
  }
}
async function checkout() {
  if (!selectedItems.value.length || !addressId.value || checkoutBusy.value) return
  try {
    await ElMessageBox.confirm(
      `将为 ${selectedItems.value.length} 件商品创建待付款订单，应付 ${money(payableTotal.value)}（含运费）。请在 ${orderSettings.value.unpaid_timeout_minutes || 30} 分钟内付款，超时后自动取消并返还库存和优惠券。`,
      '确认提交订单',
      { confirmButtonText: '确认下单', cancelButtonText: '再看看', type: 'info' }
    )
    checkoutBusy.value = true
    const response = await checkoutCart(addressId.value, selectedItems.value.map((item) => item.id), selectedCoupon.value?.claim_id || null)
    ElMessage.success(response.message || '下单成功')
    if (props.embedded) {
      await load()
      emit('order-created', items.value)
    } else {
      await router.push({ path: '/manager/my-orders', query: { pay: response.data.list[0]?.id } })
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(error?.message || '提交订单失败')
  } finally {
    checkoutBusy.value = false
  }
}
onMounted(load)
return {
useCustomerRouter,
computed,
onMounted,
ref,
watch,
customerCoupons,
mallPortal,
checkoutTotals,
couponLabel,
ElMessage,
ElMessageBox,
Delete,
Picture,
SkuSelectionDialog,
checkoutCart,
changeCartVariant,
deleteCartItem,
getAddresses,
getCart,
updateCartItem,
router,
items,
addresses,
selectedItemIds,
addressId,
loading,
checkoutBusy,
busyItemId,
variantDialogVisible,
variantDialogItem,
variantDialogKey,
coupons,
couponClaimId,
shipping,
orderSettings,
usableCoupons,
selectedCoupon,
totals,
couponDiscount,
shippingFee,
payableTotal,
selectedItems,
selectedTotal,
allSelected,
money,
cartPrice,
cartStock,
cartAvailable,
changeVariant,
openVariantDialog,
confirmVariantChange,
openProduct,
continueShopping,
manageAddresses,
goGetCoupons,
load,
changeQuantity,
removeItem,
checkout
};
}
