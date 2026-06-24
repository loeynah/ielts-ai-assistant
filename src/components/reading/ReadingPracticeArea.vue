<script setup>
import { computed, reactive, ref, watch } from 'vue'
import ReadingArticlePanel from './ReadingArticlePanel.vue'
import ReadingAnswerConsole from './ReadingAnswerConsole.vue'
import ReadingAiPanels from './ReadingAiPanels.vue'
import { loadReadingExam } from '@/api/readingExamLoader'
import { cleanPassageHtml, parseQuestionGroups } from '@/utils/readingExamParser'
import { gradeReadingAnswers } from '@/utils/readingGrader'
import { flattenReadingQuestions } from '@/utils/diagnosisNormalize'

const props = defineProps({
  lesson: { type: Object, required: true },
})

const loading = ref(true)
const error = ref('')
const exam = ref(null)
const articleHtml = ref('')
const questionGroups = ref([])
const answers = reactive({})

const gradeResults = ref({})
const gradeSummary = ref(null)
const gradedWrongAnswers = ref({})
const gradedAllAnswers = ref({})
const questionMeta = ref([])
const isGrading = ref(false)
const hasSubmitted = ref(false)

const examTitle = computed(() => exam.value?.meta?.title || props.lesson.title)
const passageText = computed(() => {
  const el = document.createElement('div')
  el.innerHTML = articleHtml.value
  return el.textContent || ''
})

function resetGrade() {
  gradeResults.value = {}
  gradeSummary.value = null
  gradedWrongAnswers.value = {}
  gradedAllAnswers.value = {}
  hasSubmitted.value = false
}

async function onSubmitGrade() {
  if (!exam.value?.answerKey) return
  isGrading.value = true
  await new Promise((r) => setTimeout(r, 280))

  const graded = gradeReadingAnswers(answers, exam.value.answerKey)
  gradeResults.value = graded.results
  gradeSummary.value = {
    correct: graded.correct,
    total: graded.total,
    band: graded.band,
  }
  gradedWrongAnswers.value = graded.wrongAnswers
  gradedAllAnswers.value = graded.allAnswers
  hasSubmitted.value = true
  isGrading.value = false
}

async function loadLesson() {
  loading.value = true
  error.value = ''
  exam.value = null
  resetGrade()
  Object.keys(answers).forEach((k) => delete answers[k])

  try {
    const data = await loadReadingExam(props.lesson.examId)
    exam.value = data
    const rawHtml = data.passage?.blocks?.[0]?.html || ''
    articleHtml.value = cleanPassageHtml(rawHtml)
    questionGroups.value = parseQuestionGroups(data)
    questionMeta.value = flattenReadingQuestions(questionGroups.value)
    questionGroups.value.forEach((g) => {
      g.questions.forEach((q) => {
        answers[q.id] = ''
      })
    })
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

watch(() => props.lesson.examId, loadLesson, { immediate: true })
</script>

<template>
  <Transition name="fade-up" appear>
    <div class="w-full space-y-6">
      <div v-if="loading" class="soft-card py-20 text-center text-slate-400">
        正在加载阅读真题…
      </div>

      <div v-else-if="error" class="soft-card py-16 text-center text-red-500">
        {{ error }}
      </div>

      <template v-else>
        <div class="reading-split grid gap-5 lg:grid-cols-2">
          <ReadingArticlePanel :title="examTitle" :html="articleHtml" />
          <ReadingAnswerConsole
            :groups="questionGroups"
            :answers="answers"
            :grade-results="gradeResults"
            :grade-summary="gradeSummary"
            :is-grading="isGrading"
            :has-submitted="hasSubmitted"
            @submit-grade="onSubmitGrade"
          />
        </div>

        <ReadingAiPanels
          :exam-id="lesson.examId"
          :exam-title="examTitle"
          :passage-text="passageText"
          :wrong-answers="gradedWrongAnswers"
          :all-answers="gradedAllAnswers"
          :question-meta="questionMeta"
          :has-submitted="hasSubmitted"
        />
      </template>
    </div>
  </Transition>
</template>

<style scoped>
.fade-up-enter-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

@media (min-width: 1024px) {
  .reading-split {
    height: min(720px, calc(100vh - 14rem));
    min-height: 560px;
  }
}
</style>
