<template>
  <!-- 登录页面的根容器 -->
  <div class="login-page">
    <!-- 消息提示框，用于显示各种操作反馈 -->
    <div id="messageBox" v-if="messageText">{{ messageText }}</div>
    <!-- 主容器，包含注册和登录表单 -->
    <div class="shell">
      <!-- 注册表单容器 -->
      <div class="container a-container" id="a-container">
        <!-- 注册表单，阻止默认提交行为 -->
        <form @submit.prevent="handleRegister" class="form" id="a-form">
          <!-- 注册表单标题 -->
          <h2 class="form_title title">创建账号</h2>
          <!-- 注册表单提示文本 -->
          <span class="form_span">请选择注册角色并完成人脸信息采集</span>
          <!-- 角色选择器组件 -->
          <div class="role-selector">
            <a-radio-group v-model:value="registerForm.role">
              <a-radio-button value="student">学生</a-radio-button>
              <a-radio-button value="teacher">教师</a-radio-button>
            </a-radio-group>
          </div>
          <!-- 注册表单输入字段 -->
          <input type="text" class="form_input" v-model="registerForm.username" placeholder="请输入用户名">
          <input type="password" class="form_input" v-model="registerForm.password" placeholder="请输入密码">
          <input type="password" class="form_input" v-model="registerForm.checkPassword" placeholder="请确认密码">
          
          <!-- 人脸采集区域 -->
          <div class="face-capture">
           <!-- 视频采集容器，当未采集到人脸图像时显示 -->
            <div class="video-container" v-if="!registerForm.faceImage">
              <img 
                :src="videoFeedUrl"
                class="stream-image"
                @load="() => isRegisterPlayerReady = true"
                @error="() => errorMessage = '视频流加载失败'"
              />
              <div class="camera-placeholder" v-if="!isRegisterPlayerReady">
                <div class="camera-icon">📺</div>
                <div class="camera-text">正在连接视频流...</div>
                <div class="camera-help">{{ errorMessage || '如无法显示视频，请检查网络连接' }}</div>
              </div>
              <a-button class="capture-btn" @click="captureFaceForRegister" :disabled="!isRegisterPlayerReady || isProcessing" :loading="isProcessing">
                {{ isProcessing ? '正在采集中...' : '采集人脸信息' }}
              </a-button>
            </div>
            <!-- 人脸预览容器，采集完成后显示 -->
            <div class="preview-container" v-else>
              <img :src="registerForm.faceImage" class="face-preview" alt="人脸预览" />
              <a-button class="recapture-btn" @click="resetCapture">重新采集</a-button>
            </div>
          </div>

          <!-- 注册提交按钮 -->
          <button class="form_button button submit" @click.prevent="handleRegister">注 册</button>
        </form>
      </div>

      <!-- 登录表单容器 -->
      <div class="container b-container" id="b-container">
        <!-- 登录表单，阻止默认提交行为 -->
        <form @submit.prevent="handleLogin" class="form" id="b-form">
          <!-- 登录表单标题，根据登录状态显示不同文本 -->
          <h2 class="form_title title">{{ isLoggedIn ? '欢迎回来' : '登入账号' }}</h2>
          <!-- 未登录状态下显示的登录表单 -->
          <template v-if="!isLoggedIn">
            <!-- 登录表单提示文本 -->
            <span class="form_span">请选择登录角色并完成人脸验证</span>
            <!-- 角色选择器组件 -->
            <div class="role-selector">
              <a-radio-group v-model:value="loginForm.role">
                <a-radio-button value="student">学生</a-radio-button>
                <a-radio-button value="teacher">教师</a-radio-button>
              </a-radio-group>
            </div>
            <!-- 登录表单输入字段 -->
            <input type="text" class="form_input" v-model="loginForm.username" placeholder="请输入用户名">
            <input type="password" class="form_input" v-model="loginForm.password" placeholder="请输入密码">
            
            <!-- 人脸验证区域 -->
            <div class="face-capture">
              <!-- 登录表单的视频容器 -->
              <div class="video-container" v-if="!loginForm.faceImage">
                <img 
                  :src="videoFeedUrl"
                  class="stream-image"
                  @load="() => isLoginPlayerReady = true"
                  @error="() => errorMessage = '视频流加载失败'"
                />
                <div class="camera-placeholder" v-if="!isLoginPlayerReady">
                  <div class="camera-icon">📺</div>
                  <div class="camera-text">正在连接视频流...</div>
                  <div class="camera-help">{{ errorMessage || '如无法显示视频，请检查网络连接' }}</div>
                </div>
                <a-button class="capture-btn" @click="captureFaceForLogin" :disabled="!isLoginPlayerReady || isProcessing" :loading="isProcessing">
                  {{ isProcessing ? '正在验证中...' : '人脸验证' }}
                </a-button>
              </div>
              <!-- 人脸预览容器，验证完成后显示 -->
              <div class="preview-container" v-else>
                <img :src="loginForm.faceImage" class="face-preview" alt="人脸预览" />
                <a-button class="recapture-btn" @click="resetLoginCapture">重新验证</a-button>
              </div>
            </div>

            <!-- 忘记密码链接 -->
            <a class="form_link">忘记密码？</a>
            <!-- 登录提交按钮 -->
            <button class="form_button button submit" @click.prevent="handleLogin">登 录</button>
          </template>
          <!-- 已登录状态下显示的用户信息 -->
          <template v-else>
            <div class="user-info">
              <!-- 欢迎文本 -->
              <span class="welcome-text">欢迎您，{{ currentUsername }}</span>
              <!-- 用户角色标签 -->
              <div class="role-tag">{{ currentRole === 'teacher' ? '教师' : '学生' }}</div>
              <!-- 退出登录按钮 -->
              <button class="form_button button submit" @click.prevent="handleLogout">退出登录</button>
            </div>
          </template>
        </form>
      </div>

      <!-- 切换面板 -->
      <div class="switch" id="switch-cnt">
        <!-- 装饰性圆形背景 -->
        <div class="switch_circle"></div>
        <div class="switch_circle switch_circle-t"></div>
        <!-- 切换到登录的面板内容 -->
        <div class="switch_container" id="switch-c1">
          <h2 class="switch_title title" style="letter-spacing: 0;">Welcome Back！</h2>
          <p class="switch_description description">已有账号，登入账号来使用我们的系统！</p>
          <button class="switch_button button switch-btn" @click="changeForm">登 录</button>
        </div>

        <!-- 切换到注册的面板内容 -->
        <div class="switch_container is-hidden" id="switch-c2">
          <h2 class="switch_title title" style="letter-spacing: 0;">Hello Friend！</h2>
          <p class="switch_description description">注册一个新账号，开始使用我们的系统！</p>
          <button class="switch_button button switch-btn" @click="changeForm">注 册</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 导入所需的Vue组件和工具
