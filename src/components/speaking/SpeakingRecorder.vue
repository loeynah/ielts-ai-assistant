<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { Mic, Square, EyeOff } from 'lucide-vue-next'
import { createLiveTranscriber } from '@/utils/speechStt'

const props = defineProps({
  maxSeconds: { type: Number, default: 30 },
  countdown: { type: Boolean, default: true },
  disabled: { type: Boolean, default: false },
  label: { type: String, default: '开始录音' },
})

const emit = defineEmits(['recorded', 'timeout'])

const phase = ref('idle') // idle | recording
const secondsLeft = ref(0)
const secondsElapsed = ref(0)
const waveHeights = ref(Array.from({ length: 12 }, () => 20))

let timer = null
let waveTimer = null
let mediaRecorder = null
let audioChunks = []
let transcriber = null
let recordStartedAt = 0

const displayTime = computed(() => {
  const s = props.countdown ? secondsLeft.value : secondsElapsed.value
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
})

function animateWaves() {
  waveTimer = setInterval(() => {
    waveHeights.value = waveHeights.value.map(() => 12 + Math.random() * 36)
  }, 120)
}

function clearTimers() {
  clearInterval(timer)
  clearInterval(waveTimer)
  timer = null
  waveTimer = null
}

async function startRecording() {
  if (props.disabled || phase.value === 'recording') return
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []
    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data)
    mediaRecorder.start()
    transcriber = createLiveTranscriber()
    transcriber?.start()
    phase.value = 'recording'
    recordStartedAt = Date.now()
    secondsLeft.value = props.maxSeconds
    secondsElapsed.value = 0
    animateWaves()

    timer = setInterval(() => {
      if (props.countdown) {
        secondsLeft.value -= 1
        if (secondsLeft.value <= 0) {
          stopRecording(true)
        }
      } else {
        secondsElapsed.value += 1
      }
    }, 1000)
  } catch {
    alert('无法访问麦克风，请检查浏览器权限。')
  }
}

function stopRecording(timedOut = false) {
  if (!mediaRecorder || mediaRecorder.state === 'inactive') return
  clearTimers()
  mediaRecorder.onstop = () => {
    const blob = new Blob(audioChunks, { type: 'audio/webm' })
    const url = URL.createObjectURL(blob)
    const elapsedSec = recordStartedAt ? (Date.now() - recordStartedAt) / 1000 : 0
    const duration = Math.max(
      elapsedSec,
      props.countdown ? props.maxSeconds - secondsLeft.value : secondsElapsed.value,
    )

    const finish = (transcript) => {
      transcriber = null
      mediaRecorder.stream.getTracks().forEach((t) => t.stop())
      phase.value = 'idle'
      emit('recorded', { blob, url, duration, transcript: transcript || '' })
      if (timedOut) emit('timeout')
    }

    if (transcriber) {
      const activeTranscriber = transcriber
      activeTranscriber
        .stop()
        .then((transcript) => finish(transcript))
        .catch(() => finish(activeTranscriber.getText() || ''))
    } else {
      finish('')
    }
  }
  mediaRecorder.stop()
}

onUnmounted(() => {
  clearTimers()
  if (mediaRecorder?.stream) {
    mediaRecorder.stream.getTracks().forEach((t) => t.stop())
  }
})

watch(
  () => props.maxSeconds,
  (v) => {
    if (phase.value === 'idle') secondsLeft.value = v
  },
)
</script>

<template>
  <div
    class="flex flex-col items-center rounded-3xl border border-dashed border-[var(--color-accent-soft)] bg-white/80 py-10"
  >
    <div
      class="mb-4 flex h-20 w-20 items-center justify-center rounded-full transition"
      :class="phase === 'recording' ? 'bg-red-50 text-red-500' : 'bg-[var(--color-accent-soft)] text-[var(--color-accent)]'"
    >
      <Mic class="h-9 w-9" :class="phase === 'recording' ? 'animate-pulse' : ''" />
    </div>

    <p
      v-if="phase === 'recording'"
      class="mb-3 font-mono text-2xl font-bold tabular-nums"
      :class="countdown && secondsLeft <= 10 ? 'text-red-500' : 'text-[var(--color-accent)]'"
    >
      {{ displayTime }}
    </p>

    <div v-if="phase === 'recording'" class="mb-4 flex h-10 items-end gap-1">
      <span
        v-for="(h, i) in waveHeights"
        :key="i"
        class="w-1 rounded-full bg-[var(--color-accent)]/60 transition-all duration-150"
        :style="{ height: `${h}px` }"
      />
    </div>

    <div class="flex items-center gap-2 text-sm text-slate-400">
      <EyeOff class="h-4 w-4" />
      录音中不会显示你说出的文字
    </div>

    <div class="mt-6 flex gap-4">
      <button
        v-if="phase !== 'recording'"
        type="button"
        class="inline-flex items-center gap-2 rounded-2xl bg-[var(--color-accent)] px-6 py-3 text-sm font-semibold text-white shadow-[var(--shadow-soft)] transition hover:opacity-90 disabled:opacity-40"
        :disabled="disabled"
        @click="startRecording"
      >
        <Mic class="h-4 w-4" />
        {{ label }}
      </button>
      <button
        v-else
        type="button"
        class="inline-flex items-center gap-2 rounded-2xl bg-red-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-red-200/40 hover:bg-red-600"
        @click="stopRecording(false)"
      >
        <Square class="h-4 w-4" />
        结束录音
      </button>
    </div>
  </div>
</template>
