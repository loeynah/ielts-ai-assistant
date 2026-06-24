<script setup>
import { onUnmounted, ref, watch } from 'vue'
import ListeningAudioStrip from './ListeningAudioStrip.vue'
import ListeningActionBar from './ListeningActionBar.vue'
import {
  collectAllAnswers,
  collectWrongAnswers,
  injectListeningStyles,
  scrollToQuestion,
  submitObjectiveAnswers,
  syncQuestionNav,
} from '@/utils/listeningIframeBridge'
import { requestListeningDiagnosis } from '@/api/listeningDiagnosis'
import ItemDiagnosisBoard from '@/components/shared/ItemDiagnosisBoard.vue'
import { useUserStore } from '@/stores/user'
import { estimatedListeningBand, formatIeltsBand } from '@/utils/ieltsScore'
import { buildListeningQuestionMeta } from '@/utils/diagnosisNormalize'

const props = defineProps({
  lesson: { type: Object, required: true },
  htmlUrl: { type: String, required: true },
  audioUrl: { type: String, required: true },
})

const iframeRef = ref(null)
const questions = ref([])
const activeQuestionId = ref('')
const timerSeconds = ref(0)
const timerText = ref('00:00')
const gradeResult = ref(null)
const isGrading = ref(false)
const isDiagnosing = ref(false)
const diagnosisResult = ref(null)
const diagnosisError = ref('')
const userStore = useUserStore()

let timerHandle = null
let syncHandle = null

function formatTimer(sec) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function startTimer() {
  stopTimer()
  timerSeconds.value = 0
  timerText.value = '00:00'
  timerHandle = setInterval(() => {
    timerSeconds.value += 1
    timerText.value = formatTimer(timerSeconds.value)
  }, 1000)
}

function stopTimer() {
  if (timerHandle) clearInterval(timerHandle)
  timerHandle = null
}

function startSync() {
  stopSync()
  syncHandle = setInterval(() => {
    if (!iframeRef.value) return
    const nav = syncQuestionNav(iframeRef.value)
    if (nav.length) questions.value = nav
  }, 1500)
}

function stopSync() {
  if (syncHandle) clearInterval(syncHandle)
  syncHandle = null
}

function onIframeLoad() {
  const iframe = iframeRef.value
  if (!iframe) return

  const boot = () => injectListeningStyles(iframe)
  boot()
  setTimeout(boot, 200)
  setTimeout(boot, 600)
  setTimeout(boot, 1200)

  setTimeout(() => {
    const nav = syncQuestionNav(iframe)
    if (nav.length) {
      questions.value = nav
      activeQuestionId.value = nav[0].id
    } else {
      const doc = iframe.contentDocument
      const count = doc?.querySelectorAll('.blank-input').length || 10
      questions.value = Array.from({ length: count }, (_, i) => ({
        id: String(i + 1),
        answered: false,
        correct: false,
        incorrect: false,
      }))
      activeQuestionId.value = '1'
    }
  }, 800)
}

function onSelectQuestion(qId) {
  activeQuestionId.value = qId
  scrollToQuestion(iframeRef.value, qId)
}

async function onSubmitObjective() {
  isGrading.value = true
  diagnosisResult.value = null
  diagnosisError.value = ''

  await new Promise((r) => setTimeout(r, 120))
  const result = submitObjectiveAnswers(iframeRef.value)
  gradeResult.value = result
  questions.value = syncQuestionNav(iframeRef.value)
  stopTimer()
  isGrading.value = false
}

