<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">风险看板</h1>
      <span class="badge bg-light text-dark">更新于 {{ currentTime }}</span>
    </div>
    <div class="row g-4 mb-4">
      <div class="col-md-3"><div class="card p-3 text-center"><h3 class="text-danger fw-bold">82</h3><span>最高风险分</span><small class="text-secondary">订单服务</small></div></div>
      <div class="col-md-3"><div class="card p-3 text-center"><h3 class="text-warning fw-bold">4</h3><span>高风险项目</span></div></div>
      <div class="col-md-3"><div class="card p-3 text-center"><h3 class="text-success fw-bold">12</h3><span>低风险项目</span></div></div>
      <div class="col-md-3"><div class="card p-3 text-center"><h3 class="text-primary fw-bold">28</h3><span>待处理告警</span></div></div>
    </div>
    <div class="card p-4">
      <h5 class="section-title">项目风险评分</h5>
      <div class="table-responsive">
        <table class="table">
          <thead><tr><th>项目</th><th>综合风险</th><th>代码质量</th><th>漏洞风险</th><th>流水线健康</th><th>状态</th></tr></thead>
          <tbody>
            <tr><td>订单服务</td><td><span class="badge bg-danger">82 (高危)</span></td><td>75</td><td>90</td><td>78</td><td><i class="fas fa-exclamation-triangle text-danger"></i> 严重</td></tr>
            <tr><td>用户中心</td><td><span class="badge bg-warning text-dark">45 (中危)</span></td><td>60</td><td>30</td><td>50</td><td><i class="fas fa-exclamation-circle text-warning"></i> 中危</td></tr>
            <tr><td>支付网关</td><td><span class="badge bg-success">28 (低危)</span></td><td>30</td><td>25</td><td>30</td><td><i class="fas fa-check-circle text-success"></i> 正常</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const currentTime = ref('')
onMounted(() => {
  const now = new Date()
  currentTime.value = `${now.getFullYear()}-${now.getMonth()+1}-${now.getDate()} ${now.getHours()}:${String(now.getMinutes()).padStart(2,'0')}`
})
</script>
