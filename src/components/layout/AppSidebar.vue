<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LogOut, Sparkles } from 'lucide-vue-next'
import { navItems } from '@/config/navigation'
import { useAuthStore } from '@/stores/auth'
import { useTasksStore } from '@/stores/tasks'
import { useUserStore } from '@/stores/user'
import { formatOptionalBand } from '@/utils/ieltsScore'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const userStore = useUserStore()
const tasksStore = useTasksStore()

const activeName = computed(() => route.name)
const targetScore = computed(() => formatOptionalBand(userStore.profile?.target_score))

function go(path) {
  if (route.path !== path) router.push(path)
}

function logout() {
  auth.logout()
  userStore.applyLocal(null)
  tasksStore.reset()
  router.replace('/login')
}
</script>

<template>
  <aside
    class="flex h-full w-[88px] shrink-0 flex-col items-center justify-between border-r border-white/60 bg-white/80 py-8 backdrop-blur-xl"
  >
    <div class="flex w-full flex-col items-center gap-8">
      <button
        type="button"
        class="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-[#7ba7e8] to-[#5b8def] text-white shadow-lg shadow-blue-200/40 transition hover:scale-105"
        title="快速制定计划"
        @click="go('/dashboard')"
      >
        <Sparkles class="h-5 w-5" />
      </button>

      <nav class="flex w-full flex-col items-center gap-3 px-3" aria-label="主导航">
        <button
          v-for="item in navItems"
          :key="item.name"
          type="button"
          class="group relative flex w-full flex-col items-center gap-1.5 rounded-2xl px-2 py-3 transition-all duration-200"
          :class="
            activeName === item.name
              ? 'bg-[var(--color-lime)] text-slate-800 shadow-md shadow-slate-200/50'
              : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
          "
          :title="item.label"
          @click="go(item.path)"
        >
          <component
            :is="item.icon"
            class="h-5 w-5"
            :stroke-width="activeName === item.name ? 2.25 : 1.75"
          />
          <span class="text-[10px] font-medium leading-none">{{ item.label }}</span>
        </button>
      </nav>
    </div>

    <div class="flex flex-col items-center gap-4 px-3">
      <div class="flex flex-col items-center gap-2 text-center">
        <div
          class="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-slate-100 to-slate-200 text-sm font-semibold text-slate-600 ring-2 ring-white"
        >
          雅
        </div>
        <div class="hidden xl:block">
          <p class="text-xs font-semibold text-slate-700">备考学员</p>
          <p class="text-[10px] text-slate-400">
            {{ targetScore === '—' ? '目标未设定' : `目标 ${targetScore}` }}
          </p>
        </div>
      </div>
      <button
        type="button"
        class="flex h-10 w-10 items-center justify-center rounded-xl text-slate-400 transition hover:bg-red-50 hover:text-red-500"
        title="退出登录"
        @click="logout"
      >
        <LogOut class="h-4 w-4" />
      </button>
    </div>
  </aside>
</template>
