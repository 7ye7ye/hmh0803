import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userApi } from '@/api/user'

export const useLoginUserStore = defineStore('loginUser', () => {
  // 从 localStorage 获取初始状态，如果没有则设为未登录
  const loginUser = ref({
    username: localStorage.getItem('username') || '未登录'
  })

  // 当前选中的菜单项
  const currentMenu = ref('home')

  // 设置当前选中的菜单项
  const setCurrentMenu = (menu) => {
    currentMenu.value = menu
  }

  // 设置登录用户
  const setLoginUser = (username) => {
    loginUser.value = {
      username: username || '未登录'
    }
    // 保存到 localStorage
    if (username && username !== '未登录') {
      localStorage.setItem('username', username)
    } else {
      localStorage.removeItem('username')
    }
  }

  // 获取当前登录用户信息
  const fetchLoginUser = async () => {
    try {
      const response = await userApi.getCurrentUser()
      if (response.data && response.data.username) {
        setLoginUser(response.data.username)
        return response.data
      } else {
        setLoginUser('未登录')
        return null
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      setLoginUser('未登录')
      return null
    }
  }

  // 检查登录状态
  const checkLoginStatus = async () => {
    try {
      const response = await userApi.getCurrentUser()
      console.log(response.data)
      if (response.data) {
        setLoginUser(response.data)
        return true
      }
      return false
    } catch (error) {
      console.error('检查登录状态失败:', error)
      setLoginUser('未登录')
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