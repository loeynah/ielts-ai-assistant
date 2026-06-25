<script setup>
defineProps({
  setLabel: { type: String, required: true },
  taskLabel: { type: String, required: true },
  minutes: { type: Number, required: true },
})

const emit = defineEmits(['confirm'])
</script>

<template>
  <div class="relative flex min-h-[580px] items-center justify-center overflow-hidden rounded-[28px]">
    <!-- 模糊占位背景 -->
    <div
      class="pointer-events-none absolute inset-0 bg-gradient-to-br from-[var(--color-surface-muted)] via-white to-[var(--color-beige)] opacity-90"
      aria-hidden="true"
    />
    <div
      class="pointer-events-none absolute inset-0 backdrop-blur-[2px]"
      aria-hidden="true"
    />

    <!-- 考前确认卡片 -->
    <div
      class="relative z-10 mx-4 w-full max-w-lg rounded-[28px] bg-white p-8 shadow-[0_24px_64px_-16px_rgb(91_141_239_/_0.22)] ring-1 ring-slate-100"
    >
      <p class="text-xs font-semibold uppercase tracking-wider text-[var(--color-accent)]">
        考前确认
      </p>
      <h2 class="mt-3 text-xl font-bold text-slate-900">
        您已选择：{{ setLabel }} —— {{ taskLabel }}
      </h2>
      <p class="mt-4 text-sm leading-relaxed text-slate-600">
        本场考试时长限制为
        <strong class="font-semibold text-slate-800">{{ minutes }} 分钟</strong>。
        请在安静、不受打扰的环境下作答。点击下方按钮将正式开启倒计时并解锁题目。
      </p>

      <button
        type="button"
        class="start-btn mt-8 w-full rounded-2xl bg-[var(--color-accent)] px-6 py-4 text-base font-semibold text-white shadow-[var(--shadow-soft-lg)] transition hover:opacity-95"
        @click="emit('confirm')"
      >
        确认进入考试 (Start Test)
      </button>
    </div>
  </div>
</template>

<style scoped>
.start-btn {
  animation: breathe 2.4s ease-in-out infinite;
}

@keyframes breathe {
  0%,
  100% {
    box-shadow: 0 16px 48px -16px rgb(91 141 239 / 0.28);
  }
  50% {
    box-shadow: 0 20px 56px -12px rgb(91 141 239 / 0.42);
  }
}
</style>
