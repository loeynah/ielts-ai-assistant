<script setup>
import { onUnmounted, ref } from 'vue'
import SoftCard from '@/components/ui/SoftCard.vue'
import SpeakingTtsButton from '@/components/speaking/SpeakingTtsButton.vue'
import SpeakingRecorder from '@/components/speaking/SpeakingRecorder.vue'
import SpeakingAudioPlayer from '@/components/speaking/SpeakingAudioPlayer.vue'
import SpeakingPracticeReport from '@/components/speaking/SpeakingPracticeReport.vue'
import { SPEAKING_TIMERS } from '@/config/speakingExams'
import { requestSpeakingPracticeGrade } from '@/api/speaking'
import { loadSpeakingHistory } from '@/utils/speakingHistory'
import { useUserStore } from '@/stores/user'
import { isSpeechRecognitionSupported } from '@/utils/speechStt'
import { hasValidSpeakingAnswer } from '@/utils/speechValidation'

const props = defineProps({
  examId: { type: String, required: true },
  examTitle: { type: String, default: '' },
  initialQuestion: { type: String, required: true },
  followUps: { type: Array, default: () => [] },
})

const emit = defineEmits(['history-updated', 'show-chart'])

const userStore = useUserStore()
const messages = ref([{ role: 'examiner', content: props.initialQuestion }])
const followUpIndex = ref(0)
const showRecorder = ref(true)
const pendingBlob = ref(null)
const transcriptDraft = ref('')
const gradeResult = ref(null)
const isGrading = ref(false)
const inputError = ref('')

const sttSupported = isSpeechRecognitionSupported()

function releasePendingAudio() {
  if (pendingBlob.value?.url) {
    URL.revokeObjectURL(pendingBlob.value.url)
  }
}

async function onRecorded(payload) {
  pendingBlob.value = payload
  transcriptDraft.value = (payload.transcript || '').trim()
  showRecorder.value = false
  inputError.value = ''
}

function resetToRecorder() {
  releasePendingAudio()
  showRecorder.value = true
  pendingBlob.value = null
  transcriptDraft.value = ''
  inputError.value = ''
}

async function submitRecording() {
  if (!pendingBlob.value || isGrading.value) return

  const transcript = transcriptDraft.value.trim()
  const duration = pendingBlob.value?.duration || 0
  if (!hasValidSpeakingAnswer({ transcript, duration })) {
    inputError.value = sttSupported
      ? '未检测到有效语音（录音过短或转写为空），请重新录音，或在下方手动输入至少一句完整英文回答后再提交。'
      : '请在下方输入至少一句完整英文回答后再提交批改。'
    return
  }

  isGrading.value = true
  gradeResult.value = null
  inputError.value = ''

  const currentQ = messages.value.filter((m) => m.role === 'examiner').at(-1)?.content || ''
  messages.value.push({ role: 'user', content: transcript })

  try {
    gradeResult.value = await requestSpeakingPracticeGrade({
      question: currentQ,
      transcript,
      duration,
      examId: props.examId,
      examTitle: props.examTitle,
      rounds: followUpIndex.value + 1,
    })
    await userStore.refresh()
    const list = await loadSpeakingHistory()
    emit('history-updated', list)
  } catch (err) {
    inputError.value = err?.message || '批改失败，请确认后端已启动。'
    messages.value.pop()
  } finally {
    isGrading.value = false
    releasePendingAudio()
    pendingBlob.value = null
  }
}

function continueNext() {
  gradeResult.value = null
  releasePendingAudio()
  transcriptDraft.value = ''
  inputError.value = ''
  const next =
    props.followUps[followUpIndex.value] ||
    'Could you elaborate with a specific example from your own experience?'
  followUpIndex.value += 1
  messages.value.push({ role: 'examiner', content: next })
  showRecorder.value = true
}

function endTraining() {
  emit('show-chart')
}

onUnmounted(releasePendingAudio)
</script>

<template>
  <SoftCard title="Part 3 自定义训练" subtitle="录音转写 · 确认后由 AI 根据你的真实回答批改">
    <div class="chat-console">
      <div class="max-h-[320px] space-y-4 overflow-y-auto rounded-[24px] bg-slate-50/60 px-5 py-5">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="flex w-full"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div class="flex max-w-[88%] items-start gap-2" :class="msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'">
            <SpeakingTtsButton v-if="msg.role === 'examiner'" :text="msg.content" />
            <div class="rounded-[18px] px-4 py-3 text-sm leading-relaxed" :class="msg.role === 'user' ? 'user-bubble' : 'ai-bubble'">
              {{ msg.content }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="showRecorder" class="mt-4 px-1">
        <SpeakingRecorder
          :max-seconds="SPEAKING_TIMERS.part3Answer"
          :countdown="true"
          label="开始录音回答"
          @recorded="onRecorded"
        />
      </div>

      <div v-else-if="pendingBlob && !gradeResult" class="mt-4 space-y-4 px-1">
        <SpeakingAudioPlayer v-if="pendingBlob.url" :src="pendingBlob.url" />

        <div class="rounded-2xl bg-white p-4 ring-1 ring-slate-100">
          <p class="mb-2 text-xs font-semibold text-slate-500">你的回答（STT 转写，可编辑）</p>
          <textarea
            v-model="transcriptDraft"
            rows="6"
            placeholder="请在此输入或确认你的英文回答…"
            class="w-full resize-y rounded-xl bg-slate-50 px-4 py-3 text-sm leading-relaxed text-slate-700 outline-none ring-1 ring-slate-200 focus:ring-[var(--color-accent)]/40"
          />
          <p v-if="!sttSupported" class="mt-2 text-xs text-amber-600">
            浏览器不支持自动转写，请手动输入你的回答。
          </p>
          <p v-else-if="transcriptDraft" class="mt-2 text-xs text-slate-400">
            转写可能不完整，请听录音核对后编辑，再提交批改。
          </p>
        </div>
        <p v-if="inputError" class="text-center text-sm text-red-500">{{ inputError }}</p>
        <div class="flex justify-center gap-3">
          <button
            type="button"
            class="rounded-2xl bg-white px-6 py-3 text-sm font-semibold text-slate-600 ring-1 ring-slate-200"
            @click="resetToRecorder"
          >
            重新录音
          </button>
          <button
            type="button"
            class="rounded-2xl bg-[var(--color-accent)] px-8 py-3 text-sm font-semibold text-white shadow-[var(--shadow-soft)] hover:opacity-90 disabled:opacity-60"
            :disabled="isGrading"
            @click="submitRecording"
          >
            {{ isGrading ? 'AI 批改中…' : '确认提交批改' }}
          </button>
        </div>
      </div>

      <div v-if="gradeResult" class="mt-5 space-y-4">
        <SpeakingPracticeReport :result="gradeResult" />
        <div class="flex flex-wrap gap-2">
          <button type="button" class="rounded-xl bg-[var(--color-accent)] px-4 py-2 text-xs font-semibold text-white" @click="continueNext">
            继续挑战下一题
          </button>
          <button type="button" class="rounded-xl bg-white px-4 py-2 text-xs font-semibold text-slate-600 ring-1 ring-slate-100" @click="endTraining">
            结束训练查看当前分数走势
          </button>
        </div>
      </div>
    </div>
  </SoftCard>
</template>
