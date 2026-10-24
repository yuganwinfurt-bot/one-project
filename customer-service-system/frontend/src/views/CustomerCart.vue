<template>
  <div class="page-container customer-page" :class="{ 'customer-cart--embedded': embedded }" v-loading="loading">
    <section class="content-card customer-page__heading">
      <div>
        <h1>购物车</h1>
        <p>选择商品规格、数量与优惠券，确认金额后提交订单并付款。</p>
      </div>
      <el-button @click="continueShopping">继续逛商品</el-button>
    </section>

    <section v-if="items.length" class="content-card cart-panel">
      <div class="cart-address">
        <div>
          <strong>收货地址</strong>
          <p v-if="!addresses.length">请先添加收货地址，再提交订单。</p>
          <p v-else>订单会使用此地址生成收货信息快照。</p>
        </div>
        <div class="cart-address__actions">
          <el-select
            v-if="addresses.length"
            v-model="addressId"
            placeholder="选择收货地址"
            class="cart-address__select"
          >
            <el-option
              v-for="address in addresses"
              :key="address.id"
              :value="address.id"
              :label="`${address.receiver_name} · ${address.phone} · ${address.detail}${address.is_default ? '（默认）' : ''}`"
            />
          </el-select>
          <el-button @click="manageAddresses">
            {{ addresses.length ? '管理地址' : '添加地址' }}
          </el-button>
        </div>
      </div>

      <div class="cart-list">
        <article v-for="item in items" :key="item.id" class="cart-item">
          <el-checkbox v-model="selectedItemIds" :value="item.id" :disabled="!cartAvailable(item)" aria-label="选择商品" />
          <button class="cart-item__image" type="button" @click="openProduct(item.product.id)">
            <el-image v-if="item.product.image_url" :src="item.product.image_url" fit="cover" />
            <el-icon v-else><Picture /></el-icon>
          </button>
          <div class="cart-item__info">
            <button class="cart-item__name" type="button" @click="openProduct(item.product.id)">
              {{ item.product.name }}
            </button>
            <span>{{ item.product.category }}</span>
            <button
              v-if="item.product.variants?.length || item.product.needs_variant_selection"
              class="cart-item__variant-trigger"
              type="button"
              :disabled="busyItemId === item.id"
              @click="openVariantDialog(item)"
            >
              <span>{{ item.product.needs_variant_selection ? '商品规格已更新，请重新选择' : `${item.product.selected_variant?.variant_name || item.product.variant_name || '规格'}：${item.product.selected_variant?.name || '请选择规格'}` }}</span>
              <small>{{ item.product.needs_variant_selection ? '选择规格 ›' : '点击修改 ›' }}</small>
            </button>
            <el-tag
              v-else-if="item.product.selected_variant"
              :type="item.product.selected_variant.unavailable ? 'danger' : 'info'"
              size="small"
            >
              {{ item.product.selected_variant.variant_name }}：{{ item.product.selected_variant.name }}
            </el-tag>
            <el-tag v-else type="info" size="small">默认规格</el-tag>
            <el-tag v-if="cartStock(item) < item.quantity" type="danger" size="small">
              库存不足，剩余 {{ cartStock(item) }} 件
            </el-tag>
          </div>
          <strong class="cart-item__price">{{ money(cartPrice(item)) }}</strong>
          <el-input-number
            :model-value="item.quantity"
            :min="1"
            :max="Math.max(1, Math.min(orderSettings.max_quantity || 99, 99, cartStock(item)))"
            :disabled="cartStock(item) < 1 || busyItemId === item.id"
            controls-position="right"
            @change="changeQuantity(item, $event)"
          />
          <strong class="cart-item__subtotal">{{ money(cartPrice(item) * item.quantity) }}</strong>
          <el-button link type="danger" :icon="Delete" @click="removeItem(item)">移除</el-button>
        </article>
      </div>

      <div class="cart-coupon-choice">
        <strong>优惠券</strong>
        <el-select v-model="couponClaimId" clearable placeholder="不使用优惠券" style="width: 320px">
          <el-option v-for="coupon in usableCoupons" :key="coupon.claim_id" :value="coupon.claim_id" :label="couponLabel(coupon)" />
        </el-select>
        <el-button link type="primary" @click="goGetCoupons">去领券</el-button>
        <span>商品 {{ money(selectedTotal) }} − 优惠 {{ money(couponDiscount) }} + 运费 {{ money(shippingFee) }}</span>
      </div>
      <div class="cart-summary">
        <div class="cart-summary__selection">
          <el-checkbox v-model="allSelected">全选</el-checkbox>
          <span>已选 {{ selectedItems.length }} 件商品</span>
        </div>
        <div class="cart-summary__checkout">
          <span>合计</span>
          <strong>{{ money(payableTotal) }}</strong>
          <el-button
            type="primary"
            :loading="checkoutBusy"
            :disabled="!selectedItems.length || !addressId || !orderSettings.checkout_enabled || selectedItems.some((item) => !cartAvailable(item))"
            @click="checkout"
          >
            提交订单，去付款
          </el-button>
        </div>
      </div>
    </section>

    <section v-else-if="!loading" class="content-card customer-empty">
      <el-empty description="购物车还是空的，去商品首页挑选喜欢的商品吧">
        <el-button type="primary" @click="continueShopping">去逛逛</el-button>
      </el-empty>
    </section>

    <SkuSelectionDialog
      v-if="variantDialogItem"
      v-model="variantDialogVisible"
      :product="variantDialogItem.product"
      :selected-key="variantDialogKey"
      :show-quantity="false"
      :loading="busyItemId === variantDialogItem.id"
      @update:selected-key="variantDialogKey = $event"
    >
      <template #footer="{ valid }">
        <el-button :disabled="busyItemId === variantDialogItem.id" @click="variantDialogVisible = false">取消</el-button>
        <el-button type="warning" :disabled="!valid" :loading="busyItemId === variantDialogItem.id" @click="confirmVariantChange">确认规格</el-button>
      </template>
    </SkuSelectionDialog>
  </div>
