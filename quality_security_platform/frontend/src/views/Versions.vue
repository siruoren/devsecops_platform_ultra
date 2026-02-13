<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">版本管理</h1>
      <button class="btn btn-primary"><i class="fas fa-plus me-2"></i>新建发布版本</button>
    </div>
    <div class="card p-4">
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr><th>版本号</th><th>创建时间</th><th>封板时间</th><th>状态</th><th>代码质量</th><th>登记应用数</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="(v, idx) in versions" :key="idx">
              <td class="fw-semibold"><a href="#" class="text-decoration-none">{{ v.version }}</a></td>
              <td>{{ v.created }}</td>
              <td>{{ v.released || '--' }}</td>
              <td><span class="badge" :class="v.statusBadge">{{ v.status }}</span></td>
              <td><span class="badge bg-success">⩾ {{ v.quality }}%</span></td>
              <td>{{ v.count }}</td>
              <td>
                <button class="btn btn-sm btn-outline-secondary"><i class="fas fa-edit"></i></button>
                <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const versions = ref([
  { version: 'V2.3.0', created: '2026-02-10', released: null, status: '开发中', statusBadge: 'bg-warning text-dark', quality: 85, count: 3 },
  { version: 'V2.2.1', created: '2026-01-25', released: '2026-02-01', status: '已封板', statusBadge: 'bg-secondary', quality: 92, count: 5 },
])
</script>
