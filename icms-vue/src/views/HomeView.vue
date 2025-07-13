<template>
  <div id="HomeView">
    <img class="bg" src="@/assets/bg6.jpg" alt="bg" />
    <div class="title-bar">
      <div class="title-cn animate__animated animate__pulse">教 室 智 能 监 控 系 统</div>
      <div class="title-en animate__animated animate__backInUp">Intelligent Classroom Monitoring System</div>
      <a-button class="title-btn animate__animated animate__backInUp" ghost>开发版本</a-button>
    </div>
    <div> 
      <button @click="navigate('userCenter')">用户中心</button>
    </div>
    <!-- Option-bar 放在背景图片下方 -->
    <div class="option-bar">
      <div class="option-item" @click="navigate('apiResponse')">
        <TeamOutlined class="option-icon animate__animated animate__swing" />
        <div class="option-text animate__animated animate__swing">智能监控api</div>
        <div class="option-text2 animate__animated animate__backInUp">提供智能监控api接口</div>
      </div>
      <div class="option-item" @click="navigate('monitoring')">
        <DeploymentUnitOutlined class="option-icon animate__animated animate__swing" />
        <div class="option-text animate__animated animate__swing">教室监控</div>
        <div class="option-text2 animate__animated animate__backInUp">提供教室监控接口</div>
      </div>
      <div class="option-item" @click="navigate('login')">
        <CarOutlined class="option-icon animate__animated animate__swing" />
        <div class="option-text animate__animated animate__swing">用户登录</div>
        <div class="option-text2 animate__animated animate__backInUp">使用用户登录接口</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {TeamOutlined, DeploymentUnitOutlined, CarOutlined } from '@ant-design/icons-vue'
import { useMenuStore } from '@/store/useMenuStore'

const router = useRouter()
const menuStore = useMenuStore()

// 根据传入的路由名称进行跳转
const navigate = (routeName) => {
  // 更新路由
  router.push({ name: routeName })
  // 更新 store 中的当前选中项
  menuStore.setCurrentMenu(routeName)
}

</script>
  
  <style scoped>
    .bg {
      height: 500px;
      width: 100%;
    }

    .title-bar {
      position: absolute; /* 绝对定位 */
      top: 30%;           /* 根据需求，放到图片中间或底部 */
      left: 50%;
      transform: translate(-50%, -50%); /* 让它在水平方向/垂直方向居中 */
      color: #fff;        /* 如果图片背景深，文字用白色 */
      text-align: center;
      align-items: flex-start; /* 左对齐 */
      gap: 100px;  /* 子元素之间的间距，可根据需要调整 */
    }

    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;700&family=Exo:wght@400;700&display=swap');

.title-cn {
    font-size: 42px;       
    font-weight: 700;      
    font-family: 'Orbitron', sans-serif; /* 未来科技风 */
    color: #ffffff;        
    text-shadow: 0 0 10px rgba(0, 0, 0, 0.8); /* 轻微发光效果 */
    margin-bottom: 10px;    
}

.title-en {
    font-size: 22px;       
    font-weight: 400;      
    font-family: 'Exo', sans-serif; /* 另一种科技字体 */
    color: #ffffff;           
    letter-spacing: 2px;   
    text-transform: uppercase; /* 统一风格 */
    text-shadow: 0 0 8px rgba(0, 0, 0, 0.6); /* 更柔和的发光 */
}


    .title-btn {
      margin-top: 20px; /* 如果需要单独设置按钮上方的间距 */
    }

    .title-bar {
      position: absolute; /* 绝对定位 */
      top: 30%;           /* 根据需求，放到图片中间或底部 */
      left: 50%;
      transform: translate(-50%, -50%); /* 让它在水平方向/垂直方向居中 */
      color: #fff;        /* 如果图片背景深，文字用白色 */
      text-align: center;
      align-items: flex-start; /* 左对齐 */
      gap: 100px;  /* 子元素之间的间距，可根据需要调整 */
    }

    /* Option-bar 样式 */
    .option-bar {
      position: absolute;
      bottom: 80px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      justify-content: space-between;
      width: 80%;  /* 根据需要调整整个区域宽度 */
    }

    .option-item {
      flex: 1;
      text-align: center;
      cursor: pointer;
      /* 添加内边距和过渡效果 */
      padding: 10px;
      transition: transform 0.3s;
    }

    .option-item:hover {
      transform: translateY(-5px);
    }

    .option-icon {
      font-size: 44px;
      color: #1890ff;
      margin-bottom: 10px;
    }

    .option-text {
      font-size: 16px;
      color: #333;
      margin-bottom: 10px;
    }

    .option-text2 {
      font-size: 13px;
      color: #a8abb6;
    }
  </style>
 