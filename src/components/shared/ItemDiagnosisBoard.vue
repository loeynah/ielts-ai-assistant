<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  mode: { type: String, default: 'listening' },
})

const activeId = ref('')

const sortedItems = computed(() =>
  [...props.items].sort((a, b) => {
    const na = parseInt(a.display_num ?? a.label, 10)
    const nb = parseInt(b.display_num ?? b.label, 10)
    if (!Number.isNaN(na) && !Number.isNaN(nb)) return na - nb
    return String(a.display_num ?? a.label).localeCompare(
      String(b.display_num ?? b.label),
      undefined,
      { numeric: true },
    )
  }),
)

const activeItem = computed(() => {
  if (!sortedItems.value.length) return null
  const id = activeId.value || sortedItems.value[0].question_id
  return sortedItems.value.find((i) => i.question_id === id) || sortedItems.value[0]
})

const activeNum = computed(() => activeItem.value?.display_num ?? activeItem.value?.label ?? '')

watch(
  () => props.items,
  (list) => {
    if (!list?.length) {
      activeId.value = ''
      return
    }
    const exists = list.some((i) => i.question_id === activeId.value)
    if (!exists) activeId.value = list[0].question_id
  },
  { immediate: true, deep: true },
)

function selectItem(id) {
  activeId.value = id
}
</script>

<template>
  <div v-if="sortedItems.length" class="space-y-4">
    <div class="flex flex-wrap gap-2">
      <button
        v-for="item in sortedItems"
        :key="item.question_id"
        type="button"
        class="flex h-9 min-w-[36px] items-center justify-center rounded-full px-2.5 text-xs font-bold transition"
        :class="
          activeItem?.question_id === item.question_id
            ? 'bg-[var(--color-accent)] text-white shadow-sm ring-2 ring-[var(--color-accent)]/30'
            : item.is_correct
              ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200'
              : 'bg-red-50 text-red-700 ring-1 ring-red-200'
        "
        @click="selectItem(item.question_id)"
      >
        {{ item.display_num ?? item.label }}
      </button>
    </div>

    <div
      v-if="activeItem"
      class="rounded-3xl bg-white p-5 shadow-[var(--shadow-soft)] ring-1 ring-slate-100"
    >
      <p
        class="text-sm font-bold"
        :class="activeItem.is_correct ? 'text-emerald-600' : 'text-red-600'"
      >
        Q{{ activeNum }}：{{ activeItem.is_correct ? '正确' : '错误' }}
      </p>

      <div class="mt-4 space-y-3 text-sm text-slate-700">
        <div>
          <p class="text-xs font-semibold text-slate-400">官方正确答案</p>
          <p class="mt-1 font-medium">{{ activeItem.correct_answer }}</p>
        </div>
        <div>
          <p class="text-xs font-semibold text-slate-400">错因解析</p>
          <p class="mt-1 leading-relaxed">{{ activeItem.error_analysis }}</p>
        </div>
        <div v-if="mode === 'listening' && activeItem.listening_tip">
          <p class="text-xs font-semibold text-slate-400">精听训练建议</p>
          <p class="mt-1 leading-relaxed">{{ activeItem.listening_tip }}</p>
        </div>
        <div v-if="mode === 'reading' && activeItem.reading_tip">
          <p class="text-xs font-semibold text-slate-400">精读针对性建议</p>
          <p class="mt-1 leading-relaxed">{{ activeItem.reading_tip }}</p>
        </div>
        <div>
          <p class="text-xs font-semibold text-slate-400">核心知识点</p>
          <p class="mt-1 leading-relaxed">{{ activeItem.knowledge_point }}</p>
        </div>
        <div v-if="mode === 'reading' && activeItem.paraphrase_pairs?.length">
          <p class="text-xs font-semibold text-slate-400">同义替换词对</p>
          <div class="mt-2 overflow-hidden rounded-2xl ring-1 ring-slate-100">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-3 py-2 font-medium">原文</th>
                  <th class="px-3 py-2 font-medium">替换/考点</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(p, i) in activeItem.paraphrase_pairs"
                  :key="i"
                  class="border-t border-slate-100"
                >
                  <td class="px-3 py-2">{{ p.original }}</td>
                  <td class="px-3 py-2 text-[var(--color-accent)]">{{ p.replacement }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
