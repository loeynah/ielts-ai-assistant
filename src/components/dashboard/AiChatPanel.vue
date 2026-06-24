<script setup>
import { nextTick, ref } from 'vue'
import { Bot, Send, Sparkles } from 'lucide-vue-next'
import SoftCard from '@/components/ui/SoftCard.vue'
import ChatMessageRow from '@/components/dashboard/ChatMessageRow.vue'
import { MOCK_CHAT_INTRO, QUICK_PROMPTS } from '@/config/chatMock'
import { requestChat } from '@/api/chat'
import { useUserStore } from '@/stores/user'
import { useTasksStore } from '@/stores/tasks'

const emit = defineEmits(['tasks-adjust'])

const userStore = useUserStore()
const tasksStore = useTasksStore()

let idCounter = 0
function nextMessageId() {
  idCounter += 1
  return `msg-${idCounter}`
}

const messages = ref([{ id: nextMessageId(), role: 'assistant', content: MOCK_CHAT_INTRO }])
const input = ref('')
const isStreaming = ref(false)
const streamingId = ref(null)
const chatRef = ref(null)
const quickPrompts = QUICK_PROMPTS

function scrollToBottom() {
  nextTick(() => {
    if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight
  })
}

function appendMessage(role, content, actions = [], meta = null) {
  const msg = { id: nextMessageId(), role, content, actions, meta }
  messages.value.push(msg)
  return msg.id
}

function updateMessageContent(id, content) {
  const msg = messages.value.find((m) => m.id === id)
  if (msg) msg.content = content
}

async function streamAssistantReply(payload) {
  const { content, actions = [], meta, emitAdjust } = payload
  isStreaming.value = true
  const aiId = appendMessage('assistant', '', actions, meta)
  streamingId.value = aiId
  scrollToBottom()

  let built = ''
  for (const char of content) {
    await new Promise((r) => setTimeout(r, 6))
    built += char
    updateMessageContent(aiId, built)
    scrollToBottom()
  }

  isStreaming.value = false
  streamingId.value = null
  if (emitAdjust) emit('tasks-adjust', emitAdjust)
}

async function applyResponseMeta(data) {
  if (data.exam_date || data.target_score != null) {
    await userStore.applyChatMeta({
      exam_date: data.exam_date,
      target_score: data.target_score,
    })
  }
}

async function sendUserText(text) {
  const trimmed = text.trim()
  if (!trimmed || isStreaming.value) return

  appendMessage('user', trimmed)
  input.value = ''
  scrollToBottom()

  const profile = userStore.profile
  try {
    const data = await requestChat(trimmed, {
      exam_date: profile?.exam_date,
      target_score: profile?.target_score,
    })
    await applyResponseMeta(data)

    const meta = {
      today_tasks: data.today_tasks || [],
      exam_date: data.exam_date,
      target_score: data.target_score,
    }

    await streamAssistantReply({
      content: data.content,
      actions: data.actions || [],
      meta,
      emitAdjust: data.emit_adjust === 'speaking-focus' ? 'speaking-focus' : data.emit_adjust,
    })
  } catch (err) {
    const msg =
      err?.status === 401
        ? '登录已失效，请刷新页面后重新登录。'
        : err?.message || '暂时无法连接 AI 管家，请确认后端已启动且 API Key 已配置。'
    await streamAssistantReply({ content: msg, actions: [] })
  }
}

function handleQuickPrompt(prompt) {
  sendUserText(prompt)
}

function handleSubmit() {
  sendUserText(input.value)
}

async function handleAction(actionId, messageId) {
  if (isStreaming.value) return

  const msg = messages.value.find((m) => m.id === messageId)
  const meta = msg?.meta || {}

  if (actionId === 'sync-plan') {
    const added = tasksStore.addTasksFromAi(meta.today_tasks || [])
    if (meta.exam_date || meta.target_score != null) {
      await userStore.applyChatMeta({
        exam_date: meta.exam_date,
        target_score: meta.target_score,
      })
    }

    const summary =
      added.length > 0
        ? `已将 ${added.length} 条今日任务同步至打卡清单，请在下方查看并勾选完成。`
        : '未捕获到可同步的具体任务，请让 AI 重新生成包含今日任务的建议后再试。'

    await streamAssistantReply({ content: summary, actions: [] })
    return
  }

  if (actionId === 'keep-plan') {
    await streamAssistantReply({
      content: '已保持原计划不变。如需再次微调，随时告诉我。',
      actions: [],
    })
  }
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSubmit()
  }
}
</script>

<template>
  <SoftCard title="AI 智能管家" subtitle="考试科普 · 英文答疑 · 两阶段动态调度">
    <template #header>
      <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--color-accent-soft)] text-[var(--color-accent)]">
        <Bot class="h-5 w-5" />
      </div>
    </template>

    <div class="chat-console">
      <div ref="chatRef" class="max-h-[420px] space-y-6 overflow-y-auto rounded-[24px] bg-slate-50/50 px-4 py-5 sm:px-6">
        <ChatMessageRow
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
          :is-streaming="isStreaming && streamingId === msg.id"
          @action="handleAction"
        />
      </div>

      <div class="space-y-4 px-4 pb-5 pt-3 sm:px-5">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="prompt in quickPrompts"
            :key="prompt"
            type="button"
            class="rounded-full border border-slate-200/80 bg-white/90 px-4 py-2 text-xs text-slate-600 transition hover:bg-[var(--color-accent-soft)] disabled:opacity-50"
            :disabled="isStreaming"
            @click="handleQuickPrompt(prompt)"
          >
            <Sparkles class="mr-1 inline h-3 w-3 text-[var(--color-accent)]" />
            {{ prompt }}
          </button>
        </div>

        <div class="flex items-end gap-3 rounded-[22px] bg-white px-4 py-3 ring-1 ring-slate-200/60">
          <textarea
            v-model="input"
            rows="2"
            placeholder="问问 AI 小助手..."
            class="min-h-[48px] flex-1 resize-none bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400"
            :disabled="isStreaming"
            @keydown="onKeydown"
          />
          <button
            type="button"
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#7ba7e8] to-[#5b8def] text-white shadow-md transition hover:brightness-105 disabled:opacity-50"
            :disabled="isStreaming || !input.trim()"
            @click="handleSubmit"
          >
            <Send class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  </SoftCard>
</template>
