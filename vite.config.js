import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'
import fs from 'node:fs'
import path from 'node:path'
import sirv from 'sirv'

const assetsRoot = path.join(__dirname, 'assets')

function staticDirPlugin(mountPath, dir, name) {
  if (!dir || !fs.existsSync(dir)) {
    console.warn(`[vite] ${name} 目录未找到，静态资源挂载已跳过: ${dir}`)
    return { name: `static-${name}-skip` }
  }
  const mount = (server) => {
    server.middlewares.use(mountPath, sirv(dir, { dev: true, single: false }))
  }
  return { name: `static-${name}`, configureServer: mount, configurePreviewServer: mount }
}

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    staticDirPlugin('/assets/reading-exams', path.join(assetsRoot, 'reading-exams'), 'reading-exams'),
    staticDirPlugin('/assets/listening', path.join(assetsRoot, 'listening'), 'listening'),
    staticDirPlugin('/assets/writing', path.join(assetsRoot, 'writing'), 'writing'),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    open: true,
  },
})
