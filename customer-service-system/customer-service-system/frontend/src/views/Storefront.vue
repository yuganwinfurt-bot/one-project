<template>
  <div class="page-container storefront-page">
    <section class="storefront-hero">
      <div class="storefront-hero__copy">
        <span class="storefront-hero__eyebrow">STORE · PRODUCT COLLECTION</span>
        <h1>发现店铺好物</h1>
        <p>浏览在售商品，查看价格、销量和买家评分。</p>
      </div>
      <div class="storefront-search">
        <el-input
          v-model="filters.keywords"
          clearable
          size="large"
          placeholder="搜索商品名称、类目或描述"
          @keyup.enter="search"
          @clear="search"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" size="large" :icon="Search" @click="search">搜索商品</el-button>
      </div>
      <div class="storefront-hero__decoration" aria-hidden="true">GOOD<br />FINDS</div>
    </section>

    <section class="storefront-toolbar content-card">
      <div class="storefront-toolbar__heading">
        <div class="storefront-toolbar__title">
          <div class="storefront-toolbar__title-row">
            <h2>{{ filters.category || '全部商品' }}</h2>
            <div class="storefront-list-toolbar">
              <span>排序方式</span>
              <el-select
                v-model="filters.sortBy"
                aria-label="商品排序方式"
                style="width: 190px"
                @change="changeSort"
              >
                <el-option label="综合排序" value="default" />
                <el-option label="价格从低到高" value="price_asc" />
                <el-option label="价格从高到低" value="price_desc" />
                <el-option label="销量从高到低" value="sales_desc" />
                <el-option label="销量从低到高" value="sales_asc" />
              </el-select>
            </div>
          </div>
          <p>共 {{ total }} 件精选商品</p>
        </div>
        <div class="storefront-toolbar__actions">
          <el-button
            v-if="isProductEditor"
            type="primary"
            @click="openListingDialog()"
          >
            上架商品
          </el-button>
          <el-button
            v-if="isAdmin"
            type="primary"
            :icon="MagicStick"
            :loading="aiBusy || aiPreparing"
            :disabled="loading || aiBusy || aiPreparing || cloudApprovalVisible"
            @click="prepareAiGeneration"
          >
            AI生成全部商品详情
          </el-button>
          <el-button :icon="Refresh" plain :disabled="aiBusy" @click="load">刷新</el-button>
        </div>
      </div>
      <div v-if="aiBusy" class="storefront-ai-progress">
        <span>正在生成并保存商品文案 {{ aiProgress.done }} / {{ aiProgress.total }}</span>
        <el-progress :percentage="aiProgress.total ? Math.round(aiProgress.done / aiProgress.total * 100) : 0" />
      </div>
      <div class="storefront-categories" aria-label="商品类目">
        <button
          class="category-chip"
          :class="{ 'category-chip--active': !filters.category }"
          type="button"
          @click="selectCategory('')"
        >
          全部
        </button>
        <button
          v-for="category in categories"
          :key="category"
          class="category-chip"
          :class="{ 'category-chip--active': filters.category === category }"
          type="button"
          @click="selectCategory(category)"
        >
          {{ category }}
        </button>
      </div>
    </section>

    <section class="storefront-grid" v-loading="loading">
      <article
        v-for="product in products"
        :key="product.id"
        class="store-product-card"
        :class="{ 'store-product-card--out-of-stock': isOutOfStock(product) }"
        tabindex="0"
        role="link"
        :aria-label="`${isOutOfStock(product) ? '缺货，' : ''}查看商品：${product.name}`"
        @click="openProduct(product)"
        @keydown.enter="openProduct(product)"
      >
        <div class="store-product-card__image-wrap">
          <el-image
            v-if="product.image_url"
            class="store-product-card__image"
            :src="product.image_url"
            :alt="`${product.name}商品图片`"
            fit="cover"
            loading="lazy"
          >
            <template #error>
              <div class="store-product-card__placeholder">
                <el-icon :size="34"><Picture /></el-icon>
                <span>商品图片暂不可用</span>
              </div>
            </template>
          </el-image>
          <div v-else class="store-product-card__placeholder">
            <el-icon :size="34"><Picture /></el-icon>
            <span>商家暂未上传图片</span>
          </div>
          <div v-if="isOutOfStock(product)" class="store-product-card__stock-overlay">
            <strong>缺货</strong>
          </div>
          <div class="store-product-card__tags">
            <span
              v-for="tag in (product.tags?.length ? product.tags : [product.category]).slice(0, 3)"
              :key="tag"
              class="store-product-card__tag"
            >
              {{ tag }}
            </span>
            <span
              v-if="(product.tags?.length || 1) > 3"
              class="store-product-card__tag store-product-card__tag--more"
            >
              +{{ (product.tags?.length || 1) - 3 }}
            </span>
          </div>
          <el-button
            v-if="isProductEditor"
            class="store-product-card__edit"
            size="small"
            type="primary"
            plain
            @click.stop="openListingDialog(product)"
            @keydown.enter.stop.prevent="openListingDialog(product)"
          >
            编辑并上架
          </el-button>
        </div>
        <div class="store-product-card__body">
          <h3 :title="product.name">{{ product.name }}</h3>
          <p class="store-product-card__description" :title="product.description">
            {{ product.description || '暂无商品介绍' }}
          </p>
          <div class="store-product-card__price-row">
            <div class="store-product-card__price-values">
              <strong><small>¥</small>{{ formatPrice(product.price) }}</strong>
              <del v-if="Number(product.discount_percent || 0) > 0">¥{{ formatPrice(product.original_price) }}</del>
              <span v-if="Number(product.discount_percent || 0) > 0" class="store-product-card__discount">
                -{{ formatPrice(product.discount_percent) }}%
              </span>
            </div>
            <span class="store-product-card__sold">已售 {{ product.sold_quantity }} 件</span>
          </div>
          <div class="store-product-card__rating">
            <el-rate :model-value="product.avg_rating" disabled allow-half />
            <span v-if="product.review_count">
              {{ product.avg_rating.toFixed(2) }} · {{ product.review_count }} 条评价
            </span>
            <span v-else>暂无评价</span>
          </div>
        </div>
      </article>
    </section>

    <el-empty
      v-if="!loading && !products.length"
      class="storefront-empty content-card"
      description="没有找到符合条件的在售商品"
    >
      <el-button @click="resetFilters">查看全部商品</el-button>
    </el-empty>

    <div v-if="total > pageSize" class="storefront-pagination content-card">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        background
        layout="total, prev, pager, next"
        @current-change="load"
      />
    </div>
    <p class="storefront-note">商品主图由商家维护；暂未上传图片的商品会显示占位图。</p>

    <el-dialog
      v-model="cloudApprovalVisible"
      title="确认将商品资料发送给云端模型"
      width="540px"
      :close-on-click-modal="false"
      :show-close="!aiBusy"
    >
      <div v-if="pendingAiGeneration" class="storefront-ai-consent">
        <el-alert type="warning" :closable="false" show-icon>
          <template #title>
            将使用 {{ modelLabel(pendingAiGeneration.profile) }} 生成 {{ pendingAiGeneration.products.length }} 件商品的详情文案。
          </template>
        </el-alert>
        <p>
          发送内容仅包含商品名称、类目和现有描述；不会发送价格、库存、销量、订单、买家评价或个人信息。生成内容会保存到商品详情中，原商品描述保持不变。
        </p>
      </div>
      <template #footer>
        <el-button :disabled="aiBusy" @click="cancelAiGeneration">取消</el-button>
        <el-button :disabled="aiBusy" @click="confirmAiGeneration(false)">仅本次同意</el-button>
        <el-button type="primary" :loading="aiBusy" @click="confirmAiGeneration(true)">
          同意并记住，以后免询问
        </el-button>
      </template>
    </el-dialog>

    <ProductListingDialog
      v-model="listingDialogVisible"
      :product="listingProduct"
      @saved="handleListingSaved"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { MagicStick, Picture, Refresh, Search } from '@element-plus/icons-vue'
