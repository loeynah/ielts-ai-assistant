<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { Calendar, ChevronLeft, ChevronRight, Star } from 'lucide-vue-next'
import SoftCard from '@/components/ui/SoftCard.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const today = ref(new Date())
const viewYear = ref(today.value.getFullYear())
const viewMonth = ref(today.value.getMonth())
const menuDay = ref(null)
const menuPos = ref({ x: 0, y: 0 })

let tickId = null

onMounted(async () => {
  await userStore.refresh()
  syncViewToExam()
  tickId = setInterval(() => {
    today.value = new Date()
  }, 60_000)
})

onUnmounted(() => {
  if (tickId) clearInterval(tickId)
})

const examDateStr = computed(() => userStore.profile?.exam_date || '2026-06-25')

const examDateObj = computed(() => {
  const d = new Date(examDateStr.value)
  return Number.isNaN(d.getTime()) ? new Date('2026-06-25') : d
})

const countdownDays = computed(() => {
  const t = new Date(today.value)
  t.setHours(0, 0, 0, 0)
  const target = new Date(examDateObj.value)
  target.setHours(0, 0, 0, 0)
  return Math.max(0, Math.round((target - t) / 86_400_000))
})

const monthLabel = computed(() =>
  new Date(viewYear.value, viewMonth.value, 1).toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
  }),
)

const calendarDays = computed(() => {
  const year = viewYear.value
  const month = viewMonth.value
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < firstDay; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  return cells
})

const examDateLabel = computed(() => {
  const d = examDateObj.value
  return `${d.toLocaleString('zh-CN', { month: 'long' })}${d.getDate()} 日`
})

const weekLabels = ['日', '一', '二', '三', '四', '五', '六']

function syncViewToExam() {
  const d = examDateObj.value
  viewYear.value = d.getFullYear()
  viewMonth.value = d.getMonth()
}

function prevMonth() {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value -= 1
  } else {
    viewMonth.value -= 1
  }
  closeMenu()
}

function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value += 1
  } else {
    viewMonth.value += 1
  }
  closeMenu()
}

function isoForDay(day) {
  const m = String(viewMonth.value + 1).padStart(2, '0')
  const d = String(day).padStart(2, '0')
  return `${viewYear.value}-${m}-${d}`
}

function isExamDay(day) {
  return isoForDay(day) === examDateStr.value.slice(0, 10)
}

function isToday(day) {
  const t = today.value
  return (
    day === t.getDate() &&
    viewMonth.value === t.getMonth() &&
    viewYear.value === t.getFullYear()
  )
}

function dayClass(day) {
  if (isExamDay(day)) {
    return 'bg-gradient-to-br from-amber-100 to-[var(--color-beige)] font-bold text-amber-800 ring-2 ring-amber-300/60 shadow-sm'
  }
  if (isToday(day)) {
    return 'bg-[var(--color-accent)] font-semibold text-white shadow-md shadow-blue-200/40'
  }
  return 'text-slate-600 hover:bg-slate-100'
}

function openMenu(day, event) {
  menuDay.value = day
  const rect = event.currentTarget.getBoundingClientRect()
  menuPos.value = { x: rect.left + rect.width / 2, y: rect.bottom + 6 }
}

function closeMenu() {
  menuDay.value = null
}

async function setExamDay() {
  if (!menuDay.value) return
  await userStore.updateExamDate(isoForDay(menuDay.value))
  closeMenu()
}

async function clearExamDay() {
  await userStore.clearExamDate()
  closeMenu()
}

const showClearOption = computed(() => menuDay.value && isExamDay(menuDay.value))

watch(examDateStr, () => syncViewToExam())
</script>

<template>
  <SoftCard :padding="'p-6'">
    <p class="mb-5 text-center text-base font-bold tracking-tight text-slate-800">
      距离 IELTS 考试还有：
      <span class="text-xl text-amber-600">🔥 {{ countdownDays }} 天</span>
    </p>

    <div class="mb-1 flex items-center justify-between gap-2">
      <div class="flex items-center gap-2">
        <Calendar class="h-4 w-4 text-[var(--color-accent)]" />
        <h3 class="text-lg font-semibold text-slate-800">学习日历</h3>
      </div>
      <div class="flex items-center gap-1">
        <button
          type="button"
          class="rounded-xl p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
          aria-label="上一月"
          @click="prevMonth"
        >
          <ChevronLeft class="h-4 w-4" />
        </button>
        <button
          type="button"
          class="rounded-xl p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
          aria-label="下一月"
          @click="nextMonth"
        >
          <ChevronRight class="h-4 w-4" />
        </button>
      </div>
    </div>
    <p class="mb-4 text-sm text-slate-400">{{ monthLabel }}</p>

    <div class="mb-2 grid grid-cols-7 gap-1 text-center text-[11px] font-medium text-slate-400">
      <span v-for="w in weekLabels" :key="w">{{ w }}</span>
    </div>
    <div class="grid grid-cols-7 gap-1.5 text-center text-sm">
      <span v-for="(day, idx) in calendarDays" :key="idx" class="aspect-square">
        <button
          v-if="day"
          type="button"
          class="relative inline-flex h-8 w-8 items-center justify-center rounded-full transition"
          :class="dayClass(day)"
          @click="openMenu(day, $event)"
        >
          {{ day }}
          <Star
            v-if="isExamDay(day)"
            class="absolute -right-0.5 -top-0.5 h-3 w-3 fill-amber-500 text-amber-500"
          />
        </button>
      </span>
    </div>
    <p class="mt-3 text-center text-[11px] text-slate-400">
      <Star class="mr-0.5 inline h-3 w-3 fill-amber-400 text-amber-400" />
      {{ examDateLabel }}考试日 · 点击日期可修改
    </p>

    <Teleport to="body">
      <div
        v-if="menuDay"
        class="fixed inset-0 z-40"
        @click="closeMenu"
      />
      <div
        v-if="menuDay"
        class="fixed z-50 min-w-[140px] rounded-2xl bg-white p-1.5 shadow-lg ring-1 ring-slate-200/80"
        :style="{ left: `${menuPos.x}px`, top: `${menuPos.y}px`, transform: 'translateX(-50%)' }"
      >
        <button
          v-if="!showClearOption"
          type="button"
          class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-xs font-medium text-slate-700 hover:bg-[var(--color-accent-soft)]"
          @click="setExamDay"
        >
          <Star class="h-3.5 w-3.5 text-amber-500" />
          设为考试日
        </button>
        <button
          v-else
          type="button"
          class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-xs font-medium text-slate-500 hover:bg-slate-50"
          @click="clearExamDay"
        >
          取消星标
        </button>
      </div>
    </Teleport>
  </SoftCard>
</template>
