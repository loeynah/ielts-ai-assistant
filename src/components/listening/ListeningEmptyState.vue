<script setup>
import { Headphones } from 'lucide-vue-next'
</script>

<template>
  <div
    class="soft-card flex min-h-[420px] flex-col items-center justify-center px-8 py-16 text-center"
  >
    <div
      class="mb-8 flex h-20 w-20 items-center justify-center rounded-[28px] bg-gradient-to-br from-[var(--color-accent-soft)] to-[var(--color-beige)] shadow-[var(--shadow-soft)] animate-[breathe_3s_ease-in-out_infinite]"
    >
      <Headphones class="h-9 w-9 text-[var(--color-accent)]" />
    </div>
    <p class="max-w-md text-base leading-relaxed text-slate-600">
      📬 请在上方选择你想练习的听力真题章节，开启今日精听训练...
    </p>
    <p class="mt-3 text-sm text-slate-400">Lesson 103 · 104 · 105 首批题库已就绪</p>
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
