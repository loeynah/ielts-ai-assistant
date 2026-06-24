import { apiFetch } from './client'

export async function fetchModuleHistory(module) {
  return await apiFetch(`/api/history/${module}`)
}
