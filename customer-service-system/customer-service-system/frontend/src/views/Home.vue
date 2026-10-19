<template>
  <div class="page-container dashboard" v-loading="loading">
    <div class="content-card dash-head">
      <div class="dash-head__text">
        <div class="dash-head__title">
          你好，{{ userInfo?.name || userInfo?.username || '同学' }}
        </div>
        <div class="dash-head__sub">
          这里是店铺整体数据概览；需要下钻分析时，去「数据分析对话」直接提问即可。
        </div>
      </div>
      <div class="dash-head__side">
        <span v-if="updatedAt" class="dash-head__time">更新于 {{ updatedAt }}</span>
        <el-tooltip
          placement="bottom"
          content="用固定问题自动跑一遍 Agent（走同一条链路），产出的动作仍需你确认"
        >
          <el-button
            type="primary"
            :icon="MagicStick"
            :loading="patrolRunning"
            @click="handlePatrol"
          >
            一键巡检
          </el-button>
        </el-tooltip>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
    </div>

    <!-- 巡检结果：系统触发的那一次运行，结论与待确认动作都摆在这里 -->
    <div v-if="patrolResult" class="content-card patrol-card">
      <div class="panel-head">
        <span class="panel-title">巡检结果</span>
        <span class="panel-sub">
          系统用固定问题「{{ patrolResult.question }}」触发{{
            patrolResult.reused ? '（沿用上次待确认的结果，未重复运行，回答只保留摘要）' : ''
          }}
        </span>
      </div>
      <div v-if="patrolResult.error" class="patrol-card__error">
        {{ patrolResult.error }}
      </div>
      <template v-else>
        <div class="patrol-card__meta">
          <el-tag size="small" effect="light" round :type="routeTone(patrolResult.route)">
            {{ routeLabel(patrolResult.route) }}
          </el-tag>
          <span>过程已写入「运行历史」</span>
        </div>
        <div v-if="patrolResult.answer" class="patrol-card__answer">
          <div v-html="renderMarkdown(patrolResult.answer)"></div>
        </div>
        <div v-if="patrolResult.actions?.length" class="patrol-card__actions">
          <div class="patrol-card__actions-title">
            发现 {{ patrolResult.actions.length }} 项需要你确认的动作：
          </div>
          <ul>
            <li v-for="(action, index) in patrolResult.actions" :key="index">
              {{ action.title || action.type }}
            </li>
          </ul>
          <el-button type="primary" @click="goHistory">去运行历史确认执行</el-button>
        </div>
        <div v-else class="patrol-card__actions">
          <span class="patrol-card__ok">本次巡检没有需要确认的动作。</span>
          <el-button type="primary" link @click="goHistory">查看运行过程</el-button>
        </div>
      </template>
    </div>

    <div class="stat-grid">
      <button
        v-for="card in cards"
        :key="card.label"
        type="button"
        class="stat-card"
        :class="card.tone ? `stat-card--${card.tone}` : ''"
        :aria-label="`${card.label}：${card.value}，点击查看${card.destination}`"
        :title="`点击查看${card.destination}`"
        @click="navigateToCard(card)"
      >
        <div class="stat-card__label">{{ card.label }}</div>
        <div class="stat-card__value">{{ card.value }}</div>
        <div class="stat-card__hint">{{ card.hint }}</div>
      </button>
    </div>

    <div class="content-card">
      <div class="panel-head">
        <span class="panel-title">近 {{ data?.trend_days || 30 }} 天订单量</span>
        <span class="panel-sub">共 {{ trendTotal }} 单 · {{ formatMoney(trendAmount) }}</span>
      </div>
      <div ref="trendEl" class="chart chart--line"></div>
    </div>

    <div class="dash-row">
      <div class="content-card">
        <div class="panel-head">
          <span class="panel-title">评分分布</span>
          <span class="panel-sub">平均 {{ data?.cards?.avg_rating ?? '-' }} 分</span>
        </div>
        <div ref="ratingEl" class="chart chart--bar"></div>
      </div>

      <div class="content-card">
        <div class="panel-head">
          <span class="panel-title">需要重点关注的商品</span>
          <span class="panel-sub">按差评（≤2 星）条数排序</span>
        </div>
        <ul v-if="worstProducts.length" class="rank-list">
          <li v-for="item in worstProducts" :key="item.product_name" class="rank-item">
            <div class="rank-item__head">
              <span class="rank-item__name">{{ item.product_name }}</span>
              <span class="rank-item__bad">{{ item.bad_count }} 条差评</span>
            </div>
            <div class="rank-item__bar">
              <span
                class="rank-item__bar-inner"
                :style="{ width: badBarWidth(item.bad_count) }"
              ></span>
            </div>
            <div class="rank-item__meta">
              平均 {{ item.avg_rating }} 分 · 共 {{ item.review_count }} 条评价
            </div>
          </li>
        </ul>
        <el-empty v-else description="暂无评价数据" :image-size="60" />
      </div>
    </div>

    <div class="content-card">
      <div class="panel-head">
        <span class="panel-title">最近预警</span>
        <el-button type="primary" link @click="goReports">查看全部</el-button>
      </div>
      <ul v-if="recentAlerts.length" class="alert-list">
        <li v-for="alert in recentAlerts" :key="alert.id" class="alert-item">
          <el-tag
            size="small"
            effect="light"
            round
            :type="alert.level === 'critical' ? 'danger' : 'warning'"
          >
            {{ alert.level === 'critical' ? '严重' : '提醒' }}
          </el-tag>
          <span class="alert-item__content">{{ alert.content }}</span>
          <span class="alert-item__product">{{ alert.product_name || '全店' }}</span>
          <span class="alert-item__time">{{ alert.create_time }}</span>
        </li>
      </ul>
      <el-empty v-else description="还没有触发过预警" :image-size="60" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, Refresh } from '@element-plus/icons-vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { getOverview } from '@/api/ecommerce'
