<template>
    <div id="MonitoringView">
      <div class="hero-section">
        <img class="bg" src="@/assets/bg5.jpg" alt="bg" />
        <div class="title-bar">
          <div class="title-cn animate__animated animate__pulse">教 室 监 控</div>
          <div class="title-en animate__animated animate__backInUp">智能监控分析，实时行为识别，打造智慧教室新标准</div>
          <a-button id="animatedElement" class="title-btn animate__animated animate__backInUp" :icon="h(SearchOutlined)" @click="jumpToRoutePlanning">进入实时监控</a-button>
        </div>
      </div>

      <!-- 信息卡片区域 -->
      <div class="monitoring-container">
        <div class="section-title">
          <span class="title-text">教室监控指标</span>
          <div class="title-line"></div>
        </div>

        <div class="cards-wrapper">
          <!-- 卡片1：出勤率 -->
          <div class="info-card">
            <div class="card-icon efficiency-icon">
              <ClockCircleOutlined />
            </div>
            <div class="card-content">
              <div class="card-title">今日出勤率</div>
              <div class="card-value">95<span class="unit">%</span></div>
              <div class="card-desc">比上周提升 <span class="highlight">+3.2%</span></div>
            </div>
          </div>

          <!-- 卡片2：抬头率 -->
          <div class="info-card">
            <div class="card-icon coverage-icon">
              <GlobalOutlined />
            </div>
            <div class="card-content">
              <div class="card-title">平均抬头率</div>
              <div class="card-value">88<span class="unit">%</span></div>
              <div class="card-desc">班级整体表现 <span class="highlight">良好</span></div>
            </div>
          </div>

          <!-- 卡片3：告警数 -->
          <div class="info-card">
            <div class="card-icon response-icon">
              <ThunderboltOutlined />
            </div>
            <div class="card-content">
              <div class="card-title">今日告警数</div>
              <div class="card-value">5<span class="unit">次</span></div>
              <div class="card-desc">较昨日减少 <span class="highlight">2次</span></div>
            </div>
          </div>

          <!-- 卡片4：在线设备 -->
          <div class="info-card">
            <div class="card-icon cost-icon">
              <DollarOutlined />
            </div>
            <div class="card-content">
              <div class="card-title">在线摄像头</div>
              <div class="card-value">8<span class="unit">台</span></div>
              <div class="card-desc">设备状态 <span class="highlight">正常</span></div>
            </div>
          </div>
        </div>

        <!-- 添加功能区块 -->
        <div class="feature-blocks">
          <div class="feature-block" @click="navigateToFeature('monitor')">
            <CarOutlined class="feature-icon" />
            <div class="feature-title">实时监控</div>
          </div>
          <div class="feature-block" @click="navigateToFeature('attendance')">
            <EnvironmentOutlined class="feature-icon" />
            <div class="feature-title">考勤管理</div>
          </div>
          <div class="feature-block" @click="navigateToFeature('behavior')">
            <ClusterOutlined class="feature-icon" />
            <div class="feature-title">行为分析</div>
          </div>
          <div class="feature-block" @click="navigateToFeature('report')">
            <LineChartOutlined class="feature-icon" />
            <div class="feature-title">数据报表</div>
          </div>
        </div>
      </div>
    </div>
  </template>

  <script setup>
  import { h } from 'vue';
  import {
    SearchOutlined,
    ClockCircleOutlined,
    GlobalOutlined,
    ThunderboltOutlined,
    DollarOutlined,
    CarOutlined,
    EnvironmentOutlined,
    ClusterOutlined,
    LineChartOutlined
  } from '@ant-design/icons-vue';
  import { onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { checkIsLoggedIn } from '@/utils/auth' // 更新导入，只使用 checkIsLoggedIn
  import { message } from 'ant-design-vue';
  const router = useRouter()

  // 修改jumpToRoutePlanning方法，确保已登录用户直接跳转
  const jumpToRoutePlanning = async () => {
    // 检查用户是否已登录
    const isLoggedIn = await checkIsLoggedIn();
    if (isLoggedIn) {
      // 如果已登录，直接跳转
      window.location.href = 'http://localhost:5000/'; // 在当前窗口跳转
    } else {
      // 未登录，跳转到登录页面并携带提示信息
      router.push({
        path: '/login',
        query: {
          redirect: '/monitor',
        }
      });
      message.error('实时监控功能仅教师可用,请登录教师账号');
    }
  }

  // 修改navigateToFeature方法，简化登录验证
  const navigateToFeature = async (feature) => {
    console.log(`准备跳转到${feature}功能`);

    // 检查用户是否已登录
    const isLoggedIn = await checkIsLoggedIn();
    if (isLoggedIn) {
      // 如果已登录，执行对应功能
      switch (feature) {
        case 'monitor':
          console.log('跳转到实时监控页面');
          router.push('/monitor');
          break;
        case 'attendance':
          console.log('跳转到考勤管理页面');
          router.push('/attendance');
          break;
        case 'behavior':
          console.log('跳转到行为分析页面');
          router.push('/behavior');
          break;
        case 'report':
          console.log('跳转到数据报表页面');
          router.push('/report');
          break;
        default:
          break;
      }
    } else {
      // 未登录，直接跳转到登录页面并携带提示信息
      const featureName = getFeatureName(feature);
      const redirectPath = feature === 'monitor' ? '/monitor' : null;

      router.push({
        path: '/login',
        query: {
          redirect: redirectPath,
          message: `${featureName}功能需要登录才能使用`
        }
      });
    }
  }

  // 获取功能名称
  const getFeatureName = (feature) => {
    const names = {
      'monitor': '实时监控',
      'attendance': '考勤管理',
      'behavior': '行为分析',
      'report': '数据报表'
    };
    return names[feature] || '当前';
  }

  onMounted(() => {
    const el = document.querySelector('#animatedElement')
    if (el && el.addEventListener) {
      el.addEventListener('animationend', (event) => {
        // 检查是否是 backInUp 动画结束
        if (event.animationName === 'backInUp') {
          // 移除第一个动画类
          el.classList.remove('animate__backInUp')
          // 触发重绘，确保动画重新触发（可选）
          void el.offsetWidth
          // 添加第二个动画类 heartBeat
          el.classList.add('animate__heartBeat')
        }
      })
    }
  })
  </script>

  <style scoped>
  @import '@/assets/styles/monitoring.css';

  /* 移除 LogsticsView 的滚动条设置，交给 BasicLayout 的 content 处理 */
  /* #monitoringView {
    overflow-y: scroll;
  } */
  </style>




