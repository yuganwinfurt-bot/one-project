import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '127.0.0.1',
    port: 35173, // 避开 Windows 当前保留的 5141–5240 端口范围。
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001', //  /api -> http://127.0.0.1:8001/api
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://127.0.0.1:8001', //  /uploads -> http://127.0.0.1:8001/uploads
        changeOrigin: true
      }
    }
  }
})
