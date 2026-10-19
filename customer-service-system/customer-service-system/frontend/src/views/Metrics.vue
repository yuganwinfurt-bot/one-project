<template>
  <div class="page-container metrics" v-loading="loading">
    <div class="content-card metrics__head">
      <div>
        <div class="metrics__title">Agent 运行观测</div>
        <div class="metrics__sub">
          统计{{ onlyMine ? '我的' : '全部用户' }}运行记录：成功率、耗时与反馈，用来判断 Agent
          稳定性和瓶颈在哪一步。
        </div>
      </div>
      <div class="metrics__side">
        <el-switch v-if="isAdmin" v-model="onlyMine" active-text="只看我的" @change="load" />
        <span v-if="updatedAt" class="metrics__time">更新于 {{ updatedAt }}</span>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
    </div>

    <div class="stat-grid">
      <div
        v-for="card in cards"
        :key="card.label"
        class="stat-card"
        :class="[
          card.tone ? `stat-card--${card.tone}` : '',
          card.action ? 'stat-card--clickable' : ''
        ]"
        :role="card.action ? 'button' : undefined"
        :tabindex="card.action ? 0 : undefined"
        :title="card.action ? '点击查看未完成运行' : undefined"
        @click="card.action && handleCardAction(card.action)"
        @keydown.enter="card.action && handleCardAction(card.action)"
        @keydown.space.prevent="card.action && handleCardAction(card.action)"
      >
        <div class="stat-card__label">{{ card.label }}</div>
        <div class="stat-card__value">{{ card.value }}</div>
        <div class="stat-card__hint">{{ card.hint }}</div>
      </div>
    </div>

    <div class="metrics__row">
      <div class="content-card">
        <div class="panel-head">
          <span class="panel-title">路由分布</span>
          <span class="panel-sub">结构化查询 vs 语义检索</span>
        </div>
        <div ref="routeEl" class="chart"></div>
      </div>

      <div class="content-card">
        <div class="panel-head">
          <span class="panel-title">各阶段平均耗时</span>
          <span class="panel-sub">倒序取前 8，找瓶颈用</span>
        </div>
        <div ref="stepEl" class="chart"></div>
      </div>
    </div>

    <div class="content-card">
      <div class="panel-head">
        <span class="panel-title">近 {{ stats?.trend_days || 14 }} 天运行量</span>
        <span class="panel-sub">共 {{ trendTotal }} 次</span>
      </div>
      <div ref="runEl" class="chart chart--line"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getStats } from '@/api/observability'
import { CHART_COLORS, CHART_TEXT_STYLE, useEchart } from '@/composables/useEchart'
import { useUser } from '@/utils/user'

defineOptions({ name: 'Metrics' })

const { userInfo } = useUser()
const isAdmin = computed(() => userInfo.value?.role === 'admin')
const router = useRouter()

const loading = ref(false)
const stats = ref(null)
const updatedAt = ref('')
const onlyMine = ref(true)

const routeEl = ref(null)
const stepEl = ref(null)
const runEl = ref(null)
const { render: renderRoute } = useEchart(routeEl)
const { render: renderStep } = useEchart(stepEl)
const { render: renderRun } = useEchart(runEl)

/** 步骤名到中文说的映射；历史数据里同一阶段可能有两种写法 */
const STEP_LABELS = {
  starting: '启动',
  context: '多轮上下文',
  routing: '意图路由',
  route: '意图路由',
  scheduling: '任务调度',
  'agent:scheduler': '调度（子图）',
  'agent:analysis': '多角色分析',
  'agent:decision': '动作决策',
  querying: '数据查询',
  deepening: '语义深挖',
  preparing: '证据整合',
  judging: '风险判断',
  deciding: '动作决策',
  confirming: '人工确认',
  executing: '动作执行',
  answering: '生成回答',
  action_pending: '等待确认',
  cancelled: '已取消'
}

const cards = computed(() => {
  const c = stats.value?.cards
  if (!c) return []
  const rated = c.up_count + c.down_count
  return [
    { label: '总运行次数', value: c.total_runs, hint: '含进行中与已取消' },
    { label: '成功', value: c.success_runs, hint: '正常跑完' },
    {
      label: '失败',
      value: c.failed_runs,
      hint: '抛异常终止',
      tone: c.failed_runs ? 'danger' : ''
    },
    { label: '已取消', value: c.cancelled_runs, hint: '用户放弃或中断' },
    {
      label: '未完成',
      value: c.unfinished_runs,
      hint: '进行中 / 待确认 · 点击查看',
      tone: c.unfinished_runs ? 'warning' : '',
      action: 'unfinished'
    },
    {
      label: '成功率',
      value: `${c.success_rate}%`,
      hint: '已结束的运行里成功的比例'
    },
    { label: '平均耗时', value: formatMs(c.avg_elapsed_ms), hint: '仅统计成功运行' },
    {
      label: '点赞率',
      value: rated ? `${c.up_rate}%` : '-',
      hint: rated ? `赞 ${c.up_count} / 踩 ${c.down_count}` : '还没有收到反馈'
    }
  ]
})

