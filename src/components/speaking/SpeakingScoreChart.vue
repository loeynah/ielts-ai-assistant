<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import SoftCard from '@/components/ui/SoftCard.vue'
import { subScoreFromHistory } from '@/utils/speakingScores'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  history: { type: Array, default: () => [] },
})

const hasData = computed(() => props.history.length > 0)

const option = computed(() => {
  const sorted = [...props.history].reverse()
  const dates = sorted.map((h) => {
    const d = new Date(h.timestamp)
    return `${d.getMonth() + 1}/${d.getDate()}`
  })

  return {
    tooltip: { trigger: 'axis' },
    legend: {
      bottom: 0,
      icon: 'circle',
      itemWidth: 8,
      textStyle: { color: '#64748b', fontSize: 11 },
    },
    grid: { left: 40, right: 20, top: 20, bottom: 48 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      min: 4,
      max: 9,
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
    },
    series: [
      {
        name: '总分',
        type: 'line',
        smooth: true,
        data: sorted.map((h) => h.overall_score),
        lineStyle: { color: '#5b8def', width: 2 },
        itemStyle: { color: '#5b8def' },
        areaStyle: { color: 'rgba(91,141,239,0.08)' },
      },
      {
        name: '流利度 FC',
        type: 'line',
        smooth: true,
        data: sorted.map((h) => subScoreFromHistory(h, 'FC')),
        lineStyle: { color: '#7ba7e8', width: 1.5 },
        itemStyle: { color: '#7ba7e8' },
        showSymbol: false,
      },
      {
        name: '词汇 LR',
        type: 'line',
        smooth: true,
        data: sorted.map((h) => subScoreFromHistory(h, 'LR')),
        lineStyle: { color: '#34d399', width: 1.5 },
        itemStyle: { color: '#34d399' },
        showSymbol: false,
      },
      {
        name: '语法 GRA',
        type: 'line',
        smooth: true,
        data: sorted.map((h) => subScoreFromHistory(h, 'GRA')),
        lineStyle: { color: '#fbbf24', width: 1.5 },
        itemStyle: { color: '#fbbf24' },
        showSymbol: false,
      },
    ],
  }
})
</script>

<template>
  <SoftCard title="口语得分走势" subtitle="多轮练习历史 · 分项维度浮动">
    <div v-if="hasData" class="h-[220px]">
      <VChart class="h-full w-full" :option="option" autoresize />
    </div>
    <p v-else class="py-10 text-center text-sm text-slate-400">
      完成一次模拟考试后，将在此展示得分趋势折线图
    </p>
  </SoftCard>
</template>
