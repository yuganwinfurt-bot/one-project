<template>
  <div class="page-container customer-page" v-loading="loading">
    <section class="content-card customer-page__heading">
      <div>
        <h1>我的收藏</h1>
        <p>收藏缺货商品后，商品补货时会在“我的消息”提醒你。</p>
      </div>
      <el-button @click="router.push('/manager/store')">继续逛商品</el-button>
    </section>

    <section v-if="items.length" class="favorite-grid">
      <article v-for="item in items" :key="item.product.id" class="content-card favorite-card">
        <button class="favorite-card__image" type="button" @click="openProduct(item.product.id)">
          <el-image v-if="item.product.image_url" :src="item.product.image_url" fit="contain" />
          <el-icon v-else :size="34"><Picture /></el-icon>
        </button>
        <div class="favorite-card__body">
          <div class="favorite-card__title-row">
            <button type="button" class="favorite-card__title" @click="openProduct(item.product.id)">
              {{ item.product.name }}
            </button>
            <el-tag v-if="!isAvailable(item.product)" type="info" size="small">暂不可购买</el-tag>
          </div>
          <span>{{ item.product.category }}</span>
          <p>{{ item.product.description || '暂无商品介绍' }}</p>
          <el-tag v-if="item.product.stock <= 0 || item.restock_waiting" type="warning" size="small">已订阅到货提醒</el-tag>
          <div class="favorite-card__footer">
            <strong>¥{{ Number(item.product.price).toFixed(2) }}</strong>
            <div>
              <el-button
                type="primary"
                plain
                :icon="ShoppingCart"
                :disabled="!isAvailable(item.product) || busyId === item.product.id"
                :loading="busyId === item.product.id"
                @click="addToCart(item.product)"
              >
                {{ item.product.variants?.length ? '选择规格' : '加入购物车' }}
              </el-button>
              <el-button
                type="danger"
                plain
                :icon="Delete"
                :disabled="busyId === item.product.id"
                @click="removeFavorite(item.product)"
              >
                取消收藏
              </el-button>
            </div>
          </div>
        </div>
      </article>
    </section>

    <section v-else-if="!loading" class="content-card customer-empty">
      <el-empty description="还没有收藏商品">
        <el-button type="primary" @click="router.push('/manager/store')">去发现商品</el-button>
      </el-empty>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Delete, Picture, ShoppingCart } from '@element-plus/icons-vue'
import { addCartItem, deleteFavorite, getFavorites } from '@/api/customer'

const router = useRouter()
const items = ref([])
const loading = ref(false)
const busyId = ref(null)

function isAvailable(product) {
  return product.shelf_status === 'on_sale' && product.review_status === 'normal' && product.stock > 0
}

async function load() {
  loading.value = true
  try {
    const response = await getFavorites()
    items.value = response.data?.list || []
  } catch (error) {
    ElMessage.error(error?.message || '加载收藏失败')
  } finally {
    loading.value = false
  }
}

function openProduct(productId) {
  router.push(`/manager/store/products/${productId}`)
}

async function addToCart(product) {
  busyId.value = product.id
  try {
    if (product.variants?.length) {
      await router.push(`/manager/store/products/${product.id}`)
      return
    }
    await addCartItem(product.id)
    ElMessage.success('已加入购物车')
  } catch (error) {
    ElMessage.error(error?.message || '加入购物车失败')
  } finally {
    busyId.value = null
  }
}

async function removeFavorite(product) {
  busyId.value = product.id
  try {
    await deleteFavorite(product.id)
    items.value = items.value.filter((item) => item.product.id !== product.id)
    ElMessage.success('已取消收藏')
  } catch (error) {
    ElMessage.error(error?.message || '取消收藏失败')
  } finally {
    busyId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.customer-page { display: grid; gap: 18px; }
.customer-page__heading { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.customer-page__heading h1 { margin: 0; color: #102237; font-size: 22px; }
.customer-page__heading p { margin: 6px 0 0; color: #728396; font-size: 14px; }
.favorite-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 300px)); gap: 20px; justify-content: start; }
.favorite-card { overflow: hidden; padding: 0; }
.favorite-card__image { display: grid; width: 100%; height: auto; aspect-ratio: 1; box-sizing: border-box; padding: 0; place-items: center; overflow: hidden; border: 0; background: #f2f5f3; color: #82929c; cursor: pointer; }
.favorite-card__image :deep(.el-image), .favorite-card__image :deep(img) { width: 100%; height: 100%; }
.favorite-card__body { display: grid; gap: 10px; padding: 16px; }
.favorite-card__title-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.favorite-card__footer { display: grid; gap: 12px; min-width: 0; }
.favorite-card__title { overflow: hidden; padding: 0; border: 0; background: none; color: #17324b; font-size: 17px; font-weight: 650; text-align: left; text-overflow: ellipsis; white-space: nowrap; cursor: pointer; }
.favorite-card__body > span { color: #8796a2; font-size: 13px; }
.favorite-card__body p { display: -webkit-box; min-height: 40px; margin: 0; overflow: hidden; color: #687b8c; font-size: 14px; line-height: 1.5; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.favorite-card__footer strong { color: #e94b42; font-size: 22px; white-space: nowrap; }
.favorite-card__footer > div { display: flex; flex-wrap: wrap; gap: 8px; min-width: 0; }
.favorite-card__footer > div :deep(.el-button) { flex: 1 1 110px; min-width: 0; margin: 0; }
.customer-empty { padding: 40px 20px; }
@media (max-width: 700px) {
  .customer-page__heading { align-items: flex-start; flex-direction: column; }
  .favorite-grid { grid-template-columns: minmax(0, 1fr); }
}
</style>
