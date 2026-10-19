<template>
  <div class="page-container semantic">
    <div class="content-card">
      <div class="semantic__title">语义检索调试</div>
      <div class="semantic__sub">
        当前连接独立 RAG 知识库“电商分析平台”。可同步商品、订单、售后、消息、日志、运行记录和功能规则；账号密码等凭证不入库，个人信息会脱敏。
        距离越小越相似（余弦距离 = 1 − 相似度），{{ RELATED_MAX_DISTANCE }} 是当前配置里的相关 /
        不相关分界。
      </div>
      <div class="semantic__toolbar">
        <el-input
          class="semantic__input"
          v-model="query"
          placeholder="例如：换货流程 / 缺货预警 / 收藏商品到货通知"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-select v-model="topK" class="semantic__topk" @change="handleSearch">
          <el-option v-for="n in [3, 5, 8, 10]" :key="n" :label="`Top ${n}`" :value="n" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="handleSearch">检索</el-button>
        <el-button :loading="syncLoading" @click="handleSync">同步后台数据到 RAG</el-button>
        <el-button tag="a" :href="ragSettingsUrl.href">前往设置 RAG</el-button>
      </div>
      <div class="semantic__examples">
        <span class="semantic__examples-label">试试：</span>
        <el-tag
          v-for="example in examples"
          :key="example"
          class="semantic__example"
          effect="plain"
          @click="runExample(example)"
        >
          {{ example }}
        </el-tag>
      </div>
    </div>

    <div v-if="syncResult" class="content-card semantic__sync-summary">
      <strong>已同步 {{ syncResult.record_count }} 条业务记录 · {{ syncResult.chunk_count }} 个检索分片</strong>
      <p>{{ syncResult.privacy_note }}</p>
      <div class="semantic__examples"><el-tag v-for="(count, type) in syncResult.by_type" :key="type" size="small" effect="plain">{{ documentType(type) }} {{ count }}</el-tag></div>
    </div>

    <div v-if="result" class="content-card">
      <div class="panel-head">
        <span class="panel-title">检索结果</span>
        <span class="panel-sub">
          命中 {{ result.hit_count }} 条 · 向量库共 {{ result.collection_size }} 条文档
        </span>
      </div>
      <ul v-if="result.hits?.length" class="hit-list">
        <li v-for="(hit, index) in result.hits" :key="hit.id" class="hit-item">
          <div class="hit-item__head">
            <span class="hit-item__rank">#{{ index + 1 }}</span>
            <el-tag
              size="small"
              effect="light"
              round
              :type="hit.metadata?.doc_type === 'product' ? 'warning' : 'info'"
            >
              {{ documentType(hit.metadata?.doc_type) }}
            </el-tag>
            <span v-if="hit.metadata?.rating" class="hit-item__rating">
              {{ '★'.repeat(hit.metadata.rating) }}{{ '☆'.repeat(5 - hit.metadata.rating) }}
            </span>
            <span class="hit-item__product">{{ productName(hit) }}</span>
            <span class="hit-item__tags">
              <el-tag v-if="hit.metadata?.has_image" size="small" effect="plain" type="success">
                含晒图
              </el-tag>
              <span class="hit-item__distance" :class="distanceClass(hit.distance)">
                距离 {{ formatDistance(hit.distance) }}
              </span>
            </span>
          </div>
          <div class="hit-item__text" v-html="renderMarkdown(hit.text)"></div>
          <div class="hit-item__meta">
            来源：{{ documentType(hit.metadata?.doc_type) }} ·
            {{ relevanceText(hit.distance) }}
          </div>
        </li>
      </ul>
      <el-empty v-else description="没有命中任何文档" :image-size="60" />
    </div>

    <div v-else class="content-card semantic__placeholder">
      <el-empty description="输入一句话，看看向量库会捞回什么" :image-size="70" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'
import { listProducts } from '@/api/ecommerce'
import { searchSemantic, syncSemanticData } from '@/api/semantic'

defineOptions({ name: 'SemanticSearch' })

/** 与后端 settings.SEMANTIC_RELEVANCE_MAX_DISTANCE 保持一致，改了后端记得同步 */
const RELATED_MAX_DISTANCE = 0.5

const isLocalProjectHost = ['127.0.0.1', 'localhost', '[::1]'].includes(window.location.hostname)
const ragSettingsUrl = new URL('/', window.location.href)
if (isLocalProjectHost) ragSettingsUrl.port = '4173'
else ragSettingsUrl.pathname = '/rag/'

const examples = ['换货后再次申请售后', '缺货预警', '收藏商品到货通知', '退货退款流程', '耳机有杂音']
const syncResult = ref(null)
const typeNames = { product: '商品', review: '评价', order: '订单', review_reply: '评价回复/追加', after_sale: '售后申请', after_sale_message: '售后沟通', after_sale_risk: '售后风险', diagnosis_report: '诊断报告', alert: '预警', platform_log: '平台日志', agent_run: '分析运行', agent_step: '运行步骤', agent_feedback: '分析反馈', user_summary: '匿名用户', address_summary: '收货区域', cart_item: '购物车', favorite: '收藏订阅', direct_conversation: '私聊会话', direct_message: '私聊消息', customer_notice: '降价通知', shipment_notice: '发货通知', review_notice: '评论通知', staff_notice: '商家通知', platform_feature: '功能规则', inventory_state: '库存监测', restock_notice: '到货通知' }
function documentType(type) { return typeNames[type] || '业务资料' }

