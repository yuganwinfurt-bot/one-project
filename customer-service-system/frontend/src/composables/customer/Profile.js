import { getUserInfo, updateUserInfo } from '@/api/user'
import { uploadFileApi } from '@/api/file'
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { useUser } from '@/utils/user'
import { ElMessage } from 'element-plus'
import { useCustomerRouter } from '@/utils/customerRouter'

export function useProfile() {
const router = useCustomerRouter()
const { updateUser } = useUser()
const isPlatformAdmin = computed(() => form.role === 'admin')
const loading = ref(false)
const submitting = ref(false)
const formRef = ref()
const form = reactive({
  username: '',
  name: '',
  role: '',
  email: '',
  phone: '',
  avatar: ''
})
const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式错误', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误', trigger: 'blur' }]
}
const roleLabel = computed(() => {
  return form.role === 'admin'
    ? '管理员'
    : form.role === 'user'
      ? '运营'
      : form.role === 'customer'
        ? '用户'
        : '未知角色'
})
const beforeAvatarUpload = (file) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!imageTypes.includes(file.type)) {
    ElMessage.error('只能上传图片')
    return false
  }
  if (file.size / 1024 / 1024 > 2) {
    ElMessage.error('上传图片大小不能超过2M')
    return false
  }
  return true
}
const handleFileUpload = async ({ file }) => {
  try {
    const res = await uploadFileApi(file)
    if (res.code === 200) {
      form.avatar = res.data?.url
    }
  } catch {}
}
const loadUserInfo = async () => {
  loading.value = true
  try {
    const res = await getUserInfo()
    if (res.code === 200) {
      Object.assign(form, res.data)
    }
  } finally {
    loading.value = false
  }
}
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const res = await updateUserInfo(form)
    if (res.code === 200) {
      updateUser(res.data)
      ElMessage.success('更新成功')
    }
  } finally {
    submitting.value = false
  }
}
function goChangePassword() {
  router.push('/manager/password')
}
onMounted(() => {
  loadUserInfo()
})
return {
getUserInfo,
updateUserInfo,
uploadFileApi,
ref,
reactive,
onMounted,
computed,
Plus,
useUser,
ElMessage,
useCustomerRouter,
router,
updateUser,
isPlatformAdmin,
loading,
submitting,
formRef,
form,
rules,
roleLabel,
beforeAvatarUpload,
handleFileUpload,
loadUserInfo,
handleSubmit,
goChangePassword
};
}
