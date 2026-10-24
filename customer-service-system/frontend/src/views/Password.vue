<template>
  <div class="page-container page-container--center">
    <div class="content-card">
      <el-alert
        v-if="isPlatformAdmin"
        title="管理员个人资料与密码修改功能已下架。"
        type="warning"
        :closable="false"
        show-icon
      />
      <el-form v-else ref="formRef" :rules="rules" :model="form" label-width="88px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            type="password"
            show-password
            v-model="form.oldPassword"
            placeholder="请输入原密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            type="password"
            show-password
            v-model="form.newPassword"
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            type="password"
            show-password
            v-model="form.confirmPassword"
            placeholder="请确认新密码"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">保存修改</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
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
