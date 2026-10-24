<template>

<div class="m-view"><MiniHeader title="个人资料" /><div class="m-scroll" v-loading="loading"><section class="m-card"><div class="m-avatar-editor"><el-upload :show-file-list="false" :before-upload="beforeAvatarUpload" :http-request="handleFileUpload"><img v-if="form.avatar" :src="form.avatar" /><span v-else>{{ (form.name || form.username || '我').slice(0,1) }}</span></el-upload><p>点击修改头像</p></div><el-form ref="formRef" :model="form" :rules="rules" label-position="top"><el-form-item label="账号"><el-input v-model="form.username" disabled /></el-form-item><el-form-item label="昵称" prop="name"><el-input v-model="form.name" maxlength="50" /></el-form-item><el-form-item label="邮箱" prop="email"><el-input v-model="form.email" inputmode="email" /></el-form-item><el-form-item label="手机号" prop="phone"><el-input v-model="form.phone" inputmode="tel" /></el-form-item></el-form><button class="m-quiet" @click="goChangePassword">修改登录密码 ›</button></section></div><footer class="m-footer"><button class="m-primary m-profile-save" :disabled="submitting" @click="handleSubmit">{{ submitting ? '保存中…' : '保存资料' }}</button></footer></div>
</template>
<script setup>
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
import { useProfile } from '@/composables/customer/Profile'

const {
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
} = useProfile()


</script>
<style scoped>
.m-avatar-editor{display:grid;justify-items:center;gap:8px;padding:8px 0 20px}.m-avatar-editor img,.m-avatar-editor .el-upload span{display:grid;place-items:center;width:72px;height:72px;border-radius:50%;object-fit:cover;background:#fbe8df;color:#d78f70;font-size:28px}.m-avatar-editor p{margin:0;font-size:11px;color:#b1b8c0}.m-profile-save{width:100%}
</style>
