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

  // 退出登录
  const logout = async () => {
    try {
      // 调用后端退出登录接口
      await userApi.logout()
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      // 无论后端是否成功，都清除前端状态
      setLoginUser({ username: '未登录' })
      // 清除前端 cookie
      document.cookie = 'JSESSIONID=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
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

  return {
    loginUser,
    currentMenu,
    setCurrentMenu,
    setLoginUser,
    fetchLoginUser,
    logout
  }
}, {
  persist: true // 启用持久化
})