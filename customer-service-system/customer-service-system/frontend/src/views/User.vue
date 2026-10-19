<template>
  <div class="page-container">
    <div class="content-card">
      <div class="toolbar-row">
        <el-input
          class="search-input"
          placeholder="请输入账号或名称查询"
          v-model="params.keywords"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <div class="toolbar-spacer" />
        <el-button type="primary" :icon="Plus" @click="handleCreate">新增运营账号</el-button>
      </div>

      <el-alert
        title="管理员可管理运营账号和注册用户资料与密码；新增运营账号仅用于创建后台账号；管理员账号凭据仅服务器管理员可修改。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 12px"
      />

      <el-table
        :header-cell-style="tableHeaderStyle"
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="username" label="账号" align="center" />
        <el-table-column prop="name" label="名称" align="center" />
        <el-table-column prop="avatar" label="头像" width="90" align="center">
          <template #default="{ row }">
            <el-avatar class="brand-avatar" :size="40" :src="row.avatar || undefined">
              {{ (row.name || row.username || '用').slice(0, 1) }}
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" align="center" />
        <el-table-column prop="phone" label="手机号" align="center" />
        <el-table-column
          prop="role"
          label="角色"
          width="100"
          align="center"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <el-tag size="small" effect="light" round :type="roleTagType(row.role)">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="online"
          label="状态"
          width="100"
          align="center"
          sortable="custom"
          :sort-orders="sortOrders"
        >
          <template #default="{ row }">
            <el-tag size="small" effect="light" round :type="row.online ? 'success' : 'info'">
              {{ row.online ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center">
          <template #default="{ row }">
            <el-button
              v-if="userInfo?.role === 'admin' && row.role !== 'admin'"
              type="primary"
              link
              :loading="switchingUserId === row.id"
              :disabled="row.status !== 1 || (switchingUserId !== null && switchingUserId !== row.id)"
              :title="row.status !== 1 ? '已禁用账号不能登录' : '在新页面以此账号登录'"
              @click="handleLoginAs(row)"
            >
              登录
            </el-button>
            <el-button
              type="primary"
              link
              :disabled="row.role === 'admin' && serverAdminChecked && !isServerAdmin"
              :title="row.role === 'admin' && serverAdminChecked && !isServerAdmin ? '仅服务器管理员可编辑管理员账号' : ''"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <template v-if="row.role === 'user' || row.role === 'customer'">
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
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

    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? `编辑${roleLabel(form.role)}账号` : '新增运营账号'"
      width="520"
      align-center
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :rules="rules"
        :model="form"
        autocomplete="off"
        label-width="80px"
        style="width: 100%; padding-right: 16px; padding-top: 8px"
        v-loading="loading"
      >
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            type="password"
            show-password
            autocomplete="new-password"
            v-model="form.password"
            :placeholder="form.id ? '输入密码以重设；留空保持不变' : '请输入初始密码'"
          />
          <div v-if="form.id" class="user-avatar-hint">密码不会从服务器读取；输入新密码后点击“确定”才会重设，留空则保持不变。</div>
          <div v-if="!form.id || form.role === 'user'" class="user-avatar-hint">最早创建的两个启用运营账号会公开显示在登录页，账号和密码修改后同步更新。</div>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item v-if="form.id && isServerAdmin" label="角色" prop="role">
          <el-select v-model="form.role">
            <el-option label="运营" value="user" />
            <el-option label="用户" value="customer" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="头像">
          <div class="user-avatar-editor">
            <el-upload
              class="user-avatar-uploader"
              :http-request="handleAvatarUpload"
              :show-file-list="false"
              accept="image/jpeg,image/png,image/gif,image/webp"
              :before-upload="beforeAvatarUpload"
            >
              <el-avatar class="brand-avatar" :size="64" :src="form.avatar || undefined">
                {{ (form.name || form.username || '用').slice(0, 1) }}
              </el-avatar>
            </el-upload>
            <span class="user-avatar-hint">点击头像上传或更换，支持 JPG、PNG、GIF、WebP，最大 2MB。</span>
          </div>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号（可留空）" />
          <div style="font-size: 12px; color: #909399; line-height: 1.5; margin-top: 4px">
            仅检查大陆手机号格式；不会发送短信验证码或验证号码是否可接通。
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="formLoading" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
defineOptions({ name: 'User' })
import { Search, Plus } from '@element-plus/icons-vue'
import {
  createUserApi,
  deleteUserApi,
  getUserPageList,
  loginAsUserApi,
  updateManagedUserApi
} from '@/api/user'
import { uploadFileApi } from '@/api/file'
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUser } from '@/utils/user'
import { useRouter } from 'vue-router'

const router = useRouter()
const { userInfo, updateUser } = useUser()

const tableHeaderStyle = {
  backgroundColor: '#f8fafc',
  color: '#475569',
  fontWeight: 600
}
const sortOrders = ['ascending', 'descending']

const params = reactive({
  page: 1,
  pageSize: 10,
  keywords: ''
})
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const sortBy = ref('')
const sortOrder = ref('ascending')
const dialogVisible = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  username: '',
  password: '',
  name: '',
  role: 'user',
  email: '',
  phone: '',
  avatar: '',
  status: 1
})
const formLoading = ref(false)
const isServerAdmin = ref(false)
const serverAdminChecked = ref(false)
const switchingUserId = ref(null)
let onlineRefreshTimer = null

