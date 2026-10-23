<template>
  <el-dialog
    :model-value="modelValue"
    class="sku-selection-dialog"
    :show-close="false"
    :append-to-body="true"
    :close-on-click-modal="!loading"
    :close-on-press-escape="!loading"
    :width="'min(680px, 96vw)'"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="sku-sheet">
      <header class="sku-sheet__header">
        <strong>选择商品规格</strong>
        <el-button text circle aria-label="关闭规格选择" :disabled="loading" @click="$emit('update:modelValue', false)">
          <el-icon><Close /></el-icon>
        </el-button>
      </header>

      <div class="sku-sheet__summary">
        <el-image v-if="product?.image_url" :src="product.image_url" fit="cover" />
        <div v-else class="sku-sheet__placeholder"><el-icon><Picture /></el-icon></div>
        <div class="sku-sheet__summary-copy">
          <strong>{{ product?.name || '商品' }}</strong>
          <b>{{ priceText }}</b>
          <span>{{ selectedVariant ? `库存 ${selectedVariant.stock} 件` : hasVariants ? '请选择规格' : `库存 ${product?.stock ?? 0} 件` }}</span>
        </div>
      </div>

      <div class="sku-sheet__options">
        <div class="sku-sheet__section-title">
          <strong>{{ product?.variant_name || '商品规格' }}</strong>
          <span v-if="hasVariants">{{ variants.length }} 款可选</span>
        </div>
        <div v-if="hasVariants" class="sku-option-list">
          <button
            v-for="variant in variants"
            :key="variant.key"
            type="button"
            class="sku-option"
            :class="{ 'is-selected': selectedKey === variant.key }"
            :disabled="Number(variant.stock) < 1"
            @click="selectVariant(variant)"
          >
            <span>{{ variant.name }}</span>
            <strong>¥{{ money(variant.price) }}</strong>
            <small>{{ Number(variant.stock) > 0 ? `库存 ${variant.stock}` : '暂时缺货' }}</small>
          </button>
        </div>
        <div v-else class="sku-option sku-option--default is-selected">
          <span>默认规格</span>
          <strong>¥{{ money(product?.price) }}</strong>
          <small>库存 {{ product?.stock ?? 0 }}</small>
        </div>
      </div>

      <div v-if="showQuantity" class="sku-sheet__quantity">
        <strong>购买数量</strong>
        <el-input-number
          :model-value="quantity"
          :min="1"
          :max="quantityLimit"
          :disabled="loading || !canConfirm"
          controls-position="right"
          @update:model-value="$emit('update:quantity', $event || 1)"
        />
      </div>

      <div v-if="$slots.extra" class="sku-sheet__extra"><slot name="extra" /></div>

      <footer class="sku-sheet__footer">
        <slot name="footer" :valid="canConfirm" :variant="selectedVariant">
          <el-button @click="$emit('update:modelValue', false)">取消</el-button>
          <el-button type="warning" :disabled="!canConfirm" :loading="loading" @click="$emit('confirm', selectedKey, quantity)">确认规格</el-button>
        </slot>
      </footer>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { Close, Picture } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  product: { type: Object, default: null },
  selectedKey: { type: String, default: '' },
  quantity: { type: Number, default: 1 },
  maxQuantity: { type: Number, default: 99 },
  showQuantity: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'update:selectedKey', 'update:quantity', 'confirm'])

const variants = computed(() => props.product?.variants || [])
const hasVariants = computed(() => variants.value.length > 0)
const selectedVariant = computed(() => variants.value.find((variant) => variant.key === props.selectedKey) || null)
const quantityLimit = computed(() => Math.max(1, Math.min(
  Number(props.maxQuantity) || 99,
  Number(selectedVariant.value?.stock ?? props.product?.stock) || 0,
  99
)))
const canConfirm = computed(() => hasVariants.value
  ? Boolean(selectedVariant.value && Number(selectedVariant.value.stock) > 0)
  : Number(props.product?.stock) > 0)
const priceText = computed(() => {
  if (selectedVariant.value) return `¥${money(selectedVariant.value.price)}`
  if (hasVariants.value) {
    const prices = variants.value.filter((variant) => Number(variant.stock) > 0).map((variant) => Number(variant.price))
    return `¥${money(prices.length ? Math.min(...prices) : props.product?.price)} 起`
  }
  return `¥${money(props.product?.price)}`
})

