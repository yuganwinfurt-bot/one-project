<template>
  <div class="page-container">
    <div class="content-card">
      <div class="toolbar-row">
        <el-input
          class="search-input"
          placeholder="按商品名 / 类目搜索"
          v-model="params.keywords"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button v-if="isProductEditor()" :loading="scanningRisks" @click="checkAfterSaleRisks">检查售后风险</el-button>

      </div>

      <el-table
        :header-cell-style="tableHeaderStyle"
        :data="tableData"
        table-layout="fixed"
        style="width: 100%"
        v-loading="loading"
        @row-click="openDetail"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="商品名称" min-width="110" show-overflow-tooltip>
          <template #default="{ row }">
            <el-input
              v-if="isEditing(row, 'name')"
              v-model="inlineValue"
              size="small"
              maxlength="100"
              autofocus
              @click.stop
              @keyup.enter="saveInlineEdit(row, 'name')"
              @keyup.esc.stop="cancelInlineEdit"
              @blur="saveInlineEdit(row, 'name')"
            />
            <span
              v-else
              class="editable-cell"
              title="点击编辑；回车或失焦保存，Esc 取消"
              @click.stop="beginInlineEdit(row, 'name')"
            >
              {{ row.name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类目" min-width="70">
          <template #default="{ row }">
            <el-input
              v-if="isEditing(row, 'category')"
              v-model="inlineValue"
              size="small"
              maxlength="50"
              autofocus
              @click.stop
              @keyup.enter="saveInlineEdit(row, 'category')"
              @keyup.esc.stop="cancelInlineEdit"
              @blur="saveInlineEdit(row, 'category')"
            />
            <span
              v-else
              class="editable-cell"
              title="点击编辑；回车或失焦保存，Esc 取消"
              @click.stop="beginInlineEdit(row, 'category')"
            >
              {{ row.category }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="price"
          label="售价"
          min-width="72"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <el-input
              v-if="isEditing(row, 'price') && !row.variants?.length"
              v-model="inlineValue"
              type="number"
              :min="0.01"
              :max="99999999.99"
              step="1"
              size="small"
              autofocus
              @click.stop
              @keyup.enter="saveInlineEdit(row, 'price')"
              @keyup.esc.stop="cancelInlineEdit"
              @blur="saveInlineEdit(row, 'price')"
            />
            <span v-else-if="row.variants?.length" class="sku-summary-cell" title="多规格售价请到规格编辑页逐项维护">
              起 {{ row.price }}
            </span>
            <span
              v-else
              class="editable-cell"
              title="点击编辑折后售价；回车或失焦保存，Esc 取消"
              @click.stop="beginInlineEdit(row, 'price')"
            >
              {{ row.price }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="discount_percent"
          label="折扣"
          min-width="74"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <el-input
              v-if="isEditing(row, 'discount_percent') && !row.variants?.length"
              v-model="inlineValue"
              type="number"
              min="0"
              max="99.99"
              step="0.01"
              size="small"
              autofocus
              @click.stop
              @keyup.enter="saveInlineEdit(row, 'discount_percent')"
              @keyup.esc.stop="cancelInlineEdit"
              @blur="saveInlineEdit(row, 'discount_percent')"
            />
            <span v-else-if="row.variants?.length" class="sku-summary-cell" title="多规格商品的统一优惠请到规格编辑页维护">
              {{ discountLabel(row) }}
            </span>
            <span
              v-else
              class="editable-cell discount-cell"
              title="点击编辑优惠百分比；回车或失焦保存，Esc 取消"
              @click.stop="beginInlineEdit(row, 'discount_percent')"
            >
              {{ discountLabel(row) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="stock"
          label="库存"
          min-width="68"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <el-input
              v-if="isEditing(row, 'stock') && !row.variants?.length"
              v-model="inlineValue"
              type="number"
              min="0"
              step="1"
              size="small"
              autofocus
              @click.stop
              @keyup.enter="saveInlineEdit(row, 'stock')"
              @keyup.esc.stop="cancelInlineEdit"
              @blur="saveInlineEdit(row, 'stock')"
            />
            <el-tooltip v-else-if="row.variants?.length" content="这是所有规格的库存总和，请在规格编辑页逐项调整" placement="top">
              <span class="sku-summary-cell">{{ row.stock }}（合计）</span>
            </el-tooltip>
            <span
              v-else
              class="editable-cell"
              title="点击编辑库存；回车或失焦保存，Esc 取消"
              @click.stop="beginInlineEdit(row, 'stock')"
            >
              {{ row.stock }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="shelf_status"
          label="上下架"
          min-width="78"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <el-dropdown
              trigger="click"
              :title="isProductEditor() ? '点击选择上下架状态' : '登录运营或管理员账号后可修改'"
              @command="(status) => changeShelfStatus(row, status)"
            >
              <span class="shelf-status-trigger" @click.stop>
                <el-tag
                  size="small"
                  effect="light"
                  round
                  :type="row.shelf_status === 'on_sale' ? 'success' : 'info'"
                >
                  {{ shelfLabel(row.shelf_status) }}
                </el-tag>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="on_sale" :disabled="row.shelf_status === 'on_sale'">
                    设为在售
                  </el-dropdown-item>
                  <el-dropdown-item command="off_shelf" :disabled="row.shelf_status === 'off_shelf'">
                    下架商品
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
        <el-table-column
          prop="review_status"
          label="复核状态"
          min-width="95"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="light"
              round
              :type="row.review_status === 'pending_review' ? 'warning' : 'success'"
            >
              {{ reviewStatusLabel(row.review_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="售后风险（近30天）" min-width="138">
          <template #default="{ row }">
            <el-tooltip v-if="row.after_sale_risk" :content="row.after_sale_risk.rule_text" placement="top">
              <el-tag :type="row.after_sale_risk.level === 'critical' ? 'danger' : row.after_sale_risk.level === 'warning' ? 'warning' : 'info'" effect="light" round>
                {{ row.after_sale_risk.level === 'critical' ? '建议复核' : row.after_sale_risk.level === 'warning' ? '售后提醒' : '未达阈值' }} · {{ row.after_sale_risk.after_sale_order_count }}笔 / {{ row.after_sale_risk.after_sale_rate }}%
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="110" show-overflow-tooltip />
        <el-table-column
          prop="create_time"
          label="创建时间"
          min-width="135"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <span class="time-text">{{ row.create_time }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="125">
          <template #default="{ row }">
            <el-button v-if="row.variants?.length && isProductEditor()" type="primary" link @click.stop="editListing(row)">
              规格编辑
            </el-button>
            <el-button type="primary" link @click.stop="goToProductPage(row)">
              商品页
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
        <el-pagination
          v-model:current-page="params.page"
          v-model:page-size="params.pageSize"
          :total="total"
          background
          small
          layout="total, prev, pager, next"
          @current-change="load"
        />
      </div>
    </div>

    <!-- 商品详情抽屉：把该商品的评价、订单与 Agent 产物串在一起 -->
    <el-drawer v-model="drawerVisible" title="商品详情" size="540px">
      <div v-if="detailLoading" class="detail-loading" v-loading="detailLoading"></div>
      <div v-else-if="detail" class="product-detail">
        <div class="product-detail__heading">
          <div class="product-detail__name">{{ detail.product.name }}</div>
          <el-button
            v-if="isProductEditor()"
            type="primary"
            plain
            size="small"
            @click="editProduct(detail.product)"
          >
            编辑商品
          </el-button>
        </div>
        <div class="product-detail__tags">
          <el-tag size="small" effect="plain">{{ detail.product.category }}</el-tag>
          <el-tag
            size="small"
            effect="light"
            round
            :type="detail.product.shelf_status === 'on_sale' ? 'success' : 'info'"
          >
            {{ shelfLabel(detail.product.shelf_status) }}
          </el-tag>
          <el-tag
            size="small"
            effect="light"
            round
            :type="detail.product.review_status === 'pending_review' ? 'warning' : 'success'"
          >
            {{ reviewStatusLabel(detail.product.review_status) }}
          </el-tag>
        </div>

        <div class="product-detail__stats">
          <div class="product-detail__stat">
            <span class="product-detail__stat-label">售价</span>
            <span class="product-detail__stat-value">{{ formatMoney(detail.product.price) }}</span>
          </div>
          <div class="product-detail__stat">
            <span class="product-detail__stat-label">库存</span>
            <span class="product-detail__stat-value">{{ detail.product.stock }}</span>
          </div>
          <div class="product-detail__stat">
            <span class="product-detail__stat-label">评价数 / 平均分</span>
            <span class="product-detail__stat-value">
              {{ detail.review_summary.review_count }} / {{ detail.review_summary.avg_rating }}
            </span>
          </div>
          <div class="product-detail__stat">
            <span class="product-detail__stat-label">订单数 / 成交额</span>
            <span class="product-detail__stat-value">
              {{ detail.order_summary.order_count }} /
              {{ formatMoney(detail.order_summary.total_amount) }}
            </span>
          </div>
        </div>

        <AfterSaleRiskCard :risk="detail.after_sale_risk" :product="detail.product" @reviewed="handleRiskReviewed" />

        <div class="product-detail__label">商品描述</div>
        <div class="product-detail__value">{{ detail.product.description }}</div>

        <div class="product-detail__label">
          评分分布（差评 {{ detail.review_summary.bad_count }} 条）
        </div>
        <ul class="rating-bars">
          <li
            v-for="bucket in detail.review_summary.rating_distribution"
            :key="bucket.rating"
            class="rating-bars__item"
          >
            <span class="rating-bars__star">{{ bucket.rating }} 星</span>
            <span class="rating-bars__track">
              <span
                class="rating-bars__fill"
                :class="`rating-bars__fill--${ratingTone(bucket.rating)}`"
                :style="{ width: barWidth(bucket.count) }"
              ></span>
            </span>
            <span class="rating-bars__count">{{ bucket.count }}</span>
          </li>
        </ul>

        <div class="product-detail__label">最近评价</div>
        <ul v-if="detail.recent_reviews.length" class="detail-list">
          <li v-for="review in detail.recent_reviews" :key="review.id" class="detail-item">
            <div class="detail-item__head">
              <el-tag
                size="small"
                effect="light"
                round
                :type="review.rating <= 2 ? 'danger' : review.rating >= 4 ? 'success' : 'warning'"
              >
                {{ review.rating }} 分
              </el-tag>
              <el-image
                v-if="review.img"
                class="review-thumb"
                :src="review.img"
                :alt="`${detail.product.name}评价晒图`"
                title="点击查看晒图"
                :preview-src-list="[review.img]"
                :initial-index="0"
                preview-teleported
                hide-on-click-modal
                fit="cover"
              />
              <span class="detail-item__time time-text">{{ review.create_time }}</span>
            </div>
            <div class="detail-item__text">{{ review.content }}</div>
          </li>
        </ul>
        <div v-else class="detail-empty">暂无评价</div>

        <div class="product-detail__label">
          最近订单
          <span v-if="detail.order_summary.last_order_time" class="detail-note">
            （最近一单 {{ detail.order_summary.last_order_time }}）
          </span>
        </div>
        <ul v-if="detail.recent_orders.length" class="detail-list">
          <li v-for="order in detail.recent_orders" :key="order.id" class="detail-item">
            <div class="detail-item__head">
              <span class="detail-item__title">{{ order.order_no }}</span>
              <el-tag size="small" effect="light" round>{{
                orderStatusLabel(order.status)
              }}</el-tag>
              <span class="detail-item__time time-text">{{ order.create_time }}</span>
            </div>
            <div class="detail-item__meta">
              {{ order.buyer_name }} · {{ formatMoney(order.amount) }} × {{ order.quantity }}
            </div>
          </li>
        </ul>
        <div v-else class="detail-empty">暂无订单</div>

        <div class="product-detail__label">相关诊断报告</div>
        <ul v-if="detail.reports.length" class="detail-list">
          <li v-for="report in detail.reports" :key="report.id" class="detail-item">
            <div class="detail-item__head">
              <el-tag
                size="small"
                effect="light"
                round
                :type="report.risk_level === 'high' ? 'danger' : 'success'"
              >
                {{ report.risk_level === 'high' ? '高风险' : '低风险' }}
              </el-tag>
              <span class="detail-item__time time-text">{{ report.create_time }}</span>
            </div>
            <div class="detail-item__text">{{ report.question }}</div>
          </li>
        </ul>
        <div v-else class="detail-empty">暂无报告（问句指名到该商品时才会写入）</div>

        <div class="product-detail__label">相关预警通知</div>
        <ul v-if="detail.alerts.length" class="detail-list">
          <li v-for="alert in detail.alerts" :key="alert.id" class="detail-item">
            <div class="detail-item__head">
              <el-tag
                size="small"
                effect="light"
                round
                :type="alert.level === 'critical' ? 'danger' : 'warning'"
              >
                {{ alert.level === 'critical' ? '严重' : '提醒' }}
              </el-tag>
              <span class="detail-item__time time-text">{{ alert.create_time }}</span>
            </div>
            <strong class="detail-item__title">{{ alert.title }}</strong>
            <div class="detail-item__text">{{ alert.content }}</div>
          </li>
        </ul>
        <div v-else class="detail-empty">暂无预警</div>
      </div>
    </el-drawer>


  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import AfterSaleRiskCard from '@/components/AfterSaleRiskCard.vue'
import { useAlertUnread } from '@/composables/useAlertUnread'
import {
  getProductDetail,
  listProducts,
  updateProduct,
  updateProductPricing,
  updateProductShelfStatus,
  scanAfterSaleRisks
} from '@/api/ecommerce'
import { getUserInfo } from '@/utils/auth'

const router = useRouter()
const { refresh: refreshAlertUnread } = useAlertUnread()

const tableHeaderStyle = {
  backgroundColor: '#f8fafc',
  color: '#475569',
  fontWeight: 600
}

const loading = ref(false)

const tableData = ref([])
const total = ref(0)
const params = reactive({ page: 1, pageSize: 10, keywords: '' })
const sortOrders = ['ascending', 'descending']
const sortBy = ref('')
const sortOrder = ref('asc')


const drawerVisible = ref(false)
const detailLoading = ref(false)
const detail = ref(null)
const editingCell = ref(null)
const inlineValue = ref('')
const savingCell = ref(false)

const scanningRisks = ref(false)

async function checkAfterSaleRisks() {
  if (scanningRisks.value) return
  scanningRisks.value = true
  try {
    const response = await scanAfterSaleRisks()
    const result = response.data
    ElMessage.success(`售后风险检查完成：提醒 ${result.warning_products} 个商品，严重 ${result.critical_products} 个，新增预警 ${result.alerts_created} 条`)
    await refreshAlertUnread()
    window.dispatchEvent(new Event('staff-message-center-updated'))
    await load()
    if (drawerVisible.value && detail.value?.product?.id) {
      const latest = await getProductDetail(detail.value.product.id)
      detail.value = latest.data
    }
  } catch { /* 请求层显示失败原因。 */ }
  finally { scanningRisks.value = false }
}

async function handleRiskReviewed(result) {
  if (detail.value?.product?.id === result.product_id) detail.value.product.review_status = result.review_status
  await load()
}

function shelfLabel(v) {
  return v === 'on_sale' ? '在售' : v === 'off_shelf' ? '已下架' : v || '-'
}

function isProductEditor() {
  return ['admin', 'user'].includes(getUserInfo()?.role)
}

function reviewStatusLabel(v) {
  return v === 'pending_review' ? '待复核' : v === 'normal' ? '正常' : v || '-'
}

function orderStatusLabel(v) {
  const map = { unpaid: '待付款', paid: '已支付', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
  return map[v] || v || '-'
}

function formatMoney(value) {
  const num = Number(value || 0)
  return `¥${num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`
}

const maxRatingCount = computed(() =>
  Math.max(1, ...(detail.value?.review_summary?.rating_distribution || []).map((b) => b.count))
)

function barWidth(count) {
  return `${Math.round((count / maxRatingCount.value) * 100)}%`
}

function ratingTone(rating) {
  if (rating <= 2) return 'bad'
  if (rating >= 4) return 'good'
  return 'mid'
}

async function load() {
  loading.value = true
  try {
    const res = await listProducts({
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords || undefined,
      sort_by: sortBy.value || undefined,
      sort_order: sortBy.value ? sortOrder.value : undefined
    })
    tableData.value = res.data?.list || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  params.page = 1
  load()
}

function handleSortChange({ prop, order }) {

  sortBy.value = order ? prop : ''
  sortOrder.value = order === 'descending' ? 'desc' : 'asc'
  params.page = 1
  load()
}

async function changeShelfStatus(row, status) {
  if (!isProductEditor()) {
    ElMessage.warning('请登录运营或管理员账号后修改商品状态')
    return
  }
  if (!row?.id || row.shelf_status === status) return

  try {
    await updateProductShelfStatus(row.id, status)
    ElMessage.success(status === 'off_shelf' ? '商品已下架' : '商品已恢复在售')
    await load()
    if (detail.value?.product?.id === row.id) {
      const res = await getProductDetail(row.id)
      detail.value = res.data || null
    }
  } catch {
    // 请求层已经显示服务端错误提示。
  }
}

function isEditing(row, field) {
  return editingCell.value?.id === row.id && editingCell.value?.field === field
}

function discountLabel(row) {
  const percent = Number(row.discount_percent || 0)
  return percent > 0 ? `优惠 ${percent}%` : '—'
}

function beginInlineEdit(row, field) {
  if (row.variants?.length && ['price', 'discount_percent', 'stock'].includes(field)) {
    ElMessage.info('多规格商品请到商品上架页编辑规格价格和库存')
    return
  }
  editingCell.value = { id: row.id, field }
  inlineValue.value = String(row[field] ?? '')
}

function editListing(row) {
  router.push({ path: `/manager/product-listing/${row.id}`, query: { returnTo: '/manager/products' } })
}

function cancelInlineEdit() {
  editingCell.value = null
  inlineValue.value = ''
}

async function saveInlineEdit(row, field) {
  if (!isEditing(row, field) || savingCell.value) return
  const rawValue = inlineValue.value
  const value = ['price', 'stock', 'discount_percent'].includes(field)
    ? Number(rawValue)
    : String(rawValue).trim()

  if (['name', 'category'].includes(field) && !value) {
    ElMessage.warning(field === 'name' ? '商品名称不能为空' : '类目不能为空')
    return
  }
  if (field === 'price' && (!Number.isFinite(value) || value <= 0)) {
    ElMessage.warning('售价必须大于 0')
    return
  }
  if (field === 'stock' && (!Number.isInteger(value) || value < 0)) {
    ElMessage.warning('库存必须是整数')
    return
  }
  if (
    field === 'discount_percent' &&
    (!Number.isFinite(value) || value < 0 || value > 99.99)
  ) {
    ElMessage.warning('折扣优惠幅度必须在 0% 到 99.99% 之间')
    return
  }

  const payload = {
    name: field === 'name' ? value : row.name,
    category: field === 'category' ? value : row.category,
    price: field === 'price' ? Number(value.toFixed(2)) : Number(Number(row.price).toFixed(2)),
    stock: field === 'stock' ? value : Number(row.stock),
    discount_percent:
      field === 'discount_percent'
        ? Number(value.toFixed(2))
        : Number(Number(row.discount_percent || 0).toFixed(2))
  }

  savingCell.value = true
  try {
    if (field === 'discount_percent') {
      await updateProductPricing(
        row.id,
        Number(row.original_price ?? row.price),
        Number(value.toFixed(2))
      )
    } else {
      await updateProduct(row.id, payload)
    }
    const fieldLabel = {
      name: '商品名称',
      category: '类目',
      price: '售价',
      discount_percent: '折扣',
      stock: '库存'
    }[field]
    ElMessage.success(`${fieldLabel}已更新`)
    cancelInlineEdit()
    await load()
    if (detail.value?.product?.id === row.id) {
      const res = await getProductDetail(row.id)
      detail.value = res.data || null
    }
  } finally {
    savingCell.value = false
  }
}

async function openDetail(row) {
  if (!row?.id) return
  drawerVisible.value = true
  detailLoading.value = true
  detail.value = null
  try {
    const res = await getProductDetail(row.id)
    detail.value = res.data || null
  } finally {
    detailLoading.value = false
  }
}

function editProduct(product) {
  if (!product?.id) return
  router.push({ name: 'ProductListing', params: { id: product.id } })
}

function goToProductPage(row) {
  if (!row?.id) return
  router.push({
    name: 'StorefrontProductDetail',
    params: { id: row.id },
    query: { from: 'products' }
  })
}



onMounted(load)
</script>

<style scoped>
.editable-cell {
  display: inline-block;
  min-width: 28px;
  padding: 3px 5px;
  margin: -3px -5px;
  border: 1px solid transparent;
  border-radius: 5px;
  cursor: text;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}


.editable-cell:hover {
  border-color: var(--app-border);
  background: #f8fbfa;
}

.discount-cell {
  white-space: nowrap;
}

.editable-cell:focus-visible {
  border-color: var(--app-primary);
  outline: none;
}

.sku-summary-cell {
  color: var(--app-text-secondary);
  cursor: default;
  white-space: nowrap;
}

.detail-loading {
  min-height: 200px;
}

.shelf-status-trigger {
  display: inline-flex;
  cursor: pointer;
}

.product-detail__name {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.product-detail__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.product-detail__tags {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.product-detail__stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 14px 0 4px;
}

.product-detail__stat {
  padding: 10px 12px;
  background: #f8fafc;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
}

.product-detail__stat-label {
  display: block;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.product-detail__stat-value {
  display: block;
  margin-top: 4px;
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text);
}

.product-detail__label {
  margin: 16px 0 6px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.product-detail__value {
  font-size: 14px;
  line-height: 1.7;
  color: var(--app-text);
  word-break: break-word;
}

.detail-note {
  color: var(--app-text-secondary);
}

.rating-bars {
  margin: 0;
  padding: 0;
  list-style: none;
}

.rating-bars__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 0;
}

.rating-bars__star {
  width: 34px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.rating-bars__track {
  flex: 1;
  height: 8px;
  border-radius: 999px;
  background: #eef3f0;
  overflow: hidden;
}

.rating-bars__fill {
  display: block;
  height: 100%;
  border-radius: 999px;
}

.rating-bars__fill--bad {
  background: #ef4444;
}

.rating-bars__fill--mid {
  background: #94a3b8;
}

.rating-bars__fill--good {
  background: #1a9c81;
}

.rating-bars__count {
  width: 28px;
  text-align: right;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.detail-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.detail-item {
  padding: 10px 0;
  border-bottom: 1px dashed var(--app-border);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item__head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-item__title {
  font-size: 13px;
  color: var(--app-text);
}

.detail-item__time {
  margin-left: auto;
  flex-shrink: 0;
}

.detail-item__text {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--app-text);
  word-break: break-word;
}

.detail-item__meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.detail-empty {
  font-size: 12px;
  color: var(--app-text-secondary);
  padding: 4px 0;
}

.review-thumb {
  width: 44px;
  height: 44px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
