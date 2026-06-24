import {
  LayoutDashboard,
  Headphones,
  BookOpen,
  Mic,
  PenLine,
} from 'lucide-vue-next'

export const navItems = [
  { name: 'Dashboard', path: '/dashboard', label: '主页', icon: LayoutDashboard },
  { name: 'Listening', path: '/listening', label: '听力', icon: Headphones },
  { name: 'Reading', path: '/reading', label: '阅读', icon: BookOpen },
  { name: 'Speaking', path: '/speaking', label: '口语', icon: Mic },
  { name: 'Writing', path: '/writing', label: '写作', icon: PenLine },
]
