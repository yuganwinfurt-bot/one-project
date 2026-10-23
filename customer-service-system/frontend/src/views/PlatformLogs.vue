<template>
  <div class="page-container platform-logs-page">
    <section class="content-card">
      <div class="platform-logs-toolbar">
        <el-input
          v-model="keywords"
          class="platform-logs-search"
          clearable
          placeholder="搜索账号、名称、商品或修改内容"
          @keyup.enter="searchLogs"
          @clear="searchLogs"
        />
        <el-button type="primary" :icon="Search" @click="searchLogs">查询</el-button>
        <el-button :icon="Refresh" :loading="loading" @click="loadLogs">刷新</el-button>
      </div>

      <el-table
        :data="rows"
        v-loading="loading"
        row-key="id"
        :row-class-name="rowClassName"
        empty-text="暂无平台操作记录"
        table-layout="fixed"
        style="width: 100%"
      >
        <el-table-column label="序号" width="62" align="center">
          <template #default="{ row }">{{ serialNumber(row) }}</template>
        </el-table-column>
        <el-table-column prop="actor_username" label="账号" width="82" show-overflow-tooltip />
        <el-table-column prop="actor_name" label="名称" width="76" show-overflow-tooltip />
        <el-table-column label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="roleType(row.actor_role)" effect="light" round>
              {{ roleLabel(row.actor_role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="时间" width="160" show-overflow-tooltip />
        <el-table-column prop="operation" label="修改内容" min-width="166" show-overflow-tooltip>
          <template #default="{ row }">
            <span :class="{ 'platform-log-operation--rollback': row.rollback_of_id }">
              {{ row.operation }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="before_value" label="修改前" min-width="150">
          <template #default="{ row }">
            <div class="platform-log-cell">
              <span class="platform-log-preview">{{ previewValue(row.before_value) }}</span>
              <el-button v-if="row.before_value" link type="primary" @click="showValueDetail(row, 'before')">详情</el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="after_value" label="修改后" min-width="160">
          <template #default="{ row }">
            <div class="platform-log-cell">
              <span class="platform-log-preview">{{ previewValue(row.after_value) }}</span>
              <el-button v-if="row.after_value" link type="primary" @click="showValueDetail(row, 'after')">详情</el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column v-if="canRollbackLogs" label="操作" width="92" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.can_rollback"
              type="danger"
              link
              @click="rollback(row)"
            >回退</el-button>
            <el-tag v-else-if="row.rolled_back_at" type="info" effect="plain">已回退</el-tag>
            <el-tooltip v-else-if="isAiSummary(row)" content="这是 AI 执行摘要；请在对应的商品或配置变更记录中回退实际修改。" placement="top">
              <span class="platform-log-summary-hint">摘要</span>
            </el-tooltip>
            <el-tooltip v-else content="该条历史记录没有保存回退快照，无法安全还原。新发生的后台配置修改会保存快照。" placement="top">
              <span>—</span>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total" class="platform-logs-pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          background
          layout="total, prev, pager, next"
          @current-change="loadLogs"
        />
      </div>
    </section>

    <el-dialog v-model="detailDialogVisible" :title="detailDialogTitle" width="min(720px, 94vw)">
      <pre class="platform-log-detail">{{ detailDialogContent }}</pre>
      <template #footer><el-button type="primary" @click="detailDialogVisible = false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { listPlatformLogs, rollbackPlatformLog } from '@/api/platformLogs'
import { getUserInfo } from '@/utils/auth'

defineOptions({ name: 'PlatformLogs' })

const rows = ref([])
const keywords = ref('')
const page = ref(1)
const pageSize = 10
const total = ref(0)
const loading = ref(false)
const canRollbackLogs = ['admin', 'user'].includes(getUserInfo()?.role)
const detailDialogVisible = ref(false)
const detailDialogTitle = ref('日志详情')
const detailDialogContent = ref('')

function serialNumber(row) {
  return row.id
}

function rowClassName({ row }) {
  return row.rolled_back_at ? 'is-rolled-back' : ''
}

function previewValue(value) {
  if (!value) return '—'
  const normalized = String(value).replace(/\s+/g, ' ').trim()
  return normalized.length > 72 ? `${normalized.slice(0, 72)}…` : normalized
}

function showValueDetail(row, key) {
  detailDialogTitle.value = `${serialNumber(row)} · ${key === 'before' ? '修改前' : '修改后'}`
  detailDialogContent.value = row[key === 'before' ? 'before_value' : 'after_value'] || '—'
  detailDialogVisible.value = true
}

function isAiSummary(row) {
  return String(row.operation || '').includes('AI 后台操作')
}

async function rollback(row) {
  const number = serialNumber(row)
  try {
    await ElMessageBox.confirm(
      `将撤销序号 ${number} 对应的修改，并新增一条回退日志。`,
      '确认回退',
      {
        confirmButtonText: '确认回退',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await rollbackPlatformLog(row.id)
    ElMessage.success(`已回退序号 ${number}`)
    await loadLogs()
  } catch (error) {
    // Axios 拦截器已显示接口错误，避免页面再弹一次相同错误。
    if (error !== 'cancel' && error !== 'close' && !error?.response && error?.code == null) {
      ElMessage.error(error?.message || '回退失败')
    }
  }
}

async function loadLogs() {
  loading.value = true
  try {
    const response = await listPlatformLogs({
      page: page.value,
      page_size: pageSize,
      keywords: keywords.value.trim() || undefined
    })
    rows.value = response.data?.list || []
    total.value = response.data?.total || 0
  } catch (error) {
    ElMessage.error(error?.message || '平台日志加载失败')
  } finally {
    loading.value = false
  }
}

function searchLogs() {
  page.value = 1
  loadLogs()
}

function roleLabel(role) {
  return { admin: '管理员', user: '运营', customer: '用户' }[role] || role || '未知'
}

function roleType(role) {
  return role === 'admin' ? 'danger' : 'success'
}

onMounted(loadLogs)
</script>

<style scoped>
.platform-logs-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.platform-logs-search {
  width: min(340px, 42vw);
}

.platform-logs-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.platform-log-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}

.platform-log-preview {
  display: block;
  min-width: 0;
  overflow: hidden;
  color: #586d80;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.platform-log-summary-hint {
  color: #8c97a3;
  cursor: help;
  font-size: 12px;
}

.platform-log-detail {
  max-height: min(65vh, 620px);
  overflow: auto;
  margin: 0;
  padding: 14px;
  border-radius: 8px;
  background: #f5f7fa;
  color: #43566a;
  font: inherit;
  line-height: 1.65;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

:deep(.el-table .cell) { overflow: hidden; }

.platform-log-operation--rollback {
  color: #e5484d;
  font-weight: 600;
}

:deep(.el-table__row.is-rolled-back .cell) {
  color: #9aa2ac;
  text-decoration: line-through;
}

@media (max-width: 680px) {
  .platform-logs-toolbar {
    flex-wrap: wrap;
  }

  .platform-logs-search {
    width: 100%;
  }

  .platform-logs-pagination {
    overflow-x: auto;
  }
}
</style>
