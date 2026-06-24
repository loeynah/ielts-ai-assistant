import { apiFetch } from './client'

export async function requestChat(message, context = {}) {
  return apiFetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message, context }),
  })
}