const beforeAvatarUpload = (file) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!imageTypes.includes(file.type)) {
    ElMessage.error('请选择 JPG、PNG、GIF 或 WebP 图片')
    return false
  }
  if (file.size / 1024 / 1024 > 2) {
    ElMessage.error('头像不能超过 2MB')
    return false
  }
  return true
}

const handleAvatarUpload = async ({ file }) => {
  try {
    const res = await uploadFileApi(file)
    if (res.code === 200 && res.data?.url) {
      form.avatar = res.data.url
      ElMessage.success('头像上传成功，保存用户后生效')
    }
  } catch {
    ElMessage.error('头像上传失败，请稍后重试')
  }
}

// 编辑时密码可留空；新增运营账号时必须设置初始密码。
const rules = computed(() => ({
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: form.id
    ? [
        {
          validator: (_rule, value, callback) => {
            if (!value || (value.length >= 6 && value.length <= 64)) callback()
            else callback(new Error('密码是 6-64 位；留空表示不修改'))
          },
          trigger: 'blur'
        }
      ]
    : [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 64, message: '密码是 6-64 位', trigger: 'blur' }
      ],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式错误', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误', trigger: 'blur' }]
}))

const resetForm = () => {
  Object.assign(form, {
    id: null,
    username: '',
    password: '',
    name: '',
    role: 'user',
    email: '',
    phone: '',
    avatar: '',
    status: 1
  })
}

const handleCreate = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  if (row.role === 'admin' && !isServerAdmin.value && !(await checkServerAdmin())) return
  resetForm()
  Object.assign(form, {
    id: row.id,
    username: row.username,
    name: row.name,
    role: row.role,
    email: row.email,
    phone: row.phone,
    avatar: row.avatar,
    status: row.status
  })
  dialogVisible.value = true
}

// 删除用户信息
const handleDelete = (row) => {
  ElMessageBox.confirm(`确认删除用户 [${row.username}] ？`, '确认删除', { type: 'warning' }).then(
    async () => {
      const res = await deleteUserApi(row.id)
      if (res.code === 200) {
        ElMessage.success('删除用户成功')
        load()
      }
    }
  )
}

// 保存用户
const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  formLoading.value = true
  try {
    let res
    if (form.id) {
      const { id, password, role, ...payload } = form
      if (isServerAdmin.value) payload.role = role
      res = await updateManagedUserApi(id, { ...payload, password: password || undefined })
    } else {
      res = await createUserApi(form)
    }
    if (res.code === 200) {
      dialogVisible.value = false
      const isCurrentUserDemoted =
        userInfo.value?.id === res.data?.id &&
        userInfo.value?.role === 'admin' &&
        res.data?.role === 'user'
      if (res.data?.id === userInfo.value?.id) updateUser(res.data)
      ElMessage.success(isCurrentUserDemoted ? '角色已改为运营' : '操作成功')
      if (isCurrentUserDemoted) {
        await router.push('/manager/home')
      } else {
        load()
      }
    }
  } finally {
    formLoading.value = false
  }
}

const checkServerAdmin = async () => {
  const url = new URL(window.location.origin)
  if (['localhost', '127.0.0.1'].includes(window.location.hostname)) {
    url.port = '8020'
    url.pathname = '/api/auth/status'
  } else {
    url.pathname = '/agent/api/auth/status'
  }
  try {
    const response = await fetch(url, { credentials: 'include', cache: 'no-store' })
    if (!response.ok) return false
    const result = await response.json()
    isServerAdmin.value = result.role === 'admin'
    return isServerAdmin.value
  } catch {
    isServerAdmin.value = false
    return false
  } finally {
    serverAdminChecked.value = true
  }
}

