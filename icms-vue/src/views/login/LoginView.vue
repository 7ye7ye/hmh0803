<template>
  <div class="login-page">
    <div id="messageBox" v-if="messageText">{{ messageText }}</div>
    <div class="shell">
      <div class="container a-container" id="a-container">
        <form @submit.prevent="handleRegister" class="form" id="a-form">
          <h2 class="form_title title">创建账号</h2>
          <span class="form_span">请选择注册角色并完成人脸信息采集</span>
          <div class="role-selector">
            <a-radio-group v-model:value="registerForm.role">
              <a-radio-button value="student">学生</a-radio-button>
              <a-radio-button value="teacher">教师</a-radio-button>
            </a-radio-group>
          </div>
          <input type="text" class="form_input" v-model="registerForm.username" placeholder="请输入用户名">
          <input type="password" class="form_input" v-model="registerForm.password" placeholder="请输入密码">
          <input type="password" class="form_input" v-model="registerForm.checkPassword" placeholder="请确认密码">
          
          <div class="face-capture">
            <div class="video-container" v-if="!registerForm.faceImage">
              <video ref="videoRef" class="capture-video" autoplay playsinline muted></video>
              <div class="camera-placeholder" v-if="!currentStream">
                <div class="camera-icon">📷</div>
                <div class="camera-text">等待摄像头权限...</div>
                <div class="camera-help">{{ errorMessage || '如看不到摄像头画面，请点击地址栏的锁头图标授予权限' }}</div>
              </div>
              <a-button class="capture-btn" @click="captureFace" :disabled="!currentStream">采集人脸信息</a-button>
            </div>
            <div class="preview-container" v-else>
              <img :src="registerForm.faceImage" class="face-preview" alt="人脸预览" />
              <a-button class="recapture-btn" @click="resetCapture">重新采集</a-button>
            </div>
          </div>

          <button class="form_button button submit" @click.prevent="handleRegister" :disabled="!isRegisterFormValid">注 册</button>
        </form>
      </div>

      <div class="container b-container" id="b-container">
        <form @submit.prevent="handleLogin" class="form" id="b-form">
          <h2 class="form_title title">{{ isLoggedIn ? '欢迎回来' : '登入账号' }}</h2>
          <template v-if="!isLoggedIn">
            <span class="form_span">请选择登录角色并完成人脸验证</span>
            <div class="role-selector">
              <a-radio-group v-model:value="loginForm.role">
                <a-radio-button value="student">学生</a-radio-button>
                <a-radio-button value="teacher">教师</a-radio-button>
              </a-radio-group>
            </div>
            <input type="text" class="form_input" v-model="loginForm.username" placeholder="请输入用户名">
            <input type="password" class="form_input" v-model="loginForm.password" placeholder="请输入密码">
            
            <div class="face-capture">
              <div class="video-container" v-if="!loginForm.faceImage">
                <video ref="loginVideoRef" class="capture-video" autoplay playsinline muted></video>
                <div class="camera-placeholder" v-if="!currentStream">
                  <div class="camera-icon">📷</div>
                  <div class="camera-text">等待摄像头权限...</div>
                  <div class="camera-help">{{ errorMessage || '如看不到摄像头画面，请点击地址栏的锁头图标授予权限' }}</div>
                </div>
                <a-button class="capture-btn" @click="captureFaceForLogin" :disabled="!currentStream">人脸验证</a-button>
              </div>
              <div class="preview-container" v-else>
                <img :src="loginForm.faceImage" class="face-preview" alt="人脸预览" />
                <a-button class="recapture-btn" @click="resetLoginCapture">重新验证</a-button>
              </div>
            </div>

            <a class="form_link">忘记密码？</a>
            <button class="form_button button submit" @click.prevent="handleLogin" :disabled="!isLoginFormValid">登 录</button>
          </template>
          <template v-else>
            <div class="user-info">
              <span class="welcome-text">欢迎您，{{ currentUsername }}</span>
              <div class="role-tag">{{ currentRole === 'teacher' ? '教师' : '学生' }}</div>
              <button class="form_button button submit" @click.prevent="handleLogout">退出登录</button>
            </div>
          </template>
        </form>
      </div>

      <div class="switch" id="switch-cnt">
        <div class="switch_circle"></div>
        <div class="switch_circle switch_circle-t"></div>
        <div class="switch_container" id="switch-c1">
          <h2 class="switch_title title" style="letter-spacing: 0;">Welcome Back！</h2>
          <p class="switch_description description">已有账号，登入账号来使用我们的系统！</p>
          <button class="switch_button button switch-btn" @click="changeForm">登 录</button>
        </div>

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
import { defineComponent, ref, reactive, onMounted, watch, computed, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLoginUserStore } from '@/store/useLoginUserStore'
import { userApi } from '@/api/user'

