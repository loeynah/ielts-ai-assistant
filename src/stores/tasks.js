import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchTasks, replaceTasks } from '@/api/tasks'

let idSeq = 100

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref([])
  const loaded = ref(false)

  const doneCount = computed(() => tasks.value.filter((t) => t.done).length)
  const totalCount = computed(() => tasks.value.length)

  function reset() {
    tasks.value = []
    loaded.value = false
  }

  async function loadFromServer() {
    try {
      const data = await fetchTasks()
      tasks.value = Array.isArray(data) ? data : []
    } catch {
      tasks.value = []
    } finally {
      loaded.value = true
    }
  }

  async function saveToServer() {
    try {
      const saved = await replaceTasks(tasks.value)
      if (Array.isArray(saved)) tasks.value = saved
    } catch {
    }
  }

  async function save() {
    await saveToServer()
  }

  function addTask(category, content, source = 'ai') {
    const text = String(content || '').trim()
    if (!text) return null
    const valid = ['listening', 'reading', 'speaking', 'writing', 'other']
    const cat = valid.includes(category) ? category : 'other'
    const task = {
      id: ++idSeq,
      category: cat,
      content: text,
      done: false,
      pinned: false,
      source,
    }
    tasks.value.push(task)
    saveToServer()
    return task
  }

  function addTasksFromAi(taskList) {
    const added = []
    ;(taskList || []).forEach(({ category, content }) => {
      const t = addTask(category, content, 'ai')
      if (t) added.push(t)
    })
    return added
  }

  function removeTask(id) {
    tasks.value = tasks.value.filter((t) => t.id !== id)
    saveToServer()
  }

  function togglePin(task) {
    task.pinned = !task.pinned
    saveToServer()
  }

  function applySpeakingFocus() {
    tasks.value = tasks.value.map((t) => {
      if (t.source !== 'system' && t.source !== 'ai') return t
      if (t.category === 'reading' || t.category === 'listening') {
        return { ...t, content: `（减半）${t.content}` }
      }
      return t
    })
    addTask('speaking', 'Part 2 话题线索专项对练 · 第 1 轮', 'ai')
    addTask('speaking', 'Part 2 话题线索专项对练 · 第 2 轮', 'ai')
  }

  return {
    tasks,
    loaded,
    doneCount,
    totalCount,
    reset,
    loadFromServer,
    addTask,
    addTasksFromAi,
    removeTask,
    togglePin,
    applySpeakingFocus,
    save,
  }
})
