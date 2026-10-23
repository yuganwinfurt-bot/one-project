<template>
  <div class="page-container mall-admin" v-loading="loading">
    <section class="content-card mall-heading">
      <div><p class="mall-eyebrow">COMMERCE OPERATIONS</p><h1>{{ title }}</h1><p>{{ description }}</p></div>
      <div class="mall-actions">
        <el-button v-if="meta.editable && resource !== 'catalog-products'" type="primary" :icon="Plus" @click="edit()">新增</el-button>
        <el-upload v-if="resource === 'storage'" :show-file-list="false" :http-request="upload"><el-button type="primary">上传文件</el-button></el-upload>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
    </section>

    <section v-if="isSettings" class="content-card mall-settings" :class="{ 'mall-settings--order': resource === 'settings-order' }">
      <el-alert v-if="meta.hint" :title="meta.hint" type="info" :closable="false" />
      <OrderSettingsForm v-if="resource === 'settings-order'" :fields="meta.fields" :model="form" :saving="saving" @save="saveSettings" @cancel="resetForm(savedSettings)" />
      <template v-else><MallFields :fields="meta.fields" :model="form" /><el-button type="primary" :loading="saving" @click="saveSettings">保存配置</el-button></template>
    </section>

    <template v-else>
      <section v-if="isStatistics" class="mall-summary">
        <article v-for="(value, label) in summary" :key="label" class="content-card"><span>{{ label }}</span><strong>{{ Number(value).toLocaleString('zh-CN', { maximumFractionDigits: 2 }) }}</strong></article>
      </section>
      <section class="content-card mall-content">
        <div v-if="resource !== 'regions'" class="mall-toolbar">
          <template v-if="isStatistics"><el-date-picker v-model="dateRange" type="daterange" value-format="YYYY-MM-DD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" @change="search" /></template>
          <template v-else><el-input v-model="keyword" placeholder="输入关键词查找" clearable style="width:260px" @keyup.enter="search" @clear="search" /><el-input-number v-if="memberResources.includes(resource)" v-model="userId" :min="1" :precision="0" :controls="false" placeholder="用户 ID" style="width:145px" /></template>
          <el-button type="primary" :icon="Search" @click="search">查找</el-button>
          <el-button :icon="Download" :disabled="!rows.length" @click="exportPage">导出当前页</el-button>
        </div>
        <el-alert v-if="resource === 'roles'" title="此角色控制商城新增运营模块的访问权限；管理员账号始终保留管理权限。" :closable="false" type="info" />
        <el-table v-if="resource === 'regions'" :data="rows" row-key="id" lazy :load="loadRegion" :tree-props="{ children:'children', hasChildren:'hasChildren' }" border>
          <el-table-column prop="name" label="区域名称" min-width="260" /><el-table-column label="区域类型"><template #default="{ row }">{{ ['','省','市','区县'][row.type] }}</template></el-table-column><el-table-column prop="code" label="区域编码" />
        </el-table>
        <el-table v-else :data="rows" border stripe empty-text="暂无记录" row-key="id" style="width:100%">
          <el-table-column v-for="column in meta.columns || []" :key="column.key" :label="column.label" :min-width="column.key.includes('time') || column.key.includes('_at') ? 175 : 130" show-overflow-tooltip>
            <template #default="{ row }"><el-tag v-if="column.key === 'enabled' || column.key === 'status'" :type="row.enabled === false || ['pending', 'expired', 0].includes(row.status) ? 'info' : 'success'">{{ display(row[column.key], column.key) }}</el-tag><span v-else>{{ display(row[column.key], column.key) }}</span></template>
          </el-table-column>
          <el-table-column v-if="hasActions" label="操作" fixed="right" width="180"><template #default="{ row }">
            <el-button v-if="meta.editable" link type="primary" @click="edit(row)">编辑</el-button>
            <el-button v-if="resource === 'feedback'" link type="primary" @click="reply(row)">{{ row.reply ? '更新回复' : '回复' }}</el-button>
            <el-button v-if="resource === 'members' && isAdmin" link :type="row.status ? 'danger' : 'success'" @click="toggleMember(row)">{{ row.status ? '禁用' : '启用' }}</el-button>
            <el-button v-if="resource === 'storage'" link type="primary" @click="openFile(row)">查看</el-button>
            <el-button v-if="meta.deletable" link type="danger" @click="remove(row)">删除</el-button>
          </template></el-table-column>
        </el-table>
        <el-pagination v-if="!isStatistics && resource !== 'regions'" v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50,100]" layout="total, sizes, prev, pager, next" @current-change="loadRows" @size-change="search" />
      </section>
    </template>

    <el-dialog v-model="dialog" :title="editingId ? '编辑记录' : '新增记录'" width="min(680px, 94vw)" :close-on-click-modal="false" destroy-on-close>
      <el-alert v-if="resource === 'coupons' && editingId" title="修改金额或有效期对新领取生效，已领取的优惠券保留领取时的规则；停用会停止所有券的使用。" type="info" :closable="false" style="margin-bottom:18px" />
      <MallFields :fields="meta.fields" :model="form" :options="meta.options" />
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, Download } from '@element-plus/icons-vue'
import MallFields from '@/components/MallFields.vue'
import OrderSettingsForm from '@/components/OrderSettingsForm.vue'
import { mallMeta, mallList, mallSave, mallDelete, mallSettings, saveMallSettings, mallStatistics, mallRegionChildren, downloadRows } from '@/api/mall'
import { uploadFileApi } from '@/api/file'
import request from '@/utils/request'
import { getUserInfo } from '@/utils/auth'

