<script setup>
import { computed, ref } from 'vue'
import {
  CheckCircle2,
  GripVertical,
  Pin,
  PinOff,
  Plus,
  Trash2,
  X,
} from 'lucide-vue-next'
import SoftCard from '@/components/ui/SoftCard.vue'
import { TASK_CATEGORIES, getCategoryMeta } from '@/config/taskCategories'
import { useTasksStore } from '@/stores/tasks'

const tasksStore = useTasksStore()

const showAddModal = ref(false)
const newCategory = ref('listening')
const newContent = ref('')

const displayTasks = computed(() => {
  const list = [...tasksStore.tasks]
  list.sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1
    return 0
  })
  return list
})

function openAddModal() {
  newCategory.value = 'listening'
  newContent.value = ''
  showAddModal.value = true
}

function confirmAdd() {
  const text = newContent.value.trim()
  if (!text) return
  tasksStore.addTask(newCategory.value, text, 'user')
  showAddModal.value = false
  newContent.value = ''
}

defineExpose({
  applySpeakingFocus: () => tasksStore.applySpeakingFocus(),
})
</script>

<template>
  <SoftCard title="今日任务打卡" subtitle="瀑布式清单 · 支持自定义 / 置顶 / 删除">
    <template #header>
      <div class="flex items-center gap-3">
        <span
          class="rounded-full bg-[var(--color-beige)] px-3 py-1 text-xs font-semibold text-slate-700"
        >
          {{ tasksStore.doneCount }} / {{ tasksStore.totalCount }} 已完成
        </span>
        <button
          type="button"
          class="inline-flex items-center gap-1.5 rounded-2xl bg-gradient-to-r from-[#7ba7e8] to-[#5b8def] px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:brightness-105"
          @click="openAddModal"
        >
          <Plus class="h-3.5 w-3.5" />
          添加打卡
        </button>
      </div>
    </template>

    <ol class="flex flex-col gap-5">
      <li
        v-for="(task, index) in displayTasks"
        :key="task.id"
        class="group relative flex gap-4 rounded-[24px] bg-gradient-to-br from-white to-[var(--color-beige)]/30 p-5 shadow-sm ring-1 ring-slate-100/80 transition hover:shadow-md"
        :class="task.pinned ? 'ring-[var(--color-accent)]/25' : ''"
      >
        <div
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-[var(--color-accent-soft)] text-sm font-bold text-[var(--color-accent)]"
        >
          {{ index + 1 }}
        </div>

        <label class="flex min-w-0 flex-1 cursor-pointer gap-4">
          <input
            v-model="task.done"
            type="checkbox"
            class="mt-1 h-5 w-5 shrink-0 rounded-md border-slate-300 text-[var(--color-accent)] focus:ring-[var(--color-accent)]"
            @change="tasksStore.save()"
          />
          <div class="min-w-0 flex-1">
            <div class="mb-2 flex flex-wrap items-center gap-2">
              <component
                :is="getCategoryMeta(task.category).icon"
                class="h-4 w-4 text-slate-400"
              />
              <span class="text-sm font-semibold text-slate-800">
                {{ getCategoryMeta(task.category).label }}
              </span>
              <span
                v-if="task.pinned"
                class="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-medium text-amber-700"
              >
                置顶
              </span>
              <span
                v-if="task.source === 'ai' || task.source === 'system'"
                class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-500"
              >
                AI 生成
              </span>
              <CheckCircle2 v-if="task.done" class="ml-auto h-4 w-4 text-emerald-500" />
            </div>
            <p class="text-sm leading-relaxed text-slate-600">{{ task.content }}</p>
          </div>
        </label>

        <div class="flex shrink-0 flex-col gap-1 opacity-0 transition group-hover:opacity-100">
          <button
            type="button"
            class="rounded-xl p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            :title="task.pinned ? '取消置顶' : '置顶'"
            @click="tasksStore.togglePin(task)"
          >
            <PinOff v-if="task.pinned" class="h-4 w-4" />
            <Pin v-else class="h-4 w-4" />
          </button>
          <button
            type="button"
            class="rounded-xl p-2 text-slate-400 hover:bg-red-50 hover:text-red-500"
            title="删除"
            @click="tasksStore.removeTask(task.id)"
          >
            <Trash2 class="h-4 w-4" />
          </button>
        </div>

        <GripVertical
          class="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-200 opacity-0 group-hover:opacity-100"
        />
      </li>
    </ol>

    <p v-if="!tasksStore.tasks.length" class="py-8 text-center text-sm text-slate-400">
      暂无任务，点击「添加打卡」或让 AI 小助手生成计划后一键同步
    </p>

    <Teleport to="body">
      <div
        v-if="showAddModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/20 p-4 backdrop-blur-sm"
        @click.self="showAddModal = false"
      >
        <div class="soft-card w-full max-w-md p-8">
          <div class="mb-6 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-slate-800">添加打卡任务</h3>
            <button
              type="button"
              class="rounded-xl p-2 text-slate-400 hover:bg-slate-100"
              @click="showAddModal = false"
            >
              <X class="h-5 w-5" />
            </button>
          </div>

          <label class="mb-2 block text-sm font-medium text-slate-600">分类</label>
          <div class="mb-5 flex flex-wrap gap-2">
            <button
              v-for="cat in TASK_CATEGORIES"
              :key="cat.key"
              type="button"
              class="inline-flex items-center gap-1.5 rounded-2xl px-3 py-2 text-xs font-medium transition"
              :class="
                newCategory === cat.key
                  ? 'bg-[var(--color-accent-soft)] text-[var(--color-accent)] ring-1 ring-[var(--color-accent)]/30'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
              "
              @click="newCategory = cat.key"
            >
              <component :is="cat.icon" class="h-3.5 w-3.5" />
              {{ cat.label }}
            </button>
          </div>

          <label class="mb-2 block text-sm font-medium text-slate-600">具体任务</label>
          <textarea
            v-model="newContent"
            rows="3"
            placeholder="例如：精听剑18 Test 2 Section 3"
            class="mb-6 w-full resize-none rounded-2xl bg-slate-50 px-4 py-3 text-sm outline-none ring-1 ring-slate-100 focus:ring-[var(--color-accent)]/40"
          />

          <div class="flex justify-end gap-3">
            <button
              type="button"
              class="rounded-2xl px-5 py-2.5 text-sm text-slate-500 hover:bg-slate-50"
              @click="showAddModal = false"
            >
              取消
            </button>
            <button
              type="button"
              class="rounded-2xl bg-gradient-to-r from-[#7ba7e8] to-[#5b8def] px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:brightness-105"
              @click="confirmAdd"
            >
              确认添加
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </SoftCard>
</template>
