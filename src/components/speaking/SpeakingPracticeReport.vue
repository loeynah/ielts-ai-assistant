<script setup>
import { computed } from 'vue'
import { Sparkles } from 'lucide-vue-next'

const props = defineProps({
  result: { type: Object, required: true },
})

const dimensions = computed(() => [
  { key: 'FC', label: '流利度 FC' },
  { key: 'LR', label: '词汇 LR' },
  { key: 'GRA', label: '语法 GRA' },
  { key: 'P', label: '发音 P' },
])

const overall = computed(() => Number(props.result.overall_score ?? props.result.score) || 0)
const sub = computed(() => props.result.sub_scores || {})
const corrections = computed(() => {
  const c = props.result.examiner_corrections
  return Array.isArray(c) ? c : []
})
</script>

<template>
  <div class="space-y-5 rounded-3xl bg-white p-5 shadow-[var(--shadow-soft)] ring-1 ring-slate-100">
    <div class="flex flex-wrap items-center gap-6">
      <div class="text-center">
        <p class="text-3xl font-bold" :class="overall > 0 ? 'text-[var(--color-accent)]' : 'text-slate-400'">
          {{ overall > 0 ? overall : '—' }}
        </p>
        <p class="text-xs text-slate-400">Overall</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="dim in dimensions"
          :key="dim.key"
          class="rounded-2xl bg-[var(--color-surface-muted)] px-3 py-2 text-center"
        >
          <p class="text-base font-bold text-slate-800">{{ sub[dim.key] ?? '—' }}</p>
          <p class="text-[10px] text-slate-400">{{ dim.label }}</p>
        </span>
      </div>
    </div>


    <div class="space-y-2">
      <div v-for="dim in dimensions" :key="dim.key">
        <div class="mb-1 flex justify-between text-xs">
          <span class="font-medium text-slate-600">{{ dim.label }}</span>
          <span class="font-semibold text-slate-800">{{ sub[dim.key] ?? '—' }}</span>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-slate-100">
          <div
            class="h-full rounded-full bg-[var(--color-accent)] transition-all duration-500"
            :style="{ width: `${((sub[dim.key] ?? 0) / 9) * 100}%` }"
          />
        </div>
      </div>
    </div>

    <div v-if="corrections.length" class="space-y-2">
      <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">考官逐句纠错</p>
      <ul class="space-y-2">
        <li
          v-for="(item, idx) in corrections"
          :key="idx"
          class="rounded-2xl bg-slate-50 px-4 py-3 text-sm"
        >
          <p v-if="item.original">
            <span class="text-red-500 line-through">{{ item.original }}</span>
          </p>
          <p v-if="item.corrected" class="mt-1 font-medium text-emerald-700">{{ item.corrected }}</p>
          <p v-if="item.reason" class="mt-1 text-xs text-slate-500">{{ item.reason }}</p>
        </li>
      </ul>
    </div>

    <div v-if="result.polished_text" class="rounded-3xl bg-emerald-50/60 p-4">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-600">AI 高分示范</p>
      <p class="text-sm leading-relaxed text-emerald-900/80">{{ result.polished_text }}</p>
    </div>

    <div v-if="result.advice" class="flex gap-2 rounded-2xl bg-[var(--color-accent-soft)] px-4 py-3">
      <Sparkles class="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent)]" />
      <p class="text-sm leading-relaxed text-slate-700">{{ result.advice }}</p>
    </div>
  </div>
</template>