const fetchAllUsers = async () => {
  const pageSize = 100
  const first = await getUserPageList({
    page: 1,
    page_size: pageSize,
    keywords: params.keywords
  })
  const firstData = first.data || {}
  const users = firstData.list || []
  const pageCount = Math.ceil((firstData.total || 0) / pageSize)
  if (pageCount <= 1) return users

  const remainingPages = await Promise.all(
    Array.from({ length: pageCount - 1 }, (_, index) =>
      getUserPageList({
        page: index + 2,
        page_size: pageSize,
        keywords: params.keywords
      })
    )
  )
  return users.concat(...remainingPages.map((res) => res.data?.list || []))
}

const sortUsers = (users) => {
  const direction = sortOrder.value === 'ascending' ? 1 : -1
  return [...users].sort((a, b) => {
    if (sortBy.value === 'role') {
      // 按页面显示的角色名称排序：管理员、运营、用户。
      const roleRank = (user) => ({ admin: 0, user: 1, customer: 2 })[user.role] ?? 3
      return (roleRank(a) - roleRank(b)) * direction
    }
    if (sortBy.value === 'online') {
      // 在线状态按离线、在线排序；反向点击后顺序反转。
      return (Number(Boolean(a.online)) - Number(Boolean(b.online))) * direction
    }
    return 0
  })
}

function roleLabel(role) {
  return { admin: '管理员', user: '运营', customer: '用户' }[role] || '未知角色'
}

function roleTagType(role) {
  return { admin: 'danger', user: 'success', customer: 'info' }[role] || 'info'
}

const handleSortChange = ({ prop, order }) => {
  sortBy.value = order ? prop : ''
  sortOrder.value = order || 'ascending'
  params.page = 1
  load()
}

const waitForPopupMessage = (popup, expectedType, timeoutMs = 15000) =>
  new Promise((resolve, reject) => {
    const cleanup = () => {
      window.removeEventListener('message', handleMessage)
      window.clearTimeout(timeoutId)
    }
    const handleMessage = (event) => {
      if (event.origin !== window.location.origin || event.source !== popup) return
      if (event.data?.type === 'account-switch-error') {
        cleanup()
        reject(new Error(event.data.message || '账号切换失败'))
      } else if (event.data?.type === expectedType) {
        cleanup()
        resolve(event.data)
      }
    }
    const timeoutId = window.setTimeout(() => {
      cleanup()
      reject(new Error('新页面响应超时，请关闭后重试'))
    }, timeoutMs)
    window.addEventListener('message', handleMessage)
  })

const handleLoginAs = async (row) => {
  if (userInfo.value?.role !== 'admin' || row.role === 'admin') return
  if (row.status !== 1) {
    ElMessage.warning('该账号已禁用，无法登录')
    return
  }

  const switchRoute = router.resolve({ name: 'SwitchAccount' })
  const popup = window.open(switchRoute.href, '_blank')
  if (!popup) {
    ElMessage.error('浏览器拦截了新页面，请允许此站点打开弹出窗口后重试')
    return
  }

  switchingUserId.value = row.id
  try {
    await waitForPopupMessage(popup, 'account-switch-ready')
    const res = await loginAsUserApi(row.id)
    if (popup.closed) throw new Error('新页面已关闭，请重试')

    const completed = waitForPopupMessage(popup, 'account-switch-complete')
    popup.postMessage(
      { type: 'account-switch-session', data: res.data },
      window.location.origin
    )
    const result = await completed
    ElMessage.success(`已在新页面登录为 ${result.username}`)
  } catch (error) {
    if (!popup.closed) popup.close()
    if (!error?.code && !error?.response) {
      ElMessage.error(error?.message || '账号切换失败，请稍后重试')
    }
  } finally {
    switchingUserId.value = null
  }
}

// 加载分页数据；排序时先读取筛选结果的所有分页，再排序并切出当前页。
const load = async (showLoading = true) => {
  if (showLoading) loading.value = true
  try {
    if (sortBy.value) {
      const users = sortUsers(await fetchAllUsers())
      total.value = users.length
      const start = (params.page - 1) * params.pageSize
      tableData.value = users.slice(start, start + params.pageSize)
      return
    }
    const res = await getUserPageList({
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords
    })
    if (res.code === 200) {
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  } finally {
    if (showLoading) loading.value = false
  }
}

const handleSearch = async () => {
  params.page = 1
  load()
}

onMounted(() => {
  checkServerAdmin()
  load()
  onlineRefreshTimer = setInterval(() => {
    if (document.visibilityState === 'visible') load(false)
  }, 30000)
})

onUnmounted(() => {
  if (onlineRefreshTimer) {
    clearInterval(onlineRefreshTimer)
    onlineRefreshTimer = null
  }
})
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

.brand-avatar {
  background: #102237;
  color: #fff;
  font-weight: 600;
}

.user-avatar-editor {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-uploader {
  cursor: pointer;
}

.user-avatar-hint {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.6;
}
</style>
