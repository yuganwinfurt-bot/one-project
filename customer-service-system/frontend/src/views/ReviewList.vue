<template>
  <div class="page-container">
    <div class="content-card">
      <div class="toolbar-row">
        <el-input
          class="search-input"
          placeholder="按评价内容 / 商品名搜索"
          v-model="params.keywords"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-select
          v-model="params.rating"
          placeholder="全部评分"
          clearable
          style="width: 130px"
          @change="handleSearch"
        >
          <el-option v-for="rating in [5, 4, 3, 2, 1]" :key="rating" :label="`${rating} 分`" :value="rating" />
        </el-select>
        <el-select
          v-model="params.replyStatus"
          placeholder="全部回复状态"
          clearable
          style="width: 150px"
          @change="handleSearch"
        >
          <el-option label="已回复" value="replied" />
          <el-option label="未回复" value="unreplied" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      </div>

      <el-table
        :header-cell-style="tableHeaderStyle"
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="product_name" label="商品" min-width="200">
          <template #default="{ row }">
            <span class="review-product-cell__name" :title="row.product_name">
              {{ row.product_name || '未知商品' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="rating"
          label="评分"
          min-width="130"
          align="center"
          header-align="center"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="light"
              round
              :type="row.rating <= 2 ? 'danger' : row.rating >= 4 ? 'success' : 'warning'"
            >
              {{ row.rating }} 分
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评价内容" min-width="340" show-overflow-tooltip />
        <el-table-column prop="img" label="晒图" min-width="140" align="center" header-align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.img"
              class="review-thumb"
              :src="row.img"
              :alt="`${row.product_name}评价晒图`"
              title="点击查看晒图"
              :preview-src-list="[row.img]"
              :initial-index="0"
              preview-teleported
              hide-on-click-modal
              fit="cover"
            >
              <template #error>
                <div class="review-thumb__error">缺图</div>
              </template>
            </el-image>
            <span v-else class="muted">无</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="create_time"
          label="评价时间"
          width="220"
          align="center"
          header-align="center"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <span class="time-text">{{ row.create_time }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" header-align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.product_id"
              type="primary"
              link
              size="small"
              @click.stop="openProductPage(row)"
            >
              前往
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
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { listReviews } from '@/api/ecommerce'

const tableHeaderStyle = {
  backgroundColor: '#f8fafc',
  color: '#475569',
  fontWeight: 600
}
const sortOrders = ['ascending', 'descending']

const loading = ref(false)
const router = useRouter()
const tableData = ref([])
const total = ref(0)
const params = reactive({
  page: 1,
  pageSize: 10,
  keywords: '',
  rating: '',
  replyStatus: '',
  sortBy: '',
  sortOrder: 'asc'
})

async function load() {
  loading.value = true
  try {
    const filters = {
      keywords: params.keywords || undefined,
      rating: params.rating || undefined,
      has_reply: params.replyStatus === 'replied'
        ? true
        : params.replyStatus === 'unreplied'
          ? false
          : undefined
    }
    if (params.sortBy) {
      const pageSize = 100
      const first = await listReviews({ ...filters, page: 1, page_size: pageSize })
      const firstData = first.data || {}
      const allReviews = [...(firstData.list || [])]
      const pageCount = Math.ceil((firstData.total || 0) / pageSize)
      if (pageCount > 1) {
        const rest = await Promise.all(
          Array.from({ length: pageCount - 1 }, (_, index) =>
            listReviews({ ...filters, page: index + 2, page_size: pageSize })
          )
        )
        rest.forEach((res) => allReviews.push(...(res.data?.list || [])))
      }
      allReviews.sort(compareReviews)
      total.value = firstData.total || 0
      const start = (params.page - 1) * params.pageSize
      tableData.value = allReviews.slice(start, start + params.pageSize)
    } else {
      const res = await listReviews({
        ...filters,
        page: params.page,
        page_size: params.pageSize
      })
      tableData.value = res.data?.list || []
      total.value = res.data?.total || 0
    }
  } finally {
    loading.value = false
  }
}

function compareReviews(a, b) {
  const comparison = params.sortBy === 'rating'
    ? Number(a.rating) - Number(b.rating)
    : new Date(a.create_time).getTime() - new Date(b.create_time).getTime()
  const ordered = params.sortOrder === 'desc' ? -comparison : comparison
  return ordered || Number(b.id) - Number(a.id)
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

function openProductPage(row) {
  if (!row?.product_id) return
  router.push({
    name: 'StorefrontProductDetail',
    params: { id: row.product_id },
    query: { from: 'reviews', review_id: row.id }
  })
}

onMounted(load)
</script>

<style scoped>
:deep(.el-table__header-wrapper .cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  white-space: nowrap;
}

:deep(.el-table__header-wrapper .caret-wrapper) {
  flex: 0 0 auto;
  margin-left: 0;
}

.review-product-cell__name {
  display: block;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.muted {
  color: var(--app-text-secondary);
  font-size: 13px;
}

.review-thumb {
  width: 52px;
  height: 52px;
  border-radius: 4px;
  cursor: pointer;
}

.review-thumb__error {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--app-text-secondary);
  background: #eef3f0;
  border-radius: 4px;
}
</style>
