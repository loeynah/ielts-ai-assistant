import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginRequest, registerRequest } from '@/api/auth'
import { cacheProfile, loadCachedProfile } from '@/api/user'

const TOKEN_KEY = 'ielts_token'
const LEGACY_KEYS = ['ielts_speaking_history', 'ielts_daily_tasks']

function clearLegacyLocalData() {
  LEGACY_KEYS.forEach((k) => localStorage.removeItem(k))
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(loadCachedProfile())

  const isLoggedIn = computed(() => Boolean(token.value))

  function _persistSession(data) {
    token.value = data.token
    user.value = data.user
    localStorage.setItem(TOKEN_KEY, data.token)
    cacheProfile(data.user)
    clearLegacyLocalData()
  }

  async function login(username, password) {
    const data = await loginRequest(username, password)
    _persistSession(data)
    return data
  }

  async function register(username, password) {
    const data = await registerRequest(username, password)
    _persistSession(data)
    return data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    cacheProfile(null)
    clearLegacyLocalData()
  }

  function setUser(profile) {
    user.value = profile
    cacheProfile(profile)
  }

  return { token, user, isLoggedIn, login, register, logout, setUser }
})
