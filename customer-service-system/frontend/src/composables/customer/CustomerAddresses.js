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

export function useCustomerAddresses() {
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
return {
onMounted,
reactive,
ref,
ElMessage,
ElMessageBox,
Plus,
mallRegionChildren,
createAddress,
deleteAddress,
getAddresses,
updateAddress,
loadRegionOptions,
selectRegion,
addresses,
loading,
saving,
dialogVisible,
formRef,
emptyForm,
form,
rules,
load,
openCreate,
openEdit,
saveAddress,
setDefault,
removeAddress
};
}
