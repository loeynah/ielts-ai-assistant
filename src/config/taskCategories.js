import { BookOpen, Headphones, Layers, Mic, PenLine } from 'lucide-vue-next'

export const TASK_CATEGORIES = [
  { key: 'listening', label: '听力', icon: Headphones },
  { key: 'reading', label: '阅读', icon: BookOpen },
  { key: 'speaking', label: '口语', icon: Mic },
  { key: 'writing', label: '写作', icon: PenLine },
  { key: 'other', label: '其他', icon: Layers },
]

export function getCategoryMeta(key) {
  return TASK_CATEGORIES.find((c) => c.key === key) || TASK_CATEGORIES[4]
}
