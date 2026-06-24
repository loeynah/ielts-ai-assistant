import { apiFetch } from './client'
import { getToken } from './client'

const PROFILE_KEY = 'ielts_user_profile'

export function loadCachedProfile() {
  try {
    const raw = localStorage.getItem(PROFILE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function cacheProfile(profile) {
  if (profile) {
    localStorage.setItem(PROFILE_KEY, JSON.stringify(profile))
  } else {
    localStorage.removeItem(PROFILE_KEY)
  }
}

export async function patchUserProfile(payload) {
  const data = await apiFetch('/api/user/profile', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
  cacheProfile(data)
  return data
}

export async function fetchUserProfile() {
  try {
    const data = await apiFetch('/api/user/profile')
    cacheProfile(data)
    return data
  } catch {
    if (!getToken()) throw new Error('no token')
    const cached = loadCachedProfile()
    if (cached) return cached
    throw new Error('profile unavailable')
  }
}