export default defineComponent({
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const loginUserStore = useLoginUserStore()
    const isRegisterForm = ref(false)
    const isLoggedIn = ref(false)
    const currentUsername = ref('')
    const currentRole = ref('')
    const messageText = ref('')
    const videoRef = ref(null)
    const loginVideoRef = ref(null)
    const currentStream = ref(null)
    const errorMessage = ref('')

    const loginForm = reactive({
      username: '',
      password: '',
      role: 'student',
      faceImage: ''
    })

    const registerForm = reactive({
      username: '',
      password: '',
      checkPassword: '',
      role: 'student',
      faceImage: ''
    })

    const isRegisterFormValid = computed(() => {
      return registerForm.username &&
             registerForm.password &&
             registerForm.checkPassword &&
             registerForm.password === registerForm.checkPassword &&
             registerForm.role &&
             registerForm.faceImage
    })

    const isLoginFormValid = computed(() => {
      return loginForm.username &&
             loginForm.password &&
             loginForm.role &&
             loginForm.faceImage
    })

    const initCamera = async (videoElement) => {
      if (!videoElement) {
        const errorMsg = '摄像头初始化失败: 视频DOM元素未找到。'
        console.error(errorMsg)
        errorMessage.value = errorMsg
        return
      }

      try {
        stopCamera()

        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
          },
          audio: false
        })

        currentStream.value = stream
        videoElement.srcObject = stream
        videoElement.onloadedmetadata = () => {
          videoElement.play().catch(err => {
            console.error('视频播放失败:', err)
            errorMessage.value = '视频播放失败，请刷新页面重试'
          })
        }
        errorMessage.value = ''
      } catch (err) {
        console.error('摄像头初始化失败:', err)
        let message = '摄像头初始化失败: '
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          message += '请在浏览器的权限提示中允许使用摄像头。如果没有看到提示，请点击地址栏的锁头图标，确保摄像头权限为"允许"。'
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
          message += '未检测到摄像头设备，请确保摄像头已正确连接。'
        } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
          message += '摄像头可能被其他应用程序占用，请关闭其他使用摄像头的程序后重试。'
        } else if (err.name === 'OverconstrainedError') {
          message += '摄像头不支持请求的分辨率。'
        } else {
          message += '请检查摄像头权限和设备连接状态。'
        }
        errorMessage.value = message
        showMessage(message)
      }
    }

    const stopCamera = () => {
      if (currentStream.value) {
        currentStream.value.getTracks().forEach(track => track.stop())
        currentStream.value = null
        // 安全地清除视频源
        if (videoRef.value && videoRef.value.srcObject) videoRef.value.srcObject = null
        if (loginVideoRef.value && loginVideoRef.value.srcObject) loginVideoRef.value.srcObject = null
      }
    }

    const captureFace = () => {
      if (!videoRef.value || !currentStream.value) return
      const video = videoRef.value
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      canvas.getContext('2d').drawImage(video, 0, 0)
      registerForm.faceImage = canvas.toDataURL('image/jpeg', 0.8)
      stopCamera()
    }

    const captureFaceForLogin = () => {
      if (!loginVideoRef.value || !currentStream.value) return
      const video = loginVideoRef.value
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      canvas.getContext('2d').drawImage(video, 0, 0)
      loginForm.faceImage = canvas.toDataURL('image/jpeg', 0.8)
      stopCamera()
    }

    const resetCapture = () => {
      registerForm.faceImage = ''
      nextTick(() => initCamera(videoRef.value))
    }

    const resetLoginCapture = () => {
      loginForm.faceImage = ''
      nextTick(() => initCamera(loginVideoRef.value))
    }

    const showMessage = (msg) => {
      messageText.value = msg
      setTimeout(() => {
        messageText.value = ''
      }, 3000)
    }

    watch(() => route.query, (newQuery) => {
      if (newQuery.message) {
        showMessage(newQuery.message)
      }
    }, { immediate: true })

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

    const handleLogout = async () => {
      try {
        await userApi.logout()
        isLoggedIn.value = false
        currentUsername.value = ''
        currentRole.value = ''
        loginUserStore.setLoginUser('')
        router.push('/login')
      } catch (error) {
        console.error('退出登录失败:', error)
      }
    }

    const handleLogin = async () => {
      try {
        const response = await userApi.login(loginForm)
        const userData = response.data
        if (userData && userData.username) {
          const { username, role } = userData
          loginUserStore.setLoginUser(username)
          currentRole.value = role
          isLoggedIn.value = true // 更新登录状态
          currentUsername.value = username // 更新当前用户名
          const redirect = route.query.redirect
          if (role === 'student') {
            router.push(redirect || '/home')
          } else if (role === 'teacher') {
            router.push('/teacher-dashboard')
          }
        } else {
          loginUserStore.setLoginUser('未登录')
          showMessage('登录失败，请检查用户名、密码或人脸信息')
        }
      } catch (error) {
        console.error('登录请求失败:', error)
        loginUserStore.setLoginUser('未登录')
        showMessage('登录失败，请检查用户名、密码或人脸信息')
      }
    }

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

    const changeForm = () => {
      isRegisterForm.value = !isRegisterForm.value
      stopCamera()
      errorMessage.value = '' // 清空错误信息
      
      const switchCtn = document.querySelector("#switch-cnt")
      const switchC1 = document.querySelector("#switch-c1")
      const switchC2 = document.querySelector("#switch-c2")
      const switchCircles = document.querySelectorAll(".switch_circle")
      const aContainer = document.querySelector("#a-container")
      const bContainer = document.querySelector("#b-container")

      switchCtn.classList.add("is-gx")
      setTimeout(() => {
        switchCtn.classList.remove("is-gx")
      }, 1500)

      switchCtn.classList.toggle("is-txr")
      switchCircles.forEach(circle => circle.classList.toggle("is-txr"))
      switchC1.classList.toggle("is-hidden")
      switchC2.classList.toggle("is-hidden")
      aContainer.classList.toggle("is-txl")
      bContainer.classList.toggle("is-txl")
      bContainer.classList.toggle("is-z")

      nextTick(() => {
        if (isRegisterForm.value) {
          initCamera(videoRef.value)
        } else {
          initCamera(loginVideoRef.value)
        }
      })
    }

    onMounted(() => {
      const main = document.querySelector("#switch-cnt")
      // 检查登录状态
      checkLoginStatus().then(() => {
        // 如果已登录，则不执行切换和摄像头初始化逻辑
        if(isLoggedIn.value) return;

        // 如果未登录，执行下面的逻辑
        const shouldRegister = route.query.register === 'true'
        if (shouldRegister) {
          // 确保DOM元素存在再执行
          if(main) changeForm()
        } else {
          nextTick(() => {
            initCamera(loginVideoRef.value)
          })
        }
      })
    })

    onUnmounted(() => {
      stopCamera()
    })

    return {
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
      videoRef,
      loginVideoRef,
      currentStream,
      errorMessage,
      captureFace,
      captureFaceForLogin,
      resetCapture,
      resetLoginCapture,
      isRegisterFormValid,
      isLoginFormValid
    }
  }
})
</script>

