<template>
  <div class="page-container">
    <div class="content-card">
      <div class="toolbar-row">
        <el-input v-model="params.keywords" class="search-input" placeholder="按订单号 / 商品 / 买家 / 原因搜索" clearable @keyup.enter="handleSearch" @clear="handleSearch" />
        <el-select v-model="params.status" placeholder="全部状态" clearable style="width: 150px" @change="handleSearch">
          <el-option label="待审核" value="pending" />
          <el-option label="处理中" value="approved" />
          <el-option label="已拒绝" value="rejected" />
          <el-option label="已完成" value="completed" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
        <el-tag v-if="productId" closable @close="clearProductFilter">{{ route.query.productName || `商品 #${productId}` }}</el-tag>
      </div>

      <el-table :data="tableData" :header-cell-style="tableHeaderStyle" v-loading="loading" style="width: 100%" empty-text="暂无售后工单">
        <el-table-column prop="order_no" label="订单号 / 咨询编号" min-width="200" show-overflow-tooltip />
        <el-table-column prop="product_name" label="商品" min-width="180" show-overflow-tooltip />
        <el-table-column label="申请用户" min-width="110">
          <template #default="{ row }">{{ row.user_name || row.username }}</template>
        </el-table-column>
        <el-table-column label="售后类型" width="120" align="center">
          <template #default="{ row }"><el-tag size="small" effect="light" round :type="serviceTypeTone(row.service_type)">{{ row.service_type === 'consultation' ? '客服咨询' : serviceTypeLabel(row.service_type) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="reason" label="申请原因" min-width="180" show-overflow-tooltip />
        <el-table-column label="状态" min-width="160" align="center">
          <template #default="{ row }"><el-tag size="small" effect="light" round :type="applicationStatusTone(row.status)">{{ row.handling_mode === 'human_requested' ? '申请人工 · 待接待' : row.handling_mode === 'human' && !row.conversation_closed ? '人工接待中' : row.record_type === 'consultation' ? (row.conversation_closed ? '咨询已结束' : 'AI接待中') : staffApplicationStatusLabel(row) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="create_time" label="申请时间" width="180" align="center" />
        <el-table-column label="操作" width="90" align="center" fixed="right">
          <template #default="{ row }"><el-button type="primary" link size="small" @click.stop="openSupportTickets(row.record_type === 'consultation' ? { supportConversationId: row.support_conversation_id } : { afterSaleId: row.id })">前往</el-button></template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
        <el-pagination v-model:current-page="params.page" v-model:page-size="params.pageSize" :total="total" background small layout="total, prev, pager, next" @current-change="load" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { listSupportTickets } from '@/api/ecommerce'
import { applicationStatusTone, serviceTypeLabel, serviceTypeTone, staffApplicationStatusLabel } from '@/utils/afterSale'
import { openSupportTickets } from '@/utils/supportPortal'

const route = useRoute()
const router = useRouter()
const tableHeaderStyle = { backgroundColor: '#f8fafc', color: '#475569', fontWeight: 600 }
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const params = reactive({ page: 1, pageSize: 10, keywords: '', status: '' })
const productId = computed(() => Number(route.query.productId) || undefined)
let requestId = 0

async function load() {
  const currentRequest = ++requestId
  loading.value = true
  try {
    const response = await listSupportTickets({ page: params.page, page_size: params.pageSize, keywords: params.keywords || undefined, status: params.status || undefined, product_id: productId.value })
    if (currentRequest !== requestId) return
    const data = response.data || {}
    tableData.value = data.list || []
    total.value = data.total || 0
    const lastPage = Math.max(1, Math.ceil(total.value / params.pageSize))
    if (params.page > lastPage) { params.page = lastPage; await load() }
  } catch (error) {
    if (currentRequest === requestId) ElMessage.error(error?.message || '加载售后工单失败')
  } finally {
    if (currentRequest === requestId) loading.value = false
  }
}

function handleSearch() { params.page = 1; load() }
function clearProductFilter() {
  const query = { ...route.query }
  delete query.productId
  delete query.productName
  router.replace({ path: route.path, query })
}
watch(productId, handleSearch)
watch(() => route.query.afterSaleId, (id) => { if (Number(id) > 0) openSupportTickets({ afterSaleId: id }) })
onMounted(() => {
  if (Number(route.query.afterSaleId) > 0) openSupportTickets({ afterSaleId: route.query.afterSaleId })
  else load()
})
</script>

<style scoped>
:deep(.el-table__header-wrapper .cell) { display: flex; align-items: center; justify-content: center; gap: 4px; white-space: nowrap; }
</style>
