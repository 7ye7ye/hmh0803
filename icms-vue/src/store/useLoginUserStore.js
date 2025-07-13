import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userApi } from '@/api/user'

export const useLoginUserStore = defineStore('loginUser', () => {
  // 从 localStorage 获取初始状态，如果没有则设为未登录
  const loginUser = ref({
    username: localStorage.getItem('username') || '未登录',
    role: localStorage.getItem('userRole') || '',
    loginTime: localStorage.getItem('loginTime') || ''
  })

  // 当前选中的菜单项
  const currentMenu = ref('home')

  // 设置当前选中的菜单项
  const setCurrentMenu = (menu) => {
    currentMenu.value = menu
  }

  // 设置登录用户
  const setLoginUser = (user) => {
    if (!user || user.username === '未登录') {
      loginUser.value = {
        username: '未登录',
        role: '',
        loginTime: ''
      }
      // 清除 localStorage
      localStorage.removeItem('username')
      localStorage.removeItem('userRole')
      localStorage.removeItem('loginTime')
    } else {
      loginUser.value = user
      // 保存到 localStorage
      localStorage.setItem('username', user.username)
      localStorage.setItem('userRole', user.role || '')
      localStorage.setItem('loginTime', user.loginTime || '')
    }
  }

  // 获取当前登录用户信息
  const fetchLoginUser = async () => {
    try {
      const response = await userApi.getCurrentUser()
      if (response.data && response.data.username) {
        setLoginUser({
          username: response.data.username,
          role: response.data.role,
          loginTime: new Date().toISOString()
        })
        return response.data
      } else {
        setLoginUser({ username: '未登录' })
        return null
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      setLoginUser({ username: '未登录' })
      return null
    }
  }

  // 检查登录状态
  const checkLoginStatus = async () => {
    try {
      const response = await userApi.getCurrentUser()
      if (response.data && response.data.username) {
        setLoginUser({
          username: response.data.username,
          role: response.data.role,
          loginTime: loginUser.value.loginTime || new Date().toISOString()
        })
        return true
      }
      return false
    } catch (error) {
      console.error('检查登录状态失败:', error)
      setLoginUser({ username: '未登录' })
      return false
    }
  }

  return {
    loginUser,
    currentMenu,
    setCurrentMenu,
    setLoginUser,
    fetchLoginUser,
    checkLoginStatus
  }
}, {
  persist: true // 启用持久化
})