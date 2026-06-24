<script setup>
import { computed, onMounted } from 'vue'
import { FileText, Mic } from 'lucide-vue-next'
import SoftCard from '@/components/ui/SoftCard.vue'
import RightCalendar from '@/components/dashboard/RightCalendar.vue'
import { formatIeltsBand } from '@/utils/ieltsScore'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => userStore.refresh())

const inboxItems = computed(() => userStore.profile?.inbox || [])

const skillScores = computed(() => {
  const s = userStore.profile?.skill_scores || {}
  return [
    { key: 'listening', label: '听力', score: formatIeltsBand(s.listening ?? 6.0) },
    { key: 'reading', label: '阅读', score: formatIeltsBand(s.reading ?? 6.0) },
    { key: 'speaking', label: '口语', score: formatIeltsBand(s.speaking ?? 6.0) },
    { key: 'writing', label: '写作', score: formatIeltsBand(s.writing ?? 6.0) },
  ]
})

const overallScore = computed(() => formatIeltsBand(userStore.profile?.overall_score ?? 6.0))
const targetScore = computed(() => formatIeltsBand(userStore.profile?.target_score ?? 7.0))
</script>

<template>
  <aside class="flex flex-col gap-6 overflow-y-auto pb-2" v-bind="$attrs">
    <RightCalendar />

    <SoftCard title="AI 批改通知" subtitle="AI Inbox · 异步报告动态流">
      <ul v-if="inboxItems.length" class="space-y-2">
        <li
          v-for="item in inboxItems"
          :key="item.id"
          class="group rounded-2xl border border-transparent bg-slate-50/60 p-4 transition hover:border-[var(--color-accent)]/15 hover:bg-white hover:shadow-[var(--shadow-soft)]"
        >
          <div class="flex gap-3">
            <span class="text-lg leading-none">{{ item.icon }}</span>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium leading-snug text-slate-700">{{ item.title }}</p>
              <p class="mt-1 text-xs font-medium text-[var(--color-accent)]">{{ item.meta }}</p>
              <p class="mt-1 text-[11px] text-slate-400">{{ item.time }}</p>
            </div>
            <FileText class="mt-0.5 h-4 w-4 shrink-0 text-slate-300" />
          </div>
        </li>
      </ul>
      <p v-else class="py-6 text-center text-sm text-slate-400">完成练习后，批改通知将在此显示</p>
    </SoftCard>

    <SoftCard
      class="bg-gradient-to-br from-white via-[var(--color-accent-soft)]/30 to-[var(--color-beige)]/40"
      title="AI 实时能力诊断"
      :subtitle="`综合 ${overallScore} · 目标 ${targetScore}`"
    >
      <div class="grid grid-cols-4 gap-2">
        <div
          v-for="skill in skillScores"
          :key="skill.key"
          class="rounded-2xl bg-white/80 px-2 py-4 text-center shadow-sm ring-1 ring-slate-100/60"
        >
          <p class="text-[10px] font-medium text-slate-400">{{ skill.label }}</p>
          <p class="mt-1 text-xl font-bold text-slate-800">{{ skill.score }}</p>
        </div>
      </div>
      <div class="mt-5 flex items-start gap-2 rounded-2xl bg-white/60 px-4 py-3 ring-1 ring-slate-100/80">
        <Mic class="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent)]" />
        <p class="text-xs leading-relaxed text-slate-500">
          <span class="animate-pulse font-medium text-slate-600">● </span>
          完成听读写说 AI 批改后，四科预估分将自动更新
        </p>
      </div>
    </SoftCard>
  </aside>
</template>
