<template>
  <el-form ref="formRef" :model="model" label-width="174px" class="order-settings-form">
    <el-form-item
      v-for="field in timeFields"
      :key="field.key"
      :label="field.label"
      :prop="field.key"
      :rules="[{ validator: (_rule, value, callback) => validate(field, value, callback), trigger: 'blur' }]"
      required
    >
      <div class="order-settings-row">
        <el-input v-model.number="model[field.key]" type="number" :min="field.min" :max="field.max" step="1">
          <template #append>{{ field.unit }}</template>
        </el-input>
        <span class="order-settings-help">{{ field.help }}</span>
      </div>
    </el-form-item>
    <el-collapse class="order-settings-extra">
      <el-collapse-item title="下单开关与购买上限" name="limits">
        <el-form-item label="允许创建订单"><el-switch v-model="model.checkout_enabled" /></el-form-item>
        <el-form-item label="单项商品购买上限"><el-input-number v-model="model.max_quantity" :min="1" :max="99" :precision="0" controls-position="right" /></el-form-item>
      </el-collapse-item>
    </el-collapse>
    <el-form-item class="order-settings-actions">
      <el-button :disabled="saving" @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">确定</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { computed, ref } from 'vue'
const props = defineProps({ model: { type: Object, required: true }, fields: { type: Array, default: () => [] }, saving: Boolean })
const emit = defineEmits(['save', 'cancel'])
const formRef = ref()
const timeFields = computed(() => props.fields.filter(field => field.unit))
function validate(field, value, callback) {
  const number = Number(value)
  callback(Number.isInteger(number) && number >= field.min && number <= field.max ? undefined : new Error(`请输入 ${field.min}～${field.max} 的整数`))
}
async function save() {
  if (await formRef.value?.validate().catch(() => false)) emit('save')
}
</script>

<style scoped>
.order-settings-form { max-width: 1180px; padding: 8px 0; }
.order-settings-form :deep(.el-form-item__label) { font-weight: 600; }
.order-settings-row { display: flex; align-items: center; flex-wrap: wrap; gap: 14px; width: 100%; }
.order-settings-row .el-input { width: min(480px, 100%); flex: 1 1 300px; }
.order-settings-help { flex: 1 1 260px; color: var(--app-text-secondary); font-size: 13px; line-height: 1.6; }
.order-settings-extra { margin: 6px 0 24px 174px; border-top: 0; max-width: 480px; }
.order-settings-extra :deep(.el-collapse-item__header) { font-weight: 400; color: var(--app-text-secondary); }
.order-settings-extra :deep(.el-form-item) { margin-bottom: 18px; }
.order-settings-extra :deep(.el-form-item__label) { font-weight: 400; }
@media (max-width: 700px) {
  .order-settings-form :deep(.el-form-item) { display: block; }
  .order-settings-form :deep(.el-form-item__content) { margin-left: 0 !important; }
  .order-settings-form :deep(.el-form-item__label) { float: none; width: auto !important; }
  .order-settings-row { gap: 6px; }
  .order-settings-extra { margin-left: 0; }
}
</style>
