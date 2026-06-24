<script setup>
import { computed, nextTick, onUnmounted, ref } from 'vue'
import { RotateCcw } from 'lucide-vue-next'
import WritingTaskSelector from '@/components/writing/WritingTaskSelector.vue'
import WritingEmptyState from '@/components/writing/WritingEmptyState.vue'
import WritingConfirmationGate from '@/components/writing/WritingConfirmationGate.vue'
import WritingDualWorkspace from '@/components/writing/WritingDualWorkspace.vue'
import WritingGradingReport from '@/components/writing/WritingGradingReport.vue'
import {
  WRITING_MENU_ITEMS,
  getDemoTask,
  getWritingTask,
  isDemoId,
} from '@/config/writingExams'
import { requestWritingGrade } from '@/api/writingGrading'
import { useUserStore } from '@/stores/user'

const examState = ref('empty')

const selectedId = ref(null)
const activeTask = ref('task1')

const essayText = ref('')
const gradingState = ref('idle')
const report = ref(null)

const secondsLeft = ref(20 * 60)
const timerActive = ref(false)
const workspaceRef = ref(null)
const userStore = useUserStore()
let timerId = null

const isDemoMode = computed(() => selectedId.value && isDemoId(selectedId.value))

const currentTask = computed(() => {
  if (!selectedId.value) return null
  if (isDemoMode.value) {
    return getDemoTask(selectedId.value)
  }
  return getWritingTask(selectedId.value, activeTask.value)
})

const selectionMeta = computed(() => {
  const item = WRITING_MENU_ITEMS.find((m) => m.id === selectedId.value)
  const taskLabel =
    isDemoMode.value || activeTask.value === 'task2' ? 'Task 2 (大作文)' : 'Task 1 (小作文)'
  return {
    setLabel: item?.label ?? '—',
    taskLabel,
    minutes: currentTask.value?.minutes ?? 20,
  }
})

function syncTimerDisplay() {
  const task = currentTask.value
  if (!task) return
  secondsLeft.value = task.minutes * 60
}

function clearTimer() {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
  timerActive.value = false
}

function startTimer() {
  clearTimer()
  syncTimerDisplay()
  timerActive.value = true
  timerId = setInterval(() => {
    if (secondsLeft.value > 0 && gradingState.value === 'idle') {
      secondsLeft.value -= 1
    }
  }, 1000)
}

function resetContent() {
  essayText.value = ''
  gradingState.value = 'idle'
  report.value = null
}

function enterLockedState() {
  examState.value = 'locked'
  clearTimer()
  resetContent()
  syncTimerDisplay()
}

function onSelectItem(id) {
  const wasDemo = selectedId.value && isDemoId(selectedId.value)
  selectedId.value = id
  if (isDemoId(id)) {
    activeTask.value = 'task2'
  } else if (wasDemo) {
    activeTask.value = 'task1'
  }
  enterLockedState()
}

function onSelectTask(taskKey) {
  if (!selectedId.value) return
  if (isDemoMode.value && taskKey === 'task1') return
  activeTask.value = taskKey
  enterLockedState()
}

async function confirmStartExam() {
  if (!currentTask.value) return
  examState.value = 'active'
  resetContent()
  startTimer()
  await nextTick()
  workspaceRef.value?.focusEditor()
}

async function submitEssay() {
  const task = currentTask.value
  if (!task || !essayText.value.trim() || gradingState.value !== 'idle') return

  gradingState.value = 'grading'
  report.value = null
  clearTimer()

  try {
    report.value = await requestWritingGrade({
      taskId: task.id,
      taskType: task.type,
      essayText: essayText.value,
      prompt: task.prompt,
    })
    gradingState.value = 'graded'
    await userStore.refresh()
  } catch {
    gradingState.value = 'idle'
    if (examState.value === 'active') {
      startTimer()
    }
  }
}

function retryTask() {
  resetContent()
  if (examState.value === 'active') {
    startTimer()
    nextTick(() => workspaceRef.value?.focusEditor())
  }
}

onUnmounted(clearTimer)
</script>

<template>
  <div class="flex w-full flex-col gap-5 pb-12">
    <header class="pt-1">
      <p class="text-sm font-medium text-[var(--color-accent)]">Writing</p>
      <h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-900">写作机考工作台</h1>
      <p class="mt-2 text-slate-500">真题组合 · 全场景机考模拟 · AI 四维深度批改评估</p>
    </header>

    <WritingTaskSelector
      :selected-id="selectedId"
      :active-task="activeTask"
      @select-item="onSelectItem"
      @select-task="onSelectTask"
    />


    <Transition name="fade" mode="out-in">
      <WritingEmptyState v-if="examState === 'empty'" key="empty" />

      <WritingConfirmationGate
        v-else-if="examState === 'locked' && currentTask"
        key="locked"
        :set-label="selectionMeta.setLabel"
        :task-label="selectionMeta.taskLabel"
        :minutes="selectionMeta.minutes"
        @confirm="confirmStartExam"
      />

      <WritingDualWorkspace
        v-else-if="examState === 'active' && currentTask"
        :key="currentTask.id"
        ref="workspaceRef"
        v-model="essayText"
        :task="currentTask"
        :seconds-left="secondsLeft"
        :timer-active="timerActive"
        :grading-state="gradingState"
        @submit="submitEssay"
      />
    </Transition>

    <Transition name="slide-up">
      <div v-if="examState === 'active' && report && gradingState === 'graded'" class="space-y-4">
        <WritingGradingReport :result="report" />
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-medium text-slate-600 shadow-[var(--shadow-soft)] hover:bg-slate-50"
          @click="retryTask"
        >
          <RotateCcw class="h-4 w-4" />
          重新作答本题
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.slide-up-enter-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(16px);
}
</style>
