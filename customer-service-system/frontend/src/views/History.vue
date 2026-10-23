<template>
  <div class="page-container history-page">
    <div class="content-card">
      <p class="history-purpose-note">运行历史记录每次分析的步骤、耗时和错误。需要保留业务结论时，可在对话中保存诊断报告。</p>
      <div v-if="unfinishedOnly" class="history-page__filter-bar">
        <span>筛选中：未完成（进行中 / 回答生成中 / 待确认）</span>
        <el-button link type="primary" @click="clearUnfinishedFilter">显示全部运行</el-button>
      </div>
      <el-table
        :data="tableData"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="tableHeaderStyle"
        @row-click="openDetail"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="question" label="问题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="route" label="路由" width="110">
          <template #default="{ row }">
            {{ routeLabel(row.route) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="140" sortable="custom" :sort-orders="sortOrders">
          <template #default="{ row }">
            <el-tag size="small" effect="light" round :type="statusTag(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="elapsed_ms" label="耗时(ms)" width="100" />
        <el-table-column prop="create_time" label="时间" width="200" sortable="custom" :sort-orders="sortOrders">
          <template #default="{ row }">
            <span class="time-text">{{ row.create_time }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="openDetail(row)">详情</el-button>
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

    <el-drawer v-model="drawerVisible" title="运行详情" size="480px">
      <template v-if="detail">
        <div class="history-page__detail-block">
          <div class="history-page__detail-label">问题</div>
          <div>{{ detail.question }}</div>
        </div>
        <div class="history-page__detail-block">
          <div class="history-page__detail-label">状态 / 路由 / 耗时</div>
          <div>
            {{ statusLabel(detail.status) }} · {{ routeLabel(detail.route) }} ·
            {{ detail.elapsed_ms ?? '-' }} ms
          </div>
        </div>
        <div class="history-page__detail-block" v-if="detail.answer_preview">
          <div class="history-page__detail-label">回答摘要（只留前 500 字，完整回答见对话页）</div>
          <div class="history-page__preview" v-html="renderMarkdown(detail.answer_preview)"></div>
        </div>
        <div class="history-page__detail-block" v-if="detail.error_message">
          <div class="history-page__detail-label">错误</div>
          <div>{{ detail.error_message }}</div>
        </div>
        <div class="history-page__detail-block" v-if="detail.pending_confirmation">
          <div class="history-page__detail-label">{{ detail.route === 'management' ? '确认后台业务操作' : '确认商品复核' }}</div>
          <p>{{ detail.pending_confirmation.message }}</p>
          <p>{{ detail.pending_confirmation.reason }}</p>
          <ul>
            <li v-for="(action, index) in detail.pending_confirmation.actions" :key="index">
              <strong>{{ action.title || action.type }}</strong>
              <div v-for="change in action.changes || []" :key="change.key">
                {{ change.label }}：{{ change.before }} → {{ change.after }}
              </div>
              <small v-if="action.notice">{{ action.notice }}</small>
            </li>
          </ul>
          <el-button :disabled="confirming" @click="handleConfirm(false)">取消</el-button>
          <el-button type="primary" :loading="confirming" @click="handleConfirm(true)">
            {{ detail.route === 'management' ? '确认执行操作' : '确认标记待复核' }}
          </el-button>
        </div>
        <div class="history-page__detail-block" v-else-if="detail.confirmation_expired">
          <el-alert
            type="warning"
            :closable="false"
            show-icon
            title="这条任务的确认会话已失效。请重新提问生成方案，并核对最新业务数据后再确认。"
          />
          <div v-if="detail.expired_actions?.length" class="history-page__expired-actions">
            <strong>原计划操作（仅供核对）</strong>
            <ul>
              <li v-for="(action, index) in detail.expired_actions" :key="index">
                <strong>{{ action.title || action.type }}</strong>
              <div v-for="change in action.changes || []" :key="change.key">
                {{ change.label }}：{{ change.before }} → {{ change.after }}
              </div>
              <small v-if="action.notice">{{ action.notice }}</small>
              </li>
            </ul>
          </div>
          <el-button type="primary" @click="retryAnalysis">重新发起分析</el-button>
        </div>
        <div class="history-page__detail-block">
          <div class="history-page__detail-label">步骤</div>
          <ul class="history-page__steps">
            <li v-for="step in detail.steps || []" :key="step.id">
              <span class="history-page__step-order">#{{ step.step_order }}</span>
              <span class="history-page__step-name">{{ step.step_name }}</span>
              <span>{{ step.summary }}</span>
              <span v-if="step.elapsed_ms != null" class="history-page__step-ms">
                {{ step.elapsed_ms }} ms
              </span>
              <!-- 结构化查询这一步记了当次 SQL，回看历史时能对照数据库复核 -->
              <pre v-if="step.detail?.sql" class="history-page__step-sql">{{
                step.detail.sql
              }}</pre>
            </li>
          </ul>
        </div>
        <div class="history-page__detail-block" v-if="detail.feedback">
          <div class="history-page__detail-label">反馈</div>
          <div>{{ detail.feedback.rating === 1 ? '点赞' : '点踩' }}</div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { getRunDetail, listRuns } from '@/api/observability'
import { confirmActions } from '@/api/chat'

const tableHeaderStyle = {
  backgroundColor: '#f8fafc',
  color: '#475569',
  fontWeight: 600
}
const sortOrders = ['ascending', 'descending']

/** 回答摘要是大模型输出的 Markdown，渲染后再展示；breaks 保住原本的换行 */
function renderMarkdown(text) {
  const html = marked.parse(text || '', { async: false, breaks: true })
  return DOMPurify.sanitize(html)
}

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const params = reactive({ page: 1, pageSize: 10 })
const sortBy = ref('')
const sortOrder = ref('asc')
const drawerVisible = ref(false)
const detail = ref(null)
const confirming = ref(false)
const router = useRouter()
const route = useRoute()
const unfinishedOnly = computed(() => route.query.unfinished === '1')
const onlyMine = computed(() => route.query.only_mine !== '0')

function routeLabel(route) {
  if (route === 'management') return '后台业务'
  if (route === 'structured') return '结构化'
  if (route === 'semantic') return '语义检索'
  if (route === 'conversation') return '模型对话'
  return route || '-'
}

function statusLabel(status) {
  const map = {
    running: '进行中',
    answering: '回答生成中',
    success: '成功',
    error: '失败',
    awaiting_confirm: '待确认',
    confirmation_expired: '确认已失效',
    cancelled: '已取消'
  }
  return map[status] || status || '-'
}

function statusTag(status) {
  const map = {
    success: 'success',
    error: 'danger',
    awaiting_confirm: 'warning',
    confirmation_expired: 'danger',
    cancelled: 'info',
    running: '',
    answering: ''
  }
  return map[status] || 'info'
}

async function load() {
  loading.value = true
  try {
    if (unfinishedOnly.value || sortBy.value) {
      // 读取全部分页后再筛选或排序，确保结果不局限于当前页。
      const allRuns = await fetchAllRuns()
      const visibleRuns = unfinishedOnly.value
        ? allRuns.filter((run) =>
            ['running', 'answering', 'awaiting_confirm', 'confirmation_expired'].includes(run.status)
          )
        : allRuns
      if (sortBy.value) visibleRuns.sort(compareRuns)
      total.value = visibleRuns.length
      const start = (params.page - 1) * params.pageSize
      tableData.value = visibleRuns.slice(start, start + params.pageSize)
    } else {
      const res = await listRuns({
        page: params.page,
        page_size: params.pageSize,
        only_mine: onlyMine.value
      })
      tableData.value = res.data?.list || []
      total.value = res.data?.total || 0
    }
  } finally {
    loading.value = false
  }
}

async function fetchAllRuns() {
  const pageSize = 50
  const first = await listRuns({ page: 1, page_size: pageSize, only_mine: onlyMine.value })
  const firstData = first.data || {}
  const allRuns = [...(firstData.list || [])]
  const pageCount = Math.ceil((firstData.total || 0) / pageSize)
  if (pageCount > 1) {
    const rest = await Promise.all(
      Array.from({ length: pageCount - 1 }, (_, index) =>
        listRuns({ page: index + 2, page_size: pageSize, only_mine: onlyMine.value })
      )
    )
    rest.forEach((res) => allRuns.push(...(res.data?.list || [])))
  }
  return allRuns
}

function compareRuns(a, b) {
  let comparison = 0
  if (sortBy.value === 'status') {
    const rank = {
      running: 0,
      answering: 0,
      awaiting_confirm: 1,
      confirmation_expired: 1,
      success: 2,
      error: 3,
      cancelled: 4
    }
    comparison = (rank[a.status] ?? 5) - (rank[b.status] ?? 5)
  } else if (sortBy.value === 'create_time') {
    comparison = new Date(a.create_time).getTime() - new Date(b.create_time).getTime()
  }
  if (sortOrder.value === 'desc') comparison *= -1
  return comparison || Number(b.id) - Number(a.id)
}

function handleSortChange({ prop, order }) {
  sortBy.value = order ? prop : ''
  sortOrder.value = order === 'descending' ? 'desc' : 'asc'
  params.page = 1
  load()
}

async function openDetail(row) {
  if (!row?.id) return
  const res = await getRunDetail(row.id)
  detail.value = res.data
  drawerVisible.value = true
}

async function handleConfirm(approved) {
  const task = detail.value?.pending_confirmation
  if (!task || confirming.value) return
  confirming.value = true
  try {
    const res = await confirmActions(task.thread_id, approved)
    ElMessage.success(res.data?.status_message || '任务已处理')
    await openDetail(detail.value)
    await load()
  } catch {
    // 业务失败由拦截器提示，保留当前任务，允许再次操作。
  } finally {
    confirming.value = false
  }
}

function retryAnalysis() {
  const question = detail.value?.question
  if (!question) return
  drawerVisible.value = false
  router.push({ path: '/manager/chat', query: { prefill: question } })
}

function clearUnfinishedFilter() {
  router.replace({ path: '/manager/history' })
}

watch(unfinishedOnly, () => {
  params.page = 1
  load()
})

watch(() => route.query.runId, (id) => {
  if (id) openDetail({ id: Number(id) })
}, { immediate: true })

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

.history-page__detail-block {
  margin-bottom: 16px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--app-text);
}

.history-page__filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  padding: 10px 14px;
  border: 1px solid #f3d39b;
  border-radius: var(--app-radius-sm);
  background: #fff8eb;
  color: #9a6700;
  font-size: 13px;
}

.history-page__detail-label {
  margin-bottom: 4px;
  font-weight: 600;
  font-size: 13px;
  color: var(--app-text-secondary);
}

.history-page__expired-actions {
  margin: 12px 0;
  font-size: 13px;
}

.history-page__preview {
  word-break: break-word;
  max-height: 220px;
  overflow-y: auto;
  padding: 8px 10px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #f8fafc;
}

/* 回答摘要是 Markdown：渲染后压掉默认间距，首尾不留空白 */
.history-page__preview :deep(p) {
  margin: 6px 0;
}

.history-page__preview :deep(p:first-child) {
  margin-top: 0;
}

.history-page__preview :deep(p:last-child) {
  margin-bottom: 0;
}

.history-page__preview :deep(ul),
.history-page__preview :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}

