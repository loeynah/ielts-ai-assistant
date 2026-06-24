<script setup>
import { ref } from 'vue'
import { ZoomIn, X } from 'lucide-vue-next'

defineProps({
  task: { type: Object, required: true },
})

const lightboxOpen = ref(false)
</script>

<template>
  <div class="flex h-full min-h-0 flex-col bg-white">

    <div class="shrink-0 border-b border-slate-100 bg-white px-6 py-5">
      <p class="text-base font-bold tracking-wide text-slate-900">
        {{ task.type === 'task1' ? 'WRITING TASK 1' : 'WRITING TASK 2' }}
      </p>
      <p class="mt-2 text-[15px] font-semibold leading-snug text-slate-800">
        {{ task.instruction }}
      </p>
      <p class="mt-1.5 text-sm font-medium text-slate-600">
        Write at least {{ task.minWords }} words.
      </p>
    </div>


    <div class="flex min-h-0 flex-1 flex-col overflow-y-auto px-6 py-6">
      <p class="shrink-0 whitespace-pre-line text-[15px] leading-relaxed text-slate-800">
        {{ task.prompt }}
      </p>


      <div
        v-if="task.imageUrl"
        class="flex min-h-0 flex-1 flex-col items-center justify-center py-8"
      >
        <button
          type="button"
          class="group relative w-full max-w-lg overflow-hidden rounded-3xl bg-white p-4 shadow-[var(--shadow-soft-lg)] ring-1 ring-slate-100/80 transition hover:shadow-[0_20px_60px_-20px_rgb(91_141_239_/_0.18)]"
          @click="lightboxOpen = true"
        >
          <img
            :src="task.imageUrl"
            :alt="task.title"
            class="mx-auto max-h-[340px] w-full object-contain"
          />
          <span
            class="absolute bottom-4 right-4 inline-flex items-center gap-1 rounded-full bg-white/95 px-3 py-1.5 text-xs font-medium text-[var(--color-accent)] opacity-0 shadow-sm ring-1 ring-slate-100 transition group-hover:opacity-100"
          >
            <ZoomIn class="h-3.5 w-3.5" />
            点击放大
          </span>
        </button>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="lightboxOpen"
          class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-6 backdrop-blur-sm"
          @click.self="lightboxOpen = false"
        >
          <div class="relative max-h-[90vh] max-w-5xl overflow-auto rounded-3xl bg-white p-4 shadow-2xl">
            <button
              type="button"
              class="absolute right-4 top-4 rounded-full bg-slate-100 p-2 text-slate-500 hover:bg-slate-200"
              @click="lightboxOpen = false"
            >
              <X class="h-4 w-4" />
            </button>
            <img :src="task.imageUrl" :alt="task.title" class="max-h-[80vh] w-full object-contain" />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
