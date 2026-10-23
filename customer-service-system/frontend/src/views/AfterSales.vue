<template>
  <div class="page-container">
    <div class="content-card after-sales-card">
      <div v-if="productFilterId" class="after-sales-filter">
        <span>已按商品筛选：{{ route.query.productName || `商品 #${productFilterId}` }}</span>
        <el-button link type="primary" @click="clearProductFilter">查看全部商品</el-button>
      </div>
      <div class="toolbar-row">
        <el-input
          v-model="params.keywords"
          class="search-input"
          clearable
          placeholder="按订单号、用户、商品或原因搜索"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-select v-model="params.status" clearable placeholder="全部状态" style="width: 150px" @change="handleSearch">
          <el-option label="待审核" value="pending" />
          <el-option label="处理中" value="approved" />
          <el-option label="已拒绝" value="rejected" />
          <el-option label="已完成" value="completed" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>

      <el-table
        :data="tableData"
        v-loading="loading"
        table-layout="fixed"
        style="width: 100%"
        empty-text="暂无售后申请"
        @row-click="openDetail"
      >
        <el-table-column prop="order_no" label="订单号" min-width="150" show-overflow-tooltip />
        <el-table-column label="商品" min-width="125" show-overflow-tooltip>
          <template #default="{ row }">{{ row.product_name || `商品 #${row.product_id}` }}</template>
        </el-table-column>
        <el-table-column label="申请用户" min-width="105">
          <template #default="{ row }">
            <button type="button" class="after-sales-user user-profile-link" @click.stop="openUserProfile(row)">
              <strong>{{ row.user_name || row.username }}</strong>
              <span>{{ row.username }}</span>
            </button>
          </template>
        </el-table-column>
        <el-table-column label="售后类型" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="serviceTypeTone(row.service_type)" effect="light" round>
              {{ serviceTypeLabel(row.service_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申请原因" min-width="135" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="after-sales-reason">
              <strong>{{ row.reason }}</strong>
              <span v-if="row.description">{{ row.description }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="135" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTone(row.status)" effect="light" round>{{ statusLabel(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="申请时间" min-width="160" />
        <el-table-column label="操作" min-width="82" align="center" header-align="center">
          <template #default="{ row }">
            <div class="after-sales-actions">
              <el-badge :value="row.unread_messages_count" :hidden="!row.unread_messages_count" :max="99">
                <el-button type="primary" link @click="openConversation(row)">沟通</el-button>
              </el-badge>
            </div>
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
    <el-drawer v-model="detailVisible" title="售后申请详情" size="480px">
      <div v-if="selected" class="after-sales-detail">
        <div class="after-sales-detail__header">
          <div class="after-sales-detail__heading">
            <span class="after-sales-detail__eyebrow">售后商品</span>
            <strong>{{ selected.product_name || `商品 #${selected.product_id}` }}</strong>
            <span class="after-sales-detail__order">订单号：{{ selected.order_no }}</span>
          </div>
          <el-tag :type="statusTone(selected.status)" effect="light" round>{{ statusLabel(selected) }}</el-tag>
        </div>

        <section class="after-sales-detail__section">
          <h3>申请信息</h3>
          <div class="after-sales-detail__grid">
            <div class="after-sales-detail__field">
              <span>申请用户</span>
              <strong>{{ selected.user_name || selected.username }}</strong>
            </div>
            <div class="after-sales-detail__field">
              <span>售后类型</span>
              <el-tag :type="serviceTypeTone(selected.service_type)" effect="light" round>
                {{ serviceTypeLabel(selected.service_type) }}
              </el-tag>
            </div>
            <div class="after-sales-detail__field">
              <span>申请时间</span>
              <strong>{{ selected.create_time || '—' }}</strong>
            </div>
            <div class="after-sales-detail__field after-sales-detail__field--wide">
              <span>申请原因</span>
              <strong>{{ selected.reason || '—' }}</strong>
            </div>
          </div>
        </section>

        <section
          v-if="(selected.service_type !== 'refund' && ['approved', 'completed'].includes(selected.status)) || selected.exchange_shipping_address || selected.exchange_tracking_no"
          class="after-sales-detail__section"
        >
          <h3>退换货与物流</h3>
          <div class="after-sales-detail__grid">
            <div v-if="selected.service_type !== 'refund' && ['approved', 'completed'].includes(selected.status)" class="after-sales-detail__field">
              <span>商品寄回</span>
              <strong>{{ returnShipmentLabel(selected) }}</strong>
            </div>
            <div v-if="selected.service_type !== 'refund' && ['approved', 'completed'].includes(selected.status)" class="after-sales-detail__field">
              <span>寄回物流单号</span>
              <strong>{{ returnTrackingLabel(selected) }}</strong>
            </div>
            <div v-if="selected.exchange_shipping_address" class="after-sales-detail__field after-sales-detail__field--wide">
              <span>换货收货地址</span>
              <strong>{{ selected.exchange_shipping_address }}</strong>
            </div>
            <div v-if="selected.exchange_tracking_no" class="after-sales-detail__field after-sales-detail__field--wide">
              <span>商家发货物流单号</span>
              <strong>{{ selected.exchange_tracking_no }}</strong>
            </div>
          </div>
        </section>

        <section class="after-sales-detail__section after-sales-detail__notes">
          <h3>说明</h3>
          <div class="after-sales-detail__note">
            <span>用户补充说明</span>
            <p>{{ selected.description || '用户未填写补充说明' }}</p>
          </div>
          <div class="after-sales-detail__note">
            <span>后台处理说明</span>
            <p>{{ selected.admin_note || '暂无处理说明' }}</p>
          </div>
        </section>
        <section v-if="selected.service_rating" class="after-sales-detail__section">
          <h3>售后服务评价</h3>
          <div class="after-sales-detail__field">
            <span>评分：{{ selected.service_rating }} / 5</span>
            <strong>{{ selected.service_feedback || '用户未补充评价内容' }}</strong>
          </div>
        </section>
      </div>
    </el-drawer>

  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { listAfterSales } from '@/api/ecommerce'
import { staffApplicationStatusLabel as statusLabel, applicationStatusTone as statusTone, serviceTypeLabel, serviceTypeTone, returnShipmentLabel, returnTrackingLabel } from '@/utils/afterSale'
import { useVisibleRefresh } from '@/utils/visibleRefresh'
import UserProfileDrawer from '@/components/UserProfileDrawer.vue'

const router = useRouter()
const route = useRoute()
const productFilterId = computed(() => {
  const id = Number(route.query.productId)
  return Number.isInteger(id) && id > 0 ? id : null
})
function clearProductFilter() { router.replace({ path: route.path, query: {} }) }
watch(productFilterId, () => { params.page = 1; load() })
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const params = reactive({ page: 1, pageSize: 10, keywords: '', status: '' })
const detailVisible = ref(false)
const selected = ref(null)
const profileVisible = ref(false), profileUserId = ref(null), profileName = ref('')
function openUserProfile(row) {
  profileUserId.value = row.user_id
  profileName.value = row.user_name || row.username
  profileVisible.value = true
}

let listRequestId = 0
async function load(silent = false) {
  const requestId = ++listRequestId
  if (silent !== true) loading.value = true
  try {
    const response = await listAfterSales({
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords || undefined,
      status: params.status || undefined,
      product_id: productFilterId.value || undefined
    })
    if (requestId !== listRequestId) return
    tableData.value = response.data?.list || []
    total.value = response.data?.total || 0
    if (selected.value) selected.value = tableData.value.find(item => item.id === selected.value.id) || selected.value
  } catch (error) {
    if (silent !== true) ElMessage.error(error?.message || '加载售后申请失败')
  } finally {
    if (requestId === listRequestId) loading.value = false
  }
}

function handleSearch() {
  params.page = 1
  load()
}

function openDetail(row, column) {
  if (column?.label === '操作') return
  selected.value = row
  detailVisible.value = true
}

function openConversation(row) {
  router.push({ path: '/manager/message-center', query: { afterSaleId: String(row.id) } })
}

onMounted(load)
useVisibleRefresh(() => load(true))
</script>

<style scoped>
.after-sales-card { min-width: 0; }
.after-sales-filter { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; color: var(--app-text-secondary); font-size: 13px; }
.user-profile-link { padding: 0; border: 0; background: transparent; cursor: pointer; text-align: left; font: inherit; }
.user-profile-link:hover strong { color: #159b83; text-decoration: underline; }
:deep(.el-table__body td:not(:last-child)) { cursor: pointer; }
.after-sales-actions { display: flex; width: 100%; align-items: center; justify-content: center; gap: 8px; white-space: nowrap; }
.after-sales-actions :deep(.el-badge) { display: inline-flex; align-items: center; }
.after-sales-actions :deep(.el-button) { min-width: 36px; margin: 0; padding: 4px 2px; }
.after-sales-user, .after-sales-reason { display: grid; gap: 4px; min-width: 0; }
.after-sales-user strong, .after-sales-reason strong { color: var(--app-text); font-weight: 500; }
.after-sales-user span, .after-sales-reason span { overflow: hidden; color: var(--app-text-secondary); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.after-sales-detail { display: grid; gap: 18px; }
.after-sales-detail__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 2px 0 16px; border-bottom: 1px solid var(--app-border); }
.after-sales-detail__heading { display: grid; gap: 6px; min-width: 0; }
.after-sales-detail__eyebrow, .after-sales-detail__order, .after-sales-detail__field > span, .after-sales-detail__note > span { color: var(--app-text-secondary); font-size: 13px; }
.after-sales-detail__heading > strong { color: var(--app-text); font-size: 17px; font-weight: 600; }
.after-sales-detail__order { overflow-wrap: anywhere; }
.after-sales-detail__section { display: grid; gap: 12px; }
.after-sales-detail__section h3 { margin: 0; color: var(--app-text); font-size: 14px; font-weight: 600; }
.after-sales-detail__grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.after-sales-detail__field, .after-sales-detail__note { display: grid; align-content: start; gap: 7px; min-width: 0; padding: 12px 14px; border: 1px solid var(--app-border); border-radius: 10px; background: var(--app-surface-muted, #f8faf9); }
.after-sales-detail__field--wide { grid-column: 1 / -1; }
.after-sales-detail__field strong { color: var(--app-text); font-size: 14px; font-weight: 500; line-height: 1.6; overflow-wrap: anywhere; }
.after-sales-detail__notes { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.after-sales-detail__notes h3 { grid-column: 1 / -1; }
.after-sales-detail__note p { margin: 0; color: var(--app-text); line-height: 1.65; white-space: pre-wrap; overflow-wrap: anywhere; }
@media (max-width: 640px) {
  .after-sales-detail__grid, .after-sales-detail__notes { grid-template-columns: minmax(0, 1fr); }
  .after-sales-detail__field--wide, .after-sales-detail__notes h3 { grid-column: auto; }
}
</style>
