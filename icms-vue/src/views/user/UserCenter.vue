# 创建用户中心页面
<template>
  <div class="user-center">
    <a-row :gutter="[24, 24]">
      <!-- 左侧用户信息卡片 -->
      <a-col :span="8">
        <a-card class="user-card">
          <template #cover>
            <div class="avatar-container">
              <a-avatar :size="120" :src="userInfo.avatarUrl">
                {{ userInfo.username?.charAt(0)?.toUpperCase() }}
              </a-avatar>
            </div>
          </template>
          <template #title>
            <div class="user-name">{{ userInfo.username || '未知用户' }}</div>
          </template>
          <template #extra>
            <a-tag :color="userInfo.role === 'teacher' ? 'blue' : 'green'">
              {{ userInfo.role === 'teacher' ? '教师' : '学生' }}
            </a-tag>
          </template>
          <a-descriptions :column="1">
            <a-descriptions-item label="账号">
              {{ userInfo.userAccount || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="邮箱">
              {{ userInfo.email || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="手机">
              {{ userInfo.phone || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="注册时间">
              {{ userInfo.createTime || '未知' }}
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-col>

      <!-- 右侧信息编辑区域 -->
      <a-col :span="16">
        <a-card title="个人信息设置">
          <a-form
            :model="formState"
            :rules="rules"
            ref="formRef"
            :label-col="{ span: 4 }"
            :wrapper-col="{ span: 16 }"
          >
            <a-form-item label="用户名" name="username">
              <a-input v-model:value="formState.username" />
            </a-form-item>

            <a-form-item label="邮箱" name="email">
              <a-input v-model:value="formState.email" />
            </a-form-item>

            <a-form-item label="手机号" name="phone">
              <a-input v-model:value="formState.phone" />
            </a-form-item>

            <a-form-item label="密码" name="password">
              <a-input-password v-model:value="formState.password" placeholder="不修改请留空" />
            </a-form-item>

            <a-form-item label="确认密码" name="confirmPassword">
              <a-input-password v-model:value="formState.confirmPassword" placeholder="不修改请留空" />
            </a-form-item>

            <a-form-item :wrapper-col="{ offset: 4, span: 16 }">
              <a-button type="primary" @click="handleSubmit" :loading="loading">
                保存修改
              </a-button>
              <a-button style="margin-left: 10px" @click="resetForm">
                重置
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 人脸信息管理卡片 -->
        <a-card title="人脸信息管理" class="mt-24">
          <div class="face-management">
            <div v-if="!isCapturing" class="face-preview">
              <img v-if="userInfo.faceImage" :src="userInfo.faceImage" alt="人脸照片" />
              <div v-else class="no-face">
                <camera-outlined />
                <p>暂无人脸信息</p>
              </div>
            </div>
            <div v-else class="camera-container">
              <video ref="videoRef" autoplay playsinline class="camera-feed"></video>
            </div>
            <div class="face-actions">
              <a-button 
                type="primary" 
                @click="handleFaceCapture" 
                :loading="isProcessing"
              >
                {{ userInfo.faceImage ? '重新采集' : '采集人脸' }}
              </a-button>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useLoginUserStore } from '@/store/useLoginUserStore'
import { userApi } from '@/api/user'
import { message } from 'ant-design-vue'
import { CameraOutlined } from '@ant-design/icons-vue'

// 状态管理
const loginUserStore = useLoginUserStore()
const formRef = ref(null)
const videoRef = ref(null)
const loading = ref(false)
const isCapturing = ref(false)
const isProcessing = ref(false)
const userInfo = ref({})

// 表单状态
const formState = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度应在 2-20 个字符之间', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', trigger: 'blur' }
  ],
  confirmPassword: [
    {
      validator: async (rule, value) => {
        if (formState.password && value !== formState.password) {
          throw new Error('两次输入的密码不一致')
        }
      },
      trigger: 'change'
    }
  ]
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await userApi.getCurrentUser()
    if (response.data) {
      userInfo.value = response.data
      // 更新表单数据
      formState.username = response.data.username || ''
      formState.email = response.data.email || ''
      formState.phone = response.data.phone || ''
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    message.error('获取用户信息失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 构建更新数据
    const updateData = {
      username: formState.username,
      email: formState.email,
      phone: formState.phone
    }
    
    // 如果输入了新密码，添加到更新数据中
    if (formState.password) {
      updateData.password = formState.password
    }

    // 调用更新接口
    const response = await userApi.updateUser(updateData)
    if (response.data.code === 0) {
      message.success('更新成功')
      await fetchUserInfo() // 重新获取用户信息
      loginUserStore.setLoginUser(formState.username) // 更新store中的用户名
    } else {
      message.error(response.data.message || '更新失败')
    }
  } catch (error) {
    console.error('更新用户信息失败:', error)
    message.error('更新失败，请检查输入信息')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
}

// 初始化摄像头
const initCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user'
      }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
    return stream
  } catch (error) {
    console.error('摄像头初始化失败:', error)
    message.error('摄像头初始化失败，请检查权限设置')
    return null
  }
}

// 处理人脸采集
const handleFaceCapture = async () => {
  if (isCapturing.value) {
    // 正在采集中，进行拍照
    if (!videoRef.value) return
    
    isProcessing.value = true
    try {
      const canvas = document.createElement('canvas')
      canvas.width = videoRef.value.videoWidth
      canvas.height = videoRef.value.videoHeight
      canvas.getContext('2d').drawImage(videoRef.value, 0, 0)
      const faceImage = canvas.toDataURL('image/jpeg', 0.8)
      
      // 调用更新人脸信息的接口
      const response = await userApi.updateFaceInfo({ faceImage })
      if (response.data.code === 0) {
        userInfo.value.faceImage = faceImage
        message.success('人脸信息更新成功')
      } else {
        message.error(response.data.message || '人脸信息更新失败')
      }
    } catch (error) {
      console.error('更新人脸信息失败:', error)
      message.error('更新人脸信息失败')
    } finally {
      isProcessing.value = false
      isCapturing.value = false
      // 停止摄像头
      if (videoRef.value?.srcObject) {
        videoRef.value.srcObject.getTracks().forEach(track => track.stop())
        videoRef.value.srcObject = null
      }
    }
  } else {
    // 开始采集
    isCapturing.value = true
    await initCamera()
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})

// 组件卸载时清理摄像头
onUnmounted(() => {
  if (videoRef.value?.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.user-center {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
}

.user-card {
  text-align: center;
}

.avatar-container {
  padding: 24px 0;
  background: linear-gradient(135deg, #1890ff 0%, #52c41a 100%);
}

.user-name {
  font-size: 20px;
  font-weight: 500;
  margin: 16px 0;
}

.mt-24 {
  margin-top: 24px;
}

.face-management {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.face-preview, .camera-container {
  width: 320px;
  height: 240px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.face-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-face {
  text-align: center;
  color: #999;
}

.no-face .anticon {
  font-size: 48px;
  margin-bottom: 8px;
}

.face-actions {
  display: flex;
  gap: 12px;
}
</style>