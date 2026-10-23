<template>
  <div class="page-container customer-page" v-loading="loading">
    <section class="content-card customer-page__heading">
      <div>
        <h1>我的地址</h1>
        <p>维护收货人、联系电话和收货地址；提交订单时可以选择使用。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreate">新增地址</el-button>
    </section>

    <section v-if="addresses.length" class="address-grid">
      <article v-for="address in addresses" :key="address.id" class="content-card address-card">
        <header class="address-card__header">
          <div>
            <strong>{{ address.receiver_name }}</strong>
            <span>{{ address.phone }}</span>
          </div>
          <el-tag v-if="address.is_default" type="success" effect="light" round>默认地址</el-tag>
        </header>
        <p class="address-card__location">
          {{ address.province }}{{ address.city }}{{ address.district }}{{ address.detail }}
        </p>
        <footer class="address-card__actions">
          <el-button v-if="!address.is_default" link type="primary" @click="setDefault(address)">
            设为默认
          </el-button>
          <el-button link type="primary" @click="openEdit(address)">编辑</el-button>
          <el-button link type="danger" @click="removeAddress(address)">删除</el-button>
        </footer>
      </article>
    </section>

    <section v-else-if="!loading" class="content-card customer-empty">
      <el-empty description="还没有收货地址">
        <el-button type="primary" @click="openCreate">添加收货地址</el-button>
      </el-empty>
    </section>

    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? '编辑收货地址' : '新增收货地址'"
      width="560px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-form-item label="选择地区"><el-cascader :props="{ lazy: true, lazyLoad: loadRegionOptions, value:'name', label:'name', leaf:'leaf', emitPath:true }" placeholder="选择省 / 市 / 区县，也可在下方填写" clearable style="width:100%" @change="selectRegion" /></el-form-item>
        <el-form-item label="收货人" prop="receiver_name">
          <el-input v-model="form.receiver_name" maxlength="50" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" maxlength="30" placeholder="请输入联系电话" />
        </el-form-item>
        <div class="address-region-fields">
          <el-form-item label="省份" prop="province">
            <el-input v-model="form.province" maxlength="50" placeholder="省/自治区" />
          </el-form-item>
          <el-form-item label="城市" prop="city">
            <el-input v-model="form.city" maxlength="50" placeholder="城市" />
          </el-form-item>
          <el-form-item label="区县" prop="district">
            <el-input v-model="form.district" maxlength="50" placeholder="区/县" />
          </el-form-item>
        </div>
        <el-form-item label="详细地址" prop="detail">
          <el-input
            v-model="form.detail"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="街道、门牌号、小区或楼栋信息"
          />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveAddress">保存地址</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { mallRegionChildren } from '@/api/mall'
import {
  createAddress,
  deleteAddress,
  getAddresses,
  updateAddress
} from '@/api/customer'

async function loadRegionOptions(node, resolve) {
  try {
    const response = await mallRegionChildren(node.level === 0 ? 0 : node.data.id)
    resolve(response.data.list.map(row => ({ ...row, leaf: row.type === 3 })))
  } catch { resolve([]) }
}
function selectRegion(names) {
  if (names?.length === 3) { [form.province, form.city, form.district] = names; formRef.value?.clearValidate(['province','city','district']) }
}
const addresses = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const formRef = ref()
const emptyForm = () => ({
  id: null,
  receiver_name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail: '',
  is_default: false
})
const form = reactive(emptyForm())
const rules = {
  receiver_name: [{ required: true, message: '请输入收货人姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { min: 6, max: 30, message: '联系电话长度应为 6-30 位', trigger: 'blur' }
  ],
  province: [{ required: true, message: '请输入省份', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  district: [{ required: true, message: '请输入区县', trigger: 'blur' }],
  detail: [{ required: true, message: '请输入详细地址', trigger: 'blur' }]
}

async function load() {
  loading.value = true
  try {
    const response = await getAddresses()
    addresses.value = response.data?.list || []
  } catch (error) {
    ElMessage.error(error?.message || '加载地址失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, emptyForm(), { is_default: addresses.value.length === 0 })
  dialogVisible.value = true
}

function openEdit(address) {
  Object.assign(form, emptyForm(), address)
  dialogVisible.value = true
}

async function saveAddress() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid || saving.value) return
  saving.value = true
  try {
    const { id, ...payload } = form
    if (id) await updateAddress(id, payload)
    else await createAddress(payload)
    dialogVisible.value = false
    ElMessage.success('收货地址已保存')
    await load()
  } catch (error) {
    ElMessage.error(error?.message || '保存地址失败')
  } finally {
    saving.value = false
  }
}

async function setDefault(address) {
  try {
    const { id, ...payload } = address
    await updateAddress(id, { ...payload, is_default: true })
    ElMessage.success('默认地址已更新')
    await load()
  } catch (error) {
    ElMessage.error(error?.message || '设置默认地址失败')
  }
}

async function removeAddress(address) {
  try {
    await ElMessageBox.confirm(`确定删除 ${address.receiver_name} 的收货地址吗？`, '删除地址', {
      type: 'warning'
    })
    await deleteAddress(address.id)
    ElMessage.success('地址已删除')
    await load()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(error?.message || '删除地址失败')
  }
}

onMounted(load)
</script>

<style scoped>
.customer-page { display: grid; gap: 18px; }
.customer-page__heading { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.customer-page__heading h1 { margin: 0; color: #102237; font-size: 22px; }
.customer-page__heading p { margin: 6px 0 0; color: #728396; font-size: 14px; }
.address-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 18px; }
.address-card { padding: 22px; }
.address-card__header { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.address-card__header > div { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; }
.address-card__header strong { color: #17324b; font-size: 16px; }
.address-card__header span { color: #62768a; }
.address-card__location { min-height: 48px; margin: 16px 0; color: #62768a; line-height: 1.7; }
.address-card__actions { display: flex; justify-content: flex-end; gap: 8px; padding-top: 12px; border-top: 1px solid #edf1ef; }
.address-region-fields { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.address-region-fields :deep(.el-form-item) { min-width: 0; margin-right: 0; }
.customer-empty { padding: 40px 20px; }
@media (max-width: 700px) { .customer-page__heading { align-items: flex-start; flex-direction: column; } .address-region-fields { grid-template-columns: 1fr; gap: 0; } }
</style>
