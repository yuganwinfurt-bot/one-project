import { sendUserLogout, updatePassword } from '@/api/user'
import { useCustomerRouter } from '@/utils/customerRouter'
import { logout } from '@/utils/auth'
import { ElMessage } from 'element-plus'
import { ref, reactive, computed } from 'vue'
import { getUserInfo } from '@/utils/auth'

export function usePassword() {
const router = useCustomerRouter()
const submitting = ref(false)
const formRef = ref()
const isPlatformAdmin = computed(() => getUserInfo()?.role === 'admin')
const isCustomerAccount = computed(() => getUserInfo()?.role === 'customer')
const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else if (value !== form.newPassword) {
    callback(new Error('确认密码跟新密码不一致'))
  } else {
    callback()
  }
}
const rules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 64, message: '新密码长度 6-64 位', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validatePass, trigger: 'blur' }]
}
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const res = await updatePassword({
      old_password: form.oldPassword,
      new_password: form.newPassword
    })
    if (res.code === 200) {
      ElMessage.success('修改密码成功')
      try {
        await sendUserLogout()
      } catch {}
      logout()
      await router.push(isCustomerAccount.value
        ? { path: '/login', query: { mode: 'user' } }
        : '/login')
    }
  } finally {
    submitting.value = false
  }
}
return {
sendUserLogout,
updatePassword,
useCustomerRouter,
router,
logout,
ElMessage,
ref,
reactive,
computed,
getUserInfo,
submitting,
formRef,
isPlatformAdmin,
isCustomerAccount,
form,
validatePass,
rules,
handleSubmit
};
}