const route = useRoute()
const resource = computed(() => String(route.params.resource || ''))
const isSettings = computed(() => resource.value.startsWith('settings-'))
const isStatistics = computed(() => resource.value.startsWith('statistics-'))
const isAdmin = getUserInfo()?.role === 'admin'
const memberResources = ['members','addresses','favorites','footprints','search-history','feedback']
const meta = ref({}), rows = ref([]), total = ref(0), summary = ref({})
const page = ref(1), pageSize = ref(20), keyword = ref(''), userId = ref(), dateRange = ref(null)
const loading = ref(false), saving = ref(false), dialog = ref(false), editingId = ref(null)
const form = reactive({})
const savedSettings = ref({})
let generation = 0, listRequest = 0
const title = computed(() => meta.value.title || (resource.value === 'regions' ? '行政区域' : '商城运营'))
const description = computed(() => resource.value === 'regions' ? '省、市、区县分级查看；参考数据来源：litemall。' : isStatistics.value ? '按所选日期汇总；有效销售统计已支付、已发货和已完成的订单。' : isSettings.value ? '保存后应用于商城展示或后续下单，已有订单保留原金额。' : '查询和维护商城业务资料。')
const hasActions = computed(() => meta.value.editable || meta.value.deletable || ['feedback','storage'].includes(resource.value) || (resource.value === 'members' && isAdmin))
function resetForm(value = {}) {
  Object.keys(form).forEach(key => delete form[key])
  Object.assign(form, value)
}
async function load() {
  const current = ++generation, key = resource.value
  loading.value = true
  try {
    if (isSettings.value) {
      const res = await mallSettings(key.slice(9))
      if (current !== generation) return
      meta.value = res.data
      savedSettings.value = { ...res.data.values }
      resetForm(res.data.values)
    } else if (isStatistics.value) {
      await loadRows(current)
    } else if (key === 'regions') {
      const res = await mallRegionChildren()
      if (current !== generation) return
      meta.value = { title:'行政区域' }
      rows.value = res.data.list.map(region => ({ ...region, hasChildren: region.type < 3 }))
    } else {
      const res = await mallMeta(key)
      if (current !== generation) return
      meta.value = res.data
      await loadRows(current)
    }
  } catch { if (current === generation) rows.value = [] } finally { if (current === generation) loading.value = false }
}
async function loadRows(current = generation) {
  // Element Plus 事件会传入页码，使用当前代际防止切页后旧请求覆盖新模块。
  if (typeof current !== 'number' || current !== generation) current = generation
  const key = resource.value, requestId = ++listRequest
  loading.value = true
  try {
    const res = isStatistics.value
      ? await mallStatistics(key.slice(11), { start:dateRange.value?.[0], end:dateRange.value?.[1] })
      : await mallList(key, { page:page.value, page_size:pageSize.value, keyword:keyword.value.trim(), user_id:userId.value || undefined })
    if (current !== generation || key !== resource.value || requestId !== listRequest) return
    rows.value = res.data.list.map((row, index) => ({ ...row, id: row.id ?? index + 1 }))
    total.value = res.data.total || rows.value.length
    if (isStatistics.value) {
      meta.value = { title:{ users:'用户统计', orders:'订单统计', products:'商品统计' }[key.slice(11)], columns:res.data.columns }
      summary.value = res.data.summary
    }
  } finally { if (current === generation && requestId === listRequest) loading.value = false }
}
function search() { page.value = 1; loadRows().catch(() => {}) }
function edit(row = null) {
  const defaults = Object.fromEntries((meta.value.fields || []).map(f => [f.key, f.default ?? (['products','staff','permissions'].includes(f.type) ? [] : ['product','category','brand'].includes(f.type) ? null : ['number','money'].includes(f.type) ? 0 : f.type === 'switch' ? false : '')]))
  resetForm({ ...defaults, ...(row ? JSON.parse(JSON.stringify(row)) : {}) })
  editingId.value = row?.id || null
  dialog.value = true
}
async function save() {
  if (saving.value) return
  saving.value = true
  try {
    let payload
    if (resource.value === 'catalog-products') payload = { brand_id:form.brand_id || null, category_id:form.category_id || null }
    else payload = { name:form.name, enabled:form.enabled, sort_order:form.sort_order, data:Object.fromEntries(meta.value.fields.filter(f => !['name','enabled','sort_order'].includes(f.key)).map(f => [f.key, form[f.key] ?? null])) }
    await mallSave(resource.value, editingId.value, payload)
    dialog.value = false
    ElMessage.success('已保存')
    await load()
    window.dispatchEvent(new Event('mall-permissions-updated'))
  } catch {} finally { saving.value = false }
}
async function saveSettings() {
  if (saving.value) return
  saving.value = true
  try { const res = await saveMallSettings(resource.value.slice(9), { ...form }); savedSettings.value = { ...res.data }; ElMessage.success('配置已保存') } catch {} finally { saving.value = false }
}
async function remove(row) {
  try {
    await ElMessageBox.confirm(`确定删除“${row.name}”吗？`, '删除记录', { type:'warning' })
    await mallDelete(resource.value, row.id)
    ElMessage.success('已删除')
    if (rows.value.length === 1 && page.value > 1) page.value--
    await loadRows()
  } catch {}
}
async function reply(row) {
  try {
    const { value } = await ElMessageBox.prompt(row.content, '回复意见反馈', { inputType:'textarea', inputValue:row.reply, inputValidator:v => Boolean(v?.trim()) || '请输入回复' })
    await mallSave('feedback', row.id, { reply:value })
    ElMessage.success('回复已保存，用户可在意见反馈页查看')
    await loadRows()
  } catch {}
}
async function toggleMember(row) {
  try {
    await ElMessageBox.confirm(`确定${row.status ? '禁用' : '启用'}买家账号“${row.username}”吗？`, '账号状态', { type:'warning' })
    await request.put(`/api/mall/admin/members/${row.id}/status`, { status:row.status ? 0 : 1 })
    await loadRows()
  } catch {}
}
async function upload({ file, onSuccess, onError }) {
  try { const res = await uploadFileApi(file); onSuccess(res.data); await loadRows() } catch (error) { onError(error) }
}
function openFile(row) { window.open(row.url, '_blank', 'noopener,noreferrer') }
async function loadRegion(tree, _node, resolve) {
  try { const res = await mallRegionChildren(tree.id); resolve(res.data.list.map(r => ({ ...r, hasChildren:r.type < 3 }))) } catch { resolve([]) }
}
function display(value, key) {
  if (key === 'enabled' || key === 'is_default') return value ? '是' : '否'
  if (key === 'status') return ({ 0:'已禁用', 1:'正常', forming:'组团中', completed:'已成团', expired:'已到期取消', pending:'待回复', replied:'已回复' })[value] || value
  if (key === 'shelf_status') return value === 'on_sale' ? '在售' : '已下架'
  if (value == null || value === '') return '—'
  return typeof value === 'object' ? JSON.stringify(value) : value
}
function exportPage() { downloadRows(rows.value, meta.value.columns, title.value) }
watch(resource, () => { dialog.value = false; meta.value = {}; rows.value = []; keyword.value = ''; userId.value = undefined; page.value = 1; load() }, { immediate:true })
</script>

<style scoped>
.mall-admin { display:grid; gap:18px; }
.mall-heading { display:flex; justify-content:space-between; align-items:center; gap:20px; }
.mall-heading h1 { margin:3px 0 8px; color:#102237; font-size:23px; }
.mall-heading p { margin:0; color:#738495; font-size:13px; }
.mall-heading .mall-eyebrow { color:#159c80; font-size:10px; letter-spacing:2px; }
.mall-actions,.mall-toolbar { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
.mall-content { min-width:0; }
.mall-toolbar { margin-bottom:20px; }
.el-pagination { margin-top:22px; justify-content:flex-end; }
.mall-summary { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; }
.mall-summary article { display:grid; gap:12px; color:#748594; }
.mall-summary strong { font-size:27px; color:#102237; }
.mall-settings { max-width:820px; }
.mall-settings--order { max-width: none; }
.mall-settings .el-alert { margin-bottom:20px; }
@media(max-width:700px) { .mall-heading { align-items:flex-start; flex-direction:column; }.mall-summary { grid-template-columns:1fr; }.el-pagination { overflow:auto; justify-content:flex-start; } }
</style>
