<script setup>
import { computed } from 'vue'
import { Sparkles } from 'lucide-vue-next'
import SoftCard from '@/components/ui/SoftCard.vue'

const props = defineProps({
  result: { type: Object, required: true },
})

const dimensions = computed(() => [
  { key: 'TR_TA', label: '任务回应 TR/TA', color: 'bg-[var(--color-accent)]' },
  { key: 'CC', label: '连贯衔接 CC', color: 'bg-sky-400' },
  { key: 'LR', label: '词汇丰富 LR', color: 'bg-emerald-400' },
  { key: 'GRA', label: '语法多样 GRA', color: 'bg-amber-400' },
])
</script>

<template>
  <SoftCard
    title="AI 深度批改报告"
    subtitle="前雅思考官标准 · 四维度官方评分"
    class="border border-[var(--color-accent-soft)] shadow-[var(--shadow-soft-lg)]"
  >
    <div class="mb-6 flex flex-wrap items-center gap-6">
      <div class="text-center">
        <p class="text-4xl font-bold text-[var(--color-accent)]">{{ result.overall_score }}</p>
        <p class="text-xs text-slate-400">Overall Band</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="dim in dimensions"
          :key="dim.key"
          class="rounded-2xl bg-[var(--color-surface-muted)] px-3 py-2 text-center"
        >
          <p class="text-base font-bold text-slate-800">{{ result.sub_scores?.[dim.key] ?? '—' }}</p>
          <p class="text-[10px] text-slate-400">{{ dim.key }}</p>
        </span>
      </div>
    </div>


    <div class="mb-6 space-y-3">
      <div v-for="dim in dimensions" :key="dim.key">
        <div class="mb-1 flex justify-between text-xs">
          <span class="font-medium text-slate-600">{{ dim.label }}</span>
          <span class="font-semibold text-slate-800">{{ result.sub_scores?.[dim.key] }}</span>
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-slate-100">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="dim.color"
            :style="{ width: `${((result.sub_scores?.[dim.key] ?? 0) / 9) * 100}%` }"
          />
        </div>
      </div>
    </div>


    <div v-if="result.strengths?.length || result.weaknesses?.length" class="mb-6 grid gap-4 md:grid-cols-2">
      <div v-if="result.strengths?.length" class="rounded-3xl bg-emerald-50/50 p-5">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-600">长处</p>
        <ul class="space-y-1.5 text-sm text-slate-700">
          <li v-for="(s, i) in result.strengths" :key="i">· {{ s }}</li>
        </ul>
      </div>
      <div v-if="result.weaknesses?.length" class="rounded-3xl bg-amber-50/50 p-5">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-amber-600">短板</p>
        <ul class="space-y-1.5 text-sm text-slate-700">
          <li v-for="(w, i) in result.weaknesses" :key="i">· {{ w }}</li>
        </ul>
      </div>
    </div>


    <div v-if="result.grammar_highlights?.length" class="mb-6">
      <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">语法修正对照</p>
      <ul class="space-y-2">
        <li
          v-for="(item, idx) in result.grammar_highlights"
          :key="idx"
          class="rounded-2xl bg-[var(--color-surface-muted)] px-4 py-3 text-sm"
        >
          <p>
            <span class="text-red-500 line-through">{{ item.original }}</span>
            <span class="mx-2 text-slate-300">→</span>
            <span class="font-medium text-emerald-700">{{ item.corrected }}</span>
          </p>
          <p class="mt-1 text-xs text-slate-400">{{ item.reason }}</p>
        </li>
      </ul>
    </div>


    <div class="mb-5 rounded-3xl bg-gradient-to-br from-[var(--color-accent-soft)] to-[var(--color-beige)] p-5">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--color-accent)]">
        AI 高分优化范文
      </p>
      <p class="whitespace-pre-line text-sm leading-relaxed text-slate-700">{{ result.polished_essay }}</p>
    </div>


    <div class="flex gap-2 rounded-2xl bg-white px-4 py-3 ring-1 ring-slate-100">
      <Sparkles class="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent)]" />
      <p class="text-sm leading-relaxed text-slate-600">{{ result.general_advice }}</p>
    </div>
  </SoftCard>
</template>
