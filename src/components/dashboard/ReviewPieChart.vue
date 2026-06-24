<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import SoftCard from '@/components/ui/SoftCard.vue'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const data = [
  { name: '听力', value: 28, color: '#38bdf8' },
  { name: '阅读', value: 32, color: '#34d399' },
  { name: '口语', value: 18, color: '#5b8def' },
  { name: '写作', value: 22, color: '#fbbf24' },
]

const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}% ({d}%)',
  },
  legend: {
    bottom: 0,
    icon: 'circle',
    itemWidth: 8,
    itemHeight: 8,
    textStyle: { color: '#64748b', fontSize: 12 },
  },
  series: [
    {
      type: 'pie',
      radius: ['48%', '72%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 3,
      },
      label: { show: false },
      data: data.map((d) => ({
        name: d.name,
        value: d.value,
        itemStyle: { color: d.color },
      })),
    },
  ],
}))
</script>

<template>
  <SoftCard title="复习时间占比" subtitle="近 7 日四科任务分配">
    <VChart class="h-[260px] w-full" :option="option" autoresize />
    <div class="mt-2 grid grid-cols-4 gap-2 text-center">
      <div v-for="item in data" :key="item.name" class="rounded-2xl bg-slate-50 py-3">
        <p class="text-lg font-bold text-slate-800">{{ item.value }}%</p>
        <p class="text-xs text-slate-400">{{ item.name }}</p>
      </div>
    </div>
  </SoftCard>
</template>
