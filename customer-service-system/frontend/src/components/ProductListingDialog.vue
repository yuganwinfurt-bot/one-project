<template>
  <component
    :is="embedded ? 'section' : ElDialog"
    :class="embedded ? 'content-card listing-page-card' : undefined"
    v-bind="embedded ? {} : dialogProps"
    @update:model-value="handleVisibilityChange"
  >
    <header v-if="embedded" class="listing-page-heading">
      <div>
        <p class="listing-page-eyebrow">商品管理</p>
        <h1>{{ product?.id ? '编辑商品' : '商品上架' }}</h1>
        <p>{{ product?.id ? '修改商品资料并保存' : '填写商品信息，完成后可在商品列表中查看和维护。' }}</p>
      </div>
    </header>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="listing-form"
    >
      <el-form-item label="商品名称" prop="name">
        <el-input v-model="form.name" maxlength="100" show-word-limit placeholder="请输入商品名称" />
      </el-form-item>
      <el-form-item label="类目" prop="category">
        <el-select v-model="form.category" filterable allow-create default-first-option style="width:100%" placeholder="选择或输入类目"><el-option v-for="item in catalogOptions.categories" :key="item.value" :value="item.label" :label="item.label" /></el-select>
      </el-form-item>
      <el-form-item label="品牌"><el-select v-model="form.brand_id" filterable clearable placeholder="选择品牌（选填）" style="width:100%"><el-option v-for="item in catalogOptions.brands" :key="item.value" :value="item.value" :label="item.label" /></el-select></el-form-item>
      <div class="listing-form__numbers">
        <el-form-item v-if="!form.has_variants" label="售价（元）" prop="price">
          <el-input-number
            v-model="form.price"
            :min="0.01"
            :max="99999999.99"
            :precision="2"
            :step="1"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="优惠（%）" prop="discount_percent">
          <el-input-number
            v-model="form.discount_percent"
            :min="0"
            :max="99.99"
            :precision="2"
            :step="1"
            controls-position="right"
          />
        </el-form-item>
      </div>
      <el-form-item v-if="!form.has_variants" label="库存" prop="stock">
        <el-input-number
          v-model="form.stock"
          :min="0"
          :max="2147483647"
          :precision="0"
          :step="1"
          controls-position="right"
        />
      </el-form-item>
      <el-form-item label="商品规格">
        <el-switch
          v-model="form.has_variants"
          active-text="启用多规格"
          inactive-text="单规格"
          @change="toggleVariants"
        />
      </el-form-item>
      <el-form-item v-if="form.has_variants" label="规格名称">
        <el-input v-model="form.variant_name" maxlength="40" placeholder="例如：容量、颜色、版本" />
      </el-form-item>
      <div v-if="form.has_variants" class="listing-skus">
        <div class="listing-skus__heading">
          <span>规格值</span><span>折后售价（元）</span><span>库存</span><span>操作</span>
        </div>
        <div v-for="(variant, index) in form.variants" :key="variant.key" class="listing-skus__row">
          <el-input v-model="variant.name" maxlength="100" :placeholder="index === 0 ? '例如：256GB' : '例如：512GB'" />
          <el-input-number v-model="variant.price" :min="0.01" :max="99999999.99" :precision="2" :step="1" controls-position="right" />
          <el-input-number v-model="variant.stock" :min="0" :max="2147483647" :precision="0" :step="1" controls-position="right" />
          <el-button link type="danger" :disabled="form.variants.length <= 1" @click="removeVariant(index)">删除</el-button>
        </div>
        <div class="listing-skus__footer">
          <el-button plain @click="addVariant">添加规格</el-button>
          <span>商品最低售价 ¥{{ variantMinPrice.toFixed(2) }} · 总库存 {{ variantTotalStock }}</span>
        </div>
        <p class="listing-skus__tip">每一行是一种可选商品规格，例如 256GB 和 512GB；颜色与容量组合可作为不同规格值分别添加。</p>
      </div>
      <el-form-item label="商品介绍" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          maxlength="10000"
          show-word-limit
          placeholder="介绍商品特点，方便买家了解"
        />
      </el-form-item>
      <el-form-item label="商品图片">
        <div class="listing-images">
          <el-upload
            v-model:file-list="imageFiles"
            :http-request="uploadImage"
            :before-upload="beforeImageUpload"
            :on-remove="removeImage"
            accept="image/jpeg,image/png,image/gif,image/webp"
            list-type="picture-card"
            :limit="3"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <span class="listing-images__tip">最多 3 张，第一张作为商品主图；单张不超过 2MB。</span>
        </div>
      </el-form-item>
      <el-alert
        :title="product?.review_status === 'pending_review'
          ? '商品会设为在售，但仍需复核通过后才会显示在商品首页。'
          : '保存后商品会直接设为在售；新商品会显示在商品首页。'"
        :type="product?.review_status === 'pending_review' ? 'warning' : 'info'"
        :closable="false"
        show-icon
      />
    </el-form>
    <div v-if="embedded" class="listing-actions">
      <el-button @click="cancel">返回商品列表</el-button>
      <el-button type="primary" :loading="saving" @click="submit">
        {{ product?.id ? '保存并上架' : '创建并上架' }}
      </el-button>
    </div>
    <template #footer v-if="!embedded">
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">
        {{ product?.id ? '保存并上架' : '创建并上架' }}
      </el-button>
    </template>
  </component>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { ElDialog, ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { uploadFileApi } from '@/api/file'
import request from '@/utils/request'
import { createProductListing, updateProductListing } from '@/api/ecommerce'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  embedded: { type: Boolean, default: false },
  product: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'saved', 'cancel'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
const dialogProps = computed(() => ({
  modelValue: visible.value,
  title: props.product?.id ? '编辑商品并上架' : '新增商品并上架',
  width: '620px',
  top: '6vh',
  closeOnClickModal: false,
  destroyOnClose: true
}))
function handleVisibilityChange(value) {
  visible.value = value
}
function cancel() {
  if (props.embedded) emit('cancel')
  else visible.value = false
}
const formRef = ref()
const saving = ref(false)
const imageFiles = ref([])
const catalogOptions = ref({ categories:[], brands:[] })
const emptyForm = () => ({
  name: '',
  category: '',
  brand_id: null,
  description: '',
  price: 0.01,
  discount_percent: 0,
  stock: 0,
  has_variants: false,
  variant_name: '',
  variants: [],
  image_urls: []
})
const form = reactive(emptyForm())
const variantMinPrice = computed(() => Math.min(...form.variants.map((item) => Number(item.price) || 0)))
const variantTotalStock = computed(() => form.variants.reduce((sum, item) => sum + (Number(item.stock) || 0), 0))

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  category: [{ required: true, message: '请输入商品类目', trigger: 'blur' }],
  price: [{ required: true, type: 'number', min: 0.01, message: '售价必须大于 0', trigger: 'change' }],
  discount_percent: [{ required: true, type: 'number', min: 0, max: 99.99, message: '优惠幅度需在 0% 到 99.99% 之间', trigger: 'change' }],
  stock: [{ required: true, type: 'number', min: 0, message: '库存不能小于 0', trigger: 'change' }]
}

