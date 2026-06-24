<script setup>
import { computed } from 'vue'
import { WRITING_MENU_ITEMS, isDemoId } from '@/config/writingExams'

const props = defineProps({
  selectedId: { type: String, default: null },
  activeTask: { type: String, default: 'task1' },
})

const emit = defineEmits(['select-item', 'select-task'])

const isDemo = computed(() => props.selectedId && isDemoId(props.selectedId))
</script>

<template>
  <div class="soft-card p-4 md:p-5">
    <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <!-- 一级选题：套题 + 独立大作文平铺同一行 -->
      <div class="flex min-w-0 flex-1 flex-wrap gap-2">
        <button
          v-for="item in WRITING_MENU_ITEMS"
          :key="item.id"
          type="button"
          class="rounded-2xl px-4 py-2.5 text-left transition"
          :class="
            selectedId === item.id
              ? 'bg-[var(--color-accent)] text-white shadow-[var(--shadow-soft)]'
              : 'bg-white text-slate-600 ring-1 ring-slate-100 hover:bg-[var(--color-surface-muted)]'
          "
          @click="emit('select-item', item.id)"
        >
          <p class="text-sm font-semibold">{{ item.label }}</p>
          <p class="mt-0.5 text-[10px] opacity-80">{{ item.subtitle }}</p>
        </button>
      </div>

      <!-- 右侧统一 Task 切换 -->
      <div
        class="flex shrink-0 items-center gap-1 self-end rounded-2xl bg-white p-1 shadow-[var(--shadow-soft)] ring-1 ring-slate-100 lg:self-center"
      >
        <button
          type="button"
          class="rounded-xl px-4 py-2 text-xs font-semibold transition"
          :class="
            activeTask === 'task1' && !isDemo
              ? 'bg-[var(--color-accent)] text-white shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          "
          :disabled="isDemo"
          @click="emit('select-task', 'task1')"
        >
          Task 1 (小作文)
        </button>
        <button
          type="button"
          class="rounded-xl px-4 py-2 text-xs font-semibold transition"
          :class="
            activeTask === 'task2' || isDemo
              ? 'bg-[var(--color-accent)] text-white shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          "
          @click="emit('select-task', 'task2')"
        >
          Task 2 (大作文)
        </button>
      </div>
    </div>
  </div>
</template>
