<script setup>
import { onUnmounted, ref, watch } from 'vue'
import { Headphones, Pause, Play } from 'lucide-vue-next'

const props = defineProps({
  audioSrc: { type: String, required: true },
  title: { type: String, default: '' },
  section: { type: String, default: '' },
})

const audioRef = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref(1)

function formatTime(sec) {
  if (!Number.isFinite(sec)) return '00:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function togglePlay() {
  const el = audioRef.value
  if (!el) return
  if (el.paused) {
    el.play()
    isPlaying.value = true
  } else {
    el.pause()
    isPlaying.value = false
  }
}

function onSeek(e) {
  const el = audioRef.value
  if (!el || !duration.value) return
  el.currentTime = (Number(e.target.value) / 100) * duration.value
}

function setSpeed(rate) {
  playbackRate.value = rate
  if (audioRef.value) audioRef.value.playbackRate = rate
}

watch(
  () => props.audioSrc,
  () => {
    isPlaying.value = false
    currentTime.value = 0
    duration.value = 0
    audioRef.value?.pause()
    audioRef.value?.load()
  },
)

onUnmounted(() => audioRef.value?.pause())
</script>

<template>
  <section
    class="border-b border-slate-100/80 bg-gradient-to-br from-white via-[var(--color-accent-soft)]/25 to-[var(--color-beige)]/20 px-8 py-8"
  >
    <div class="mb-6 flex items-center gap-3">
      <div
        class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white shadow-sm ring-1 ring-slate-100"
      >
        <Headphones class="h-5 w-5 text-[var(--color-accent)]" />
      </div>
      <div>
        <p class="text-xs font-medium text-[var(--color-accent)]">{{ section }} · 真题音频控制塔</p>
        <h3 class="text-lg font-semibold text-slate-800">{{ title }}</h3>
      </div>
    </div>

    <audio
      ref="audioRef"
      :src="audioSrc"
      preload="metadata"
      class="hidden"
      @timeupdate="currentTime = audioRef?.currentTime || 0"
      @loadedmetadata="duration = audioRef?.duration || 0"
      @ended="isPlaying = false"
    />

    <div class="flex flex-wrap items-center gap-6">
      <button
        type="button"
        class="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#7ba7e8] to-[#5b8def] text-white shadow-lg shadow-blue-200/40 transition hover:scale-105"
        @click="togglePlay"
      >
        <Pause v-if="isPlaying" class="h-7 w-7" />
        <Play v-else class="ml-1 h-7 w-7" />
      </button>

      <div class="min-w-[220px] flex-1">
        <input
          type="range"
          min="0"
          max="100"
          step="0.1"
          :value="duration ? (currentTime / duration) * 100 : 0"
          class="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200/80 accent-[var(--color-accent)]"
          @input="onSeek"
        />
        <div class="mt-3 flex justify-between font-mono text-sm text-slate-500">
          <span>{{ formatTime(currentTime) }}</span>
          <span>{{ formatTime(duration) }}</span>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <span class="text-xs text-slate-400">倍速</span>
        <button
          v-for="rate in [1, 1.25, 1.5]"
          :key="rate"
          type="button"
          class="rounded-full px-4 py-2 text-sm font-medium transition"
          :class="
            playbackRate === rate
              ? 'bg-[var(--color-accent)] text-white shadow-sm'
              : 'bg-white text-slate-600 ring-1 ring-slate-200/80 hover:bg-slate-50'
          "
          @click="setSpeed(rate)"
        >
          {{ rate }}x
        </button>
      </div>
    </div>
  </section>
</template>