import { runPatrol } from '@/api/patrol'
import { useAlertUnread } from '@/composables/useAlertUnread'
import { CHART_COLORS, CHART_TEXT_STYLE, useEchart } from '@/composables/useEchart'
import { useUser } from '@/utils/user'

defineOptions({ name: 'Home' })

const router = useRouter()
const { userInfo } = useUser()

// 未读数与顶栏铃铛、诊断报告页签共用同一个数据源，避免三处数字不一致
const { unread: alertUnread, refresh: refreshAlertUnread } = useAlertUnread()

const loading = ref(false)
const data = ref(null)
const updatedAt = ref('')

// 巡检：系统触发的运行，结果单独展示，不改对话页的会话
const patrolRunning = ref(false)
const patrolResult = ref(null)

const trendEl = ref(null)
const ratingEl = ref(null)
const { render: renderTrend } = useEchart(trendEl)
const { render: renderRating } = useEchart(ratingEl)

const cards = computed(() => {
  const c = data.value?.cards
  if (!c) return []
  return [
    {
      label: '商品数', value: c.product_count, hint: '全部商品',
      to: '/manager/products', destination: '商品数据'
    },
    {
      label: '订单数', value: c.order_count, hint: '累计订单',
      to: '/manager/orders', destination: '订单数据'
    },
    {
      label: '评价数', value: c.review_count, hint: '累计评价',
      to: '/manager/reviews', destination: '评价数据'
    },
    {
      label: '平均评分', value: c.avg_rating, hint: '满分 5 分',
      to: '/manager/reviews', destination: '评价数据'
    },
    {
      label: '累计成交', value: formatMoney(c.total_amount), hint: '订单实付合计（不含已取消）',
      to: '/manager/orders', destination: '订单数据'
    },
    {
      label: '高风险诊断报告',
      value: c.high_risk_reports,
      hint: 'Agent 判定需人工确认',
      tone: c.high_risk_reports ? 'warning' : '',
      to: '/manager/reports', destination: '诊断报告'
    },
    {
      label: '未读预警',
      value: alertUnread,
      hint: '站内通知',
      tone: alertUnread ? 'danger' : '',
      to: { path: '/manager/reports', query: { tab: 'alerts' } }, destination: '预警列表'
    },
    {
      label: '待复核商品', value: c.pending_review_products, hint: '人工复核状态',
      to: '/manager/products', destination: '商品数据'
    }
  ]
})

const worstProducts = computed(() => data.value?.worst_products || [])
const recentAlerts = computed(() => data.value?.recent_alerts || [])

