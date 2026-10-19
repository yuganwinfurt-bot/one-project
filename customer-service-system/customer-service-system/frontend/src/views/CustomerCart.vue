<template>
  <div class="page-container customer-page" v-loading="loading">
    <section class="content-card customer-page__heading">
      <div>
        <h1>购物车</h1>
        <p>确认商品和收货地址后即可提交演示订单。</p>
      </div>
      <el-button @click="router.push('/manager/store')">继续逛商品</el-button>
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
          <el-button @click="router.push('/manager/addresses')">
            {{ addresses.length ? '管理地址' : '添加地址' }}
          </el-button>
        </div>
      </div>

      <div class="cart-list">
        <article v-for="item in items" :key="item.id" class="cart-item">
          <el-checkbox v-model="selectedItemIds" :value="item.id" aria-label="选择商品" />
          <button class="cart-item__image" type="button" @click="openProduct(item.product.id)">
            <el-image v-if="item.product.image_url" :src="item.product.image_url" fit="cover" />
            <el-icon v-else><Picture /></el-icon>
          </button>
          <div class="cart-item__info">
            <button class="cart-item__name" type="button" @click="openProduct(item.product.id)">
              {{ item.product.name }}
            </button>
            <span>{{ item.product.category }}</span>
            <el-tag v-if="item.product.stock < item.quantity" type="danger" size="small">
              库存不足，剩余 {{ item.product.stock }} 件
            </el-tag>
          </div>
          <strong class="cart-item__price">{{ money(item.product.price) }}</strong>
          <el-input-number
            :model-value="item.quantity"
            :min="1"
            :max="Math.max(1, Math.min(99, item.product.stock))"
            :disabled="item.product.stock < 1 || busyItemId === item.id"
            controls-position="right"
            @change="changeQuantity(item, $event)"
          />
          <strong class="cart-item__subtotal">{{ money(Number(item.product.price) * item.quantity) }}</strong>
          <el-button link type="danger" :icon="Delete" @click="removeItem(item)">移除</el-button>
        </article>
      </div>

      <div class="cart-summary">
        <div class="cart-summary__selection">
          <el-checkbox v-model="allSelected">全选</el-checkbox>
          <span>已选 {{ selectedItems.length }} 件商品</span>
        </div>
        <div class="cart-summary__checkout">
          <span>合计</span>
          <strong>{{ money(selectedTotal) }}</strong>
          <el-button
            type="primary"
            :loading="checkoutBusy"
            :disabled="!selectedItems.length || !addressId || selectedItems.some((item) => item.product.stock < item.quantity)"
            @click="checkout"
          >
            提交订单
          </el-button>
        </div>
      </div>
    </section>

    <section v-else-if="!loading" class="content-card customer-empty">
      <el-empty description="购物车还是空的，去商品首页挑选喜欢的商品吧">
        <el-button type="primary" @click="router.push('/manager/store')">去逛逛</el-button>
      </el-empty>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { Delete, Picture } from '@element-plus/icons-vue'
import {
  checkoutCart,
  deleteCartItem,
  getAddresses,
  getCart,
  updateCartItem
} from '@/api/customer'

const router = useRouter()
const items = ref([])
const addresses = ref([])
const selectedItemIds = ref([])
const addressId = ref(null)
const loading = ref(false)
const checkoutBusy = ref(false)
const busyItemId = ref(null)

const selectedItems = computed(() => items.value.filter((item) => selectedItemIds.value.includes(item.id)))
const selectedTotal = computed(() =>
  selectedItems.value.reduce((sum, item) => sum + Number(item.product.price) * item.quantity, 0)
)
const allSelected = computed({
  get: () => items.value.length > 0 && selectedItems.value.length === items.value.length,
  set: (checked) => {
    selectedItemIds.value = checked ? items.value.map((item) => item.id) : []
  }
})

function money(value) {
  return `¥${Number(value || 0).toFixed(2)}`
}

function openProduct(productId) {
  router.push(`/manager/store/products/${productId}`)
}

async function load() {
  loading.value = true
  try {
    const [cartResponse, addressResponse] = await Promise.all([getCart(), getAddresses()])
    items.value = cartResponse.data?.list || []
    addresses.value = addressResponse.data?.list || []
    selectedItemIds.value = items.value.map((item) => item.id)
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
    ElMessage.success('已移出购物车')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(error?.message || '移除失败')
  }
}

async function checkout() {
  if (!selectedItems.value.length || !addressId.value || checkoutBusy.value) return
  try {
    await ElMessageBox.confirm(
      `将为 ${selectedItems.value.length} 件商品创建演示订单，合计 ${money(selectedTotal.value)}。此操作会扣减库存。`,
      '确认提交订单',
      { confirmButtonText: '确认下单', cancelButtonText: '再看看', type: 'info' }
    )
    checkoutBusy.value = true
    const response = await checkoutCart(addressId.value, selectedItems.value.map((item) => item.id))
    ElMessage.success(response.message || '下单成功')
    await router.push('/manager/my-orders')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(error?.message || '提交订单失败')
  } finally {
    checkoutBusy.value = false
  }
}

onMounted(load)
</script>

<style scoped>
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
