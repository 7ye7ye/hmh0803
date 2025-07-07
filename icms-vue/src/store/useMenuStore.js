import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMenuStore = defineStore('menu', () => {
  // 当前选中的菜单项
  const currentMenu = ref('home')

  // 设置当前选中的菜单项
  const setCurrentMenu = (menu) => {
    currentMenu.value = menu
  }

  return {
    currentMenu,
    setCurrentMenu
  }
}, {
  persist: true // 启用持久化
}) 