import { getStorefrontProducts, updateProductAiDetail } from '@/api/ecommerce'
import ProductListingDialog from '@/components/ProductListingDialog.vue'
import { getUserInfo } from '@/utils/auth'
import { completeWithAgentModel, getActiveAgentModel, isCloudAgentModel } from '@/utils/agentModel'

const router = useRouter()
const products = ref([])
const categories = ref([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = 12
const filters = reactive({ keywords: '', category: '', sortBy: 'default' })
const isAdmin = computed(() => getUserInfo()?.role === 'admin')
const isProductEditor = computed(() => ['admin', 'user'].includes(getUserInfo()?.role))
const listingDialogVisible = ref(false)
const listingProduct = ref(null)
const aiBusy = ref(false)
const aiPreparing = ref(false)
const aiProgress = ref({ done: 0, total: 0 })
const cloudApprovalVisible = ref(false)
const pendingAiGeneration = ref(null)
const CLOUD_CONSENT_STORAGE_KEY = 'ecom-analysis-agent.cloud-model-consent.v1'

function formatPrice(value) {
  return Number(value || 0).toFixed(2)
}

function isOutOfStock(product) {
  return Number(product.stock) <= 0
}

async function load() {
  loading.value = true
  try {
    const response = await getStorefrontProducts({
      page: page.value,
      page_size: pageSize,
      keywords: filters.keywords.trim() || undefined,
      category: filters.category || undefined,
      sort_by: filters.sortBy
    })
    products.value = response.data?.list || []
    categories.value = response.data?.categories || []
    total.value = response.data?.total || 0
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  load()
}

function selectCategory(category) {
  filters.category = category
  page.value = 1
  load()
}

function changeSort() {
  page.value = 1
  load()
}

function resetFilters() {
  filters.keywords = ''
  filters.category = ''
  filters.sortBy = 'default'
  page.value = 1
  load()
}

function cloudConsentStorageKey() {
  const user = getUserInfo()
  const owner = user?.id ?? user?.username ?? 'anonymous'
  return `${CLOUD_CONSENT_STORAGE_KEY}:${owner}`
}

function cloudConsentKey(profile) {
  return JSON.stringify([
    profile?.provider || profile?.vendor || '',
    profile?.endpoint || '',
    profile?.model || ''
  ])
}

function hasRememberedCloudConsent(profile) {
  try {
    return window.localStorage.getItem(cloudConsentStorageKey()) === cloudConsentKey(profile)
  } catch {
    return false
  }
}

function rememberCloudConsent(profile) {
  try {
    window.localStorage.setItem(cloudConsentStorageKey(), cloudConsentKey(profile))
  } catch {
    ElMessage.warning('浏览器无法记住授权；本次仍会继续生成')
  }
}

function modelLabel(profile) {
  return `${profile?.vendor || profile?.provider || 'Agent 模型'} · ${profile?.name || profile?.model || ''}`
}

async function prepareAiGeneration() {
  if (!isAdmin.value || aiBusy.value || aiPreparing.value) return
  aiPreparing.value = true
  try {
    const firstResponse = await getStorefrontProducts({ page: 1, page_size: 60 })
    const firstData = firstResponse.data || {}
    const allProducts = [...(firstData.list || [])]
    const pages = Math.ceil((firstData.total || 0) / 60)
    for (let currentPage = 2; currentPage <= pages; currentPage += 1) {
      const pageResponse = await getStorefrontProducts({ page: currentPage, page_size: 60 })
      allProducts.push(...(pageResponse.data?.list || []))
    }
    if (!allProducts.length) {
      ElMessage.info('目前没有可生成文案的在售商品')
      return
    }
    const profile = await getActiveAgentModel()
    const pending = { profile, products: allProducts }
    if (isCloudAgentModel(profile) && !hasRememberedCloudConsent(profile)) {
      pendingAiGeneration.value = pending
      cloudApprovalVisible.value = true
      return
    }
    await runAiGeneration(pending)
  } catch (error) {
    ElMessage.error(error?.message || '准备生成商品文案失败')
  } finally {
    aiPreparing.value = false
  }
}

function cancelAiGeneration() {
  pendingAiGeneration.value = null
  cloudApprovalVisible.value = false
}

async function confirmAiGeneration(remember) {
  const pending = pendingAiGeneration.value
  if (!pending || aiBusy.value) return
  if (remember) rememberCloudConsent(pending.profile)
  cloudApprovalVisible.value = false
  await runAiGeneration(pending)
}

function parseAiJson(value) {
  const text = String(value || '').trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '')
  try {
    return JSON.parse(text)
  } catch {
    const start = text.indexOf('{')
    const end = text.lastIndexOf('}')
    if (start >= 0 && end > start) return JSON.parse(text.slice(start, end + 1))
    throw new Error('模型返回内容不是有效 JSON，请重试')
  }
}

async function runAiGeneration(pending) {
  aiBusy.value = true
  pendingAiGeneration.value = null
  const items = pending.products.map(({ id, name, category, description }) => ({
    id,
    name,
    category,
    description
  }))
  aiProgress.value = { done: 0, total: items.length }
  let saved = 0
  try {
    // 每批 5 件，降低单次上下文长度，兼容 Agent 控制台的本地模型。
    for (let offset = 0; offset < items.length; offset += 5) {
      const batch = items.slice(offset, offset + 5)
      const answer = await completeWithAgentModel(
        pending.profile,
        [
          {
            role: 'system',
            content:
              '你是电商商品文案编辑。只依据输入的商品名称、类目和现有描述写中文详情文案。严禁补造材质、尺寸、功能、认证、产地、保修、优惠等未提供事实；资料不足时使用中性表达，不做绝对化或保证性承诺。只返回严格 JSON，不要 Markdown，格式为 {"products":[{"id":数字,"headline":"短标题","selling_points":["卖点一","卖点二","卖点三"],"detail":"约100至180字的详情介绍"}]}。必须为输入里的每个 id 返回一项。'
          },
          {
            role: 'user',
            content: `请为以下商品生成详情文案：\n${JSON.stringify(batch)}`
          }
        ]
      )
      const parsed = parseAiJson(answer)
      const generated = new Map((parsed.products || []).map((entry) => [Number(entry.id), entry]))
      for (const product of batch) {
        const entry = generated.get(Number(product.id))
        if (!entry || typeof entry.headline !== 'string' || typeof entry.detail !== 'string') {
          throw new Error(`模型没有完整返回「${product.name}」的文案；已保存 ${saved} 件`)
        }
        const content = {
          headline: entry.headline.slice(0, 120),
          selling_points: Array.isArray(entry.selling_points)
            ? entry.selling_points.filter((point) => typeof point === 'string').slice(0, 5)
            : [],
          detail: entry.detail.slice(0, 3000)
        }
        await updateProductAiDetail(product.id, JSON.stringify(content))
        saved += 1
        aiProgress.value.done = saved
      }
    }
    await load()
    ElMessage.success(`已为 ${saved} 件商品生成并保存详情文案`)
  } catch (error) {
    ElMessage.error(`生成中断，已保存 ${saved} 件商品文案：${error?.message || '请重试'}`)
  } finally {
    aiBusy.value = false
    aiProgress.value = { done: 0, total: 0 }
  }
}

function openProduct(product) {
  router.push({ name: 'StorefrontProductDetail', params: { id: product.id } })
}

function openListingDialog(product = null) {
  listingProduct.value = product
  listingDialogVisible.value = true
}

async function handleListingSaved() {
  const isNewProduct = !listingProduct.value?.id
  listingProduct.value = null
  if (isNewProduct) {
    filters.keywords = ''
    filters.category = ''
    filters.sortBy = 'default'
    page.value = 1
  }
  await load()
}

onMounted(load)
</script>

<style scoped>
.storefront-page {
  display: grid;
  gap: 18px;
  padding-bottom: 16px;
}

.storefront-hero {
  position: relative;
  display: flex;
  min-height: 190px;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  overflow: hidden;
  padding: 30px 38px;
  border-radius: 14px;
  background: linear-gradient(115deg, #102237 0%, #174858 58%, #1a9c81 100%);
  color: #fff;
}

.storefront-hero__copy,
.storefront-search {
  position: relative;
  z-index: 1;
}

.storefront-hero__eyebrow {
  color: #91e0cf;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.16em;
}

.storefront-hero h1 {
  margin: 10px 0 8px;
  font-size: clamp(25px, 3vw, 34px);
  letter-spacing: 0.02em;
}

.storefront-hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
  font-size: 14px;
}

.storefront-search {
  display: flex;
  width: min(470px, 46%);
  gap: 9px;
  padding: 6px;
  border-radius: 11px;
  background: #fff;
  box-shadow: 0 12px 30px rgba(10, 32, 45, 0.18);
}

.storefront-search :deep(.el-input__wrapper) {
  box-shadow: none;
}

.storefront-search .el-button {
  flex-shrink: 0;
}

.storefront-hero__decoration {
  position: absolute;
  right: 29%;
  bottom: -26px;
  color: rgba(255, 255, 255, 0.07);
  font-family: Georgia, serif;
  font-size: 72px;
  font-weight: 700;
  line-height: 0.82;
  letter-spacing: -0.05em;
  transform: rotate(-9deg);
  user-select: none;
}

.storefront-toolbar {
  padding: 18px 20px 14px;
}

.storefront-toolbar__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.storefront-toolbar__title {
  min-width: 0;
}

.storefront-toolbar__title-row {
  display: flex;
  align-items: center;
  gap: 18px;
}

.storefront-toolbar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.storefront-ai-progress {
  display: grid;
  grid-template-columns: minmax(150px, auto) minmax(180px, 1fr);
  align-items: center;
  gap: 16px;
  margin-top: 14px;
  color: #168b75;
  font-size: 12px;
}

.storefront-ai-consent p {
  margin: 16px 0 0;
  color: #526a78;
  font-size: 13px;
  line-height: 1.8;
}

.storefront-toolbar h2 {
  margin: 0;
  color: var(--app-text);
  font-size: 18px;
}

.storefront-toolbar p {
  margin: 4px 0 0;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.storefront-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.storefront-list-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--app-text-secondary);
  font-size: 13px;
}

.category-chip {
  min-height: 32px;
  padding: 0 14px;
  border: 1px solid #dce6e2;
  border-radius: 18px;
  background: #fff;
  color: #52677b;
  cursor: pointer;
  font: inherit;
  font-size: 13px;
  transition: all 0.18s ease;
}

.category-chip:hover,
.category-chip--active {
  border-color: #1a9c81;
  background: #e9f4f0;
  color: #117963;
}

.storefront-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  min-height: 180px;
}

