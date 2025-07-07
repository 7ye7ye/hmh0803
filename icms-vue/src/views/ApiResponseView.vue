<template>
  <div class="wrapper">
    <div id="ApiResponseView">
      <div class="hero-section">
        <img class="bg" src="@/assets/bg3.jpg" alt="bg" />
        <div class="title-bar">
          <div class="title-cn animate__animated animate__pulse">智 能 教 室 监 控 API</div>
          <div class="title-en animate__animated animate__backInUp">让课堂管理更高效，让教学监控更智能，提供考勤管理、行为分析、数据报表的一站式解决方案</div>
          <a-button id="animatedElement" class="title-btn animate__animated animate__backInUp" :icon="h(SearchOutlined)" @click="jumpToEchartsPage">点击查看教室监控大数据平台</a-button>
        </div>
      </div>
      
      <!-- API服务区域 -->
      <div class="api-services-container">
        <div class="section-title">
          <span class="title-text">API服务能力</span>
          <div class="title-line"></div>
        </div>
        
        <!-- API状态卡片 -->
        <div class="api-stats">
          <div class="stat-card">
            <FieldTimeOutlined class="stat-icon" />
            <div class="stat-value">99.9<span class="unit">%</span></div>
            <div class="stat-label">API可用性</div>
          </div>
          <div class="stat-card">
            <RiseOutlined class="stat-icon" />
            <div class="stat-value">20<span class="unit">ms</span></div>
            <div class="stat-label">平均响应时间</div>
          </div>
          <div class="stat-card">
            <ApiOutlined class="stat-icon" />
            <div class="stat-value">32<span class="unit">个</span></div>
            <div class="stat-label">API接口数量</div>
          </div>
          <div class="stat-card">
            <TeamOutlined class="stat-icon" />
            <div class="stat-value">248<span class="unit">个</span></div>
            <div class="stat-label">服务客户</div>
          </div>
        </div>
        
        <!-- API服务列表 -->
        <div class="api-services">
          <div class="service-item">
            <div class="service-icon optimization-icon">
              <CompassOutlined />
            </div>
            <div class="service-content">
              <div class="service-title">行为识别API</div>
              <div class="service-desc">基于计算机视觉和深度学习的实时行为识别服务</div>
              <div class="service-tags">
                <span class="service-tag">实时监控</span>
                <span class="service-tag">行为分析</span>
                <span class="service-tag">快速响应</span>
              </div>
              <a-button type="primary" size="small" class="service-btn" @click="navigateToApiDocs('behavior')">
                查看文档
              </a-button>
            </div>
          </div>
          
          <div class="service-item">
            <div class="service-icon demand-icon">
              <FundOutlined />
            </div>
            <div class="service-content">
              <div class="service-title">考勤管理API</div>
              <div class="service-desc">基于人脸识别的智能考勤服务，支持多种考勤场景</div>
              <div class="service-tags">
                <span class="service-tag">人脸识别</span>
                <span class="service-tag">自动考勤</span>
                <span class="service-tag">数据统计</span>
              </div>
              <a-button type="primary" size="small" class="service-btn" @click="navigateToApiDocs('attendance')">
                查看文档
              </a-button>
            </div>
          </div>
          
          <div class="service-item">
            <div class="service-icon logistics-icon">
              <ClusterOutlined />
            </div>
            <div class="service-content">
              <div class="service-title">数据分析API</div>
              <div class="service-desc">提供课堂数据分析、学生表现评估的全方位分析服务</div>
              <div class="service-tags">
                <span class="service-tag">数据分析</span>
                <span class="service-tag">实时统计</span>
                <span class="service-tag">智能评估</span>
              </div>
              <a-button type="primary" size="small" class="service-btn" @click="navigateToApiDocs('analytics')">
                查看文档
              </a-button>
            </div>
          </div>
          
          <div class="service-item">
            <div class="service-icon resource-icon">
              <AppstoreOutlined />
            </div>
            <div class="service-content">
              <div class="service-title">设备管理API</div>
              <div class="service-desc">支持多教室、多摄像头的智能设备管理服务</div>
              <div class="service-tags">
                <span class="service-tag">设备管理</span>
                <span class="service-tag">状态监控</span>
                <span class="service-tag">远程控制</span>
              </div>
              <a-button type="primary" size="small" class="service-btn" @click="navigateToApiDocs('device')">
                查看文档
              </a-button>
            </div>
          </div>
        </div>
        
        <!-- 开发资源 -->
        <div class="dev-resources">
          <div class="section-subtitle">开发资源</div>
          <div class="resources-grid">
            <div class="resource-card" @click="navigateToResource('docs')">
              <BookOutlined class="resource-icon" />
              <div class="resource-title">API文档</div>
            </div>
            <div class="resource-card" @click="navigateToResource('sdk')">
              <CodeOutlined class="resource-icon" />
              <div class="resource-title">SDK下载</div>
            </div>
            <div class="resource-card" @click="navigateToResource('examples')">
              <FileOutlined class="resource-icon" />
              <div class="resource-title">示例代码</div>
            </div>
            <div class="resource-card" @click="navigateToResource('console')">
              <ControlOutlined class="resource-icon" />
              <div class="resource-title">开发者控制台</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </template>
  
<script setup>
  import { h } from 'vue';
  import { 
    SearchOutlined,
    FieldTimeOutlined,
    RiseOutlined,
    ApiOutlined,
    TeamOutlined,
    CompassOutlined,
    FundOutlined,
    ClusterOutlined,
    AppstoreOutlined,
    BookOutlined,
    CodeOutlined,
    FileOutlined,
    ControlOutlined
  } from '@ant-design/icons-vue';
  import { onMounted } from 'vue'
  // import { useRouter } from 'vue-router'
  // const router = useRouter()  

  const jumpToEchartsPage = () => {
      //  router.push('/data-visualization')
      window.location.href = '/Echarts-Demo-master/index.html'
    }
    
  const navigateToApiDocs = (apiType) => {
    console.log(`跳转到${apiType} API文档`)
    // 可以根据实际需求实现具体跳转逻辑
  }
  
  const navigateToResource = (resourceType) => {
    console.log(`跳转到${resourceType}资源`)
    // 可以根据实际需求实现具体跳转逻辑
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
@import '@/assets/styles/api.css'; 
</style>

  