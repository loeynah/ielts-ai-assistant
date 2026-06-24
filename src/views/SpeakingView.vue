<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { CheckCircle2, ChevronRight, RotateCcw } from 'lucide-vue-next'
import SoftCard from '@/components/ui/SoftCard.vue'
import SpeakingScoreChart from '@/components/speaking/SpeakingScoreChart.vue'
import SpeakingTtsButton from '@/components/speaking/SpeakingTtsButton.vue'
import SpeakingRecorder from '@/components/speaking/SpeakingRecorder.vue'
import SpeakingExamReport from '@/components/speaking/SpeakingExamReport.vue'
import SpeakingPracticeChat from '@/components/speaking/SpeakingPracticeChat.vue'
import {
  SPEAKING_EXAMS,
  SPEAKING_TIMERS,
  getSpeakingExam,
} from '@/config/speakingExams'
import { loadSpeakingHistory } from '@/utils/speakingHistory'
import { requestSpeakingExamGrade } from '@/api/speaking'
import { useUserStore } from '@/stores/user'
import { preloadVoices } from '@/utils/speechTts'
import { countValidExamAnswers, hasValidSpeakingAnswer } from '@/utils/speechValidation'

const modes = [
  { id: 'exam', label: '标准模拟考试', desc: '盲盒录音 · 提交后才揭晓文本' },
  { id: 'practice', label: '自定义训练', desc: '自由对话 · 考官 Part 3 追问' },
]

const activeMode = ref('exam')
const selectedExamId = ref(SPEAKING_EXAMS[0].id)
const history = ref([])
const userStore = useUserStore()
const scrollToChart = ref(false)

/** exam flow: select → part1 → part2_prep → part2_record → part3 → done → report */
const examPhase = ref('select')
const part1Index = ref(0)
const part3Index = ref(0)
const prepSecondsLeft = ref(SPEAKING_TIMERS.part2Prep)
const recordings = ref({ part1: [], part2: null, part3: [] })
const isGrading = ref(false)
const report = ref(null)
const examRecordError = ref('')

let prepTimer = null

const exam = computed(() => getSpeakingExam(selectedExamId.value))

const part1Done = computed(() => recordings.value.part1.length >= exam.value.part1.length)
const part3Done = computed(() => recordings.value.part3.length >= exam.value.part3.length)
const allPartsDone = computed(
  () => part1Done.value && recordings.value.part2 && part3Done.value,
)

const partTabs = [
  { id: 'part1', label: 'PART 1' },
  { id: 'part2', label: 'PART 2' },
  { id: 'part3', label: 'PART 3' },
]

const activeExamPart = computed(() => {
  if (['part1'].includes(examPhase.value)) return 'part1'
  if (['part2_prep', 'part2_record'].includes(examPhase.value)) return 'part2'
  if (['part3', 'done', 'report'].includes(examPhase.value)) return 'part3'
  return ''
})

const recorderSeconds = computed(() => {
  if (examPhase.value === 'part1') return SPEAKING_TIMERS.part1Answer
  if (examPhase.value === 'part2_record') return SPEAKING_TIMERS.part2Record
  if (examPhase.value === 'part3') return SPEAKING_TIMERS.part3Answer
  return 30
})

function selectExam(id) {
  selectedExamId.value = id
  resetExam()
  examPhase.value = 'part1'
}

function resetExam() {
  clearPrepTimer()
  examPhase.value = 'select'
  part1Index.value = 0
  part3Index.value = 0
  prepSecondsLeft.value = SPEAKING_TIMERS.part2Prep
  recordings.value = { part1: [], part2: null, part3: [] }
  report.value = null
}

function clearPrepTimer() {
  clearInterval(prepTimer)
  prepTimer = null
}

function onPart1Recorded(payload) {
  examRecordError.value = ''
  if (!hasValidSpeakingAnswer(payload)) {
    examRecordError.value = '未检测到有效语音（录音过短或转写为空），请重新录音后再进入下一题。'
    return
  }
  recordings.value.part1.push(payload)
  if (part1Index.value < exam.value.part1.length - 1) {
    part1Index.value += 1
  } else {
    examPhase.value = 'part2_prep'
    startPrepCountdown()
  }
}

