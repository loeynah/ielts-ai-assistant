<script setup>
import { ref } from 'vue'
import { BookMarked, MessageCircle, Sparkles, Send } from 'lucide-vue-next'
import SoftCard from '@/components/ui/SoftCard.vue'
import ItemDiagnosisBoard from '@/components/shared/ItemDiagnosisBoard.vue'
import { requestReadingAssistant, requestReadingDiagnosis } from '@/api/readingDiagnosis'
import { useUserStore } from '@/stores/user'
import { formatIeltsBand } from '@/utils/ieltsScore'

const props = defineProps({
  examId: { type: String, required: true },
  examTitle: { type: String, default: '' },
  passageText: { type: String, default: '' },
  wrongAnswers: { type: Object, default: () => ({}) },
  allAnswers: { type: Object, default: () => ({}) },
  questionMeta: { type: Array, default: () => [] },
  hasSubmitted: { type: Boolean, default: false },
})

const userStore = useUserStore()
const isDiagnosing = ref(false)
const diagnosis = ref(null)
const assistantMode = ref('sentence')
const assistantInput = ref('')
const assistantMessages = ref([
  { role: 'ai', content: '我是阅读随身 AI 助理。可粘贴长难句拆解成分，或输入单词查释义与同义替换。' },
])
const isAssistantLoading = ref(false)

async function runDiagnosis() {
  if (!Object.keys(props.allAnswers).length) return
  isDiagnosing.value = true
  diagnosis.value = null
  try {
    diagnosis.value = await requestReadingDiagnosis({
      examId: props.examId,
      wrongAnswers: props.wrongAnswers,
      allAnswers: props.allAnswers,
      questionMeta: props.questionMeta,
      passageText: props.passageText,
    })
    const items = diagnosis.value.items || []
    const wrongCount = items.filter((i) => !i.is_correct).length
    const score = diagnosis.value.updated_score ?? 6
    userStore.recordGrade('reading', score, {
      title: `阅读 ${props.examTitle || props.examId} AI 深度诊断已送达`,
      meta: `预估分 ${formatIeltsBand(score)} · ${wrongCount} 题需复盘`,
    })
    await userStore.refresh()
  } finally {
    isDiagnosing.value = false
  }
}

async function sendAssistant() {
  const text = assistantInput.value.trim()
  if (!text || isAssistantLoading.value) return
  assistantMessages.value.push({ role: 'user', content: text })
  assistantInput.value = ''
  isAssistantLoading.value = true
  const reply = await requestReadingAssistant({
    mode: assistantMode.value,
    text,
    examTitle: props.examTitle,
  })
  assistantMessages.value.push({ role: 'ai', content: reply })
  isAssistantLoading.value = false
}
</script>

<template>
  <div class="space-y-6">
    <SoftCard title="AI 深度诊断" subtitle="客观错题切片解析 · 同义替换词对">
      <p v-if="!hasSubmitted" class="mb-4 rounded-2xl bg-slate-50 px-4 py-3 text-xs text-slate-500">
        请先在右侧答题卡底部完成「提交客观题答案」核对，再生成 AI 深度诊断。
      </p>

      <button
        type="button"
        class="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-[#7ba7e8] to-[#5b8def] px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-200/30 transition hover:brightness-105 disabled:opacity-60"
        :disabled="isDiagnosing || !hasSubmitted"
        @click="runDiagnosis"
      >
        <Sparkles class="h-4 w-4" />
        {{ isDiagnosing ? 'AI 分析中…' : '✨ 生成 AI 深度诊断' }}
      </button>

      <p v-if="hasSubmitted && questionMeta.length" class="mt-3 text-xs text-slate-400">
        共 {{ questionMeta.length }} 题 · 题号 {{ questionMeta[0]?.num }}–{{ questionMeta[questionMeta.length - 1]?.num }}
      </p>

      <div v-if="diagnosis?.items?.length" class="mt-6">
        <ItemDiagnosisBoard :items="diagnosis.items" mode="reading" />
      </div>
    </SoftCard>

    <SoftCard title="阅读随身 AI 助理" subtitle="长难句成分拆解 · 智能查词与同义替换追踪">
      <div class="mb-4 flex gap-2">
        <button
          type="button"
          class="rounded-2xl px-4 py-2 text-xs font-medium transition"
          :class="assistantMode === 'sentence' ? 'bg-[var(--color-accent-soft)] text-[var(--color-accent)]' : 'bg-slate-50 text-slate-500'"
          @click="assistantMode = 'sentence'"
        >
          <MessageCircle class="mr-1 inline h-3.5 w-3.5" />
          长难句分析
        </button>
        <button
          type="button"
          class="rounded-2xl px-4 py-2 text-xs font-medium transition"
          :class="assistantMode === 'word' ? 'bg-[var(--color-accent-soft)] text-[var(--color-accent)]' : 'bg-slate-50 text-slate-500'"
          @click="assistantMode = 'word'"
        >
          <BookMarked class="mr-1 inline h-3.5 w-3.5" />
          智能查词
        </button>
      </div>

      <div class="chat-console">
        <div class="max-h-[200px] space-y-3 overflow-y-auto rounded-[20px] bg-slate-50/60 px-4 py-4">
          <div
            v-for="(msg, idx) in assistantMessages"
            :key="idx"
            class="flex"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[90%] whitespace-pre-wrap rounded-[16px] px-4 py-2.5 text-xs leading-relaxed"
              :class="msg.role === 'user' ? 'user-bubble' : 'ai-bubble'"
            >
              {{ msg.content }}
            </div>
          </div>
        </div>
        <div class="mt-3 flex gap-2 px-1 pb-1">
          <input
            v-model="assistantInput"
            type="text"
            :placeholder="assistantMode === 'word' ? '输入单词，如 ubiquitous' : '粘贴不懂的长难句…'"
            class="flex-1 rounded-2xl bg-white px-4 py-2.5 text-sm ring-1 ring-slate-200/60 outline-none focus:ring-[var(--color-accent)]/40"
            @keydown.enter="sendAssistant"
          />
          <button
            type="button"
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--color-accent)] text-white"
            :disabled="isAssistantLoading"
            @click="sendAssistant"
          >
            <Send class="h-4 w-4" />
          </button>
        </div>
      </div>
    </SoftCard>
  </div>
</template>