</template>

<script setup>
import { useCustomerCart } from '@/composables/customer/CustomerCart'
const props = defineProps({ embedded: { type: Boolean, default: false } })
const emit = defineEmits(['continue-shopping', 'open-product', 'manage-addresses', 'show-coupons', 'order-created', 'cart-updated'])
const {
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
} = useCustomerCart(props,emit)
</script>

<style scoped>
.customer-cart--embedded { display:grid; gap:12px; }
.customer-cart--embedded .content-card { border-color:#edf0ef; border-radius:10px; box-shadow:none; }
.customer-cart--embedded .customer-page__heading { align-items:center; }
.customer-cart--embedded .customer-page__heading h1 { font-size:19px; }
.customer-cart--embedded .cart-panel { padding:16px; }
.customer-cart--embedded .cart-item { gap:12px; padding:12px 0; }
.customer-cart--embedded .cart-address { align-items:flex-start; }
.customer-cart--embedded .cart-summary { padding-top:14px; }
.cart-coupon-choice { padding-top:20px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.cart-coupon-choice > span { color:#7a8d84; font-size:12px; }
.customer-page { display: grid; gap: 18px; }
.customer-page__heading { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.customer-page__heading h1 { margin: 0; color: #102237; font-size: 22px; }
.customer-page__heading p, .cart-address p { margin: 6px 0 0; color: #728396; font-size: 14px; }
.cart-panel { padding: 24px; }
.cart-address { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding-bottom: 20px; border-bottom: 1px solid #e8eeec; }
.cart-address__actions { display: flex; gap: 10px; align-items: center; }
.cart-address__select { width: min(480px, 42vw); }
.cart-list { display: grid; }
.cart-item { display: grid; grid-template-columns: 26px 84px minmax(180px, 1fr) 110px 130px 120px 70px; align-items: center; gap: 18px; padding: 18px 0; border-bottom: 1px solid #edf1ef; }
.cart-item__image { display: grid; width: 84px; height: 84px; place-items: center; overflow: hidden; border: 1px solid #e0e8e5; border-radius: 12px; background: #f2f6f4; color: #82929c; cursor: pointer; }
.cart-item__image :deep(.el-image), .cart-item__image :deep(img) { width: 100%; height: 100%; }
.cart-item__info { display: grid; justify-items: start; gap: 7px; }
.cart-item :deep(.el-input-number) { width: 100%; min-width: 0; }
.cart-item__variant-trigger { display: inline-flex; align-items: center; gap: 8px; max-width: min(420px, 100%); padding: 0; border: 0; background: transparent; color: #697c8e; text-align: left; cursor: pointer; }
.cart-item__variant-trigger > span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cart-item__variant-trigger small { flex: 0 0 auto; color: #e28a37; font-size: 12px; }
.cart-item__variant-trigger:disabled { cursor: wait; opacity: .65; }
.cart-item__name { padding: 0; border: 0; background: none; color: #17324b; font-size: 15px; font-weight: 600; text-align: left; cursor: pointer; }
.cart-item__info > span { color: #8796a2; font-size: 13px; }
.cart-item__price, .cart-item__subtotal { color: #142b40; font-variant-numeric: tabular-nums; }
.cart-item__subtotal { color: #e94b42; }
.cart-summary { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding-top: 22px; }
.cart-summary__selection { display: flex; align-items: center; gap: 16px; color: #748597; font-size: 14px; }
.cart-summary__checkout { display: flex; align-items: center; gap: 18px; color: #617286; }
.cart-summary__checkout strong { color: #e94b42; font-size: 24px; }
.customer-empty { padding: 40px 20px; }
@media (max-width: 1000px) {
  .cart-item { grid-template-columns: 24px 72px minmax(140px, 1fr) 95px 110px; }
  .cart-item__price { display: none; }
  .cart-item__image { width: 72px; height: 72px; }
}
@media (max-width: 700px) {
  .customer-page__heading, .cart-address, .cart-summary { align-items: flex-start; flex-direction: column; }
  .cart-address__actions, .cart-address__select { width: 100%; }
  .cart-address__actions { flex-wrap: wrap; }
  .cart-item { grid-template-columns: 24px 64px minmax(100px, 1fr) auto; gap: 10px; }
  .cart-item__image { width: 64px; height: 64px; }
  .cart-item :deep(.el-input-number) { grid-column: 3; }
  .cart-item__subtotal { grid-column: 4; grid-row: 2; }
  .cart-item > .el-button { grid-column: 4; grid-row: 1; }
  .cart-summary__checkout { width: 100%; justify-content: space-between; }
}
</style>