import { defineComponent, ref, reactive, onMounted, watch, computed, onUnmounted, nextTick} from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLoginUserStore } from '@/store/useLoginUserStore'
import { userApi } from '@/api/user'
import { aiApi } from '../../api/ai'
import { message } from 'ant-design-vue';

export default defineComponent({
  name: 'LoginView',
  setup() {
    // 初始化路由和状态管理
    const router = useRouter()
    const route = useRoute()
    const loginUserStore = useLoginUserStore()

    // 视频流URL
    const videoFeedUrl = computed(() => {
      const baseUrl = process.env.VUE_APP_AI_API
      return `${baseUrl}/ai/facial/video_feed_cors?t=${Date.now()}`
    })

    // 监听视频流加载状态
    watch(videoFeedUrl, () => {
      const img = document.querySelector('.stream-image')
      if (img) {
        img.onload = () => {
          isRegisterPlayerReady.value = true
          isLoginPlayerReady.value = true
        }
        img.onerror = () => {
          errorMessage.value = '视频流加载失败'
          isRegisterPlayerReady.value = false
          isLoginPlayerReady.value = false
        }
      }
    })

    // 组件状态管理
    const isRegisterForm = ref(false)  // 控制显示注册还是登录表单
    const isLoggedIn = ref(false)      // 用户登录状态
    const currentUsername = ref('')     // 当前登录用户名
    const currentRole = ref('')         // 当前用户角色
    const messageText = ref('')         // 消息提示文本
    const isRegisterPlayerReady = ref(false) // 注册播放器就绪状态
    const isLoginPlayerReady = ref(false)    // 登录播放器就绪状态
    const errorMessage = ref('')        // 错误消息
    const isProcessing = ref(false)     // 处理状态标志

    // 登录表单数据
    const loginForm = reactive({
      username: '',
      password: '',
      role: 'student',
      faceEmbedding: null // 用于存储特征向量
    })

    // 注册表单数据
    const registerForm = reactive({
      username: '',
      password: '',
      checkPassword: '',
      role: 'student',
      faceImage: '',
      faceEmbedding: null // 用于存储特征向量
    })

    // 注册表单验证计算属性
    const isRegisterFormValid = computed(() => {
      return registerForm.username &&
             registerForm.password &&
             registerForm.checkPassword &&
             registerForm.password === registerForm.checkPassword &&
             registerForm.role &&
             registerForm.faceImage
    })

    // 登录表单验证计算属性
    const isLoginFormValid = computed(() => {
      return loginForm.username &&
             loginForm.password &&
             loginForm.role &&
             loginForm.faceEmbedding
    })

    // 注册时捕获人脸的函数
    const captureFaceForRegister = async () => {      
      isProcessing.value =true

      try {
        const response=await aiApi.start_facial_recognition()
        const faceEmbedding = response.data.data.vector
        console.log('response',response)
        console.log('faceEmbedding:', faceEmbedding)

        if (faceEmbedding) {
          registerForm.faceEmbedding = faceEmbedding
          showMessage('人脸信息采集成功')
        }
      } catch (error) {
        console.error('人脸采集失败:', error)
        showMessage('人脸采集失败，请重试')
      } finally {
        isProcessing.value = false
      }
    }

   
    // 重置注册人脸采集的函数
    const resetCapture = () => {
      captureFaceForLogin()      // 重新捕获
    }

    // 重置登录人脸采集的函数
    const resetLoginCapture = () => {
      captureFaceForLogin()      // 重新捕获
    }

    // 显示消息提示的函数
    const showMessage = (msg) => {
      console.log('msg:', msg)
      message.info(msg)
    }

    // 监听路由查询参数变化，显示消息
    watch(() => route.query, (newQuery) => {
      if (newQuery.message) {
        showMessage(newQuery.message)
      }
    }, { immediate: true })

    // 检查登录状态的函数
    const checkLoginStatus = async () => {
      try {
        const response = await userApi.getCurrentUser()
        if (response.data && response.data.username) {
          isLoggedIn.value = true
          currentUsername.value = response.data.username
          currentRole.value = response.data.role
          loginUserStore.setLoginUser(response.data.username)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    }

    // 退出登录的函数
    const handleLogout = async () => {
      try {
        await loginUserStore.logout()
        isLoggedIn.value = false
        currentUsername.value = ''
        currentRole.value = ''
        router.push('/login')
      } catch (error) {
        console.error('退出登录失败:', error)
        showMessage('退出登录失败，请重试')
      }
    }

     // 登录时捕获人脸的函数
     const captureFaceForLogin = async () => {      
      isProcessing.value =true
      try {
        const response =await userApi.login(loginForm)
        console.log('faceEmbedding:', response.data.faceEmbedding)

        if (response.data.faceEmbedding) {
          loginForm.faceEmbedding = response
          showMessage('人脸验证信息采集成功')
        }
      } catch (error) {
        console.error('人脸验证采集失败:', error)
        showMessage('人脸验证采集失败，请确认该账户是否为本人')
      } finally {
        isProcessing.value = false
      }
    }

    // 处理登录的函数
    const handleLogin = async () => {                                                                                                                                                             
      try {
        const response = await userApi.login(loginForm)
        const userData = response.data
        if (userData && userData.username) {
          const { username, role } = userData
          // 在 store 中保存用户信息
          loginUserStore.setLoginUser({
            username,
            role,
            loginTime: new Date().toISOString()
          })
          currentRole.value = role
          isLoggedIn.value = true 
          currentUsername.value = username 
          const redirect = route.query.redirect
          if (role === 'student') {
            router.push(redirect || '/home')
          } else if (role === 'teacher') {
            router.push('/teacher-dashboard')
          }
        } else {
          loginUserStore.setLoginUser({ username: '未登录' })
          showMessage(response.data.message || '登录失败，请检查用户名、密码或人脸信息')
        }
      } catch (error) {
        console.error('登录请求失败:', error)
        loginUserStore.setLoginUser({ username: '未登录' })
        showMessage('登录失败，请检查用户名、密码或人脸信息')
      }
    }

    // 处理注册的函数
    const handleRegister = async () => {
      if (registerForm.password !== registerForm.checkPassword) {
        showMessage('两次输入的密码不一致')
        return
      }
      
      try {
        const response = await userApi.register(registerForm)
        const { data } = response
        if (data.code === 0) {
          showMessage('注册成功，请登录')
          changeForm()
        } else {
          showMessage(data.message || '注册失败，请检查信息后重试')
        }
      } catch (error) {
        console.error('注册失败:', error)
        showMessage('注册失败，请检查信息后重试')
      }
    }

    // 切换登录/注册表单的函数
    const changeForm = () => {
      isRegisterForm.value = !isRegisterForm.value
      errorMessage.value = ''
      
      // 使用 nextTick 确保 DOM 已更新
      nextTick(() => {
        // 获取DOM元素
        const switchCtn = document.querySelector("#switch-cnt")
        const switchC1 = document.querySelector("#switch-c1")
        const switchC2 = document.querySelector("#switch-c2")
        const switchCircles = document.querySelectorAll(".switch_circle")
        const aContainer = document.querySelector("#a-container")
        const bContainer = document.querySelector("#b-container")

        if (!switchCtn || !switchC1 || !switchC2 || !aContainer || !bContainer) {
          console.error('Some DOM elements not found')
          return
        }

        // 添加过渡动画类
        switchCtn.classList.add("is-gx")
        setTimeout(() => {
          switchCtn.classList.remove("is-gx")
        }, 1500)

        // 切换表单显示状态
        switchCtn.classList.toggle("is-txr")
        switchCircles.forEach(circle => circle.classList.toggle("is-txr"))
        switchC1.classList.toggle("is-hidden")
        switchC2.classList.toggle("is-hidden")
        aContainer.classList.toggle("is-txl")
        bContainer.classList.toggle("is-txl")
        bContainer.classList.toggle("is-z")
      })
    }

    // 组件挂载时的处理
    onMounted(() => {
      // 处理 ResizeObserver 错误
      window.addEventListener('error', (e) => {
        if (e.message === 'ResizeObserver loop completed with undelivered notifications.') {
          const resizeObserverErr = e;
          resizeObserverErr.stopImmediatePropagation();
        }
      });

      checkLoginStatus().then(() => {
        if(isLoggedIn.value) return;

        // 设置视频流就绪状态的延迟检查
        setTimeout(() => {
          isRegisterPlayerReady.value = true;
          isLoginPlayerReady.value = true;
        }, 1000);

        // 在 nextTick 中处理路由查询参数
        nextTick(() => {
          const shouldRegister = route.query.register === 'true'
          if (shouldRegister) {
            changeForm()
          }
        })
      })
    })

    // 组件卸载时的清理
    onUnmounted(() => {
      // 移除 ResizeObserver 错误处理
      window.removeEventListener('error', () => {});
      
      // 清理相关状态
      isRegisterPlayerReady.value = false;
      isLoginPlayerReady.value = false;
    })

    // 返回组件所需的响应式数据和方法
    return {
      videoFeedUrl,
      loginForm,
      registerForm,
      isRegisterForm,
      isLoggedIn,
      currentUsername,
      currentRole,
      handleLogin,
      handleRegister,
      handleLogout,
      changeForm,
      messageText,
      isRegisterPlayerReady,
      isLoginPlayerReady,
      errorMessage,
      captureFaceForRegister,
      captureFaceForLogin,
      resetCapture,
      resetLoginCapture,
      isRegisterFormValid,
      isLoginFormValid,
      isProcessing
    }
  }
})
</script>

<style scoped>
/* 导入字体图标库 */
@import url('./fonts/iconfont.css');

.stream-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
  display: block; /* 防止图片底部间隙 */
}

/* 消息提示框样式 - 固定定位在顶部中间 */
#messageBox {
  position: fixed;
  top: 1px;
  left: 50%;
  transform: translateX(-50%);
  padding: 2px 24px;
  background: rgba(75, 112, 226, 0.8);
  color: #fff;
  border-radius: 6px;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 9999;
}

