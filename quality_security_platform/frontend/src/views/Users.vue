<template>
  <div>
    <h1 class="page-title mb-4">用户管理</h1>
    <div class="card p-4">
      <div class="d-flex justify-content-between mb-3">
        <div class="input-group w-25">
          <span class="input-group-text bg-white"><i class="fas fa-search"></i></span>
          <input type="text" class="form-control" placeholder="搜索用户...">
        </div>
        <button class="btn btn-primary"><i class="fas fa-plus me-2"></i>新建用户</button>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>用户</th>
              <th>邮箱</th>
              <th>部门</th>
              <th>职位</th>
              <th>角色</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in users" :key="index">
              <td><div class="d-flex align-items-center"><span class="avatar me-2" :style="{ backgroundColor: user.avatarColor }">{{ user.initials }}</span>{{ user.username }}</div></td>
              <td>{{ user.email }}</td>
              <td>{{ user.department }}</td>
              <td>{{ user.position }}</td>
              <td><span class="badge" :class="user.roleBadge">{{ user.role }}</span></td>
              <td><span class="badge" :class="user.statusBadge">{{ user.status }}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-secondary me-1"><i class="fas fa-edit"></i></button>
                <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="card mt-4 p-4">
      <h5 class="section-title">角色权限</h5>
      <div class="table-responsive">
        <table class="table table-sm">
          <thead>
            <tr><th>角色</th><th>权限数</th><th>成员数</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr><td>系统管理员</td><td>32</td><td>2</td><td><a href="#">配置</a></td></tr>
            <tr><td>开发人员</td><td>18</td><td>7</td><td><a href="#">配置</a></td></tr>
            <tr><td>测试人员</td><td>15</td><td>4</td><td><a href="#">配置</a></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const users = ref([
  { username: 'admin', email: 'admin@example.com', department: '研发中心', position: '架构师', role: '超级管理员', roleBadge: 'bg-primary', status: '激活', statusBadge: 'bg-success', initials: 'AD', avatarColor: '#0d6efd' },
  { username: 'zhangli', email: 'zhang.li@example.com', department: '测试部', position: '测试工程师', role: '测试人员', roleBadge: 'bg-info', status: '激活', statusBadge: 'bg-success', initials: 'ZL', avatarColor: '#6f42c1' },
  { username: 'wangwei', email: 'wang.wei@example.com', department: '研发部', position: 'Java开发', role: '开发人员', roleBadge: 'bg-secondary', status: '未激活', statusBadge: 'bg-warning text-dark', initials: 'WW', avatarColor: '#20c997' },
])
</script>
