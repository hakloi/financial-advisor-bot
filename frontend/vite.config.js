import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://api:8000',
      '/users': 'http://api:8000',
      '/chat/send': 'http://api:8000',
      '/chat/history': 'http://api:8000',
      '/chat/messages': 'http://api:8000',
    }
  }
})