/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  user-select: none; /* 禁止文本选择，提升用户体验 */
}

/* 登录页面主容器 - 使用flex布局居中内容 */
.login-page {
  width: 100%;
  height: 85vh;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  background-color: #f0f2f5;
  color: #666;
}

/* 主要内容外壳 - 包含登录和注册表单的容器 */
.shell {
  position: relative;
  width: 80vw;
  max-width: 1400px;
  min-width: 1200px;
  height: 30vh;
  min-height: 600px;
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border-radius: 20px;
  overflow: hidden;
}

/* 表单容器基础样式 */
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  width: 60%;
  height: 100%;
  padding: 1px;
  background-color: #fff;
  transition: 1.25s;
}

/* 注册表单容器位置 */
.a-container {
  left: 40%;
  z-index: 10;
}

/* 登录表单容器位置 */
.b-container {
  left: 40%;
  z-index: 0;
}

/* 表单通用样式 */
.form {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 10px 0;
  overflow: hidden;
}

/* 表单标题样式 */
.form_title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 15px;
  color: #333;
  letter-spacing: 2px;
}

/* 表单提示文本样式 */
.form_span {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

/* 角色选择器容器样式 */
.role-selector {
  margin-bottom: 15px;
}

/* 表单输入框样式 */
.form_input {
  width: 100%;
  max-width: 400px;
  height: 45px;
  margin-bottom: 12px;
  padding: 0 20px;
  font-size: 14px;
  border: 2px solid #eee;
  border-radius: 10px;
  background-color: #fff;
  transition: all 0.3s ease;
}

/* 输入框获得焦点时的样式 */
.form_input:focus {
  border-color: #4B70E2;
  box-shadow: 0 0 0 3px rgba(75, 112, 226, 0.1);
  outline: none;
}

/* 人脸采集区域样式 */
.face-capture {
  width: 100%;
  max-width: 400px;
  margin: 20px auto;
  position: relative;
}

/* 视频容器样式 */
.video-container {
  width: 100%;
  max-width: 400px;
  height: 300px;
  position: relative;
  background-color: #f5f5f5;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

/* 视频元素样式 */
.capture-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

/* 摄像头占位符样式 */
.camera-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

/* 摄像头图标样式 */
.camera-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #666;
}

/* 摄像头提示文本样式 */
.camera-text {
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
}

/* 摄像头帮助文本样式 */
.camera-help {
  font-size: 14px;
  color: #666;
  max-width: 80%;
  line-height: 1.4;
}

/* 采集按钮样式 */
.capture-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 采集按钮悬停效果 */
.capture-btn:hover:not(:disabled) {
  background-color: #45a049;
  transform: translateX(-50%) scale(1.05);
}

/* 采集按钮禁用状态 */
.capture-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 预览容器样式 */
.preview-container {
  width: 100%;
  max-width: 400px;
  height: 300px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  margin: 0 auto;
}

/* 人脸预览图片样式 */
.face-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
  display: block;
}

