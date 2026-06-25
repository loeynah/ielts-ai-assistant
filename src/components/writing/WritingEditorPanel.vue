<script setup>
import { computed, ref } from 'vue'
import { Sparkles } from 'lucide-vue-next'
import { countWords } from '@/utils/wordCount'

const props = defineProps({
  task: { type: Object, required: true },
  modelValue: { type: String, default: '' },
  secondsLeft: { type: Number, required: true },
  timerActive: { type: Boolean, default: false },
  gradingState: { type: String, default: 'idle' },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const textareaRef = ref(null)

const wordCount = computed(() => countWords(props.modelValue))

const timerLabel = computed(() => {
  const m = Math.floor(props.secondsLeft / 60)
  const s = props.secondsLeft % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const isLocked = computed(() => props.gradingState === 'grading' || props.gradingState === 'graded')
const isGrading = computed(() => props.gradingState === 'grading')
const minWordsMet = computed(() => wordCount.value >= props.task.minWords)

function focusEditor() {
  textareaRef.value?.focus()
}

defineExpose({ focusEditor })
</script>

<template>
  <div class="flex h-full min-h-0 flex-col bg-white">
    <!-- 倒计时 -->
    <div
      class="flex shrink-0 items-center justify-end border-b border-slate-100 bg-white px-6 py-4"
    >
      <div class="text-right">
        <p
          class="font-mono text-3xl font-bold tabular-nums"
          :class="timerActive ? 'text-[var(--color-accent)]' : 'text-slate-300'"
        >
          {{ timerLabel }}
        </p>
        <p class="text-[11px] text-slate-400">
          {{ timerActive ? `剩余时间 · ${task.minutes} 分钟` : '点击选题后开始计时' }}
        </p>
      </div>
    </div>

    <!-- 编辑器 -->
    <div class="relative flex min-h-0 flex-1 flex-col px-6 pt-5">
      <textarea
        ref="textareaRef"
        :value="modelValue"
        class="min-h-0 flex-1 resize-none rounded-3xl bg-[var(--color-surface-muted)]/40 p-5 text-[15px] leading-relaxed text-slate-700 outline-none transition placeholder:text-slate-300 focus:bg-white focus:shadow-[var(--shadow-soft)] disabled:cursor-not-allowed disabled:opacity-60"
        :disabled="isLocked"
        :placeholder="`在此输入你的 ${task.type === 'task1' ? 'Task 1' : 'Task 2'} 作文…`"
        @input="emit('update:modelValue', $event.target.value)"
      />

      <p
        v-if="isGrading"
        class="mt-3 flex shrink-0 items-center gap-2 text-sm text-[var(--color-accent)]"
      >
        <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-[var(--color-accent)] border-t-transparent" />
        AI 阅卷官正在深度扫描文本并评估四大维度得分…
      </p>
    </div>

    <!-- 状态条：固定底边距防截断 -->
    <div
      class="mt-auto flex shrink-0 flex-wrap items-center justify-between gap-3 border-t border-slate-100 bg-white px-6 py-4 pb-6"
    >
      <span class="text-sm text-slate-500">
        Word count:
        <strong
          class="font-semibold"
          :class="minWordsMet ? 'text-emerald-600' : 'text-slate-700'"
        >
          {{ wordCount }}
        </strong>
        <span class="text-slate-400"> / 至少 {{ task.minWords }}</span>
      </span>

      <button
        type="button"
        class="inline-flex items-center gap-2 rounded-2xl bg-[var(--color-accent)] px-6 py-3 text-sm font-semibold text-white shadow-[var(--shadow-soft)] transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="isGrading || isLocked || !modelValue.trim()"
        @click="emit('submit')"
      >
        <Sparkles class="h-4 w-4" :class="isGrading ? 'animate-pulse' : ''" />
        {{ isGrading ? '批改中…' : '提交 AI 深度批改' }}
      </button>
    </div>
  </div>
</template>
