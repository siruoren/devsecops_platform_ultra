<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">项目管理</h1>
      <div>
        <button class="btn btn-outline-secondary me-2"><i class="fas fa-server me-2"></i>环境管理</button>
        <button class="btn btn-primary"><i class="fas fa-plus me-2"></i>新建应用</button>
      </div>
    </div>
    <div class="card p-4">
      <div class="row mb-4">
        <div class="col-md-5">
          <div class="input-group">
            <span class="input-group-text bg-white"><i class="fas fa-search"></i></span>
            <input type="text" class="form-control" placeholder="应用名 / Git仓库...">
          </div>
        </div>
      </div>
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr><th>应用名</th><th>仓库地址</th><th>环境</th><th>负责人</th><th>SonarQube</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="(proj, idx) in projects" :key="idx">
              <td class="fw-semibold">{{ proj.name }}</td>
              <td><code>{{ proj.repo }}</code></td>
              <td><span class="badge" :class="proj.envBadge">{{ proj.env }}</span></td>
              <td>{{ proj.owner }}</td>
              <td><a href="#"><i class="fas fa-external-link-alt me-1"></i>查看</a></td>
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
const projects = ref([
  { name: '订单服务', repo: 'git@gitlab.com/order', env: '生产', envBadge: 'bg-success', owner: '张工' },
  { name: '用户中心', repo: 'git@gitlab.com/user', env: '测试', envBadge: 'bg-warning text-dark', owner: '李工' },
  { name: '支付网关', repo: 'git@gitlab.com/pay', env: '预发', envBadge: 'bg-info', owner: '王工' },
])
</script>
