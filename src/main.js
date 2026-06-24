import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setUnauthorizedHandler } from './api/client'
import { useAuthStore } from './stores/auth'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

setUnauthorizedHandler(() => {
  const auth = useAuthStore(pinia)
  auth.logout()
  if (router.currentRoute.value.name !== 'Login') {
    router.push('/login')
  }
})

app.mount('#app')