function money(value) {
  return Number(value || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function selectVariant(variant) {
  if (Number(variant.stock) < 1) return
  if (props.selectedKey !== variant.key) {
    emitUpdate('update:selectedKey', variant.key)
    emitUpdate('update:quantity', 1)
  }
}

function emitUpdate(name, value) {
  emit(name, value)
}
</script>

<style>
.sku-selection-dialog.el-dialog {
  overflow: hidden;
  border-radius: 18px;
}
.sku-selection-dialog .el-dialog__header { display: none; }
.sku-selection-dialog .el-dialog__body { padding: 0; }
.sku-sheet { display: grid; gap: 18px; max-height: min(78vh, 780px); overflow-y: auto; padding: 20px 22px 0; }
.sku-sheet__header { display: flex; align-items: center; justify-content: space-between; color: #182b3d; font-size: 18px; }
.sku-sheet__summary { display: flex; align-items: center; gap: 16px; min-height: 104px; padding: 12px; border: 1px solid #e6ece9; border-radius: 14px; background: #f8faf9; }
.sku-sheet__summary :is(.el-image, .sku-sheet__placeholder) { flex: 0 0 88px; width: 88px; height: 88px; border-radius: 10px; background: #edf3f0; }
.sku-sheet__summary img { width: 100%; height: 100%; object-fit: cover; }
.sku-sheet__placeholder { display: grid; place-items: center; color: #8a9a94; font-size: 24px; }
.sku-sheet__summary-copy { display: grid; gap: 6px; min-width: 0; }
.sku-sheet__summary-copy strong { overflow: hidden; color: #263b4d; text-overflow: ellipsis; white-space: nowrap; }
.sku-sheet__summary-copy b { color: #e64d3e; font-size: 22px; }
.sku-sheet__summary-copy span { color: #84918c; font-size: 13px; }
.sku-sheet__section-title { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; color: #263b4d; }
.sku-sheet__section-title span { color: #89968f; font-size: 12px; }
.sku-option-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 10px; }
.sku-option { display: grid; gap: 5px; min-width: 0; padding: 12px; border: 1px solid #e4eae7; border-radius: 12px; background: #f6f8f7; color: #263b4d; text-align: left; cursor: pointer; transition: border-color .16s ease, background-color .16s ease, color .16s ease; }
.sku-option:hover:not(:disabled) { border-color: #f2a35e; }
.sku-option.is-selected { border-color: #f18b3c; background: #fff5ec; color: #bd571b; }
.sku-option strong { font-size: 15px; }
.sku-option small { color: #8a9691; font-size: 12px; }
.sku-option:disabled { color: #aeb7b3; cursor: not-allowed; opacity: .65; }
.sku-option--default { width: min(280px, 100%); cursor: default; }
.sku-sheet__quantity { display: flex; align-items: center; justify-content: space-between; padding-top: 2px; color: #263b4d; }
.sku-sheet__extra { padding-top: 2px; }
.sku-sheet__footer { position: sticky; bottom: 0; display: flex; justify-content: flex-end; gap: 10px; padding: 12px 0 18px; border-top: 1px solid #edf0ee; background: #fff; }
.sku-sheet__footer .el-button--warning { border-color: #ef7432; background: linear-gradient(100deg, #ff9d00, #f45423); }
@media (max-width: 600px) {
  .sku-selection-dialog.el-dialog { position: fixed; bottom: 0; width: 100% !important; max-height: 88vh; margin: 0 !important; border-radius: 18px 18px 0 0; }
  .el-overlay-dialog:has(.sku-selection-dialog) { display: flex; align-items: flex-end; }
  .sku-sheet { max-height: 86vh; gap: 14px; padding: 14px 16px 0; }
  .sku-sheet__summary :is(.el-image, .sku-sheet__placeholder) { flex-basis: 72px; width: 72px; height: 72px; }
  .sku-option-list { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
  .sku-option { padding: 10px; }
  .sku-sheet__footer { padding-bottom: max(14px, env(safe-area-inset-bottom)); }
  .sku-sheet__footer > .el-button { flex: 1; }
}
</style>
