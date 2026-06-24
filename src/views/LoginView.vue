<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Sparkles } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const auth = useAuthStore()
const userStore = useUserStore()

const isRegister = ref(false)
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    if (isRegister.value) {
      if (password.value !== confirmPassword.value) {
        error.value = '两次输入的密码不一致'
        return
      }
      if (password.value.length < 6) {
        error.value = '密码至少 6 位'
        return
      }
      await auth.register(username.value.trim(), password.value)
    } else {
      await auth.login(username.value.trim(), password.value)
    }
    await userStore.initializeAfterLogin()
    router.replace('/dashboard')
  } catch (err) {
    error.value = err?.message || (isRegister.value ? '注册失败，用户名可能已存在' : '账号或密码错误')
  } finally {
    loading.value = false
  }
}

function toggleMode() {
  isRegister.value = !isRegister.value
  error.value = ''
  confirmPassword.value = ''
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
            :autocomplete="isRegister ? 'new-password' : 'current-password'"
            class="w-full rounded-2xl bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none ring-1 ring-slate-100 focus:ring-[var(--color-accent)]/40"
          />
        </div>
        <div v-if="isRegister">
          <label class="mb-1.5 block text-xs font-medium text-slate-500">确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            autocomplete="new-password"
            class="w-full rounded-2xl bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none ring-1 ring-slate-100 focus:ring-[var(--color-accent)]/40"
          />
        </div>
        <p v-if="error" class="text-center text-sm text-red-500">{{ error }}</p>
        <button
          type="submit"
          class="w-full rounded-2xl bg-[var(--color-accent)] py-3.5 text-sm font-semibold text-white shadow-[var(--shadow-soft-lg)] transition hover:opacity-95 disabled:opacity-60"
          :disabled="loading"
        >
          {{ loading ? (isRegister ? '注册中…' : '登录中…') : isRegister ? '注册并进入' : '进入备考系统' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-slate-500">
        <button type="button" class="font-medium text-[var(--color-accent)] hover:underline" @click="toggleMode">
          {{ isRegister ? '已有账号？返回登录' : '没有账号？立即注册' }}
        </button>
      </p>
    </div>
  </div>
</template>
