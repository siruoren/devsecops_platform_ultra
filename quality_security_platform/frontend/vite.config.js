import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://backend:8000',  // Docker 服务名
        changeOrigin: true
      }
    }
  }
})
