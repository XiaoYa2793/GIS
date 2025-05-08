import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath, URL } from 'url'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/videos': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/images': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    },
    fs: {
      // 允许访问上层目录的文件
      allow: ['..']
    }
  },
  // 禁用 favicon 请求
  experimental: {
    renderBuiltUrl(filename) {
      if (filename === 'favicon.ico') return false
      return filename
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  // 为前端提供静态视频文件的备用方案
  publicDir: path.resolve(__dirname, 'static'),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
}) 