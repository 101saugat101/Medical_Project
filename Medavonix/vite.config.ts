import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server : {
    port : 8000,
    host : true,
    proxy:{
    '/transcribe': {
      target: "http://fs.wiseyak.com:8048/",
      changeOrigin: false,
      // rewrite: (path) => path.replace(/^\/api/, '')
    }
  }},
})
