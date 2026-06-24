<script setup>
import { CheckCircle2, Sparkles } from 'lucide-vue-next'

defineProps({
  timerText: { type: String, default: '00:00' },
  questions: { type: Array, default: () => [] },
  activeQuestionId: { type: String, default: '' },
  gradeResult: { type: Object, default: null },
  isGrading: { type: Boolean, default: false },
  isDiagnosing: { type: Boolean, default: false },
})

defineEmits(['select-question', 'submit-objective', 'submit-diagnosis'])
</script>

<template>
  <footer
    class="border-t border-slate-100 bg-gradient-to-b from-white to-[var(--color-accent-soft)]/20 px-8 py-8"
  >
    <div class="mb-6 text-center">
      <p class="text-[11px] font-medium uppercase tracking-widest text-slate-400">
        {{ gradeResult ? '练习用时（已交卷）' : '练习计时' }}
      </p>
      <p class="mt-1 font-mono text-3xl font-semibold tracking-wider text-slate-800">
        {{ timerText }}
      </p>
      <p
        v-if="gradeResult"
        class="mt-3 inline-flex items-center gap-2 rounded-full bg-[var(--color-beige)] px-4 py-1.5 text-sm font-semibold text-slate-700"
      >
        <CheckCircle2 class="h-4 w-4 text-emerald-500" />
        客观题得分：{{ gradeResult.correct }} / {{ gradeResult.total }}
      </p>
    </div>

    <div v-if="questions.length" class="mb-8 flex flex-wrap justify-center gap-3">
      <button
        v-for="q in questions"
        :key="q.id"
        type="button"
        class="flex h-12 min-w-[48px] items-center justify-center rounded-2xl px-4 text-sm font-semibold transition duration-200 hover:-translate-y-0.5 hover:shadow-md"
        :class="[
          activeQuestionId === q.id
            ? 'bg-[var(--color-accent)] text-white shadow-md shadow-blue-200/40'
            : 'bg-white text-slate-600 ring-1 ring-slate-200/80',
          q.correct ? '!bg-emerald-100 !text-emerald-800 !ring-emerald-200' : '',
          q.incorrect ? '!bg-red-50 !text-red-700 !ring-red-200' : '',
          q.answered && !q.correct && !q.incorrect
            ? '!bg-blue-50 !text-blue-700 !ring-blue-200'
            : '',
        ]"
        @click="$emit('select-question', q.id)"
      >
        {{ q.id }}
      </button>
    </div>

    <div class="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
      <button
        type="button"
        class="inline-flex items-center gap-2 rounded-[22px] bg-white px-8 py-4 text-sm font-semibold text-slate-700 shadow-md ring-1 ring-slate-200/80 transition hover:bg-slate-50 disabled:opacity-60"
        :disabled="isGrading || isDiagnosing"
        @click="$emit('submit-objective')"
      >
        <CheckCircle2 class="h-5 w-5 text-[var(--color-accent)]" />
        {{ isGrading ? '批改中…' : '提交客观题答案' }}
      </button>

      <button
        type="button"
        class="group inline-flex items-center gap-2.5 rounded-[22px] bg-gradient-to-r from-[#7ba7e8] to-[#5b8def] px-8 py-4 text-sm font-semibold text-white shadow-lg shadow-blue-200/40 transition hover:brightness-105 disabled:opacity-60"
        :disabled="isDiagnosing || isGrading || !gradeResult"
        @click="$emit('submit-diagnosis')"
      >
        <Sparkles class="h-5 w-5 transition group-hover:animate-pulse" />
        {{ isDiagnosing ? 'AI 诊断生成中…' : '✨ 生成 AI 深度诊断' }}
      </button>
    </div>
  </footer>
</template>
