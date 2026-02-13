<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">CI/CD 流水线</h1>
      <button class="btn btn-primary"><i class="fas fa-play me-2"></i>触发构建</button>
    </div>
    <div class="row">
      <div class="col-md-8">
        <div class="card p-4">
          <h5 class="section-title">最近构建</h5>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr><th>构建ID</th><th>流水线</th><th>版本</th><th>状态</th><th>耗时</th><th>触发人</th><th>操作</th></tr>
              </thead>
              <tbody>
                <tr><td><code>#245</code></td><td>订单服务构建</td><td>release/2.3.0</td><td><span class="badge bg-success">成功</span></td><td>2m35s</td><td>admin</td><td><a href="#">详情</a></td></tr>
                <tr><td><code>#244</code></td><td>用户中心测试</td><td>feature/login</td><td><span class="badge bg-danger">失败</span></td><td>1m12s</td><td>zhangli</td><td><a href="#">详情</a></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card p-4">
          <h5 class="section-title">流水线状态</h5>
          <canvas id="pipelineChart" style="height: 200px;"></canvas>
          <div class="mt-3">
            <div class="d-flex justify-content-between"><span>成功率</span><span class="fw-bold">86.5%</span></div>
            <div class="progress mt-1 mb-3" style="height: 8px;"><div class="progress-bar bg-success" style="width: 86.5%"></div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Chart from 'chart.js/auto'
onMounted(() => {
  const ctx = document.getElementById('pipelineChart').getContext('2d')
  new Chart(ctx, {
    type: 'doughnut',
    data: { labels: ['成功', '失败'], datasets: [{ data: [86.5, 13.5], backgroundColor: ['#198754', '#dc3545'], borderWidth: 0 }] },
    options: { cutout: '70%', plugins: { legend: { display: false } } }
  })
})
</script>
