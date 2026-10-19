<template>
  <div class="page-container">
    <div class="content-card">
      <p class="report-purpose-note">诊断报告保存分析结论和证据；预警仅提醒新的风险变化。普通查询可在对话中按需保存为报告。</p>
      <div class="toolbar-row">
        <el-input
          class="search-input"
          :placeholder="isReportTab ? '按问题 / 摘要 / 商品搜索' : '按标题 / 内容 / 商品搜索'"
          v-model="params.keywords"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button v-if="!isReportTab" :disabled="reading || !alertUnread" @click="handleReadAll">
          全部标记已读
        </el-button>
      </div>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="诊断报告" name="reports" />
        <el-tab-pane :label="alertTabLabel" name="alerts" />
      </el-tabs>

      <!-- 诊断报告 -->
      <el-table
        v-if="isReportTab"
        class="report-list-table"
        :header-cell-style="tableHeaderStyle"
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        @row-click="openDetail"
      >
        <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="product_name" label="关联商品" width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.product_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="risk_level" label="诊断风险" width="90">
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="light"
              round
              :type="row.risk_level === 'high' ? 'danger' : 'success'"
            >
              {{ row.risk_level === 'high' ? '高' : '低' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="evidence_count" label="证据数" width="80" />
        <el-table-column prop="summary" label="摘要" min-width="220" show-overflow-tooltip />
        <el-table-column prop="create_time" label="生成时间" width="170" />
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.product_id"
              type="primary"
              link
              @click.stop="goToProduct(row)"
            >
              前往
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 预警通知 -->
      <el-table
        v-else
        class="report-list-table"
        :header-cell-style="tableHeaderStyle"
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        @row-click="openDetail"
      >
        <el-table-column prop="level" label="级别" width="90">
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="light"
              round
              :type="row.level === 'critical' ? 'danger' : 'warning'"
            >
              {{ row.level === 'critical' ? '严重' : '提醒' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" width="160" show-overflow-tooltip />
        <el-table-column prop="content" label="内容" min-width="240" show-overflow-tooltip />
        <el-table-column prop="product_name" label="关联商品" width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.product_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="create_time" label="触发时间" width="170" />
        <el-table-column prop="is_read" label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" effect="light" round :type="row.is_read ? 'info' : 'danger'">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.product_id"
              type="primary"
              link
              @click.stop="goToProduct(row)"
            >
              前往
            </el-button>
            <el-button
              v-if="!row.is_read"
              type="primary"
              link
              :loading="reading"
              @click.stop="handleReadOne(row)"
            >
              标为已读
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

    <!-- 详情抽屉：报告正文 / 预警内容 -->
    <el-drawer
      v-model="drawerVisible"
      :title="isReportTab ? '诊断报告详情' : '预警通知详情'"
      size="480px"
    >
      <div v-if="detail" v-loading="detailLoading" class="report-detail">
        <template v-if="isReportTab">
          <div class="report-detail__label">用户问题</div>
          <div class="report-detail__value">{{ detail.question }}</div>
          <div class="report-detail__label">关联商品</div>
          <div class="report-detail__value">
            {{ detail.product_name || '-' }}
          </div>
          <div class="report-detail__label">诊断风险 / 查询路由</div>
          <div class="report-detail__value">
            {{ detail.risk_level === 'high' ? '较高风险信号' : '常规分析' }} ·
            {{ detail.route || '-' }}
          </div>
          <el-alert
            v-if="detail.risk_level === 'high'"
            class="report-detail__confirm-note"
            type="info"
            :closable="false"
            show-icon
            title="报告保存分析结论及证据，预警负责风险提醒；修改商品复核状态需要单独确认。"
          />
          <div class="report-detail__label">证据条数</div>
          <div class="report-detail__value">{{ detail.evidence_count }}</div>
          <div class="report-detail__label">证据明细</div>
          <el-alert
            v-if="detail.evidence_load_failed"
            type="error"
            :closable="false"
            show-icon
            :title="detail.evidence_endpoint_missing
              ? '后端尚未加载证据详情接口，请重启后端并刷新页面。'
              : '证据明细读取失败，请关闭后重新打开详情重试。'"
          />
          <template v-else-if="detail.evidence === null || detail.evidence === undefined">
            <el-alert
              type="info"
              :closable="false"
              show-icon
              title="这是一条旧报告，生成时只保存了证据数量，没有保存证据原文，因此无法在此恢复明细。"
            />
          </template>
          <el-empty
            v-else-if="detail.evidence.length === 0"
            description="本次分析没有可展示的证据明细"
            :image-size="56"
          />
          <ul v-else class="report-detail__evidence-list">
            <li v-for="(item, index) in detail.evidence" :key="index">
              <div class="report-detail__evidence-head">
                <strong>{{ item.product_name || item.product_id || `证据 ${index + 1}` }}</strong>
                <el-tag v-if="item.rating != null" size="small" effect="light" round>
                  {{ item.rating }} 分
                </el-tag>
                <el-tag size="small" effect="light" round type="info">
                  {{ evidenceSourceLabel(item) }}
                </el-tag>
              </div>
              <p v-if="item.content" class="report-detail__evidence-content">{{ item.content }}</p>
              <p v-if="item.image_caption" class="report-detail__evidence-caption">
                晒图内容：{{ item.image_caption }}
              </p>
              <div v-if="evidenceFields(item).length" class="report-detail__evidence-fields">
                <div v-for="([key, value]) in evidenceFields(item)" :key="key">
                  <span>{{ key }}</span>{{ formatEvidenceValue(value) }}
                </div>
              </div>
            </li>
          </ul>
          <div class="report-detail__label">报告正文</div>
          <div class="report-detail__body" v-html="renderReport(detail.summary)"></div>
          <el-button v-if="detail.source_run_id" link type="primary" @click="router.push({ path: '/manager/history', query: { runId: detail.source_run_id } })">
            查看本次分析的运行过程
          </el-button>
        </template>
        <template v-else>
          <div class="report-detail__label">标题</div>
          <div class="report-detail__value">{{ detail.title }}</div>
          <div class="report-detail__label">级别</div>
          <div class="report-detail__value">
            {{ detail.level === 'critical' ? '严重' : '提醒' }}
          </div>
          <div class="report-detail__label">关联商品</div>
          <div class="report-detail__value">
            {{ detail.product_name || '-' }}
          </div>
          <div class="report-detail__label">预警内容</div>
          <pre class="report-detail__pre">{{ detail.content }}</pre>
          <el-button v-if="detail.report_id" link type="primary" @click="router.push({ path: '/manager/reports', query: { tab: 'reports', reportId: detail.report_id } })">
            查看关联诊断报告
          </el-button>
        </template>
        <div class="report-detail__label">{{ isReportTab ? '生成时间' : '触发时间' }}</div>
        <div class="report-detail__value">{{ detail.create_time }}</div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import {
  getReportDetail,
  listAlerts,
  listReports,
  markAlertRead,
  markAllAlertsRead
} from '@/api/ecommerce'
import { useAlertUnread } from '@/composables/useAlertUnread'

const tableHeaderStyle = {
  backgroundColor: '#f8fafc',
  color: '#475569',
  fontWeight: 600
}

function renderReport(text) {
  return DOMPurify.sanitize(marked.parse(text || '', { async: false, breaks: true }))
}

const route = useRoute()
const router = useRouter()
// 顶栏铃铛会带着 ?tab=alerts 跳进来，直接落到预警页签
const activeTab = ref(route.query.tab === 'alerts' ? 'alerts' : 'reports')
const isReportTab = computed(() => activeTab.value === 'reports')
const loading = ref(false)
const reading = ref(false)
const tableData = ref([])
const total = ref(0)
const drawerVisible = ref(false)
const detail = ref(null)
const detailLoading = ref(false)
const params = reactive({ page: 1, pageSize: 10, keywords: '' })
const pendingAlertReads = new Map()

// 未读数是全局统计（顶栏铃铛共用一个数据源），不跟着页签和分页走：
// 否则切到「诊断报告」页签时看不到有没有未读预警
const { unread: alertUnread, refresh: refreshAlertUnread } = useAlertUnread()

const alertTabLabel = computed(() =>
  alertUnread.value ? `预警通知（${alertUnread.value} 未读）` : '预警通知'
)

async function load() {
  loading.value = true
  try {
    const query = {
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords || undefined
    }
    const res = isReportTab.value ? await listReports(query) : await listAlerts(query)
    tableData.value = res.data?.list || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

function handleTabChange() {
  params.page = 1
  params.keywords = ''
  tableData.value = []
  load()
}

// 已经停在诊断报告页签时，铃铛跳过来只变 query，需要手动切页签
watch(
  () => route.query.tab,
  (tab) => {
    const next = tab === 'alerts' ? 'alerts' : 'reports'
    if (next === activeTab.value) return
    activeTab.value = next
    handleTabChange()
  }
)

watch(
  () => route.query.reportId,
  (reportId) => {
    if (!reportId) return
    activeTab.value = 'reports'
    openDetail({ id: Number(reportId) })
  },
  { immediate: true }
)

function handleSearch() {
  params.page = 1
  load()
}

async function handleReadOne(row) {
  if (!row?.id || reading.value) return
  reading.value = true
  try {
    await ensureAlertRead(row)
    ElMessage.success('已标记为已读')
  } finally {
    reading.value = false
  }
}

async function ensureAlertRead(row) {
  if (!row?.id || row.is_read) return
  if (pendingAlertReads.has(row.id)) return pendingAlertReads.get(row.id)
  const request = markAlertRead(row.id)
    .then(async () => {
      row.is_read = 1
      if (!isReportTab.value) {
        const visibleRow = tableData.value.find((item) => item.id === row.id)
        if (visibleRow) visibleRow.is_read = 1
        if (detail.value?.id === row.id) detail.value.is_read = 1
      }
      await refreshAlertUnread({ force: true })
    })
    .finally(() => pendingAlertReads.delete(row.id))
  pendingAlertReads.set(row.id, request)
  return request
}

async function handleReadAll() {
  if (reading.value) return
  reading.value = true
  try {
    const res = await markAllAlertsRead()
    ElMessage.success(`已标记 ${res.data?.updated ?? 0} 条为已读`)
    await Promise.all([load(), refreshAlertUnread({ force: true })])
  } finally {
    reading.value = false
  }
}

async function openDetail(row) {
  detail.value = row
  drawerVisible.value = true
  if (!isReportTab.value) {
    try {
      await ensureAlertRead(row)
    } catch {
      // 请求拦截器已提示失败，保留详情以便继续查看。
    }
    return
  }
  if (!row?.id) return
  detailLoading.value = true
  try {
    const res = await getReportDetail(row.id)
    detail.value = res.data || row
  } catch (error) {
    const endpointMissing = error.response?.status === 404
    detail.value = {
      ...row,
      evidence_load_failed: true,
      evidence_endpoint_missing: endpointMissing
    }
    ElMessage.error(
      endpointMissing
        ? '后端尚未加载证据详情接口，请重启后端并刷新页面'
        : '证据明细加载失败，请稍后重试'
    )
  } finally {
    detailLoading.value = false
  }
}

async function goToProduct(row) {
  if (!row?.product_id) return
  if (!isReportTab.value) {
    try {
      await ensureAlertRead(row)
    } catch {
      // 已读写入失败时仍允许前往商品，请求拦截器会提示失败。
    }
  }
  router.push({ name: 'ProductDetail', params: { id: row.product_id } })
}

function evidenceSourceLabel(item) {
  const sources = item.sources || [item.source].filter(Boolean)
  if (sources.includes('structured') && sources.includes('semantic')) return '结构化 + 语义'
  if (sources.includes('semantic')) return '语义检索'
  if (sources.includes('structured')) return '数据库'
  return '来源未知'
}

function evidenceFields(item) {
  const hidden = new Set([
    'id',
    'source',
    'sources',
    'product_id',
    'product_name',
    'rating',
    'content',
    'image_caption',
    'distance'
  ])
  return Object.entries(item || {}).filter(([key, value]) => !hidden.has(key) && value != null && value !== '')
}

function formatEvidenceValue(value) {
  return typeof value === 'object' ? JSON.stringify(value) : String(value)
}

onMounted(() => {
  // 未读数进页面就取，和当前停在哪个页签无关
  refreshAlertUnread()
  load()
})
</script>

<style scoped>
.report-list-table :deep(.el-table__row) {
  cursor: pointer;
}

.report-detail__label {
  margin: 14px 0 4px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.report-detail__value {
  font-size: 14px;
  line-height: 1.6;
  color: var(--app-text);
  word-break: break-word;
}

.report-detail__pre {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #f8fafc;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.report-detail__confirm-note {
  margin: 12px 0 4px;
}

.report-detail__evidence-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.report-detail__evidence-list > li {
  padding: 11px 12px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: #f8fafc;
}

.report-detail__evidence-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.report-detail__evidence-content,
.report-detail__evidence-caption {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}

.report-detail__evidence-caption {
  color: var(--app-text-secondary);
}

.report-detail__evidence-fields {
  display: grid;
  gap: 5px;
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.5;
  word-break: break-word;
}

.report-detail__evidence-fields span {
  display: inline-block;
  margin-right: 6px;
  color: var(--app-text-secondary);
}
.report-purpose-note {
  margin: 0 0 14px;
  font-size: 13px;
  color: var(--app-text-secondary);
}
.report-detail__body {
  overflow-wrap: anywhere;
  overflow-x: auto;
  font-size: 14px;
  line-height: 1.75;
}
.report-detail__body :deep(table) { width: 100%; border-collapse: collapse; }
.report-detail__body :deep(th), .report-detail__body :deep(td) { padding: 6px; border: 1px solid var(--app-border); }
</style>
