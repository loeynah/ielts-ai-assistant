<script setup>
import { onUnmounted, ref, watch } from 'vue'
import { Pause, Play } from 'lucide-vue-next'

const props = defineProps({
  src: { type: String, required: true },
})

const audioRef = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)

function togglePlay() {
  const el = audioRef.value
  if (!el) return
  if (isPlaying.value) el.pause()
  else el.play()
}

function onPlay() {
  isPlaying.value = true
}

function onPause() {
  isPlaying.value = false
}

function onTimeUpdate() {
  currentTime.value = audioRef.value?.currentTime || 0
}

function onLoaded() {
  duration.value = audioRef.value?.duration || 0
}

function onEnded() {
  isPlaying.value = false
  currentTime.value = 0
  if (audioRef.value) audioRef.value.currentTime = 0
}

function seek(event) {
  const el = audioRef.value
  if (!el) return
  el.currentTime = Number(event.target.value)
}

function format(seconds) {
  const sec = Math.max(0, Math.floor(seconds || 0))
  return `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`
}

watch(
  () => props.src,
  () => {
    isPlaying.value = false
    currentTime.value = 0
    duration.value = 0
    audioRef.value?.pause()
  },
)

onUnmounted(() => {
  audioRef.value?.pause()
})
</script>

<template>
  <div class="rounded-xl bg-slate-50 px-4 py-3 ring-1 ring-slate-200/80">
    <p class="mb-2 text-xs font-semibold text-slate-500">录音回放 · 点击播放重新听你的回答</p>
    <audio
      ref="audioRef"
      :src="src"
      class="hidden"
      preload="metadata"
      @play="onPlay"
      @pause="onPause"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoaded"
      @ended="onEnded"
    />
    <div class="flex items-center gap-3">
      <button
        type="button"
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[var(--color-accent)] text-white transition hover:opacity-90"
        @click="togglePlay"
      >
        <Pause v-if="isPlaying" class="h-4 w-4" />
        <Play v-else class="h-4 w-4 translate-x-0.5" />
      </button>
      <input
        type="range"
        min="0"
        :max="duration || 1"
        step="0.1"
        :value="currentTime"
        class="min-w-0 flex-1 accent-[var(--color-accent)]"
        @input="seek"
      />
      <span class="shrink-0 text-xs tabular-nums text-slate-500">
        {{ format(currentTime) }} / {{ format(duration) }}
      </span>
    </div>
  </div>
</template>
