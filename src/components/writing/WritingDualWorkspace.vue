<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { GripVertical } from 'lucide-vue-next'
import WritingPromptPanel from './WritingPromptPanel.vue'
import WritingEditorPanel from './WritingEditorPanel.vue'

defineProps({
  task: { type: Object, required: true },
  modelValue: { type: String, default: '' },
  secondsLeft: { type: Number, required: true },
  timerActive: { type: Boolean, default: false },
  gradingState: { type: String, default: 'idle' },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const containerRef = ref(null)
const editorRef = ref(null)
const leftPercent = ref(50)
const isDragging = ref(false)

function onMouseMove(e) {
  if (!isDragging.value || !containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const pct = ((e.clientX - rect.left) / rect.width) * 100
  leftPercent.value = Math.min(70, Math.max(30, pct))
}

function stopDrag() {
  isDragging.value = false
}

function startDrag() {
  isDragging.value = true
}

function focusEditor() {
  editorRef.value?.focusEditor()
}

defineExpose({ focusEditor })

onMounted(() => {
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', stopDrag)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', stopDrag)
})
</script>

<template>
  <div
    ref="containerRef"
    class="workspace-shell flex min-h-[580px] items-stretch overflow-hidden rounded-[28px] bg-white shadow-[var(--shadow-soft-lg)] ring-1 ring-slate-100/80 select-none"
    :class="isDragging ? 'cursor-col-resize' : ''"
  >
    <!-- 左栏：纯白等高卡片 -->
    <div
      class="flex min-h-0 min-w-0 flex-col self-stretch overflow-hidden"
      :style="{ width: `${leftPercent}%` }"
    >
      <WritingPromptPanel :task="task" class="h-full" />
    </div>

    <!-- 可拖动分隔条 -->
    <div
      class="relative z-10 flex w-2 shrink-0 cursor-col-resize items-stretch self-stretch bg-slate-50 hover:bg-[var(--color-accent-soft)]"
      @mousedown.prevent="startDrag"
    >
      <div class="flex w-full items-center justify-center">
        <GripVertical class="h-5 w-5 text-slate-300" />
      </div>
    </div>

    <!-- 右栏：答题沙盒等高卡片 -->
    <div class="flex min-h-0 min-w-0 flex-1 flex-col self-stretch overflow-hidden">
      <WritingEditorPanel
        ref="editorRef"
        :task="task"
        :model-value="modelValue"
        :seconds-left="secondsLeft"
        :timer-active="timerActive"
        :grading-state="gradingState"
        @update:model-value="emit('update:modelValue', $event)"
        @submit="emit('submit')"
      />
    </div>
  </div>
</template>