.history-page__preview :deep(li) {
  margin: 2px 0;
}

.history-page__preview :deep(h1),
.history-page__preview :deep(h2),
.history-page__preview :deep(h3),
.history-page__preview :deep(h4) {
  margin: 8px 0 4px;
  font-size: 14px;
}

.history-page__preview :deep(strong) {
  font-weight: 600;
}

.history-page__preview :deep(hr) {
  border: none;
  border-top: 1px dashed var(--app-border);
  margin: 8px 0;
}

.history-page__preview :deep(code) {
  padding: 1px 4px;
  border-radius: 4px;
  background: #eef2f7;
  font-size: 12px;
}

.history-page__steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.history-page__steps li {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 13px;
  line-height: 1.5;
}

.history-page__step-order {
  color: var(--app-text-secondary);
}

.history-page__step-name {
  font-weight: 600;
}

.history-page__step-sql {
  width: 100%;
  margin: 2px 0 4px;
  padding: 6px 8px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #f8fafc;
  font-family: Consolas, Menlo, monospace;
  font-size: 12px;
  line-height: 1.6;
  color: var(--app-text);
  white-space: pre-wrap;
  word-break: break-all;
}

.history-page__step-ms {
  color: var(--app-text-secondary);
  margin-left: auto;
}
.history-purpose-note {
  margin: 0 0 14px;
  font-size: 13px;
  color: var(--app-text-secondary);
}
</style>
