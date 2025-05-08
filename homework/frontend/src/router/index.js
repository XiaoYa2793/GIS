import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/attractions',
      name: 'attractions',
      component: () => import('../components/AttractionList.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/historical-maps',
      name: 'historical-maps',
      component: () => import('../views/HistoricalMapView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/simple-maps',
      name: 'simple-maps',
      component: () => import('../views/SimpleMapView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/time-space-journey',
      name: 'TimeSpaceJourney',
      component: () => import('../views/TimeSpaceJourney.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/recommendations',
      name: 'recommendations',
      component: () => import('../views/RecommendationView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/recommendation/:id',
      name: 'recommendation-detail',
      component: () => import('../views/RecommendationView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/navigation',
      name: 'navigation',
      component: () => import('../components/Navigation.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/travel-assistant',
      name: 'travel-assistant',
      component: () => import('../views/TravelAssistant.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/time-space-view',
      name: 'time-space-view',
      component: () => import('../views/TimeSpaceView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/UserProfileView.vue'),
      meta: {
        requiresAuth: true
      }
    }
  ]
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
  console.log(`路由导航: 从 ${from.path} 到 ${to.path}`);
  
  // 检查用户是否已登录
  const isAuthenticated = !!localStorage.getItem('accessToken');
  
  // 如果需要登录但用户未登录，重定向到登录页面
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next({ name: 'login' });
    return;
  }
  
  // 如果用户已登录并且访问的是登录页，则重定向到首页
  if (to.name === 'login' && isAuthenticated) {
    next({ name: 'home' });
    return;
  }
  
  // 检查是否是直接访问需要身份验证的页面（比如刷新或直接通过URL访问）
  const isDirectAccess = from.name === null || from.name === undefined;
  
  // 如果是直接访问了需要身份验证的页面，且用户已登录，强制刷新一次以确保正确加载状态
  if (isDirectAccess && to.matched.some(record => record.meta.requiresAuth) && isAuthenticated) {
    // 使用会话存储来防止无限刷新循环
    const hasRefreshed = sessionStorage.getItem('has_refreshed_' + to.fullPath);
    if (!hasRefreshed) {
      // 标记此路径已经刷新过
      sessionStorage.setItem('has_refreshed_' + to.fullPath, 'true');
      // 使用location.reload()强制刷新页面
      window.location.reload();
      return;
    }
    // 清除刷新标记，以便用户下次手动刷新页面时能再次触发
    sessionStorage.removeItem('has_refreshed_' + to.fullPath);
  }
  
  next();
});

export default router 