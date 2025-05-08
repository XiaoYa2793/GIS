<template>
  <div id="app" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <ThreeBackground />
    
    <!-- 登录页面 -->
    <template v-if="!isAuthenticated">
      <router-view></router-view>
    </template>
    
    <!-- 已登录后的系统界面 -->
    <template v-else>
      <!-- 顶部导航栏 -->
      <header class="header">
        <h2 class="app-title">北京旅游系统</h2>
        
        <!-- 用户头像下拉菜单 -->
        <div class="user-menu">
          <el-dropdown @command="handleUserCommand" trigger="click">
            <div class="user-avatar">
              <el-avatar :size="36" :src="userAvatarUrl">
                {{ userInfo.username ? userInfo.username.charAt(0).toUpperCase() : 'U' }}
              </el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><user /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><switch-button /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- 左侧导航栏 -->
      <nav class="sidebar" :class="{ 'collapsed': sidebarCollapsed }">
        <div class="sidebar-header">
          <div class="logo">BTS</div>
          <div class="logo-text" v-show="!sidebarCollapsed">Beijing Travel System</div>
        </div>
        
        <!-- 导航栏切换按钮 -->
        <button class="toggle-sidebar" @click="toggleSidebar">
          <i class="fas" :class="sidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'"></i>
        </button>
        
        <div class="nav-links">
          <router-link to="/" class="nav-link" exact-active-class="router-link-active">
            <i class="fas fa-home"></i>
            <span v-show="!sidebarCollapsed">首页</span>
            <div class="hover-effect"></div>
          </router-link>
          <router-link to="/attractions" class="nav-link" exact-active-class="router-link-active">
            <i class="fas fa-landmark"></i>
            <span v-show="!sidebarCollapsed">景点列表</span>
            <div class="hover-effect"></div>
          </router-link>
          <router-link to="/recommendations" class="nav-link">
            <i class="fas fa-search"></i>
            <span v-show="!sidebarCollapsed">景点推荐</span>
            <div class="hover-effect"></div>
          </router-link>
          <router-link to="/navigation" class="nav-link">
            <i class="fas fa-map-marker-alt"></i>
            <span v-show="!sidebarCollapsed">实地导航</span>
            <div class="hover-effect"></div>
          </router-link>
          <router-link to="/simple-maps" class="nav-link" exact-active-class="router-link-active">
            <i class="fas fa-map-marked-alt"></i>
            <span v-show="!sidebarCollapsed">简化地图 (调试)</span>
            <div class="hover-effect"></div>
          </router-link>
          <router-link to="/travel-assistant" class="nav-link">
            <i class="fas fa-comments"></i>
            <span v-show="!sidebarCollapsed">旅游助手</span>
            <div class="hover-effect"></div>
          </router-link>
        </div>
      </nav>

      <!-- 主要内容区域 -->
      <main class="main-content" :class="{ 'expanded': sidebarCollapsed }">
        <router-view></router-view>
      </main>
    </template>
  </div>
</template>

<script setup>
import ThreeBackground from './components/ThreeBackground.vue'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 导航栏收起状态
const sidebarCollapsed = ref(false)

// 用户登录状态和信息
const isAuthenticated = ref(false)
const userInfo = ref({})

// 用户头像URL - 如果没有则使用默认头像
const userAvatarUrl = computed(() => {
  // 这里可以配置返回用户的头像URL，如果有的话
  return '';
})

// 检查用户登录状态
const checkAuth = () => {
  const token = localStorage.getItem('accessToken')
  const user = localStorage.getItem('user')
  
  if (token && user) {
    isAuthenticated.value = true
    try {
      userInfo.value = JSON.parse(user)
      console.log('用户已登录:', userInfo.value.username)
    } catch (e) {
      console.error('解析用户信息失败:', e)
      // 如果解析失败，清除可能损坏的存储数据
      localStorage.removeItem('accessToken')
      localStorage.removeItem('user')
      isAuthenticated.value = false
      userInfo.value = {}
    }
  } else {
    isAuthenticated.value = false
    userInfo.value = {}
    console.log('用户未登录')
    
    // 如果用户未登录且不在登录页，则重定向到登录页
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
    }
  }
}

// 处理用户下拉菜单命令
const handleUserCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    // 清除登录信息
    localStorage.removeItem('accessToken')
    localStorage.removeItem('user')
    isAuthenticated.value = false
    userInfo.value = {}
    
    ElMessage.success('已成功退出登录')
    router.push('/login')
  }
}

// 切换导航栏展开/收起
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  
  // 将状态保存到本地存储中，以便刷新后保持状态
  localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value)
}