const trendPoints = computed(() => data.value?.order_trend || [])
const trendTotal = computed(() => trendPoints.value.reduce((sum, p) => sum + p.count, 0))
const trendAmount = computed(() => trendPoints.value.reduce((sum, p) => sum + p.amount, 0))
const maxBadCount = computed(() =>
  Math.max(1, ...worstProducts.value.map((item) => item.bad_count))
)

function formatMoney(value) {
  const num = Number(value || 0)
  return `¥${num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`
}

function badBarWidth(count) {
  return `${Math.max(6, Math.round((count / maxBadCount.value) * 100))}%`
}

function navigateToCard(card) {
  if (card.to) router.push(card.to)
}

function routeLabel(route) {
  if (route === 'structured') return '结构化查询'
  if (route === 'semantic') return '语义检索'
  return '未判定'
}

function routeTone(route) {
  if (route === 'structured') return 'success'
  if (route === 'semantic') return 'info'
  return 'warning'
}

function renderMarkdown(text) {
  // 巡检回答和对话页一样是 Markdown，渲染前统一消毒
  const html = marked.parse(text || '', { async: false })
  return DOMPurify.sanitize(html)
}

async function handlePatrol() {
  if (patrolRunning.value) return
  patrolRunning.value = true
  patrolResult.value = null
  try {
    const res = await runPatrol()
    patrolResult.value = res.data || null
    if (patrolResult.value?.reused) {
      ElMessage.info('上一次巡检还没有确认，已直接沿用结果')
    } else {
      ElMessage.success('巡检完成')
    }
    // 巡检可能写了报告/预警，概览数据要跟着刷新
    await load()
  } finally {
    patrolRunning.value = false
  }
}

function goHistory() {
  router.push('/manager/history')
}

function drawTrend() {
  const points = trendPoints.value
  renderTrend({
    color: [CHART_COLORS[0]],
    textStyle: CHART_TEXT_STYLE,
    grid: { left: 8, right: 16, top: 24, bottom: 8, containLabel: true },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value) => `${value} 单`
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: points.map((p) => p.date.slice(5)),
      axisLine: { lineStyle: { color: '#dbe4e1' } },
      axisTick: { show: false },
      axisLabel: { interval: Math.max(0, Math.ceil(points.length / 10) - 1) }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#eef3f0' } }
    },
    series: [
      {
        name: '订单量',
        type: 'line',
        smooth: true,
        symbolSize: 6,
        data: points.map((p) => p.count),
        areaStyle: { opacity: 0.12 },
        tooltip: {
          // 折线图上顺带给出当天成交额，避免再画一条金额轴
          formatter: (params) => {
            const point = points[params[0].dataIndex]
            return `${point.date}<br/>订单 ${point.count} 单<br/>成交 ${formatMoney(point.amount)}`
          }
        }
      }
    ]
  })
}

