<script setup>
defineProps({
  title: { type: String, default: '' },
  html: { type: String, default: '' },
})
</script>

<template>
  <div class="flex h-full min-h-0 flex-col overflow-hidden rounded-[24px] bg-white ring-1 ring-slate-100/80">
    <div class="border-b border-slate-100 px-6 py-4">
      <h3 class="text-lg font-semibold text-slate-800">{{ title }}</h3>
      <p class="mt-1 text-xs text-slate-400">文章精读区 · 独立滚动</p>
    </div>
    <div
      class="reading-article prose prose-slate max-w-none flex-1 overflow-y-auto overscroll-contain px-8 py-6 text-[15px] leading-[1.85] text-slate-700"
      v-html="html"
    />
  </div>
</template>

<style scoped>
.reading-article :deep(h2),
.reading-article :deep(h3),
.reading-article :deep(h4) {
  margin: 1.5rem 0 1rem;
  font-weight: 600;
  color: #1e293b;
}
.reading-article :deep(p) {
  margin-bottom: 1rem;
}
.reading-article :deep(strong) {
  color: var(--color-accent);
}
</style>
