<template>
  <div class="page-container">
    <div class="content-card">
      <div class="toolbar-row">
        <el-input
          class="search-input"
          placeholder="按订单号 / 买家 / 商品名搜索"
          v-model="params.keywords"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      </div>

      <el-table
        :header-cell-style="tableHeaderStyle"
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        @row-click="openDetail"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="order_no" label="订单号" width="230" show-overflow-tooltip />
        <el-table-column prop="product_name" label="商品" width="210" show-overflow-tooltip />
        <el-table-column prop="buyer_name" label="买家" min-width="140">
          <template #default="{ row }"><el-button class="buyer-profile-link" type="primary" link @click.stop="openUserProfile(row)">{{ row.buyer_name }}</el-button></template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" min-width="90" sortable="custom" :sort-orders="sortOrders" />
        <el-table-column prop="amount" label="实付" min-width="100" sortable="custom" :sort-orders="sortOrders" />
        <el-table-column prop="status" label="状态" min-width="205" sortable="custom" :sort-orders="sortOrders">
          <template #default="{ row }">
            <el-tag size="small" effect="light" round :type="statusTag(row)">
              {{ orderStatusLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tracking_no" label="物流单号" min-width="170" show-overflow-tooltip>
          <template #default="{ row }">
            <div v-if="row.tracking_no">发货：{{ row.tracking_no }}</div>
            <div v-if="row.exchange_tracking_no">换货：{{ row.exchange_tracking_no }}</div>
            <div v-if="row.return_tracking_no">寄回：{{ row.return_tracking_no }}</div>
            <span v-if="!row.tracking_no && !row.exchange_tracking_no && !row.return_tracking_no">
              {{ ['shipped', 'completed'].includes(row.status) ? '未录入' : '—' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="下单时间" min-width="210" sortable="custom" :sort-orders="sortOrders">
          <template #default="{ row }">
            <span class="time-text">{{ row.create_time }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="hasOrderActions" label="操作" width="140" align="center" header-align="center" fixed="right">
          <template #default="{ row }">
            <el-button v-if="canShipOrder(row) && row.status === 'paid'" type="success" link @click.stop="shipOrder(row)">
              发货
            </el-button>
            <el-button
              v-else-if="canShipOrder(row)"
              type="warning"
              link
              @click.stop="shipOrder(row)"
            >
              补录物流
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

    <UserProfileDrawer v-model="profileVisible" :user-id="profileUserId" :display-name="profileName" />
    <!-- 订单详情抽屉：订单本身 + 这笔订单的评价 -->
    <el-drawer v-model="drawerVisible" title="订单详情" size="480px">
      <div v-if="detailLoading" class="detail-loading" v-loading="detailLoading"></div>
      <div v-else-if="detail" class="order-detail">
        <div class="order-detail__no">{{ detail.order.order_no }}</div>
        <div class="order-detail__tags">
          <el-tag size="small" effect="light" round :type="statusTag(detail.order)">
            {{ orderStatusLabel(detail.order) }}
          </el-tag>
        </div>

        <div class="order-detail__list">
          <div class="order-detail__row">
            <span class="order-detail__label">商品</span>
            <span class="order-detail__value">{{ detail.order.product_name || '-' }}</span>
          </div>
          <div class="order-detail__row">
            <span class="order-detail__label">买家</span>
            <span class="order-detail__value">{{ detail.order.buyer_name }}</span>
          </div>
          <div class="order-detail__row">
            <span class="order-detail__label">原订单发货单号</span>
            <span class="order-detail__value">{{ detail.order.tracking_no || (detail.order.exchange_tracking_no ? '无，换货单号见下方' : '尚未发货') }}</span>
          </div>
          <div v-if="detail.order.exchange_tracking_no" class="order-detail__row">
            <span class="order-detail__label">换货发货单号</span>
            <span class="order-detail__value">{{ detail.order.exchange_tracking_no }}</span>
          </div>
          <div v-if="detail.order.return_tracking_no" class="order-detail__row">
            <span class="order-detail__label">买家寄回单号</span>
            <span class="order-detail__value">{{ detail.order.return_tracking_no }}</span>
          </div>
          <div class="order-detail__row">
            <span class="order-detail__label">数量 / 实付</span>
            <span class="order-detail__value">
              {{ detail.order.quantity }} 件 / {{ formatMoney(detail.order.amount) }}
            </span>
          </div>
          <div class="order-detail__row">
            <span class="order-detail__label">下单时间</span>
            <span class="order-detail__value time-text">{{ detail.order.create_time }}</span>
          </div>
        </div>

        <div class="order-detail__section">这笔订单的评价</div>
        <div v-if="detail.review" class="order-detail__review">
          <div class="order-detail__review-head">
            <el-tag
              size="small"
              effect="light"
              round
              :type="
                detail.review.rating <= 2
                  ? 'danger'
                  : detail.review.rating >= 4
                    ? 'success'
                    : 'warning'
              "
            >
              {{ detail.review.rating }} 分
            </el-tag>
            <span class="order-detail__review-time time-text">
              {{ detail.review.create_time }}
            </span>
          </div>
          <div class="order-detail__review-text">{{ detail.review.content }}</div>
          <el-image
            v-if="detail.review.img"
            class="review-thumb"
            :src="detail.review.img"
            :alt="`${detail.order.product_name}评价晒图`"
            title="点击查看晒图"
            :preview-src-list="[detail.review.img]"
            :initial-index="0"
            preview-teleported
            hide-on-click-modal
            fit="cover"
          >
            <template #error>
              <div class="review-thumb__error">缺图</div>
            </template>
          </el-image>
        </div>
        <div v-else class="order-detail__empty">该订单暂无评价</div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getOrderDetail, listOrders, shipOrder as shipOrderApi } from '@/api/ecommerce'
import { staffOrderStatusLabel as orderStatusLabel, canShipOrder } from '@/utils/afterSale'
import { useVisibleRefresh } from '@/utils/visibleRefresh'
import UserProfileDrawer from '@/components/UserProfileDrawer.vue'

const tableHeaderStyle = {
  backgroundColor: '#f8fafc',
  color: '#475569',
  fontWeight: 600
}
const sortOrders = ['ascending', 'descending']

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const hasOrderActions = computed(() => tableData.value.some(canShipOrder))
const params = reactive({ page: 1, pageSize: 10, keywords: '', sortBy: '', sortOrder: 'asc' })

const drawerVisible = ref(false)
const detailLoading = ref(false)
const detail = ref(null)
const profileVisible = ref(false), profileUserId = ref(null), profileName = ref('')
function openUserProfile(row) {
  profileUserId.value = row.buyer_user_id
  profileName.value = row.buyer_name
  profileVisible.value = true
}

function statusTag(order) {
  if (order?.after_sale_status === 'rejected') return 'danger'
  if (order && typeof order === 'object' && ['pending', 'approved', 'completed'].includes(order.after_sale_status)) {
    return { refund: 'danger', return: 'warning', exchange: 'warning' }[order.after_sale_service_type] || 'success'
  }
  if (order && typeof order === 'object' && order.exchange_tracking_no) return 'warning'
  const v = typeof order === 'object' ? order?.status : order
  const map = {
    paid: '',
    shipped: 'warning',
    completed: 'success',
    cancelled: 'info'
  }
  return map[v] || 'info'
}

function formatMoney(value) {
  const num = Number(value || 0)
  return `¥${num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`
}

let orderRequestId = 0
async function load(silent = false) {
  const requestId = ++orderRequestId
  if (silent !== true) loading.value = true
  try {
    const filters = { keywords: params.keywords || undefined }
    if (params.sortBy) {
      const pageSize = 100
      const first = await listOrders({ ...filters, page: 1, page_size: pageSize })
      const firstData = first.data || {}
      const allOrders = [...(firstData.list || [])]
      const pageCount = Math.ceil((firstData.total || 0) / pageSize)
      if (pageCount > 1) {
        const rest = await Promise.all(
          Array.from({ length: pageCount - 1 }, (_, index) =>
            listOrders({ ...filters, page: index + 2, page_size: pageSize })
          )
        )
        rest.forEach((res) => allOrders.push(...(res.data?.list || [])))
      }
      if (requestId !== orderRequestId) return
      allOrders.sort(compareOrders)
      total.value = firstData.total || 0
      const start = (params.page - 1) * params.pageSize
      tableData.value = allOrders.slice(start, start + params.pageSize)
    } else {
      const res = await listOrders({
        ...filters,
        page: params.page,
        page_size: params.pageSize
      })
      if (requestId !== orderRequestId) return
      tableData.value = res.data?.list || []
      total.value = res.data?.total || 0
    }
    const updatedDetail = tableData.value.find(row => row.id === detail.value?.order?.id)
    if (updatedDetail) detail.value.order = { ...detail.value.order, ...updatedDetail }
  } finally {
    if (requestId === orderRequestId) loading.value = false
  }
}

function compareOrders(a, b) {
  let comparison = 0
  if (params.sortBy === 'status') {
    comparison = orderStatusLabel(a).localeCompare(orderStatusLabel(b), 'zh-CN')
  } else if (params.sortBy === 'create_time') {
    comparison = new Date(a.create_time).getTime() - new Date(b.create_time).getTime()
  } else {
    comparison = Number(a[params.sortBy] || 0) - Number(b[params.sortBy] || 0)
  }
  if (params.sortOrder === 'desc') comparison *= -1
  return comparison || Number(b.id) - Number(a.id)
}

function handleSearch() {
  params.page = 1
  load()
}

function handleSortChange({ prop, order }) {
  params.sortBy = order ? prop : ''
  params.sortOrder = order === 'descending' ? 'desc' : 'asc'
  params.page = 1
  load()
}

async function openDetail(row) {
  if (!row?.id) return
  drawerVisible.value = true
  detailLoading.value = true
  detail.value = null
  try {
    const res = await getOrderDetail(row.id)
    detail.value = res.data || null
  } finally {
    detailLoading.value = false
  }
}

async function shipOrder(row) {
  let trackingNo
  const isBackfill = row.status !== 'paid'
  try {
    const result = await ElMessageBox.prompt(
      isBackfill
        ? `为订单 ${row.order_no} 补充已发货的物流单号。`
        : `填写订单 ${row.order_no} 的物流单号，提交后将标记为已发货。`,
      isBackfill ? '补录物流单号' : '订单发货',
      {
        confirmButtonText: isBackfill ? '保存单号' : '确认发货',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入物流单号',
        inputValidator: (value) => value?.trim() ? true : '请填写物流单号',
        inputErrorMessage: '请填写物流单号',
        type: 'warning'
      }
    )
    trackingNo = result.value.trim()
  } catch {
    return
  }

  try {
    const response = await shipOrderApi(row.id, trackingNo)
    row.status = response.data?.status || row.status
    row.tracking_no = response.data?.tracking_no || trackingNo
    if (detail.value?.order?.id === row.id) {
      detail.value.order.status = row.status
      detail.value.order.tracking_no = row.tracking_no
    }
    ElMessage.success(isBackfill ? '物流单号已补录' : '物流单号已保存，订单已发货')
  } catch (error) {
    ElMessage.error(error?.message || '订单发货失败')
  }
}

onMounted(load)
useVisibleRefresh(() => load(true))
</script>

<style scoped>
:deep(.el-table__header-wrapper .cell) {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 4px;
  white-space: nowrap;
}

:deep(.el-table__header-wrapper th.is-center .cell) {
  justify-content: center;
}

:deep(.el-table__header-wrapper .caret-wrapper) {
  flex: 0 0 auto;
  margin-left: 0;
}

.detail-loading {
  min-height: 200px;
}

.order-detail__no {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.order-detail__tags {
  margin-top: 8px;
}

.order-detail__list {
  margin-top: 14px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  overflow: hidden;
}

.order-detail__row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 9px 12px;
  font-size: 13px;
}

.order-detail__row + .order-detail__row {
  border-top: 1px solid var(--app-border);
}

.order-detail__label {
  width: 76px;
  flex-shrink: 0;
  color: var(--app-text-secondary);
}

.order-detail__value {
  color: var(--app-text);
  word-break: break-word;
}

.order-detail__section {
  margin: 18px 0 8px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.order-detail__review {
  padding: 12px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #f8fafc;
}

.order-detail__review-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.order-detail__review-time {
  font-size: 12px;
}

.order-detail__review-text {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--app-text);
  word-break: break-word;
}

.order-detail__empty {
  padding: 12px;
  font-size: 13px;
  color: var(--app-text-secondary);
  border: 1px dashed var(--app-border);
  border-radius: var(--app-radius-sm);
}

.review-thumb {
  display: block;
  width: 72px;
  height: 72px;
  margin-top: 10px;
  border-radius: 4px;
  cursor: pointer;
}

.review-thumb__error {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--app-text-secondary);
  background: #eef3f0;
  border-radius: 4px;
}
</style>
