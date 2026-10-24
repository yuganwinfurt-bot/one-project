<template>

<div class="m-view"><MiniHeader title="购物车" back="/mini-store"><template #right><button class="m-quiet" @click="continueShopping">逛商品</button></template></MiniHeader><div class="m-scroll" v-loading="loading"><template v-if="items.length"><section class="m-card"><div class="m-row"><strong>送至</strong><button class="m-quiet" @click="manageAddresses">管理地址 ›</button></div><select v-if="addresses.length" v-model="addressId" class="m-native-select"><option v-for="address in addresses" :key="address.id" :value="address.id">{{ address.receiver_name }} {{ address.phone }} · {{ address.province }}{{ address.city }}{{ address.detail }}</option></select><p v-else class="m-muted">请先添加收货地址</p></section><article v-for="item in items" :key="item.id" class="m-card m-cart-item"><input type="checkbox" class="m-check" v-model="selectedItemIds" :value="item.id" :disabled="!cartAvailable(item)" :aria-label="`选择${item.product.name}`" /><div class="m-cart-copy"><div class="m-item"><img v-if="item.product.image_url" :src="item.product.image_url" class="m-item-image" @click="openProduct(item.product.id)" /><span v-else class="m-item-fallback" @click="openProduct(item.product.id)">商品</span><div><h3 @click="openProduct(item.product.id)">{{ item.product.name }}</h3><button v-if="item.product.variants?.length || item.product.needs_variant_selection" class="m-variant" @click="openVariantDialog(item)">{{ item.product.selected_variant?.name || '选择规格' }} ›</button><p v-else>默认规格</p><strong class="m-price">{{ money(cartPrice(item)) }}</strong></div></div><div class="m-cart-actions"><button class="m-quiet" @click="removeItem(item)">移除</button><div class="m-stepper"><button :disabled="item.quantity<=1 || busyItemId===item.id" @click="changeQuantity(item,item.quantity-1)">−</button><span>{{ item.quantity }}</span><button :disabled="item.quantity>=Math.min(cartStock(item),orderSettings.max_quantity || 99) || busyItemId===item.id" @click="changeQuantity(item,item.quantity+1)">+</button></div></div><p v-if="!cartAvailable(item)" class="m-muted">规格或库存已变化，请重新选择</p></div></article><section class="m-card"><div class="m-row"><strong>优惠券</strong><button class="m-quiet" @click="goGetCoupons">去领券 ›</button></div><select v-model="couponClaimId" class="m-native-select"><option :value="null">不使用优惠券</option><option v-for="coupon in usableCoupons" :key="coupon.claim_id" :value="coupon.claim_id">{{ couponLabel(coupon) }}</option></select><div class="m-detail-line"><span>商品金额</span><span>{{ money(selectedTotal) }}</span></div><div class="m-detail-line"><span>运费 / 优惠</span><span>{{ money(shippingFee) }} / −{{ money(couponDiscount) }}</span></div></section></template><div v-else-if="!loading" class="m-empty"><span>♧</span><p>购物车还是空的</p><button class="m-primary" @click="continueShopping">去挑选好物</button></div></div><footer v-if="items.length" class="m-footer"><label class="m-all"><input type="checkbox" class="m-check" v-model="allSelected" />全选</label><div><small class="m-muted">合计</small> <strong class="m-price">{{ money(payableTotal) }}</strong></div><button class="m-primary" :disabled="checkoutBusy || !selectedItems.length || !addressId || !orderSettings.checkout_enabled || selectedItems.some(i=>!cartAvailable(i))" @click="checkout">{{ checkoutBusy ? '下单中…' : `结算(${selectedItems.length})` }}</button></footer>
    <SkuSelectionDialog class="m-sku"
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
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
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
.m-cart-item{display:flex;gap:9px}.m-check{width:19px;height:19px;accent-color:#ed6957;flex:none;align-self:center}.m-cart-copy{flex:1;min-width:0}.m-cart-actions{display:flex;align-items:center;justify-content:space-between;margin-top:8px}.m-stepper{display:flex;align-items:center;border:1px solid #edf0f2;border-radius:6px;overflow:hidden}.m-stepper button{width:34px;height:34px;border:0;background:#f7f8fa;font-size:18px}.m-stepper button:disabled{color:#c4ccd2}.m-stepper span{width:36px;text-align:center;font-size:13px}.m-variant{border:0;padding:4px 7px;border-radius:4px;background:#f5f6f8;color:#9ca6af;font-size:11px;margin-bottom:6px}.m-all{display:flex;gap:7px;align-items:center;color:#8c9ba7;font-size:12px}.m-footer .m-price{font-size:18px}
</style>