const query = ref('')
const topK = ref(5)
const loading = ref(false)
const syncLoading = ref(false)
const result = ref(null)
const productNames = ref({})

function formatDistance(distance) {
  return typeof distance === 'number' ? distance.toFixed(3) : '-'
}

function distanceClass(distance) {
  if (typeof distance !== 'number') return ''
  return distance <= RELATED_MAX_DISTANCE ? 'is-related' : 'is-unrelated'
}

function productName(hit) {
  const id = hit.metadata?.product_id
  return productNames.value[id] || hit.metadata?.name || '平台业务'
}

function relevanceText(distance) {
  if (typeof distance !== 'number') return '距离未知'
  return distance <= RELATED_MAX_DISTANCE
    ? `距离 ≤ ${RELATED_MAX_DISTANCE}，判定为相关`
    : `距离 > ${RELATED_MAX_DISTANCE}，判定为不相关`
}

/** 向量文档里可能带 Markdown（晒图描述由大模型生成），按 Markdown 渲染；
 *  breaks 打开，普通评价的换行才不会被合并成一段 */
function renderMarkdown(text) {
  const html = marked.parse(text || '', { async: false, breaks: true })
  return DOMPurify.sanitize(html)
}

async function loadProductNames() {
  const res = await listProducts({ page: 1, page_size: 100 })
  const map = {}
  for (const item of res.data?.list || []) {
    map[item.id] = item.name
  }
  productNames.value = map
}

async function handleSearch() {
  const text = query.value.trim()
  if (!text) return
  loading.value = true
  try {
    const res = await searchSemantic(text, topK.value)
    result.value = res.data || null
  } finally {
    loading.value = false
  }
}

async function handleSync() {
  if (syncLoading.value) return
  syncLoading.value = true
  try {
    const res = await syncSemanticData()
    const data = res.data || {}
    syncResult.value = data
    ElMessage.success(`已同步 ${data.record_count || 0} 条后台业务记录到“电商分析平台”知识库`)
    if (query.value.trim()) await handleSearch()
  } finally {
    syncLoading.value = false
  }
}

function runExample(example) {
  query.value = example
  handleSearch()
}

onMounted(loadProductNames)
</script>

<style scoped>
.semantic {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-gap);
}

.semantic__title {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.semantic__sub {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--app-text-secondary);
}

.semantic__toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 14px;
}

.semantic__input {
  max-width: 460px;
}
.semantic__sync-summary p { color: var(--app-text-secondary); font-size: 13px; line-height: 1.6; }

.semantic__topk {
  width: 110px;
}

.semantic__examples {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.semantic__examples-label {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.semantic__example {
  cursor: pointer;
}

.semantic__placeholder {
  padding: 24px 0;
}

.panel-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
}

.panel-sub {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.hit-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.hit-item {
  padding: 12px 0;
  border-bottom: 1px dashed var(--app-border);
}

.hit-item:last-child {
  border-bottom: none;
}

.hit-item__head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.hit-item__rank {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text-secondary);
}

.hit-item__rating {
  font-size: 13px;
  color: #f59e0b;
  letter-spacing: 1px;
}

.hit-item__product {
  font-size: 13px;
  color: var(--app-text);
}

.hit-item__tags {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.hit-item__distance {
  font-size: 12px;
  padding: 1px 8px;
  border-radius: 999px;
  background: #eef3f0;
  color: var(--app-text-secondary);
}

.hit-item__distance.is-related {
  background: #dcfce7;
  color: #15803d;
}

.hit-item__distance.is-unrelated {
  background: #fee2e2;
  color: #b91c1c;
}

.hit-item__text {
  margin: 8px 0 4px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--app-text);
  word-break: break-word;
}

/* 渲染出来的 Markdown 压一下默认间距，避免命中列表被撑得过松 */
.hit-item__text :deep(p) {
  margin: 6px 0;
}

.hit-item__text :deep(p:first-child) {
  margin-top: 0;
}

.hit-item__text :deep(p:last-child) {
  margin-bottom: 0;
}

.hit-item__text :deep(ul),
.hit-item__text :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}

.hit-item__text :deep(li) {
  margin: 2px 0;
}

.hit-item__text :deep(h1),
.hit-item__text :deep(h2),
.hit-item__text :deep(h3),
.hit-item__text :deep(h4) {
  margin: 10px 0 4px;
  font-size: 14px;
}

.hit-item__text :deep(strong) {
  font-weight: 600;
}

.hit-item__meta {
  font-size: 12px;
  color: var(--app-text-secondary);
}
</style>