function startPrepCountdown() {
  prepSecondsLeft.value = SPEAKING_TIMERS.part2Prep
  prepTimer = setInterval(() => {
    prepSecondsLeft.value -= 1
    if (prepSecondsLeft.value <= 0) {
      clearPrepTimer()
      examPhase.value = 'part2_record'
    }
  }, 1000)
}

function skipPrep() {
  clearPrepTimer()
  examPhase.value = 'part2_record'
}

function onPart2Recorded(payload) {
  examRecordError.value = ''
  if (!hasValidSpeakingAnswer(payload)) {
    examRecordError.value = 'Part 2 未检测到有效语音，请重新录音（至少 2 秒且含完整英文回答）。'
    return
  }
  recordings.value.part2 = payload
  examPhase.value = 'part3'
  part3Index.value = 0
}

function onPart3Recorded(payload) {
  examRecordError.value = ''
  if (!hasValidSpeakingAnswer(payload)) {
    examRecordError.value = '未检测到有效语音，请重新录音后再进入下一题。'
    return
  }
  recordings.value.part3.push(payload)
  if (part3Index.value < exam.value.part3.length - 1) {
    part3Index.value += 1
  } else {
    examPhase.value = 'done'
  }
}

function buildExamPayload() {
  const e = exam.value
  return {
    part1: recordings.value.part1.map((rec, i) => ({
      question: e.part1[i] || '',
      transcript: (rec.transcript || '').trim(),
      duration: rec.duration || 0,
    })),
    part2: recordings.value.part2
      ? {
          question: `${e.part2.title}. You should say: ${e.part2.cues.join('. ')}`,
          transcript: (recordings.value.part2.transcript || '').trim(),
          duration: recordings.value.part2.duration || 0,
        }
      : null,
    part3: recordings.value.part3.map((rec, i) => ({
      question: e.part3[i] || '',
      transcript: (rec.transcript || '').trim(),
      duration: rec.duration || 0,
    })),
  }
}

async function submitExam() {
  examRecordError.value = ''
  const payload = buildExamPayload()
  if (countValidExamAnswers(payload) < 1) {
    examRecordError.value = '本次考试未检测到任何有效口语回答，无法交卷评分。请返回重新录音。'
    return
  }
  isGrading.value = true
  try {
    const grade = await requestSpeakingExamGrade({
      examId: selectedExamId.value,
      ...payload,
    })
    report.value = grade
    examPhase.value = 'report'
    await userStore.refresh()
    history.value = await loadSpeakingHistory()
  } finally {
    isGrading.value = false
  }
}

