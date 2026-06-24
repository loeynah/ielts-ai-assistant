<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Sparkles } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const auth = useAuthStore()
const userStore = useUserStore()

const username = ref('admin')
const password = ref('123456')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    userStore.applyLocal(auth.user)
    router.replace('/dashboard')
  } catch {
    error.value = '账号或密码错误，请使用 admin / 123456'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-[#f8fafc] via-[#eef3f9] to-[#f5f0e8] p-6">
    <div class="w-full max-w-md rounded-[32px] bg-white/95 p-10 shadow-[0_24px_64px_-16px_rgb(91_141_239_/_0.2)] ring-1 ring-slate-100">
      <div class="mb-8 text-center">
        <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--color-accent-soft)] text-[var(--color-accent)]">
          <Sparkles class="h-7 w-7" />
        </div>
        <h1 class="text-2xl font-bold text-slate-900">雅思智能备考助手</h1>
        <p class="mt-2 text-sm text-slate-500">IELTS AI Prep Companion</p>
      </div>

      <form class="space-y-5" @submit.prevent="onSubmit">
        <div>
          <label class="mb-1.5 block text-xs font-medium text-slate-500">账号</label>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            class="w-full rounded-2xl bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none ring-1 ring-slate-100 focus:ring-[var(--color-accent)]/40"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-medium text-slate-500">密码</label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            class="w-full rounded-2xl bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none ring-1 ring-slate-100 focus:ring-[var(--color-accent)]/40"
          />
        </div>
        <p v-if="error" class="text-center text-sm text-red-500">{{ error }}</p>
        <button
          type="submit"
          class="w-full rounded-2xl bg-[var(--color-accent)] py-3.5 text-sm font-semibold text-white shadow-[var(--shadow-soft-lg)] transition hover:opacity-95 disabled:opacity-60"
          :disabled="loading"
        >
          {{ loading ? '登录中…' : '进入备考系统' }}
        </button>
      </form>
    </div>
  </div>
</template>
