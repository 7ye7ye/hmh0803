<template>
    <div id="globalHeader">
      <a-row :wrap="false">
        <!-- 左侧：Logo + 标题（固定宽度） -->
        <a-col flex="300px">
            <img class="logo" src="@/assets/BJTUlogo.png" alt="logo" />
        </a-col>
        <!-- 中间：菜单（自适应宽度，占满中间区域） -->
        <a-col flex="auto">
            <a-menu
                class="menu"
                v-model:selectedKeys="current"
                mode="horizontal"
                :items="items"
                @click="handleClick"
            />
        </a-col>
        <!-- 右侧：登录按钮（固定宽度） -->
        <a-col flex="120px">
          <div class="user-login-status">
            <div v-if="loginUserStore.loginUser.username === '未登录'">
              <a-button type="primary" ghost @click="jumpToLoginPage">登录</a-button>
            </div>
            <div v-else class="user-info">
              <a-dropdown>
                <a class="ant-dropdown-link" @click.prevent>
                  <UserOutlined />
                  <span class="username">{{ loginUserStore.loginUser.username }}</span>
                  <DownOutlined />
                </a>
                <template #overlay>
                  <a-menu>
                    <a-menu-item key="0" @click="jumpToUserCenter">
                      <UserOutlined />
                      <span>个人中心</span>
                    </a-menu-item>
                    <a-menu-item key="1" @click="handleLogout">
                      <LogoutOutlined />
                      <span>退出登录</span>
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </div>
          </div>
        </a-col>
      </a-row>
    </div>
  </template>
  
  <script setup>
  import { ref, watchEffect, onMounted} from 'vue'
  import { useRouter } from 'vue-router'
  import { useLoginUserStore  } from '@/store/useLoginUserStore'
  import { useMenuStore } from '@/store/useMenuStore'
  import { DownOutlined, UserOutlined, LogoutOutlined} from '@ant-design/icons-vue'
  import { userApi } from '@/api/user'

  const loginUserStore = useLoginUserStore()
  const router = useRouter()
  const menuStore = useMenuStore()
  
  // 初始化选中项，使用 store 中的状态
  const current = ref([menuStore.currentMenu])
  
  const items = ref([
    { key: 'home', label: '首页', title: '首页' },
    { key: 'apiResponse', label: '智能监控api', title: '快速响应api' },
    { key: 'monitoring', label: '教室监控', title: '教室监控' },
  ])
  
  const handleClick = (e) => {
    current.value = [e.key]
    menuStore.setCurrentMenu(e.key)
    router.push({ name: e.key })
  }
  
  // 监听 store 中的状态变化
  watchEffect(() => {
    current.value = [menuStore.currentMenu]
  })

  // 检查登录状态
  const checkAuth = async () => {
    await loginUserStore.checkLoginStatus()
  }

  onMounted(async () => {
    await checkAuth()
  })

  // 每次路由变化时检查登录状态
  watchEffect(async () => {
    await checkAuth()
  })

  const jumpToLoginPage = () => {
    router.push('/login')
  }

  const handleLogout = async () => {
    try {
      // 调用后端退出登录接口
      await userApi.logout()
      
      // 清除前端状态
      loginUserStore.setLoginUser('未登录')
      
      // 清除前端 cookie
      document.cookie = 'JSESSIONID=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
      
      // 跳转到登录页
      router.push('/login')
    } catch (error) {
      console.error('退出登录失败:', error)
      // 即使后端接口失败，也清除前端状态
      loginUserStore.setLoginUser('未登录')
      router.push('/login')
    }
  }

  const jumpToUserCenter = async () => {
      router.push('/user/center');
  }

  </script>
  
  <style scoped>
  #globalHeader {
    width: 100%;
}

    .logo {
        height: 45px;
        padding-left: 60px;
    }

    .menu {
        height: 50px;
        align-items: center;
        font-size: 16px;
        margin-left: 30px;
        }

    .user-login-status {
        display: flex;
        justify-content: center; /* 水平居中 */
        align-items: center;     /* 垂直居中 */
        width: 100%;
        height: 100%;
        padding: 0;
    }

    .user-info {
        display: flex;
        align-items: center;
    }

    .ant-dropdown-link {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #4B70E2;
        cursor: pointer;
    }

    .username {
        margin: 0 4px;
        max-width: 80px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    :deep(.anticon) {
        font-size: 16px;
    }

  </style>