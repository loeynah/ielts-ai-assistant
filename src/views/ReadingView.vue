<script setup>
import { computed, ref } from 'vue'
import ReadingEmptyState from '@/components/reading/ReadingEmptyState.vue'
import ReadingPracticeArea from '@/components/reading/ReadingPracticeArea.vue'
import { READING_PASSAGES } from '@/config/readingLessons'

const activePassageId = ref(null)
const activeLessonId = ref(null)

const activePassage = computed(() =>
  activePassageId.value
    ? READING_PASSAGES.find((p) => p.id === activePassageId.value)
    : null,
)

const activeLesson = computed(() => {
  if (!activePassage.value || !activeLessonId.value) return null
  return activePassage.value.lessons.find((l) => l.id === activeLessonId.value) || null
})

function selectPassage(id) {
  activePassageId.value = id
  activeLessonId.value = null
}

function selectLesson(id) {
  activeLessonId.value = id
}
</script>

<template>
  <div class="flex w-full flex-col gap-8 pb-10">
    <header class="pt-2">
      <p class="text-sm font-medium text-[var(--color-accent)]">Reading</p>
      <h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-900">阅读真题训练</h1>
      <p class="mt-2 text-slate-500">双栏学术精读 · AI双轨实时赋能</p>
    </header>

    <!-- 第一级：Passage -->
    <div>
      <p class="mb-3 text-xs font-medium uppercase tracking-wider text-slate-400">选择篇章</p>
      <div class="flex flex-wrap gap-3">
        <button
          v-for="passage in READING_PASSAGES"
          :key="passage.id"
          type="button"
          class="rounded-2xl px-6 py-3 text-sm font-semibold transition duration-200"
          :class="
            activePassageId === passage.id
              ? 'bg-[var(--color-accent)] text-white shadow-lg shadow-blue-200/40'
              : 'bg-white text-slate-600 shadow-sm hover:-translate-y-0.5 hover:shadow-md'
          "
          @click="selectPassage(passage.id)"
        >
          {{ passage.label }}
        </button>
      </div>
    </div>

    <!-- 第二级：Lesson -->
    <div v-if="activePassage">
      <p class="mb-3 text-xs font-medium uppercase tracking-wider text-slate-400">精选真题</p>
      <div class="flex flex-wrap gap-3">
        <button
          v-for="lesson in activePassage.lessons"
          :key="lesson.id"
          type="button"
          class="rounded-2xl px-5 py-3 text-left transition duration-200"
          :class="
            activeLessonId === lesson.id
              ? 'bg-[var(--color-beige)] text-slate-800 ring-2 ring-[var(--color-accent)]/30 shadow-md'
              : 'bg-white text-slate-600 shadow-sm hover:shadow-md'
          "
          @click="selectLesson(lesson.id)"
        >
          <span class="block text-xs font-medium text-[var(--color-accent)]">{{ lesson.label }}</span>
          <span class="mt-0.5 block text-sm font-semibold">{{ lesson.title }}</span>
        </button>
      </div>
    </div>

    <ReadingEmptyState v-if="!activeLesson" />

    <ReadingPracticeArea v-else :lesson="activeLesson" />
  </div>
</template>