/* 重新采集按钮样式 */
.recapture-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #ff4444;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 重新采集按钮悬停效果 */
.recapture-btn:hover {
  background-color: #ff3333;
  transform: translateX(-50%) scale(1.05);
}

/* 表单提交按钮样式 */
.form_button {
  width: 100%;
  max-width: 400px;
  height: 45px;
  margin-top: 15px;
  border-radius: 22px;
  font-size: 15px;
  font-weight: 600;
  background-color: #4B70E2;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 表单按钮悬停效果 */
.form_button:hover {
  background-color: #3857b8;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(75, 112, 226, 0.3);
}

/* 表单按钮禁用状态 */
.form_button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 切换面板容器样式 */
.switch {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 40%;
  padding: 30px;
  z-index: 200;
  transition: 1.25s;
  background: linear-gradient(135deg, #4B70E2, #3857b8);
  overflow: hidden;
}

/* 切换面板背景圆形装饰 */
.switch_circle {
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  bottom: -60%;
  left: -60%;
  transition: 1.25s;
}

/* 切换面板顶部圆形装饰 */
.switch_circle-t {
  top: -30%;
  left: 60%;
  width: 300px;
  height: 300px;
}

/* 切换面板内容容器样式 */
.switch_container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  position: absolute;
  width: 100%;
  padding: 30px;
  transition: 1.25s;
  color: white;
}

/* 切换面板标题样式 */
.switch_title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 15px;
}

