<script setup>
import { computed, ref } from 'vue'
import { Sparkles } from 'lucide-vue-next'
import SoftCard from '@/components/ui/SoftCard.vue'

const props = defineProps({
  result: { type: Object, required: true },
})

const activePart = ref('part1')

const partTabs = [
  { id: 'part1', label: '查看 Part 1 报告' },
  { id: 'part2', label: '查看 Part 2 报告' },
  { id: 'part3', label: '查看 Part 3 报告' },
]

const partData = computed(() => props.result.parts?.[activePart.value] || null)

const legacyMode = computed(() => !props.result.parts)

const noAnswer = computed(() => {
  const text = partData.value?.user_text || ''
  return !text || text.includes('未检测到有效语音') || text.includes('未作答')
})

const overallLabel = computed(() => {
  if (props.result.overall_score === 0) return '未作答'
  return 'Overall'
})
</script>

<template>
  <SoftCard
    title="AI 批改报告"
    subtitle="Part 级报告分发 · 四维度官方标准批改"
    class="border-2 border-[var(--color-accent-soft)]"
  >
    <div class="mb-6 flex flex-wrap items-center gap-6">
      <div class="text-center">
        <p class="text-4xl font-bold" :class="result.overall_score === 0 ? 'text-slate-400' : 'text-[var(--color-accent)]'">
          {{ result.overall_score === 0 ? '—' : result.overall_score }}
        </p>
        <p class="text-xs text-slate-400">{{ overallLabel }}</p>
      </div>
      <div v-if="result.sub_scores" class="flex flex-wrap gap-3">
        <span
          v-for="(score, key) in result.sub_scores"
          :key="key"
          class="rounded-2xl bg-[var(--color-surface-muted)] px-4 py-2 text-center"
        >
          <p class="text-lg font-bold text-slate-800">{{ score }}</p>
          <p class="text-[10px] text-slate-400">{{ key }}</p>
        </span>
      </div>
    </div>

    <div v-if="!legacyMode" class="mb-5 flex flex-wrap gap-2">
      <button
        v-for="tab in partTabs"
        :key="tab.id"
        type="button"
        class="rounded-xl px-4 py-2 text-xs font-semibold transition"
        :class="
          activePart === tab.id
            ? 'bg-[var(--color-accent)] text-white shadow-sm'
            : 'bg-white text-slate-500 ring-1 ring-slate-100 hover:bg-slate-50'
        "
        @click="activePart = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <template v-if="partData">
      <div v-if="partData.sub_scores" class="mb-4 flex flex-wrap gap-2">
        <span
          v-for="(score, key) in partData.sub_scores"
          :key="key"
          class="rounded-xl bg-[var(--color-accent-soft)] px-3 py-1.5 text-xs font-semibold text-[var(--color-accent)]"
        >
          {{ key }}: {{ score }}
        </span>
      </div>
      <div class="grid gap-4 md:grid-cols-2">
        <div class="rounded-3xl bg-red-50/60 p-5">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-red-400">你的原文 (STT)</p>
          <p class="text-sm leading-relaxed" :class="noAnswer ? 'text-slate-400 italic' : 'text-red-900/80'">
            {{ partData.user_text || '（未检测到有效语音，无法转写）' }}
          </p>
        </div>
        <div class="rounded-3xl bg-emerald-50/60 p-5">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-500">AI 高分范文</p>
          <p class="text-sm leading-relaxed" :class="noAnswer || !partData.polished_text ? 'text-slate-400 italic' : 'text-emerald-900/80'">
            {{ noAnswer || !partData.polished_text ? '（需先完成有效作答后才能生成范文）' : partData.polished_text }}
          </p>
        </div>
      </div>
      <ul class="mt-5 space-y-2">
        <li
          v-for="(tip, idx) in partData.advice"
          :key="idx"
          class="flex gap-2 rounded-2xl bg-[var(--color-accent-soft)] px-4 py-3 text-sm text-slate-700"
        >
          <Sparkles class="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent)]" />
          {{ tip }}
        </li>
      </ul>
    </template>

    <template v-else>
      <div class="grid gap-4 md:grid-cols-2">
        <div class="rounded-3xl bg-red-50/60 p-5">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-red-400">你的原文 (STT)</p>
          <p class="text-sm leading-relaxed text-red-900/80">{{ result.user_original_text }}</p>
        </div>
        <div class="rounded-3xl bg-emerald-50/60 p-5">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-500">AI 高分范文</p>
          <p class="text-sm leading-relaxed text-emerald-900/80">{{ result.polished_text }}</p>
        </div>
      </div>
      <ul class="mt-5 space-y-2">
        <li
          v-for="(tip, idx) in result.suggestions"
          :key="idx"
          class="flex gap-2 rounded-2xl bg-[var(--color-accent-soft)] px-4 py-3 text-sm text-slate-700"
        >
          <Sparkles class="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent)]" />
          {{ tip }}
        </li>
      </ul>
    </template>

    <p v-if="result.general_advice" class="mt-5 text-sm text-slate-500">{{ result.general_advice }}</p>
  </SoftCard>
</template>
