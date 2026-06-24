<script setup>
import { CheckCircle2 } from 'lucide-vue-next'

const props = defineProps({
  groups: { type: Array, default: () => [] },
  answers: { type: Object, required: true },
  gradeResults: { type: Object, default: () => ({}) },
  gradeSummary: { type: Object, default: null },
  isGrading: { type: Boolean, default: false },
  hasSubmitted: { type: Boolean, default: false },
})

defineEmits(['submit-grade'])

function getBadgeClass(qid) {
  if (!props.hasSubmitted) {
    return 'bg-[var(--color-accent-soft)] text-[var(--color-accent)]'
  }
  const status = props.gradeResults[qid]
  if (status === 'correct') return 'bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200/80'
  if (status === 'incorrect') return 'bg-red-50 text-red-600 ring-1 ring-red-200/80'
  return 'bg-slate-100 text-slate-400 ring-1 ring-slate-200/80'
}
</script>

<template>
  <div
    class="flex h-full min-h-0 flex-col overflow-hidden rounded-[24px] bg-gradient-to-b from-white to-[var(--color-accent-soft)]/10 ring-1 ring-slate-100/80"
  >
    <div class="border-b border-slate-100 px-6 py-4">
      <h3 class="text-lg font-semibold text-slate-800">答题卡</h3>
      <p class="mt-1 text-xs text-slate-400">原生交互 · 判断 / 选择 / 填空</p>
    </div>

    <div class="flex-1 space-y-6 overflow-y-auto overscroll-contain px-5 py-5">
      <section v-for="group in groups" :key="group.groupId" class="space-y-4">
        <h4 class="text-sm font-semibold text-slate-800">{{ group.title }}</h4>
        <div
          v-if="group.introHtml"
          class="rounded-2xl bg-slate-50/80 px-4 py-3 text-xs leading-relaxed text-slate-500"
          v-html="group.introHtml"
        />

        <div
          v-if="group.summaryHtml"
          class="reading-summary rounded-2xl bg-white px-4 py-4 text-sm leading-relaxed text-slate-700 ring-1 ring-slate-100/80"
          v-html="group.summaryHtml"
        />

        <div
          v-if="group.wordPoolOptions?.length"
          class="flex flex-wrap gap-2 rounded-2xl bg-slate-50/80 px-4 py-3"
        >
          <span
            v-for="opt in group.wordPoolOptions"
            :key="opt.value"
            class="rounded-xl bg-white px-2.5 py-1 text-xs text-slate-600 ring-1 ring-slate-200/80"
          >
            {{ opt.label }}
          </span>
        </div>

        <div
          v-for="q in group.questions"
          :key="q.id"
          class="rounded-[20px] bg-white p-4 shadow-sm ring-1 ring-slate-100/80 transition hover:shadow-md hover:ring-[var(--color-accent)]/20"
          :class="
            hasSubmitted && gradeResults[q.id] === 'incorrect'
              ? 'ring-red-100/80'
              : hasSubmitted && gradeResults[q.id] === 'correct'
                ? 'ring-emerald-100/80'
                : ''
          "
        >
          <div
            v-if="group.summaryHtml && q.type === 'select'"
            class="flex items-center gap-3"
          >
            <span
              class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-colors duration-300"
              :class="getBadgeClass(q.id)"
            >
              {{ q.num }}
            </span>
            <select
              v-model="answers[q.id]"
              class="min-w-0 flex-1 rounded-2xl border-0 bg-slate-50 px-4 py-3 text-sm text-slate-700 ring-1 ring-slate-200/80 outline-none focus:ring-[var(--color-accent)]/40"
            >
              <option value="">请选择 {{ q.num }}</option>
              <option v-for="opt in q.options" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <template v-else>
            <p class="mb-3 text-sm font-medium leading-relaxed text-slate-700">
              <span
                class="mr-2 inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-colors duration-300"
                :class="getBadgeClass(q.id)"
              >
                {{ q.num }}
              </span>
              {{ q.label }}
            </p>

            <div v-if="q.type === 'tfng'" class="flex flex-wrap gap-2">
              <button
                v-for="opt in q.options"
                :key="opt"
                type="button"
                class="rounded-2xl px-4 py-2 text-xs font-medium transition"
                :class="
                  answers[q.id] === opt
                    ? 'bg-[var(--color-accent)] text-white shadow-sm'
                    : 'bg-slate-50 text-slate-600 ring-1 ring-slate-200/80 hover:bg-[var(--color-accent-soft)]'
                "
                @click="answers[q.id] = opt"
              >
                {{ opt }}
              </button>
            </div>

            <select
              v-else-if="q.type === 'select'"
              v-model="answers[q.id]"
              class="w-full rounded-2xl border-0 bg-slate-50 px-4 py-3 text-sm text-slate-700 ring-1 ring-slate-200/80 outline-none focus:ring-[var(--color-accent)]/40"
            >
              <option value="">请选择</option>
              <option v-for="opt in q.options" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <input
              v-else-if="q.type === 'blank'"
              v-model="answers[q.id]"
              type="text"
              :placeholder="q.placeholder"
              class="w-full rounded-2xl border-0 bg-slate-50 px-4 py-3 text-sm ring-1 ring-slate-200/80 outline-none focus:ring-[var(--color-accent)]/40"
            />
          </template>
        </div>
      </section>

      <div
        class="mt-2 rounded-[24px] bg-gradient-to-br from-white to-[var(--color-accent-soft)]/20 p-6 shadow-sm ring-1 ring-slate-100/80"
      >
        <p
          v-if="gradeSummary"
          class="mb-4 text-center text-sm font-semibold text-slate-700"
        >
          得分:
          <span class="text-[var(--color-accent)]">{{ gradeSummary.correct }}</span>
          / {{ gradeSummary.total }}
          <span class="ml-2 text-slate-500">(Band {{ gradeSummary.band }})</span>
        </p>

        <button
          type="button"
          class="flex w-full items-center justify-center gap-2 rounded-[22px] bg-white px-6 py-4 text-sm font-semibold text-slate-700 shadow-md ring-1 ring-slate-200/80 transition hover:bg-slate-50 hover:shadow-lg disabled:opacity-60"
          :disabled="isGrading"
          @click="$emit('submit-grade')"
        >
          <CheckCircle2 class="h-5 w-5 text-[var(--color-accent)]" />
          {{ isGrading ? '核对中…' : hasSubmitted ? '重新提交客观题答案' : '提交客观题答案' }}
        </button>

        <p
          v-if="hasSubmitted && gradeSummary"
          class="mt-4 text-center text-xs leading-relaxed text-slate-400"
        >
          客观题已核对完毕，请向下滚动点击
          <span class="font-medium text-[var(--color-accent)]">✨ 生成 AI 深度诊断</span>
          获取错因推导与同义替换解析
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reading-summary :deep(h5) {
  margin: 0 0 0.75rem;
  font-weight: 600;
  color: #1e293b;
}
.reading-summary :deep(p) {
  margin-bottom: 0.75rem;
}
.reading-summary :deep(.summary-blank-mark) {
  color: var(--color-accent);
  font-weight: 600;
}
</style>
