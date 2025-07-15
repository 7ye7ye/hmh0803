<template>
  <div class="attendance-view">
    <a-row :gutter="[24, 24]">
      <!-- 左侧统计卡片 -->
      <a-col :span="8">
        <a-card class="statistics-card">
          <template #title>考勤统计</template>
          <a-statistic-countdown
            title="今日考勤时间"
            :value="deadline"
            format="HH:mm:ss"
            prefix="剩余"
            style="margin-bottom: 20px"
          />
          <a-row :gutter="16">
            <a-col :span="12">
              <a-statistic
                title="已签到"
                :value="statistics.signedCount"
                :value-style="{ color: '#3f8600' }"
              >
                <template #suffix>
                  <span>/ {{ statistics.totalCount }}</span>
                </template>
              </a-statistic>
            </a-col>
            <a-col :span="12">
              <a-statistic
                title="未签到"
                :value="statistics.unsignedCount"
                :value-style="{ color: '#cf1322' }"
              >
                <template #suffix>
                  <span>/ {{ statistics.totalCount }}</span>
                </template>
              </a-statistic>
            </a-col>
          </a-row>
        </a-card>

        <!-- 考勤规则设置 -->
        <a-card title="考勤规则设置" class="mt-24">
          <a-form :model="attendanceRule" layout="vertical">
            <a-form-item label="考勤开始时间">
              <a-time-picker v-model:value="attendanceRule.startTime" format="HH:mm" />
            </a-form-item>
            <a-form-item label="考勤结束时间">
              <a-time-picker v-model:value="attendanceRule.endTime" format="HH:mm" />
            </a-form-item>
            <a-form-item label="迟到判定（分钟）">
              <a-input-number v-model:value="attendanceRule.lateThreshold" :min="1" :max="60" />
            </a-form-item>
            <a-button type="primary" block @click="saveAttendanceRule">保存规则</a-button>
          </a-form>
        </a-card>
      </a-col>

      <!-- 右侧考勤记录表格 -->
      <a-col :span="16">
        <a-card>
          <template #title>
            <div class="card-title-wrapper">
              <span>考勤记录</span>
              <div class="card-extra">
                <a-range-picker 
                  v-model:value="dateRange"
                  @change="handleDateRangeChange"
                  style="margin-right: 16px"
                />
                <a-button type="primary" @click="exportAttendance">
                  导出记录
                </a-button>
              </div>
            </div>
          </template>
          
          <a-table
            :columns="columns"
            :data-source="attendanceRecords"
            :loading="loading"
            :pagination="pagination"
            @change="handleTableChange"
          >
            <!-- 状态列自定义渲染 -->
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="getStatusColor(record.status)">
                  {{ getStatusText(record.status) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'action'">
                <a @click="showAttendanceDetail(record)">查看详情</a>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>

    <!-- 考勤详情弹窗 -->
    <a-modal
      v-model:visible="detailModalVisible"
      title="考勤详情"
      :footer="null"
      width="600px"
    >
      <div v-if="selectedRecord">
        <div class="detail-header">
          <a-avatar :size="64" :src="selectedRecord.avatarUrl">
            {{ selectedRecord.studentName?.charAt(0) }}
          </a-avatar>
          <div class="detail-info">
            <h3>{{ selectedRecord.studentName }}</h3>
            <p>学号：{{ selectedRecord.studentId }}</p>
          </div>
        </div>
        <a-descriptions :column="2" class="mt-24">
          <a-descriptions-item label="签到时间">
            {{ selectedRecord.signTime }}
          </a-descriptions-item>
          <a-descriptions-item label="签到状态">
            <a-tag :color="getStatusColor(selectedRecord.status)">
              {{ getStatusText(selectedRecord.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="位置信息">
            {{ selectedRecord.location || '未记录' }}
          </a-descriptions-item>
          <a-descriptions-item label="设备信息">
            {{ selectedRecord.device || '未记录' }}
          </a-descriptions-item>
        </a-descriptions>
        <div class="face-image-container mt-24">
          <h4>签到照片</h4>
          <img 
            :src="selectedRecord.faceImage || ''"
            alt="签到照片" 
            class="face-image" 
          />
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { attendanceApi } from '@/api/attendance'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'

// 状态管理
const loading = ref(false)
const dateRange = ref([])
const detailModalVisible = ref(false)
const selectedRecord = ref(null)
const attendanceRecords = ref([]) // 添加考勤记录数组

// 考勤统计数据
const statistics = reactive({
  totalCount: 0,
  signedCount: 0,
  unsignedCount: 0
})

// 考勤规则设置
const attendanceRule = reactive({
  startTime: null,
  endTime: null,
  lateThreshold: 15
})

// 计算截止时间
const deadline = computed(() => {
  if (!attendanceRule.endTime) return dayjs().endOf('day')
  return dayjs(attendanceRule.endTime)
})

// 表格列定义
const columns = [
  {
    title: '序号',
    key: 'index',
    customRender: ({ index }) => index + 1,
  },
  {
    title: '姓名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '签到时间',
    dataIndex: 'timestamp',
    key: 'timestamp',
    customRender: ({ text }) => {
      return dayjs(text).format('YYYY年MM月DD日 HH:mm:ss')
    }
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    filters: [
      { text: '已签到', value: 'signed' },
      { text: '迟到', value: 'late' },
      { text: '未签到', value: 'unsigned' },
    ],
  },
  {
    title: '操作',
    key: 'action',
  },
]

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
})

// 获取状态颜色
const getStatusColor = (status) => {
  const colors = {
    signed: 'success',
    late: 'warning',
    unsigned: 'error',
  }
  return colors[status] || 'default'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    signed: '已签到',
    late: '迟到',
    unsigned: '未签到',
  }
  return texts[status] || '未知'
}

// 获取考勤记录
const fetchAttendanceRecords = async () => {
  loading.value = true
  try {
    // 调用获取考勤记录的接口
    const response = await attendanceApi.getAttendanceRecords({
      startDate: dateRange.value[0]?.format('YYYY-MM-DD'),
      endDate: dateRange.value[1]?.format('YYYY-MM-DD'),
      page: pagination.current,
      pageSize: pagination.pageSize,
    })
    console.log('获取考勤记录',response)
    if (response.data) {
      attendanceRecords.value = response.data
      pagination.total = response.data.total
      console.log('考勤记录',attendanceRecords.value)
      // 更新统计数据
      statistics.totalCount = response.data.total
      statistics.signedCount = response.data.signedCount
      statistics.unsignedCount = response.data.unsignedCount
    }
  } catch (error) {
    console.error('获取考勤记录失败:', error)
    message.error('获取考勤记录失败')
  } finally {
    loading.value = false
  }
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  pagination.current = 1 // 重置页码
  fetchAttendanceRecords()
}

// 处理表格变化（排序、筛选、分页）
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchAttendanceRecords()
}

// 显示考勤详情
const showAttendanceDetail = (record) => {
  selectedRecord.value = record
  console.log('selectedRecord',selectedRecord.value)
  detailModalVisible.value = true
}

// 导出考勤记录
const exportAttendance = async () => {
  try {
    const response = await attendanceApi.exportAttendance({
      startDate: dateRange.value[0]?.format('YYYY-MM-DD'),
      endDate: dateRange.value[1]?.format('YYYY-MM-DD'),
    })
    
    // 处理文件下载
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `考勤记录_${dayjs().format('YYYY-MM-DD')}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    message.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    message.error('导出失败')
  }
}

// 保存考勤规则
const saveAttendanceRule = async () => {
  try {
    // 这里替换为实际的API调用
    await attendanceApi.updateAttendanceRule(attendanceRule)
    message.success('规则保存成功')
  } catch (error) {
    console.error('保存规则失败:', error)
    message.error('保存规则失败')
  }
}

// 组件挂载时获取数据
onMounted(async () => {
  // 设置默认日期范围为当天
  dateRange.value = [dayjs(), dayjs()]
  await fetchAttendanceRecords()
})
</script>

<style scoped>
.attendance-view {
  max-width: 1400px;
  margin: 24px auto;
  padding: 0 24px;
}

.statistics-card {
  margin-bottom: 24px;
}

.mt-24 {
  margin-top: 24px;
}

.card-title-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.card-extra {
  display: flex;
  align-items: center;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-info {
  h3 {
    margin: 0;
    font-size: 18px;
  }
  p {
    margin: 4px 0 0;
    color: #666;
  }
}

.face-image-container {
  h4 {
    margin-bottom: 12px;
  }
}

.face-image {
  width: 100%;
  max-width: 320px;
  border-radius: 8px;
}
</style> 