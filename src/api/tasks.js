import { apiFetch } from './client'

export async function fetchTasks() {
  return await apiFetch('/api/tasks')
}

export async function replaceTasks(tasks) {
  return await apiFetch('/api/tasks', {
    method: 'PUT',
    body: JSON.stringify({ tasks }),
  })
}