<style scoped>
/* 导入字体图标 */
@import url('./fonts/iconfont.css');

/* 消息提示框样式 */
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
  display: none;
  z-index: 9999;
}

/* 全局重置样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  user-select: none; /* 禁止文本选择 */
}

/* 登录页面容器 */
.login-page {
  width: 100%;
  height: 85vh; /* 使用视口高度 */
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  background-color: #f0f2f5;
  color: #666;
}

/* 主容器样式 */
.shell {
  position: relative;
  width: 80vw; /* 使用视口宽度的80% */
  max-width: 1400px; /* 最大宽度限制 */
  min-width: 1200px; /* 最小宽度限制 */
  height: 30vh;
  min-height: 600px;
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border-radius: 20px;
  overflow: hidden;
}

/* 表单容器样式 */
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

/* 注册表单容器初始位置 */
.a-container {
  left: 40%;  /* 初始位置在右侧 */
  z-index: 10;
}

/* 登录表单容器初始位置 */
.b-container {
  left: 40%;  /* 初始位置在右侧 */
  z-index: 0;
}

/* 表单样式 */
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

/* 社交图标容器 */
.form_icons {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
  gap: 15px;
}

/* 单个图标样式 */
.iconfont {
  font-size: 20px;
  padding: 12px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  color: #666;
  transition: all 0.3s ease;
}

