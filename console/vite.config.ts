import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    cors: false,
    hmr: false,
    port: 6182,
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // rewrite: (path) => path.replace(/^\/api\/v1/, '')
      }
    }
  }
})