watch(
  () => [props.modelValue, props.embedded, props.product],
  async ([opened, embedded, product]) => {
    if (!opened && !embedded) return
    Object.assign(form, emptyForm(), product ? {
      name: product.name || '',
      category: product.category || '',
      description: product.description || '',
      price: Number(product.price || 0.01),
      discount_percent: Number(product.discount_percent || 0),
      stock: Number(product.stock || 0),
      has_variants: Boolean(product.variants?.length),
      variant_name: product.variant_name || '',
      variants: (product.variants || []).map((item) => ({ ...item, price: Number(item.price), stock: Number(item.stock) })),
      image_urls: [...(product.image_urls?.length ? product.image_urls : product.image_url ? [product.image_url] : [])]
    } : {})
    imageFiles.value = form.image_urls.map((url, index) => ({
      name: `商品图片${index + 1}`,
      url,
      status: 'success'
    }))
    try {
      const [optionsResponse, catalogResponse] = await Promise.all([
        request.get('/api/mall/catalog-options'),
        product?.id ? request.get(`/api/mall/product-catalog/${product.id}`) : Promise.resolve({ data:{ brand_id:null } })
      ])
      if ((!props.modelValue && !props.embedded) || props.product?.id !== product?.id) return
      catalogOptions.value = optionsResponse.data
      form.brand_id = catalogResponse.data.brand_id
    } catch {}
    await nextTick()
    formRef.value?.clearValidate()
  },
  { immediate: true }
)

function beforeImageUpload(file) {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!imageTypes.includes(file.type)) {
    ElMessage.error('商品图片仅支持 JPG、PNG、GIF 或 WebP')
    return false
  }
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('单张商品图片不能超过 2MB')
    return false
  }
  return true
}

async function uploadImage({ file, onSuccess, onError }) {
  try {
    const response = await uploadFileApi(file)
    const url = response.data?.url
    if (!url) throw new Error('上传结果中没有图片地址')
    form.image_urls = [...form.image_urls, url].slice(0, 3)
    onSuccess({ url })
  } catch (error) {
    onError(error)
  }
}

function removeImage(file) {
  const url = file.response?.url || file.url
  form.image_urls = form.image_urls.filter((item) => item !== url)
}