.store-product-card {
  overflow: hidden;
  border: 1px solid #dce6e2;
  border-radius: 13px;
  background: #fff;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.store-product-card:hover,
.store-product-card:focus-visible {
  border-color: #a8d7ca;
  box-shadow: 0 12px 28px rgba(20, 58, 59, 0.1);
  outline: none;
  transform: translateY(-3px);
}

.store-product-card--out-of-stock {
  filter: grayscale(1);
  background: #f1f3f4;
}

.store-product-card--out-of-stock .store-product-card__image,
.store-product-card--out-of-stock .store-product-card__placeholder {
  opacity: 0.58;
}

.store-product-card__stock-overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: grid;
  place-items: center;
  background: rgba(240, 242, 244, 0.15);
  pointer-events: none;
}

.store-product-card__stock-overlay strong {
  padding: 10px 24px 10px 30px;
  border: 4px solid currentColor;
  border-radius: 9px;
  color: #48525c;
  background: rgba(255, 255, 255, 0.84);
  font-size: clamp(36px, 3.5vw, 56px);
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: 6px;
  transform: rotate(-12deg);
}

.store-product-card__image-wrap {
  position: relative;
  aspect-ratio: 1 / 0.82;
  overflow: hidden;
  background: #eef3f0;
}

.store-product-card__image,
.store-product-card__placeholder {
  width: 100%;
  height: 100%;
}

