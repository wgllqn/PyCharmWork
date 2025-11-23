import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    target: 'esnext',
    outDir: 'dist',
  },
  server: {
    port: 3000,
    open: true,
    host: '0.0.0.0',  // 允许局域网访问
    proxy: {
      '/api': {
        target: 'http://192.168.106.201:8000',  // 使用本机IP
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/upload': {
        target: 'http://192.168.106.201:8000',
        changeOrigin: true,
      },
      '/query': {
        target: 'http://192.168.106.201:8000',
        changeOrigin: true,
      },
      '/visualize': {
        target: 'http://192.168.106.201:8000',
        changeOrigin: true,
      },
    },
  },
});