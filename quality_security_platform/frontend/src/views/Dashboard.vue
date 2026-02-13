<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">仪表盘</h1>
      <div>
        <span class="badge bg-light text-dark me-2">
          <i class="far fa-calendar-alt me-1"></i>{{ currentDate }}
        </span>
        <span class="badge bg-light text-dark">
          <i class="far fa-clock me-1"></i>{{ currentTime }}
        </span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="row g-4 mb-5">
      <div v-for="stat in stats" :key="stat.title" class="col-md-3">
        <div class="card p-3 stat-card" :style="{ borderLeftColor: stat.color }">
          <div class="d-flex justify-content-between">
            <div>
              <span class="text-secondary">{{ stat.title }}</span>
              <h2 class="mt-2 mb-0 fw-bold">{{ stat.value }}</h2>
              <small :class="`text-${stat.trendColor}`">
                <i :class="`fas fa-arrow-${stat.trendIcon}`"></i> {{ stat.trend }}
              </small>
            </div>
            <div class="bg-opacity-10 p-3 rounded-3" :style="{ backgroundColor: stat.bgColor }">
              <i :class="`fas fa-${stat.icon} fa-2x`" :style="{ color: stat.color }"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 风险趋势 & 最近构建 -->
    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="section-title mb-0">风险趋势 (订单服务)</h5>
            <span class="badge bg-light text-dark">近7天</span>
          </div>
          <!-- ✅ 修复：固定图表容器高度 -->
          <div style="position: relative; height: 300px; width: 100%;">
            <canvas id="riskChart"></canvas>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="card p-4">
          <h5 class="section-title">最新告警</h5>
          <div class="list-group list-group-flush">
            <div v-for="alert in alerts" :key="alert.title" 
                 class="list-group-item px-0 border-0 d-flex justify-content-between align-items-start">
              <div>
                <span :class="`badge bg-${alert.level} mb-1`">{{ alert.levelName }}</span>
                <div class="fw-semibold">{{ alert.title }}</div>
                <small class="text-secondary">{{ alert.description }}</small>
              </div>
              <span class="text-secondary small">{{ alert.time }}</span>
            </div>
          </div>
          <hr>
          <h5 class="section-title mt-3">最近构建</h5>
          <div class="list-group list-group-flush">
            <div v-for="build in recentBuilds" :key="build.id" 
                 class="list-group-item px-0 border-0 d-flex justify-content-between">
              <span>{{ build.name }}</span>
              <span :class="`badge bg-${build.statusColor}`">{{ build.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Chart from 'chart.js/auto'

const currentDate = new Date().toLocaleDateString('zh-CN')
const currentTime = new Date().toLocaleTimeString('zh-CN', { hour12: false })

const stats = ref([
  { title: '项目总数', value: 24, trend: '+2', trendColor: 'success', trendIcon: 'up', color: '#0d6efd', bgColor: 'rgba(13,110,253,0.1)', icon: 'cubes' },
  { title: '发布版本', value: 8, trend: '+3', trendColor: 'success', trendIcon: 'up', color: '#198754', bgColor: 'rgba(25,135,84,0.1)', icon: 'tag' },
  { title: '高危漏洞', value: 37, trend: '+5', trendColor: 'danger', trendIcon: 'up', color: '#dc3545', bgColor: 'rgba(220,53,69,0.1)', icon: 'shield-hacked' },
  { title: '构建成功率', value: '86.5%', trend: '-1.2%', trendColor: 'warning', trendIcon: 'down', color: '#ffc107', bgColor: 'rgba(255,193,7,0.1)', icon: 'chart-line' }
])

const alerts = ref([
  { level: 'danger', levelName: '严重', title: '订单服务 - 高风险', description: '综合风险分 82', time: '10分钟前' },
  { level: 'warning', levelName: '中危', title: '用户中心 - 漏洞累积', description: '3个未修复', time: '2小时前' },
  { level: 'info', levelName: '提醒', title: '支付网关 - 版本变更', description: 'fastjson 1.2.83', time: '昨天' }
])

const recentBuilds = ref([
  { id: 245, name: '订单服务 #245', status: '成功', statusColor: 'success' },
  { id: 12, name: '用户中心 #12', status: '失败', statusColor: 'danger' },
  { id: 98, name: '网关服务 #98', status: '运行中', statusColor: 'secondary' }
])

onMounted(() => {
  const canvas = document.getElementById('riskChart')
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['2/7', '2/8', '2/9', '2/10', '2/11', '2/12', '2/13'],
      datasets: [{
        label: '风险评分',
        data: [65, 70, 68, 75, 80, 78, 82],
        borderColor: '#dc3545',
        backgroundColor: 'rgba(220,53,69,0.1)',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,  // ✅ 保持宽高比
      plugins: {
        tooltip: { mode: 'index' },
        legend: { display: false }
      }
    }
  })
})
</script>

<style scoped>
.page-title { font-size: 1.75rem; font-weight: 600; color: #1e2a41; }
.section-title { font-size: 1.25rem; font-weight: 600; color: #2c3e50; margin-bottom: 1rem; }
.stat-card { border-left-width: 4px; border-left-style: solid; border-radius: 12px; }
</style>