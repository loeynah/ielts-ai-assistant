<script setup>
import { BookOpen } from 'lucide-vue-next'
</script>

<template>
  <div
    class="soft-card flex min-h-[400px] flex-col items-center justify-center px-8 py-16 text-center"
  >
    <div
      class="mb-8 flex h-20 w-20 items-center justify-center rounded-[28px] bg-gradient-to-br from-[var(--color-accent-soft)] to-[var(--color-beige)] shadow-[var(--shadow-soft)] animate-[breathe_3s_ease-in-out_infinite]"
    >
      <BookOpen class="h-9 w-9 text-[var(--color-accent)]" />
    </div>
    <p class="max-w-lg text-base leading-relaxed text-slate-600">
      📖 请在上方选择雅思阅读真题，开启泛读与精读专项训练...
    </p>
    <p class="mt-3 text-sm text-slate-400">Passage 1 / 2 / 3 · 每模块精选 2 篇模版真题</p>
  </div>
</template>

<style scoped>
@keyframes breathe {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.04);
    opacity: 0.92;
  }
}
</style>
