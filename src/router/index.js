import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: '主页 (Home Page)', navLabel: 'Dashboard' },
  },
  {
    path: '/listening',
    name: 'Listening',
    component: () => import('@/views/ListeningView.vue'),
    meta: { title: '听力训练', navLabel: 'Listening' },
  },
  {
    path: '/reading',
    name: 'Reading',
    component: () => import('@/views/ReadingView.vue'),
    meta: { title: '阅读训练', navLabel: 'Reading' },
  },
  {
    path: '/speaking',
    name: 'Speaking',
    component: () => import('@/views/SpeakingView.vue'),
    meta: { title: '口语评测', navLabel: 'Speaking' },
  },
  {
    path: '/writing',
    name: 'Writing',
    component: () => import('@/views/WritingView.vue'),
    meta: { title: '写作批改', navLabel: 'Writing' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (auth.isLoggedIn && to.name === 'Login') return '/dashboard'
    return true
  }
  if (!auth.isLoggedIn) return '/login'
  const userStore = useUserStore()
  if (!userStore.profile) {
    try {
      await userStore.initializeAfterLogin()
    } catch {
      auth.logout()
      return '/login'
    }
  }
  return true
})

router.afterEach((to) => {
  const base = '雅思智能备考助手'
  document.title = to.meta.title ? `${to.meta.title} · ${base}` : base
})

export default router
