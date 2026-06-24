import { apiFetch } from './client'

export async function registerRequest(username, password) {
  return await apiFetch('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export async function loginRequest(username, password) {
  return await apiFetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}
