import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/login': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/logout': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/register': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/me': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/session': {
        target: 'http://backend:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})