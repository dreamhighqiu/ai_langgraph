
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVdWV1ZnPT06NzA1NWRmZDQ=

import { defineConfig, loadEnv } from 'vite'
import path from 'path'
import { fileURLToPath } from 'url'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
// TODO  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVdWV1ZnPT06NzA1NWRmZDQ=

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig(({ mode }: { mode: string }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
    // base: env.VITE_BASE_URL || '/webui/',
    base: '/webui/',
  build: {
    outDir: path.resolve(__dirname, '../lightrag/api/webui'),
    emptyOutDir: true,
    chunkSizeWarningLimit: 3800,
    rollupOptions: {
      // Let Vite handle chunking automatically to avoid circular dependency issues
      output: {
        // Ensure consistent chunk naming format
        chunkFileNames: 'assets/[name]-[hash].js',
        // Entry file naming format
        entryFileNames: 'assets/[name]-[hash].js',
        // Asset file naming format
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: env.VITE_API_PROXY === 'true' && env.VITE_API_ENDPOINTS ?
      Object.fromEntries(
          env.VITE_API_ENDPOINTS.split(',').map((endpoint: string) => [
          endpoint,
          {
              target: env.VITE_BACKEND_URL || 'http://localhost:9621',
            changeOrigin: true,
            rewrite: endpoint === '/api' ?
                (path: string) => path.replace(/^\/api/, '') :
              endpoint === '/docs' || endpoint === '/redoc' || endpoint === '/openapi.json' || endpoint === '/static' ?
                  (path: string) => path : undefined
          }
        ])
      ) : {}
    }
  }
})
