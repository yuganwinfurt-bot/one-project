<template>
  <el-form label-position="top" class="mall-fields">
    <el-form-item v-for="field in fields" :key="field.key" :label="field.label" :required="field.required">
      <el-switch v-if="field.type === 'switch'" v-model="model[field.key]" />
      <el-input-number v-else-if="['number', 'money'].includes(field.type)" v-model="model[field.key]" :min="field.min ?? 0" :max="field.max ?? 99999999" :precision="field.type === 'money' ? 2 : 0" controls-position="right" />
      <el-date-picker v-else-if="field.type === 'datetime'" v-model="model[field.key]" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" placeholder="选择时间" />
      <el-select v-else-if="selectTypes.includes(field.type)" v-model="model[field.key]" filterable clearable :multiple="['products', 'staff', 'permissions'].includes(field.type)" :placeholder="`请选择${field.label}`" style="width:100%">
        <el-option v-for="option in fieldOptions(field)" :key="option.value" :label="option.label" :value="option.value" />
      </el-select>
      <div v-else-if="field.type === 'image'" class="mall-image-field">
        <el-input v-model="model[field.key]" placeholder="图片地址，也可上传本地图片" maxlength="500" />
        <el-upload :show-file-list="false" :http-request="(args) => upload(args, field.key)" accept="image/png,image/jpeg,image/gif,image/webp"><el-button>上传图片</el-button></el-upload>
        <el-image v-if="model[field.key]" :src="model[field.key]" style="width:80px;height:60px" fit="contain" />
      </div>
      <el-input v-else v-model="model[field.key]" :type="field.type === 'textarea' ? 'textarea' : 'text'" :rows="4" :maxlength="field.type === 'textarea' ? 10000 : field.key === 'name' ? 120 : 500" show-word-limit />
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { uploadFileApi } from '@/api/file'
const props = defineProps({ fields: { type: Array, default: () => [] }, model: { type: Object, required: true }, options: { type: Object, default: () => ({}) } })
const selectTypes = ['select', 'product', 'products', 'brand', 'category', 'staff', 'permissions']
function fieldOptions(field) {
  const key = { product: 'products', brand: 'brands', category: 'categories' }[field.type] || field.type
  return field.options || props.options[key] || []
}
async function upload({ file, onSuccess, onError }, key) {
  if (!['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type) || file.size > 2 * 1024 * 1024) {
    const error = new Error('请选择 2MB 以内的 JPG、PNG、GIF 或 WebP 图片')
    ElMessage.warning(error.message)
    onError(error)
    return
  }
  try {
    const response = await uploadFileApi(file)
    props.model[key] = response.data.url
    onSuccess(response.data)
  } catch (error) { onError(error) }
}
</script>

<style scoped>
.mall-fields { display: grid; gap: 4px; }
.mall-image-field { width: 100%; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.mall-image-field .el-input { flex: 1; min-width: 180px; }
</style>