.store-product-card__image {
  display: block;
  transition: transform 0.25s ease;
}

.store-product-card:hover .store-product-card__image {
  transform: scale(1.035);
}

.store-product-card__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 9px;
  color: #8a9ba0;
  font-size: 12px;
}

.store-product-card__tags {
  position: absolute;
  top: 11px;
  left: 11px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  max-width: calc(100% - 22px);
}

.store-product-card__edit {
  position: absolute;
  z-index: 2;
  top: 10px;
  right: 10px;
  border-color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.94);
}

.store-product-card__tag {
  padding: 5px 9px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  color: #286c63;
  font-size: 11px;
}

.store-product-card__tag--more {
  color: #657780;
}

.store-product-card__body {
  padding: 13px 14px 15px;
}

.store-product-card h3 {
  overflow: hidden;
  margin: 0;
  color: #172b40;
  font-size: 15px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.store-product-card__description {
  overflow: hidden;
  height: 18px;
  margin: 7px 0 12px;
  color: #80909a;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.store-product-card__price-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.store-product-card__price-values {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 5px 8px;
}

.store-product-card__price-row strong {
  color: #e25443;
  font-size: 23px;
  line-height: 1;
}

.store-product-card__price-row small {
  margin-right: 2px;
  font-size: 14px;
}

.store-product-card__price-values del,
.store-product-card__price-row .store-product-card__sold,
.store-product-card__rating span {
  color: #82909a;
  font-size: 11px;
}

.store-product-card__price-values del {
  font-size: 12px;
}

.store-product-card__discount {
  padding: 2px 5px;
  border-radius: 4px;
  background: #fff0ec;
  color: #df5b45;
  font-size: 10px;
}

.store-product-card__rating {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 11px;
}

.store-product-card__rating :deep(.el-rate) {
  height: 16px;
}

.store-product-card__rating :deep(.el-rate__icon) {
  margin-right: 1px;
  font-size: 13px;
}

.storefront-empty {
  padding: 24px;
}

.storefront-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 14px 18px;
}

.storefront-note {
  margin: -5px 2px 0;
  color: #8a989f;
  font-size: 11px;
  text-align: right;
}

@media (max-width: 1200px) {
  .storefront-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 850px) {
  .storefront-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 22px;
    padding: 25px;
  }
  .storefront-search {
    width: min(100%, 560px);
  }
  .storefront-hero__decoration {
    right: 6%;
  }
  .storefront-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .storefront-toolbar__title-row {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }
  .storefront-toolbar__heading {
    align-items: flex-start;
    flex-direction: column;
  }
  .storefront-toolbar__actions {
    width: 100%;
    flex-wrap: wrap;
  }
  .storefront-ai-progress {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}

@media (max-width: 520px) {
  .storefront-grid {
    grid-template-columns: 1fr;
  }
  .storefront-search {
    flex-direction: column;
  }
  .storefront-search .el-button {
    width: 100%;
  }
}
</style>
