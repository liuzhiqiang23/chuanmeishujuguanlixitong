import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'

// https://vitejs.dev/config/
export default defineConfig({
  // 与旧 vue-cli 的 publicPath: './' 保持一致，产物可用相对路径部署
  base: './',
  plugins: [
    vue(),
    // svg 雪碧图：替代 webpack 的 svg-sprite-loader
    createSvgIconsPlugin({
      iconDirs: [path.resolve(process.cwd(), 'src/icons/svg')],
      symbolId: 'icon-[name]'
    })
  ],
  resolve: {
    // webpack 迁移过来大量省略 .vue 后缀的 import，这里补上扩展名解析
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue'],
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: 'localhost',
    port: 8002,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/eda': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'admin',
    assetsDir: 'static',
    sourcemap: false,
    chunkSizeWarningLimit: 4000,
    // 不清空输出目录：前端产物含 public/ 下上千个第三方组件文件（ueditor/echarts），
    // 每次构建全量删除易触发编辑器的批量删除保护导致构建中断；
    // 资源文件名带内容哈希，旧文件残留不影响运行（index.html 始终引用最新 bundle）。
    emptyOutDir: false
  }
})
