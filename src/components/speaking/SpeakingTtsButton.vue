<script setup>
import { ref } from 'vue'
import { Volume2 } from 'lucide-vue-next'
import { speakText, stopSpeaking } from '@/utils/speechTts'

const props = defineProps({
  text: { type: String, required: true },
})

const isPlaying = ref(false)

function toggle() {
  if (isPlaying.value) {
    stopSpeaking()
    isPlaying.value = false
    return
  }
  isPlaying.value = true
  speakText(props.text, {
    onEnd: () => {
      isPlaying.value = false
    },
  })
}
</script>

<template>
  <button
    type="button"
    class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-[var(--color-accent)] shadow-sm ring-1 ring-slate-200/80 transition hover:bg-[var(--color-accent)] hover:text-white"
    title="AI 考官读题 (TTS)"
    @click="toggle"
  >
    <Volume2 class="h-4 w-4" :class="isPlaying ? 'animate-pulse' : ''" />
  </button>
</template>
