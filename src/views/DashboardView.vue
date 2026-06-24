<script setup>
defineOptions({ name: 'Dashboard' })

import { onMounted, ref } from 'vue'
import AiChatPanel from '@/components/dashboard/AiChatPanel.vue'
import TaskChecklist from '@/components/dashboard/TaskChecklist.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const taskListRef = ref(null)

function onTasksAdjust(mode) {
  if (mode === 'speaking-focus') {
    taskListRef.value?.applySpeakingFocus()
  }
}

onMounted(() => userStore.initializeAfterLogin())
</script>

<template>
  <div class="flex w-full max-w-[1120px] flex-col gap-10 pb-10">
    <header class="pt-2">
      <p class="text-sm font-medium text-[var(--color-accent)]">Home Page</p>
      <h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-900">主页</h1>
      <p class="mt-3 text-slate-500">AI智能助手 · 今日任务 · 温和专注的备考空间</p>
    </header>

    <AiChatPanel @tasks-adjust="onTasksAdjust" />

    <TaskChecklist ref="taskListRef" />
  </div>
</template>