/* 切换面板描述文本样式 */
.switch_description {
  font-size: 14px;
  text-align: center;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 20px;
}

/* 切换按钮样式 */
.switch_button {
  padding: 0 40px;
  height: 45px;
  border: 2px solid white;
  border-radius: 22px;
  font-size: 15px;
  font-weight: 600;
  background: transparent;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 切换按钮悬停效果 */
.switch_button:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

/* 切换面板向右移动动画类 */
.is-txr {
  left: 60%;
  transition: 1.25s;
  transform-origin: left;
}

/* 切换面板向左移动动画类 */
.is-txl {
  left: 0;
  transition: 1.25s;
  transform-origin: right;
}

/* 控制元素层级的类 */
.is-z {
  z-index: 200;
  transition: 1.25s;
}

/* 隐藏元素的类 */
.is-hidden {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  transition: 1.25s;
}

/* 角色标签样式 */
.role-tag {
  display: inline-block;
  padding: 5px 12px;
  background-color: #4B70E2;
  color: white;
  border-radius: 15px;
  margin: 10px 0;
  font-size: 14px;
}

/* 用户信息容器样式 */
.user-info {
  text-align: center;
}

/* 欢迎文本样式 */
.welcome-text {
  font-size: 20px;
  color: #4B70E2;
  font-weight: 600;
  margin-bottom: 8px;
}

/* Video.js播放器样式调整 */
::v-deep .video-js .vjs-big-play-button {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

::v-deep .vjs-fluid {
  padding-top: 0 !important;
}
</style>