/* 图标悬停效果 */
.iconfont:hover {
  border-color: #4B70E2;
  color: #4B70E2;
  transform: translateY(-2px);
}

/* 表单提示文本 */
.form_span {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

/* 角色选择器容器 */
.role-selector {
  margin-bottom: 15px;
}

/* 输入框样式 */
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

/* 输入框焦点状态 */
.form_input:focus {
  border-color: #4B70E2;
  box-shadow: 0 0 0 3px rgba(75, 112, 226, 0.1);
}

/* 人脸采集区域样式 */
.face-capture {
  width: 100%;
  margin: 1px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

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
}

.capture-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

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

.camera-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #666;
}

.camera-text {
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
}

.camera-help {
  font-size: 14px;
  color: #666;
  max-width: 80%;
  line-height: 1.4;
}

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

.capture-btn:hover:not(:disabled) {
  background-color: #45a049;
  transform: translateX(-50%) scale(1.05);
}

.capture-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.preview-container {
  width: 100%;
  max-width: 400px;
  height: 300px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
}

.face-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

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

/* 切换面板容器 */
.switch {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;  /* 初始位置在左侧 */
  height: 100%;
  width: 40%;
  padding: 30px;
  z-index: 200;
  transition: 1.25s;
  background: linear-gradient(135deg, #4B70E2, #3857b8);
  overflow: hidden;
}

/* 切换面板背景圆形 */
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

/* 切换面板顶部圆形 */
.switch_circle-t {
  top: -30%;
  left: 60%;
  width: 300px;
  height: 300px;
}

/* 切换面板内容容器 */
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

/* 切换面板标题 */
.switch_title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 15px;
}

/* 切换面板描述文本 */
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

/* 向右移动动画 */
.is-txr {
  left: 60%;  /* 移动到右侧60%的位置 */
  transition: 1.25s;
  transform-origin: left;
}

/* 向左移动动画 */
.is-txl {
  left: 0;  /* 移动到最左侧 */
  transition: 1.25s;
  transform-origin: right;
}

/* 控制层级 */
.is-z {
  z-index: 200;
  transition: 1.25s;
}

/* 隐藏元素 */
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

/* 用户信息容器 */
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
</style> 