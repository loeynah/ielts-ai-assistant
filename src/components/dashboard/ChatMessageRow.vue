<script setup>
import { Bot, User } from 'lucide-vue-next'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
  isStreaming: { type: Boolean, default: false },
})

const emit = defineEmits(['action'])

function onAction(actionId) {
  emit('action', actionId, props.message.id)
}
</script>

<template>
  <div
    class="flex w-full gap-3"
    :class="message.role === 'user' ? 'flex-row-reverse' : 'flex-row'"
  >
    <div
      class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
      :class="
        message.role === 'user'
          ? 'bg-gradient-to-br from-[#7ba7e8] to-[#5b8def] text-white'
          : 'bg-white text-[var(--color-accent)] ring-1 ring-slate-200/80'
      "
    >
      <User v-if="message.role === 'user'" class="h-4 w-4" />
      <Bot v-else class="h-4 w-4" />
    </div>

    <div
      class="flex max-w-[min(100%,680px)] flex-col gap-2"
      :class="message.role === 'user' ? 'items-end' : 'items-start'"
    >
      <div
        class="rounded-[18px] px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap"
        :class="message.role === 'user' ? 'user-bubble' : 'ai-bubble'"
      >
        {{ message.content }}
        <span
          v-if="isStreaming"
          class="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-slate-400 align-middle"
        />
      </div>

      <div
        v-if="message.role === 'assistant' && message.actions?.length"
        class="flex flex-wrap gap-2"
      >
        <button
          v-for="act in message.actions"
          :key="act.id"
          type="button"
          class="rounded-full bg-white px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm ring-1 ring-slate-200/80 transition hover:bg-[var(--color-beige)]"
          @click="onAction(act.id)"
        >
          {{ act.label }}
        </button>
      </div>
    </div>
  </div>
</template>
