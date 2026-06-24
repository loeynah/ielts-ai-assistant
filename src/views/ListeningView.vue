<script setup>
import { computed, ref } from 'vue'
import { ExternalLink } from 'lucide-vue-next'
import ListeningEmptyState from '@/components/listening/ListeningEmptyState.vue'
import ListeningPracticeArea from '@/components/listening/ListeningPracticeArea.vue'
import {
  getLessonById,
  lessonAudioUrl,
  lessonHtmlUrl,
  listeningLessons,
} from '@/config/listeningLessons'

const activeLessonId = ref(null)

const activeLesson = computed(() =>
  activeLessonId.value ? getLessonById(activeLessonId.value) : null,
)
const htmlUrl = computed(() =>
  activeLesson.value ? lessonHtmlUrl(activeLesson.value) : '',
)
const audioUrl = computed(() =>
  activeLesson.value ? lessonAudioUrl(activeLesson.value) : '',
)

function selectLesson(lessonId) {
  activeLessonId.value = lessonId
}
</script>

<template>
  <div class="flex w-full flex-col gap-8 pb-10">
    <header class="flex flex-wrap items-end justify-between gap-4 pt-2">
      <div>
        <p class="text-sm font-medium text-[var(--color-accent)]">Listening</p>
        <h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-900">听力真题训练</h1>
        <p class="mt-2 text-slate-500">本地题目训练</p>
      </div>
      <a
        v-if="activeLesson"
        :href="htmlUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center gap-2 rounded-2xl bg-white px-4 py-2.5 text-sm font-medium text-slate-600 shadow-sm transition hover:text-[var(--color-accent)]"
      >
        <ExternalLink class="h-4 w-4" />
        新窗口打开
      </a>
    </header>

    <div class="flex flex-wrap gap-3">
      <button
        v-for="lesson in listeningLessons"
        :key="lesson.lessonId"
        type="button"
        class="rounded-2xl px-5 py-3 text-left transition duration-200"
        :class="
          activeLessonId === lesson.lessonId
            ? 'bg-[var(--color-accent)] text-white shadow-lg shadow-blue-200/40'
            : 'bg-white text-slate-600 shadow-sm hover:-translate-y-0.5 hover:shadow-md'
        "
        @click="selectLesson(lesson.lessonId)"
      >
        <span class="block text-xs opacity-80">{{ lesson.section }}</span>
        <span class="block text-sm font-semibold">Lesson {{ lesson.lessonId }}</span>
        <span
          class="mt-1 block max-w-[180px] truncate text-[11px] opacity-70"
        >
          {{ lesson.title }}
        </span>
      </button>
    </div>

    <ListeningEmptyState v-if="!activeLessonId" />

    <ListeningPracticeArea
      v-else-if="activeLesson"
      :lesson="activeLesson"
      :html-url="htmlUrl"
      :audio-url="audioUrl"
    />
  </div>
</template>