// 从本地存储加载导航栏状态
if (typeof localStorage !== 'undefined') {
  const savedState = localStorage.getItem('sidebarCollapsed')
  if (savedState !== null) {
    sidebarCollapsed.value = savedState === 'true'
  }
}

// 初始化加载用户状态
onMounted(() => {
  checkAuth()
  
  // 添加存储事件监听器，当localStorage变化时检查登录状态
  window.addEventListener('storage', checkAuth)
  
  // 在组件卸载时移除监听器
  return () => {
    window.removeEventListener('storage', checkAuth)
  }
})
</script>

<style>
/* 移除全局滚动条 */
::-webkit-scrollbar {
  display: none;
}

/* 确保内容可以滚动但滚动条不可见 */
* {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

body {
  margin: 0;
  overflow-x: hidden;
  background: #0a192f;
}

#app {
  display: flex;
  min-height: 100vh;
  font-family: 'Roboto', sans-serif;
  color: #fff;
}

/* 顶部导航栏样式 */
.header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background: rgba(26, 31, 44, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-sizing: border-box;
  z-index: 101;
}

.app-title {
  margin: 0;
  color: #42b983;
  font-size: 1.5rem;
}

.user-menu {
  display: flex;
  align-items: center;
}

.user-avatar {
  cursor: pointer;
  transition: transform 0.2s;
}

.user-avatar:hover {
  transform: scale(1.1);
}

.el-avatar {
  background-color: #42b983;
  color: #fff;
  font-weight: bold;
  box-shadow: 0 4px 10px rgba(66, 185, 131, 0.3);
}

.sidebar {
  width: 280px;
  background: rgba(26, 31, 44, 0.8);
  backdrop-filter: blur(10px);
  color: #fff;
  padding: 2rem 1rem;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 60px; /* 顶部导航栏高度 */
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 15px rgba(0,0,0,0.1);
  z-index: 100;
  transition: all 0.3s ease;
}

/* 收起时的侧边栏样式 */
.sidebar.collapsed {
  width: 70px;
  padding: 2rem 0.5rem;
}

.sidebar-header {
  text-align: center;
  margin-bottom: 3rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo {
  font-size: 2.5rem;
  font-weight: bold;
  color: #42b983;
  text-shadow: 0 0 10px rgba(66,185,131,0.3);
  margin-bottom: 0.5rem;
}

.logo-text {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.7);
  letter-spacing: 2px;
  transition: opacity 0.3s ease;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 3rem;
}

.nav-link {
  text-decoration: none;
  color: #fff;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.nav-link i {
  margin-right: 1rem;
  font-size: 1.2rem;
  min-width: 20px;
  text-align: center;
}

.sidebar.collapsed .nav-link {
  padding: 1rem;
  justify-content: center;
}

.sidebar.collapsed .nav-link i {
  margin-right: 0;
  font-size: 1.2rem;
}

.nav-link:hover {
  background: rgba(66,185,131,0.2);
}

.nav-link.router-link-active {
  background: rgba(66,185,131,0.3);
  box-shadow: 0 0 20px rgba(66,185,131,0.1);
}

/* 主内容区域调整 */
.main-content {
  flex: 1;
  margin-left: 280px;
  padding: 20px;
  padding-top: 80px; /* 顶部导航栏高度 + 间距 */
  transition: margin-left 0.3s ease;
}

.main-content.expanded {
  margin-left: 70px;
}

/* 玻璃态效果 */
.main-content > * {
  background: rgba(26, 31, 44, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 添加导航栏切换按钮 */
.toggle-sidebar {
  position: absolute;
  top: 50%;
  right: -15px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #42b983;
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transform: translateY(-50%);
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
  z-index: 101;
  transition: all 0.3s ease;
}

.toggle-sidebar:hover {
  background: #3aa876;
  transform: translateY(-50%) scale(1.1);
}

/* 添加一些动画效果 */
@keyframes glow {
  0% { box-shadow: 0 0 5px rgba(66,185,131,0.2); }
  50% { box-shadow: 0 0 20px rgba(66,185,131,0.4); }
  100% { box-shadow: 0 0 5px rgba(66,185,131,0.2); }
}

.nav-link.router-link-active {
  animation: glow 2s infinite;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(0);
    transition: transform 0.3s ease;
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .main-content {
    margin-left: 0;
    width: 100%;
    padding: 1rem;
  }
  
  .toggle-sidebar {
    right: auto;
    left: 10px;
    top: 10px;
    transform: none;
  }
  
  .sidebar.collapsed .toggle-sidebar {
    right: auto;
    left: 10px;
  }
}
</style> 