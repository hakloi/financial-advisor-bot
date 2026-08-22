import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/chat/send': 'http://localhost:8000',
      '/chat/history': 'http://localhost:8000',
    }
  }
})
