<template>
  <div class="page-container page-container--center">
    <div class="content-card profile-card">
      <div class="profile-heading">
        <h1>个人资料</h1>
        <p>{{ isPlatformAdmin ? '管理员资料已设为只读，无法在后台修改。' : '修改你的头像、名称、邮箱和手机号。' }}</p>
      </div>
      <el-form
        ref="formRef"
        :rules="rules"
        :model="form"
        label-width="80px"
        :disabled="isPlatformAdmin"
        v-loading="loading"
      >
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            :disabled="isPlatformAdmin"
            :http-request="handleFileUpload"
            :show-file-list="false"
            accept="image/jpeg,image/png,image/gif,image/webp"
            :before-upload="beforeAvatarUpload"
          >
            <img v-if="form.avatar" :src="form.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="账号">
          <el-input disabled v-model="form.username" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="角色">
          <el-input disabled v-model="roleLabel" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item v-if="!isPlatformAdmin">
          <el-button type="primary" :loading="submitting" @click="handleSubmit">保存修改</el-button>
        </el-form-item>
      </el-form>
      <el-divider v-if="form.role !== 'admin'" />
      <section v-if="form.role !== 'admin'" class="profile-security">
        <div>
          <h2>账号安全</h2>
          <p>密码不会显示在个人资料中，可通过验证原密码来设置新密码。</p>
        </div>
        <el-button @click="goChangePassword">修改密码</el-button>
      </section>
    </div>
  </div>
</template>

<script setup>
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
.profile-heading {
  margin-bottom: 22px;
}

.profile-heading h1 {
  margin: 0;
  color: var(--app-text);
  font-size: 18px;
  font-weight: 600;
}

.profile-heading p {
  margin: 6px 0 0;
  color: var(--app-text-secondary);
  font-size: 13px;
}

.profile-security {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.profile-security h2 {
  margin: 0;
  color: var(--app-text);
  font-size: 15px;
  font-weight: 600;
}

.profile-security p {
  margin: 6px 0 0;
  color: var(--app-text-secondary);
  font-size: 12px;
  line-height: 1.6;
}

.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  display: block;
  object-fit: cover;
}
</style>
<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--app-border);
  border-radius: var(--app-radius-sm);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  background: #f8fafc;
  transition: var(--el-transition-duration-fast);
}
.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
  background: #f0f7ff;
}
.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  text-align: center;
}
</style>
