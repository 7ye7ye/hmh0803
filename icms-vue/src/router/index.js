import { createRouter, createWebHistory } from 'vue-router'
import { useLoginUserStore } from '@/store/useLoginUserStore' // 引入 Store

import HomeView from '@/views/HomeView.vue'
import ApiResponseView from '@/views/ApiResponseView.vue'
import MonitoringView from '@/views/MonitoringView.vue'
import LoginView from '@/views/login/LoginView.vue'

const routes = [
  {
    path: '/',
    redirect: '/home' // 根路径重定向到 home
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
  },
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
    path: '/user/attendance',
    name: 'userAttendance',
    component: () => import('@/views/user/AttendanceView.vue'),
    meta: {
      requiresAuth: true,
      // requiresUser: true, // 保持原样，如果这个meta有特殊用途
      title: '考勤管理'
    }
  },
  {
    path: '/api-response',
    name: 'apiResponse',
    component: ApiResponseView,
  },
  {
    path: '/monitoring',
    name: 'monitoring',
    component: MonitoringView,
    meta: {
      requiresAuth: true,      // 监控页面也需要登录
      requiresTeacher: true,   // 监控页面需要教师角色
      title: '实时监控'
    }
  },

  {
    path: '/login',
    name: 'login',
    component: LoginView
  }
  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由导航守卫
router.beforeEach(async (to, from, next) => {
  const loginUserStore = useLoginUserStore()

  // 如果是登录页面，直接放行
  if (to.name === 'login') {
    return next()
  }

  // 1. 检查是否需要登录 (requiresAuth)
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const isLoggedIn = loginUserStore.loginUser.username !== '未登录' // 总是检查最新的登录状态

    if (!isLoggedIn) {
      // 未登录，重定向到登录页面
      return next({
        path: '/login',
        query: {
          redirect: to.fullPath,
          message: '请先登录才能访问该页面。'
        }
      })
    }
  }

  // 2. 检查是否需要教师角色 (requiresTeacher)
  if (to.matched.some(record => record.meta.requiresTeacher)) {
    // 确保用户已登录且角色信息已加载
    if (loginUserStore.loginUser.role !== 'teacher') { // 假设教师角色字符串是 'teacher'
      // 不是教师，重定向到登录页面并给出提示
      return next({
        path: '/login',
        query: {
          redirect: to.fullPath,
          message: '您没有权限访问此页面，实时监控功能仅教师可用。'
        }
      })
    }
  }

  // 其他情况，直接访问
  next()
})

export default router