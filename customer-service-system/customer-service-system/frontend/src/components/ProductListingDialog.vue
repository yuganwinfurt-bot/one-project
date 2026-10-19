<template>
  <el-dialog
    v-model="visible"
    :title="product?.id ? '编辑商品并上架' : '新增商品并上架'"
    width="620px"
    top="6vh"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="96px"
      class="listing-form"
    >
      <el-form-item label="商品名称" prop="name">
        <el-input v-model="form.name" maxlength="100" show-word-limit placeholder="请输入商品名称" />
      </el-form-item>
      <el-form-item label="类目" prop="category">
        <el-input v-model="form.category" maxlength="50" placeholder="例如：数码、家居、服饰" />
      </el-form-item>
      <div class="listing-form__numbers">
        <el-form-item label="折后售价（元）" prop="price">
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
      <el-form-item label="库存" prop="stock">
        <el-input-number
          v-model="form.stock"
          :min="0"
          :max="2147483647"
          :precision="0"
          :step="1"
          controls-position="right"
        />
      </el-form-item>
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
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">
        {{ product?.id ? '保存并上架' : '创建并上架' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { uploadFileApi } from '@/api/file'
import { createProductListing, updateProductListing } from '@/api/ecommerce'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  product: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'saved'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
const formRef = ref()
const saving = ref(false)
const imageFiles = ref([])
const emptyForm = () => ({
  name: '',
  category: '',
  description: '',
  price: 0.01,
  discount_percent: 0,
  stock: 0,
  image_urls: []
})
const form = reactive(emptyForm())

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  category: [{ required: true, message: '请输入商品类目', trigger: 'blur' }],
  price: [{ required: true, type: 'number', min: 0.01, message: '售价必须大于 0', trigger: 'change' }],
  discount_percent: [{ required: true, type: 'number', min: 0, max: 99.99, message: '优惠幅度需在 0% 到 99.99% 之间', trigger: 'change' }],
  stock: [{ required: true, type: 'number', min: 0, message: '库存不能小于 0', trigger: 'change' }]
}

watch(
  () => props.modelValue,
  async (opened) => {
    if (!opened) return
    const product = props.product
    Object.assign(form, emptyForm(), product ? {
      name: product.name || '',
      category: product.category || '',
      description: product.description || '',
      price: Number(product.price || 0.01),
      discount_percent: Number(product.discount_percent || 0),
      stock: Number(product.stock || 0),
      image_urls: [...(product.image_urls?.length ? product.image_urls : product.image_url ? [product.image_url] : [])]
    } : {})
    imageFiles.value = form.image_urls.map((url, index) => ({
      name: `商品图片${index + 1}`,
      url,
      status: 'success'
    }))
    await nextTick()
    formRef.value?.clearValidate()
  }
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

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid || saving.value) return
  const payload = {
    name: form.name.trim(),
    category: form.category.trim(),
    description: form.description.trim(),
    price: Number(Number(form.price).toFixed(2)),
    discount_percent: Number(Number(form.discount_percent).toFixed(2)),
    stock: Number(form.stock),
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
    visible.value = false
  } catch {
    // 请求拦截器会显示服务端错误信息，保留表单便于修改后重试。
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.listing-form {
  padding: 4px 8px 0 0;
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
  margin: 2px 0 8px 96px;
  width: calc(100% - 96px);
}

@media (max-width: 640px) {
  .listing-form__numbers {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
