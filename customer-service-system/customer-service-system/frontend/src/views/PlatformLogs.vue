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
        style="width: 100%"
      >
        <el-table-column label="序号" width="76" align="center">
          <template #default="{ row }">{{ serialNumber(row) }}</template>
        </el-table-column>
        <el-table-column prop="actor_username" label="账号" min-width="120" show-overflow-tooltip />
        <el-table-column prop="actor_name" label="名称" min-width="100" show-overflow-tooltip />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleType(row.actor_role)" effect="light" round>
              {{ roleLabel(row.actor_role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="时间" min-width="180" />
        <el-table-column prop="operation" label="修改内容" min-width="270" show-overflow-tooltip>
          <template #default="{ row }">
            <span :class="{ 'platform-log-operation--rollback': row.rollback_of_id }">
              {{ row.operation }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="before_value" label="修改前" min-width="190" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="platform-log-value">{{ row.before_value || '—' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="after_value" label="修改后" min-width="190" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="platform-log-value">{{ row.after_value || '—' }}</div>
          </template>
        </el-table-column>
        <el-table-column v-if="isAdmin" label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.can_rollback"
              type="danger"
              link
              @click="rollback(row)"
            >回退</el-button>
            <el-tag v-else-if="row.rolled_back_at" type="info" effect="plain">已回退</el-tag>
            <span v-else>—</span>
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
const isAdmin = getUserInfo()?.role === 'admin'

function serialNumber(row) {
  return row.id
}

function rowClassName({ row }) {
  return row.rolled_back_at ? 'is-rolled-back' : ''
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
  width: min(380px, 48vw);
}

.platform-logs-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.platform-log-value {
  white-space: pre-line;
  overflow-wrap: anywhere;
}

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
