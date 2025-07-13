import { createRouter, createWebHistory } from 'vue-router'
import { useLoginUserStore } from '@/store/useLoginUserStore' // 引入 Store
// import { showLoginPrompt } from '@/utils/auth' // 引入验证服务

import HomeView from '@/views/HomeView.vue'
import ApiResponseView from '@/views/ApiResponseView.vue'
import MonitoringView from '@/views/MonitoringView.vue'
import LoginView from '@/views/login/LoginView.vue'

const routes = [
  {
    path: '/',
    redirect: '/home'  // 根路径重定向到 home
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    // meta: { requiresAuth: true }  // 移除登录要求
  },
  // {
  //   path: '/admin',
  //   name: 'admin',
  //   component: HomeView,  // 这里应该改成你的管理员页面组件
  //   meta: { requiresAuth: true, requiresAdmin: true }  // 需要管理员权限
  // },
  {
    path: '/user/center',
    name: 'userCenter',
    component: () => import('@/views/user/UserCenter.vue'),
    meta: { 
      requiresAuth: true,
      title: '个人中心'
    }
  },
  {
    path: '/api-response',
    name: 'apiResponse',
    component: ApiResponseView,
    // meta: { requiresAuth: true } // 移除登录要求
  },
  {
    path: '/monitoring',
    name: 'monitoring',
    component: MonitoringView,
    // meta: { requiresAuth: true } // 移除登录要求
  },
 
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由导航守卫 - 简化为非强制登录模式
router.beforeEach(async (to, from, next) => {
  const loginUserStore = useLoginUserStore()
  
  // 如果是登录页面，直接放行
  if (to.name === 'login') {
    return next();
  }
  
  // 如果目标路由需要登录且用户是直接访问该路由（没有从应用内部其他页面跳转）
  if (to.matched.some(record => record.meta.requiresAuth) && 
      (!from.name || from.path === '/')) {
    // 检查登录状态
    const isLoggedIn = await loginUserStore.checkLoginStatus()
    if (!isLoggedIn) {
      // 重定向到登录页面，携带返回路径和提示信息
      return next({
        path: '/login',
        query: { 
          redirect: to.fullPath,
          message: '当前页面需要登录才能访问'
        }
      });
    }
  }
  
  // 其他情况，直接访问
  return next();
});

export default router
