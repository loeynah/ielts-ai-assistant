import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginRequest } from '@/api/auth'
import { cacheProfile, loadCachedProfile } from '@/api/user'

const TOKEN_KEY = 'ielts_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(loadCachedProfile())

  const isLoggedIn = computed(() => Boolean(token.value))

  async function login(username, password) {
    const data = await loginRequest(username, password)
    token.value = data.token
    user.value = data.user
    localStorage.setItem(TOKEN_KEY, data.token)
    cacheProfile(data.user)
    return data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    cacheProfile(null)
  }

  function setUser(profile) {
    user.value = profile
    cacheProfile(profile)
  }

  return { token, user, isLoggedIn, login, logout, setUser }
})
