// /media/yagaven_25/coding/Projects/codeNames/vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  },
  preview: {
    port: 4173
  }
});