const trendPoints = computed(() => stats.value?.run_trend || [])
const trendTotal = computed(() => trendPoints.value.reduce((sum, p) => sum + p.count, 0))

function formatMs(ms) {
  const value = Number(ms || 0)
  if (!value) return '-'
  return value >= 1000 ? `${(value / 1000).toFixed(1)} s` : `${value} ms`
}

function stepLabel(name) {
  return STEP_LABELS[name] || name
}

function handleCardAction(action) {
  if (action === 'unfinished') {
    router.push({
      path: '/manager/history',
      query: { unfinished: '1', only_mine: onlyMine.value ? '1' : '0' }
    })
  }
}

function drawRoute() {
  const buckets = stats.value?.route_distribution || []
  renderRoute({
    color: CHART_COLORS,
    textStyle: CHART_TEXT_STYLE,
    tooltip: { trigger: 'item', formatter: '{b}：{c} 次（{d}%）' },
    legend: { bottom: 0, itemWidth: 10, itemHeight: 10, textStyle: CHART_TEXT_STYLE },
    series: [
      {
        name: '路由分布',
        type: 'pie',
        radius: ['42%', '66%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,
        label: { formatter: '{b} {c}' },
        data: buckets.map((b) => ({ name: b.name, value: b.count }))
      }
    ]
  })
}

function drawStep() {
  const rows = [...(stats.value?.step_stats || [])].reverse()
  renderStep({
    color: [CHART_COLORS[0]],
    textStyle: CHART_TEXT_STYLE,
    grid: { left: 8, right: 64, top: 16, bottom: 8, containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const row = rows[params[0].dataIndex]
        return `${stepLabel(row.step_name)}<br/>平均 ${formatMs(row.avg_ms)} · 最大 ${formatMs(
          row.max_ms
        )}<br/>样本 ${row.count} 次`
      }
    },
    xAxis: {
      type: 'value',
      axisLabel: { formatter: (value) => `${Math.round(value / 1000)}s` },
      splitLine: { lineStyle: { color: '#eef3f0' } }
    },
    yAxis: {
      type: 'category',
      data: rows.map((r) => stepLabel(r.step_name)),
      axisLine: { lineStyle: { color: '#dbe4e1' } },
      axisTick: { show: false }
    },
    series: [
      {
        name: '平均耗时',
        type: 'bar',
        barMaxWidth: 16,
        data: rows.map((r) => r.avg_ms),
        itemStyle: { borderRadius: [0, 4, 4, 0] },
        label: {
          show: true,
          position: 'right',
          formatter: (params) => formatMs(params.value),
          color: '#687984',
          fontSize: 12
        }
      }
    ]
  })
}

function drawRunTrend() {
  const points = trendPoints.value
  renderRun({
    color: [CHART_COLORS[4]],
    textStyle: CHART_TEXT_STYLE,
    grid: { left: 8, right: 16, top: 24, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis', valueFormatter: (value) => `${value} 次` },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: points.map((p) => p.date.slice(5)),
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
        name: '运行量',
        type: 'line',
        smooth: true,
        symbolSize: 6,
        data: points.map((p) => p.count),
        areaStyle: { opacity: 0.12 }
      }
    ]
  })
}

async function load() {
  loading.value = true
  try {
    const res = await getStats({ only_mine: onlyMine.value, trend_days: 14 })
    stats.value = res.data || null
    updatedAt.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    drawRoute()
    drawStep()
    drawRunTrend()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.metrics {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-gap);
}

.metrics__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.metrics__title {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.metrics__sub {
  margin-top: 4px;
  font-size: 13px;
  color: var(--app-text-secondary);
}

.metrics__side {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.metrics__time {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--app-space-gap);
}

.stat-card {
  padding: 14px 16px;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  box-shadow: var(--app-shadow);
}

.stat-card--clickable {
  cursor: pointer;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.stat-card--clickable:hover,
.stat-card--clickable:focus-visible {
  border-color: var(--app-primary, #16a085);
  box-shadow: 0 8px 20px rgb(15 23 42 / 8%);
  outline: none;
  transform: translateY(-1px);
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

.metrics__row {
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
  height: 260px;
}

.chart--line {
  height: 220px;
}

@media (max-width: 1100px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .metrics__row {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
