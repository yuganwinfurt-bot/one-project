/**
 * ECharts 组合式封装：只注册用到的图表与组件，避免整包引入。
 * 组件里只要拿到容器 ref，然后在数据到位时调用 render(option) 即可。
 */
import { nextTick, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  LineChart,
  BarChart,
  PieChart,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  CanvasRenderer
])

export const CHART_COLORS = ['#1a9c81', '#567a8a', '#d9a441', '#b96572', '#78a789', '#887c9a']

/** 图表里统一的字体与文字色，页面按需覆盖 */
export const CHART_TEXT_STYLE = {
  color: '#687984',
  fontFamily: 'inherit'
}

export function useEchart(elRef) {
  const ready = ref(false)
  let chart = null
  let observer = null

  async function render(option) {
    // 数据晚于挂载到达时容器才刚渲染出来，等一次 DOM 再初始化
    await nextTick()
    const el = elRef.value
    if (!el) return
    if (!chart) {
      chart = echarts.init(el)
      // 窗口缩放、侧栏变化都会改变容器宽度，交给 ResizeObserver 兜住
      observer = new ResizeObserver(() => chart && chart.resize())
      observer.observe(el)
      ready.value = true
    }
    chart.setOption(option, true)
  }

  onBeforeUnmount(() => {
    if (observer) observer.disconnect()
    if (chart) chart.dispose()
    observer = null
    chart = null
  })

  return { render, ready }
}
