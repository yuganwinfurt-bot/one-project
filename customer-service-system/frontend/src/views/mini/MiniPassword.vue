<template>

<div class="m-view"><MiniHeader title="修改密码" back="/mini-store/profile" /><div class="m-scroll"><section class="m-card"><p class="m-muted">使用原密码确认身份，再设置新的登录密码。</p><el-form ref="formRef" :model="form" :rules="rules" label-position="top"><el-form-item label="原密码" prop="oldPassword"><el-input v-model="form.oldPassword" type="password" autocomplete="current-password" show-password /></el-form-item><el-form-item label="新密码" prop="newPassword"><el-input v-model="form.newPassword" type="password" autocomplete="new-password" show-password /></el-form-item><el-form-item label="确认新密码" prop="confirmPassword"><el-input v-model="form.confirmPassword" type="password" autocomplete="new-password" show-password /></el-form-item></el-form></section></div><footer class="m-footer"><button class="m-primary" style="width:100%" :disabled="submitting" @click="handleSubmit">{{ submitting ? '保存中…' : '确认修改' }}</button></footer></div>
</template>
<script setup>
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
import { usePassword } from '@/composables/customer/Password'

const {
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
} = usePassword()


</script>
<style scoped>

</style>