async function onSubmitDiagnosis() {
  if (!gradeResult.value) {
    diagnosisError.value = '请先点击「提交客观题答案」完成批改，再生成 AI 深度诊断。'
    return
  }

  isDiagnosing.value = true
  diagnosisResult.value = null
  diagnosisError.value = ''

  const allAnswers =
    gradeResult.value?.allAnswers ||
    collectAllAnswers(iframeRef.value) ||
    {}

  if (!Object.keys(allAnswers).length) {
    diagnosisError.value = '未能读取作答结果，请重新提交客观题答案后再试。'
    isDiagnosing.value = false
    return
  }

  const wrongAnswers =
    gradeResult.value?.wrongAnswers ||
    collectWrongAnswers(iframeRef.value) ||
    {}

  const questionMeta =
    questions.value.length > 0
      ? questions.value.map((q) => ({
          id: String(q.id).startsWith('q') ? String(q.id) : `q${q.id}`,
          num: String(q.id).replace(/^q/i, ''),
        }))
      : buildListeningQuestionMeta(allAnswers)

  try {
    diagnosisResult.value = await requestListeningDiagnosis({
      lessonId: props.lesson.lessonId,
      wrongAnswers,
      allAnswers,
      questionMeta,
    })
    const items = diagnosisResult.value.items || []
    const total = items.length
    const correct = items.filter((i) => i.is_correct).length
    const score =
      diagnosisResult.value.updated_score ??
      estimatedListeningBand(correct, total)
    userStore.recordGrade('listening', score, {
      title: `听力 ${props.lesson.title} AI 深度诊断已送达`,
      meta: `预估分 ${formatIeltsBand(score)} · ${total - correct} 题需复盘`,
    })
    await userStore.refresh()
    questions.value = syncQuestionNav(iframeRef.value)
  } catch (err) {
    diagnosisError.value = err?.message || '诊断请求失败，请确认已登录且后端已启动。'
  } finally {
    isDiagnosing.value = false
  }
}

watch(
  () => props.lesson.lessonId,
  () => {
    gradeResult.value = null
    diagnosisResult.value = null
    diagnosisError.value = ''
    questions.value = []
    activeQuestionId.value = ''
    startTimer()
    startSync()
  },
  { immediate: true },
)

onUnmounted(() => {
  stopTimer()
  stopSync()
})
</script>

<template>
  <Transition name="fade-up" appear>
    <div class="soft-card w-full overflow-hidden">
      <!-- 上：原生音频控制塔 -->
      <ListeningAudioStrip
        :audio-src="audioUrl"
        :title="lesson.title"
        :section="lesson.section"
      />

      <!-- 中：精简 iframe 填空区 -->
      <div class="listening-iframe-viewport relative w-full overflow-hidden bg-white">
        <iframe
          ref="iframeRef"
          :key="lesson.lessonId"
          :src="htmlUrl"
          class="listening-iframe w-full border-0 bg-white"
          title="listening-practice"
          scrolling="yes"
          @load="onIframeLoad"
        />
      </div>

      <!-- 下：原生交卷 + AI 诊断 -->
      <ListeningActionBar
        :timer-text="timerText"
        :questions="questions"
        :active-question-id="activeQuestionId"
        :grade-result="gradeResult"
        :is-grading="isGrading"
        :is-diagnosing="isDiagnosing"
        @select-question="onSelectQuestion"
        @submit-objective="onSubmitObjective"
        @submit-diagnosis="onSubmitDiagnosis"
      />

      <div
        v-if="diagnosisError"
        class="border-t border-red-100 bg-red-50/60 px-8 py-4 text-sm text-red-600"
      >
        {{ diagnosisError }}
      </div>

      <div
        v-if="diagnosisResult?.items?.length"
        class="border-t border-slate-100 bg-gradient-to-br from-slate-50 to-[var(--color-beige)]/30 px-8 py-8"
      >
        <h4 class="mb-4 text-sm font-semibold text-[var(--color-accent)]">AI 深度诊断报告 · 按题切片</h4>
        <ItemDiagnosisBoard :items="diagnosisResult.items" mode="listening" />
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.listening-iframe-viewport {
  height: min(56vh, 620px);
}

.listening-iframe {
  display: block;
  height: calc(min(56vh, 620px) + 88px);
  margin-top: -88px;
}

.fade-up-enter-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
</style>