function makeVariant(name = '', price = Number(form.price) || 0.01, stock = 0) {
  const key = globalThis.crypto?.randomUUID?.() || `sku-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
  return { key, name, price, stock }
}

function toggleVariants(enabled) {
  if (enabled) {
    if (!form.variants.length) {
      form.variant_name = ''
      form.variants = [makeVariant('', Number(form.price) || 0.01, Number(form.stock) || 0), makeVariant('', Number(form.price) || 0.01, 0)]
    }
    return
  }
  if (form.variants.length) {
    form.price = variantMinPrice.value || form.price
    form.stock = variantTotalStock.value
  }
  form.variant_name = ''
  form.variants = []
}

function addVariant() {
  form.variants.push(makeVariant('', variantMinPrice.value || Number(form.price) || 0.01, 0))
}

function removeVariant(index) {
  if (form.variants.length > 1) form.variants.splice(index, 1)
}

async function submit() {
  if (form.has_variants) {
    if (!form.variant_name.trim()) {
      ElMessage.warning('请填写规格名称，例如“容量”')
      return
    }
    if (!form.variants.length || form.variants.some((item) => !item.name.trim() || !(Number(item.price) > 0) || !Number.isInteger(Number(item.stock)) || Number(item.stock) < 0)) {
      ElMessage.warning('请为每个规格填写名称、有效售价和库存')
      return
    }
    const names = form.variants.map((item) => item.name.trim())
    if (new Set(names).size !== names.length) {
      ElMessage.warning('规格值不能重复')
      return
    }
  }
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid || saving.value) return
  const payload = {
    name: form.name.trim(),
    category: form.category.trim(),
    brand_id: form.brand_id || null,
    description: form.description.trim(),
    price: Number(Number(form.has_variants ? variantMinPrice.value : form.price).toFixed(2)),
    discount_percent: Number(Number(form.discount_percent).toFixed(2)),
    stock: Number(form.has_variants ? variantTotalStock.value : form.stock),
    variant_name: form.has_variants ? form.variant_name.trim() : null,
    variants: form.has_variants ? form.variants.map((item) => ({
      ...item,
      name: item.name.trim(),
      price: Number(Number(item.price).toFixed(2)),
      stock: Number(item.stock)
    })) : [],
    image_urls: [...form.image_urls]
  }
  saving.value = true
  try {
    const isEditing = Boolean(props.product?.id)
    const response = isEditing
      ? await updateProductListing(props.product.id, payload)
      : await createProductListing(payload)
    ElMessage.success(isEditing ? '商品资料已保存并上架' : '商品已创建并上架')
    emit('saved', response.data)
    if (!props.embedded) visible.value = false
  } catch {
    // 请求拦截器会显示服务端错误信息，保留表单便于修改后重试。
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.listing-page-card {
  padding: 24px;
}

.listing-page-heading {
  margin-bottom: 22px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--app-border);
}

.listing-page-eyebrow {
  margin: 0 0 6px;
  color: var(--app-primary);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
}

.listing-page-heading h1 {
  margin: 0;
  color: var(--app-text);
  font-size: 24px;
}

.listing-page-heading p:last-child {
  margin: 8px 0 0;
  color: var(--app-text-secondary);
  font-size: 14px;
}

.listing-form {
  padding: 4px 8px 0 0;
}

.listing-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px solid var(--app-border);
}

.listing-form__numbers {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 14px;
}

.listing-form__numbers :deep(.el-input-number),
.listing-form > :deep(.el-form-item) .el-input-number {
  width: 100%;
}

.listing-skus {
  margin: 0 0 20px 120px;
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: #fafbfc;
}

.listing-skus__heading,
.listing-skus__row {
  display: grid;
  grid-template-columns: minmax(130px, 1.3fr) minmax(150px, 1fr) minmax(120px, 0.8fr) 44px;
  align-items: center;
  gap: 10px;
}

.listing-skus__heading {
  margin-bottom: 8px;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.listing-skus__row + .listing-skus__row { margin-top: 9px; }
.listing-skus__row :deep(.el-input-number) { width: 100%; }
.listing-skus__footer { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 12px; color: var(--app-text-secondary); font-size: 12px; }
.listing-skus__tip { margin: 10px 0 0; color: var(--app-muted); font-size: 12px; line-height: 1.5; }

.listing-images {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.listing-images__tip {
  color: var(--app-muted);
  font-size: 12px;
  line-height: 1.5;
}

.listing-form :deep(.el-alert) {
  margin: 2px 0 8px 120px;
  width: calc(100% - 120px);
}

@media (max-width: 640px) {
  .listing-form__numbers {
    grid-template-columns: 1fr;
    gap: 0;
  }
  .listing-skus { margin-left: 0; padding: 12px; }
  .listing-skus__heading { display: none; }
  .listing-skus__row { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 42px; }
  .listing-skus__row > :first-child { grid-column: 1 / -1; }
  .listing-skus__footer { align-items: flex-start; flex-direction: column; }
  .listing-form :deep(.el-alert) { margin-left: 0; width: 100%; }
}
</style>
