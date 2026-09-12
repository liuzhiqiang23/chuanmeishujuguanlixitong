import { createStore } from 'vuex'
import getters from './getters'

// Vite 下替代 webpack 的 require.context 自动加载所有 module
const modulesFiles = import.meta.glob('./modules/*.js', { eager: true })

const modules = Object.keys(modulesFiles).reduce((modules, modulePath) => {
  // './modules/app.js' => 'app'
  const moduleName = modulePath.replace(/^\.\/modules\/(.*)\.js$/, '$1')
  modules[moduleName] = modulesFiles[modulePath].default
  return modules
}, {})

const store = createStore({
  modules,
  getters
})

export default store
