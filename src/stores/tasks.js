import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { mockDailyPlan } from '@/config/resources'

const STORAGE_KEY = 'ielts_daily_tasks'
let idSeq = 100

function loadTasks() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function persistTasks(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

function seedTasks() {
  return Object.entries(mockDailyPlan.tasks).map(([key, content]) => ({
    id: ++idSeq,
    category: key,
    content,
    done: false,
    pinned: false,
    source: 'system',
  }))
}

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref(loadTasks() || seedTasks())

  const doneCount = computed(() => tasks.value.filter((t) => t.done).length)
  const totalCount = computed(() => tasks.value.length)

  function save() {
    persistTasks(tasks.value)
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
    save()
    return task
  }

  /** 追加 AI 同步的多条今日任务（不重复清空已有） */
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
    save()
  }

  function togglePin(task) {
    task.pinned = !task.pinned
    save()
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
    doneCount,
    totalCount,
    addTask,
    addTasksFromAi,
    removeTask,
    togglePin,
    applySpeakingFocus,
    save,
  }
})