const formatPrep = (s) =>
  `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

onUnmounted(clearPrepTimer)
onMounted(async () => {
  preloadVoices()
  history.value = await loadSpeakingHistory()
})

function onHistoryUpdated(list) {
  history.value = list
}
</script>

<template>
  <div class="flex w-full flex-col gap-8 pb-10">
    <header class="pt-2">
      <p class="text-sm font-medium text-[var(--color-accent)]">Speaking</p>
      <h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-900">口语评测</h1>
      <p class="mt-2 text-slate-500">标准模拟考试 · 自定义训练 · AI深度诊断</p>
    </header>

    <SpeakingScoreChart ref="chartRef" :history="history" :class="scrollToChart ? 'ring-2 ring-[var(--color-accent)]' : ''" />

    <div class="flex flex-wrap gap-3">
      <button
        v-for="mode in modes"
        :key="mode.id"
        type="button"
        class="rounded-2xl px-5 py-3 text-left transition"
        :class="
          activeMode === mode.id
            ? 'bg-[var(--color-accent)] text-white shadow-[var(--shadow-soft-lg)]'
            : 'bg-white text-slate-600 shadow-[var(--shadow-soft)] hover:bg-slate-50'
        "
        @click="activeMode = mode.id"
      >
        <p class="text-sm font-semibold">{{ mode.label }}</p>
        <p class="mt-0.5 text-xs opacity-80">{{ mode.desc }}</p>
      </button>
    </div>

    <!-- 标准模拟考试 -->
    <template v-if="activeMode === 'exam'">
      <!-- PART 进度标签 -->
      <div v-if="examPhase !== 'select'" class="flex flex-wrap gap-2">
        <span
          v-for="tab in partTabs"
          :key="tab.id"
          class="rounded-xl px-5 py-2 text-xs font-semibold transition"
          :class="
            activeExamPart === tab.id
              ? 'bg-[var(--color-accent)] text-white shadow-sm'
              : 'bg-white text-slate-400 ring-1 ring-slate-100'
          "
        >
          {{ tab.label }}
        </span>
      </div>

      <!-- 选卷 -->
      <div v-if="examPhase === 'select'" class="grid gap-4 sm:grid-cols-3">
        <button
          v-for="item in SPEAKING_EXAMS"
          :key="item.id"
          type="button"
          class="soft-card soft-card-hover p-5 text-left transition"
          @click="selectExam(item.id)"
        >
          <p class="font-semibold text-slate-800">{{ item.title }}</p>
          <p class="mt-1 text-xs text-slate-400">Part 1 · {{ item.part1Topic }}</p>
          <p class="mt-3 line-clamp-2 text-sm text-slate-600">{{ item.part2.title }}</p>
          <span class="mt-4 inline-flex items-center gap-1 text-xs font-medium text-[var(--color-accent)]">
            开始通关 <ChevronRight class="h-3.5 w-3.5" />
          </span>
        </button>
      </div>

      <!-- Part 1 -->
      <SoftCard
        v-else-if="examPhase === 'part1'"
        title="Part 1 基础问答"
        :subtitle="`第 ${part1Index + 1} / ${exam.part1.length} 题 · 每题 ${SPEAKING_TIMERS.part1Answer} 秒`"
      >
        <div class="rounded-3xl bg-gradient-to-br from-[var(--color-accent-soft)] to-[var(--color-beige)] p-6">
          <div class="flex items-start gap-3">
            <SpeakingTtsButton :text="exam.part1[part1Index]" />
            <p class="text-lg font-medium text-slate-800">{{ exam.part1[part1Index] }}</p>
          </div>
        </div>
        <div class="mt-6">
          <SpeakingRecorder
            :max-seconds="recorderSeconds"
            :label="`回答第 ${part1Index + 1} 题`"
            @recorded="onPart1Recorded"
          />
          <p v-if="examRecordError" class="mt-3 text-center text-sm text-red-500">{{ examRecordError }}</p>
        </div>
      </SoftCard>

      <!-- Part 2 准备 -->
      <SoftCard
        v-else-if="examPhase === 'part2_prep'"
        title="Part 2 话题卡 · 准备时间"
        subtitle="1 分钟准备 · 期间可构思要点"
      >
        <div class="rounded-3xl bg-gradient-to-br from-[var(--color-accent-soft)] to-[var(--color-beige)] p-8">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-lg font-semibold text-slate-800">{{ exam.part2.title }}</p>
              <p class="mt-2 text-sm text-slate-500">You should say:</p>
              <ul class="mt-3 space-y-2">
                <li
                  v-for="(cue, idx) in exam.part2.cues"
                  :key="idx"
                  class="flex gap-2 text-sm text-slate-700"
                >
                  <span class="font-semibold text-[var(--color-accent)]">{{ idx + 1 }}.</span>
                  {{ cue }}
                </li>
              </ul>
            </div>
            <SpeakingTtsButton :text="`${exam.part2.title}. You should say: ${exam.part2.cues.join('. ')}`" />
          </div>
        </div>
        <div class="mt-8 flex flex-col items-center">
          <p class="font-mono text-4xl font-bold text-[var(--color-accent)]">
            {{ formatPrep(prepSecondsLeft) }}
          </p>
          <p class="mt-2 text-sm text-slate-400">准备倒计时</p>
          <button
            type="button"
            class="mt-6 rounded-2xl bg-[var(--color-accent)] px-6 py-3 text-sm font-semibold text-white hover:opacity-90"
            @click="skipPrep"
          >
            跳过准备，开始录音
          </button>
        </div>
      </SoftCard>

      <!-- Part 2 录音 -->
      <SoftCard
        v-else-if="examPhase === 'part2_record'"
        title="Part 2 话题盲盒"
        subtitle="录音期间不显示任何转写文本 · 限时 2 分钟"
      >
        <div class="rounded-3xl bg-gradient-to-br from-[var(--color-accent-soft)] to-[var(--color-beige)] p-8">
          <div class="flex items-start gap-3">
            <SpeakingTtsButton :text="exam.part2.title" />
            <div>
              <p class="text-lg font-semibold text-slate-800">{{ exam.part2.title }}</p>
              <ul class="mt-3 space-y-1.5">
                <li v-for="(cue, idx) in exam.part2.cues" :key="idx" class="text-sm text-slate-600">
                  {{ idx + 1 }}. {{ cue }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="mt-6">
          <SpeakingRecorder
            :max-seconds="SPEAKING_TIMERS.part2Record"
            label="开始 Part 2 录音"
            @recorded="onPart2Recorded"
          />
          <p v-if="examRecordError" class="mt-3 text-center text-sm text-red-500">{{ examRecordError }}</p>
        </div>
      </SoftCard>

      <!-- Part 3 -->
      <SoftCard
        v-else-if="examPhase === 'part3'"
        title="Part 3 深度追问"
        :subtitle="`第 ${part3Index + 1} / ${exam.part3.length} 题`"
      >
        <div class="rounded-3xl bg-[var(--color-surface-muted)] p-6">
          <div class="flex items-start gap-3">
            <SpeakingTtsButton :text="exam.part3[part3Index]" />
            <p class="text-lg font-medium text-slate-800">{{ exam.part3[part3Index] }}</p>
          </div>
        </div>
        <div class="mt-6">
          <SpeakingRecorder
            :max-seconds="SPEAKING_TIMERS.part3Answer"
            :label="`回答 Part 3 第 ${part3Index + 1} 题`"
            @recorded="onPart3Recorded"
          />
          <p v-if="examRecordError" class="mt-3 text-center text-sm text-red-500">{{ examRecordError }}</p>
        </div>
      </SoftCard>

      <!-- 交卷 -->
      <SoftCard
        v-else-if="examPhase === 'done'"
        title="全部 Part 已完成"
        subtitle="点击交卷后，系统将首次揭晓 STT 文本与 AI 批改"
      >
        <div class="flex flex-col items-center py-8">
          <CheckCircle2 class="mb-4 h-14 w-14 text-emerald-500" />
          <p class="text-slate-600">Part 1 · Part 2 · Part 3 录音均已保存（盲盒模式）</p>
          <p v-if="examRecordError" class="mt-4 text-center text-sm text-red-500">{{ examRecordError }}</p>
          <button
            type="button"
            class="mt-6 rounded-2xl bg-[var(--color-accent)] px-8 py-3.5 text-sm font-semibold text-white shadow-[var(--shadow-soft-lg)] hover:opacity-90 disabled:opacity-50"
            :disabled="!allPartsDone || isGrading"
            @click="submitExam"
          >
            {{ isGrading ? 'STT 转写 + AI 批改中…' : '交卷' }}
          </button>
        </div>
      </SoftCard>

      <!-- 报告 -->
      <Transition name="fade">
        <div v-if="examPhase === 'report' && report" class="space-y-4">
          <SpeakingExamReport :result="report" />
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-medium text-slate-600 shadow-[var(--shadow-soft)] hover:bg-slate-50"
            @click="resetExam"
          >
            <RotateCcw class="h-4 w-4" />
            再练一套
          </button>
        </div>
      </Transition>
    </template>

    <!-- 自定义训练 -->
    <template v-else>
      <SpeakingPracticeChat
        :exam-id="selectedExamId"
        :exam-title="exam.title"
        :initial-question="exam.part3[0]"
        :follow-ups="exam.part3.slice(1)"
        @history-updated="onHistoryUpdated"
        @show-chart="scrollToChart = true"
      />
    </template>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
</style>