function drawRating() {
  const buckets = data.value?.rating_distribution || []
  const colors = { 1: '#b96572', 2: '#d9a441', 3: '#94a3a8', 4: '#6d9d94', 5: '#1a9c81' }
  renderRating({
    textStyle: CHART_TEXT_STYLE,
    grid: { left: 8, right: 16, top: 24, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis', valueFormatter: (value) => `${value} 条` },
    xAxis: {
      type: 'category',
      data: buckets.map((b) => `${b.rating} 星`),
      axisLine: { lineStyle: { color: '#dbe4e1' } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#eef3f0' } }
    },
    series: [
      {
        name: '评价数',
        type: 'bar',
        barMaxWidth: 48,
        data: buckets.map((b) => ({
          value: b.count,
          itemStyle: { color: colors[b.rating] || CHART_COLORS[0], borderRadius: [4, 4, 0, 0] }
        }))
      }
    ]
  })
}

function goReports() {
  router.push('/manager/reports')
}

async function load() {
  loading.value = true
  try {
    // 未读数走共享数据源，刷新时一起对一次，避免"点刷新但未读数不动"
    const [res] = await Promise.all([getOverview({ trend_days: 30 }), refreshAlertUnread()])
    data.value = res.data || null
    updatedAt.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    drawTrend()
    drawRating()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-gap);
}

.dash-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.dash-head__title {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.dash-head__sub {
  margin-top: 4px;
  font-size: 13px;
  color: var(--app-text-secondary);
}

.dash-head__side {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.dash-head__time {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--app-space-gap);
}

.stat-card {
  display: block;
  position: relative;
  width: 100%;
  box-sizing: border-box;
  padding: 14px 16px;
  color: inherit;
  font: inherit;
  text-align: left;
  appearance: none;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  box-shadow: var(--app-shadow);
  cursor: pointer;
  transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
}

.stat-card::after {
  content: '→';
  position: absolute;
  top: 12px;
  right: 16px;
  color: var(--app-primary, #0f9f83);
  font-size: 17px;
  opacity: 0.45;
  transition: opacity 160ms ease, transform 160ms ease;
}

.stat-card:hover {
  border-color: var(--app-primary, #0f9f83);
  box-shadow: 0 6px 18px rgb(15 159 131 / 10%);
  transform: translateY(-2px);
}

.stat-card:hover::after {
  opacity: 1;
  transform: translateX(3px);
}

.stat-card:focus-visible {
  outline: 3px solid rgb(15 159 131 / 30%);
  outline-offset: 2px;
}

.stat-card__label {
  font-size: 13px;
  color: var(--app-text-secondary);
}

.stat-card__value {
  margin: 6px 0 2px;
  font-size: 24px;
  font-weight: 600;
  color: var(--app-text);
  line-height: 1.2;
}

.stat-card__hint {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.stat-card--warning .stat-card__value {
  color: #f59e0b;
}

.stat-card--danger .stat-card__value {
  color: #ef4444;
}

.dash-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--app-space-gap);
}

.panel-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.patrol-card__meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.patrol-card__answer {
  margin-top: 10px;
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #f8fafc;
  font-size: 13px;
  line-height: 1.8;
  color: var(--app-text);
  word-break: break-word;
  max-height: 260px;
  overflow-y: auto;
}

/* 巡检回答是 Markdown，压一下标题和段落的默认间距 */
.patrol-card__answer :deep(h1),
.patrol-card__answer :deep(h2),
.patrol-card__answer :deep(h3),
.patrol-card__answer :deep(h4) {
  margin: 12px 0 6px;
  font-size: 14px;
}

.patrol-card__answer :deep(h1:first-child),
.patrol-card__answer :deep(h2:first-child),
.patrol-card__answer :deep(h3:first-child) {
  margin-top: 0;
}

.patrol-card__answer :deep(p) {
  margin: 6px 0;
}

.patrol-card__answer :deep(ul),
.patrol-card__answer :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}

.patrol-card__answer :deep(hr) {
  border: none;
  border-top: 1px dashed var(--app-border);
  margin: 10px 0;
}

.patrol-card__actions {
  margin-top: 12px;
}

.patrol-card__actions-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text);
}

.patrol-card__actions ul {
  margin: 6px 0 10px;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--app-text);
}

.patrol-card__ok {
  font-size: 13px;
  color: var(--app-text-secondary);
}

.patrol-card__error {
  font-size: 13px;
  color: #b91c1c;
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

.chart {
  width: 100%;
}

.chart--line {
  height: 240px;
}

.chart--bar {
  height: 240px;
}

.rank-list,
.alert-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.rank-item + .rank-item {
  margin-top: 14px;
}

.rank-item__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.rank-item__name {
  font-size: 13px;
  color: var(--app-text);
}

.rank-item__bad {
  font-size: 12px;
  color: #ef4444;
  flex-shrink: 0;
}

.rank-item__bar {
  margin: 6px 0 4px;
  height: 6px;
  border-radius: 999px;
  background: #eef3f0;
  overflow: hidden;
}

.rank-item__bar-inner {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #f59e0b, #ef4444);
}

.rank-item__meta {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 0;
  font-size: 13px;
  border-bottom: 1px dashed var(--app-border);
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-item__content {
  flex: 1;
  color: var(--app-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alert-item__product {
  color: var(--app-text-secondary);
  flex-shrink: 0;
}

.alert-item__time {
  color: var(--app-text-secondary);
  font-size: 12px;
  flex-shrink: 0;
}

@media (max-width: 1100px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dash-row {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
