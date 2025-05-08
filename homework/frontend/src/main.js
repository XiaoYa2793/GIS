import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import './assets/map-animations.css'

// 引入Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入Element Plus图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 全局登录状态检查函数
const checkInitialAuthState = () => {
  const token = localStorage.getItem('accessToken')
  const user = localStorage.getItem('user')
  
  // 检查URL是否已经在登录页
  const isLoginPage = window.location.pathname === '/login'
  
  if (!token || !user) {
    // 未登录状态，重定向到登录页
    if (!isLoginPage) {
      window.location.href = '/login'
    }
  } else {
    // 已登录状态，如果在登录页则重定向到首页
    if (isLoginPage) {
      window.location.href = '/'
    }
  }
}

// 应用启动时进行一次状态检查
checkInitialAuthState()

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus)
app.mount('#app')