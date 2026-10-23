<template>
  <section v-if="risk" class="after-sale-risk" :class="`is-${risk.level}`" aria-label="商品售后风险">
    <header>
      <strong>近{{ risk.window_days }}天订单售后情况</strong>
      <el-tag :type="risk.level === 'critical' ? 'danger' : risk.level === 'warning' ? 'warning' : 'success'" round>
        {{ risk.level === 'critical' ? '严重预警 · 建议复核' : risk.level === 'warning' ? '售后集中提醒' : '未达到预警阈值' }}
      </el-tag>
    </header>
    <div class="after-sale-risk__summary">
      <strong>{{ risk.after_sale_order_count }} / {{ risk.order_count }} 笔</strong>
      <span>涉及售后，占有效订单 {{ risk.after_sale_rate }}%</span>
    </div>
    <p>退款 {{ risk.refund_count }} 笔 · 退货退款 {{ risk.return_count }} 笔 · 换货 {{ risk.exchange_count }} 笔</p>
    <p class="after-sale-risk__note">{{ risk.scope_text }}</p>
    <p class="after-sale-risk__note">{{ risk.rule_text }}</p>
    <div class="after-sale-risk__actions">
      <el-button size="small" @click="viewApplications">查看售后申请</el-button>
      <el-button v-if="risk.needs_review" size="small" type="warning" :loading="saving" :disabled="product?.review_status === 'pending_review'" @click="confirmReview">
        {{ product?.review_status === 'pending_review' ? '已标记待复核' : '标记待复核' }}
      </el-button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { confirmAfterSaleRiskReview } from '@/api/ecommerce'
const props = defineProps({ risk: Object, product: Object })
const emit = defineEmits(['reviewed'])
const router = useRouter()
const saving = ref(false)
function viewApplications() {
  if (props.product?.id) router.push({ path: '/manager/after-sales', query: { productId: String(props.product.id), productName: props.product.name } })
}
async function confirmReview() {
  if (saving.value || !props.risk?.needs_review || props.product?.review_status === 'pending_review') return
  const productId = props.product.id
  try {
    await ElMessageBox.confirm(`确认将“${props.product.name}”标记为待人工复核？该商品会暂时从买家商品首页隐藏，请先核查售后原因。`, '确认商品复核', {
      confirmButtonText: '确认标记待复核', cancelButtonText: '取消', type: 'warning'
    })
  } catch { return }
  saving.value = true
  try {
    const response = await confirmAfterSaleRiskReview(productId)
    if (props.product?.id === productId) emit('reviewed', response.data)
    ElMessage.success('商品已标记待人工复核')
  } catch { /* 请求层显示服务端返回的最新状态。 */ }
  finally { saving.value = false }
}
</script>

<style scoped>
.after-sale-risk { display: grid; gap: 12px; padding: 16px; margin-top: 18px; border: 1px solid #dfe9e4; border-radius: 10px; background: #f7faf8; }
.after-sale-risk.is-warning { border-color: #f4d6a2; background: #fffbf2; }
.after-sale-risk.is-critical { border-color: #f1bbbb; background: #fff6f5; }
.after-sale-risk header { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; justify-content: space-between; }
.after-sale-risk__summary { display: flex; align-items: baseline; flex-wrap: wrap; gap: 8px; }
.after-sale-risk__summary strong { font-size: 22px; color: #102237; }
.after-sale-risk p { margin: 0; font-size: 13px; line-height: 1.6; }
.after-sale-risk .after-sale-risk__note { color: #738396; font-size: 12px; }
.after-sale-risk__actions { display: flex; flex-wrap: wrap; gap: 8px; }
.after-sale-risk__actions .el-button { margin-left: 0; }
</style>
