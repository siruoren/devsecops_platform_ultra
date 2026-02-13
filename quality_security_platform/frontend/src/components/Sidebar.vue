<template>
  <nav id="sidebar" :class="{ active: isCollapsed }">
    <div class="sidebar-header">
      <h3>QSP</h3>
      <small>质量安全平台 v5.0</small>
    </div>
    <ul class="components list-unstyled">
      <li v-for="item in menuItems" :key="item.path" :class="{ active: $route.path === item.path }">
        <router-link :to="item.path">
          <i :class="item.icon"></i> {{ item.name }}
        </router-link>
      </li>
      <hr>
      <li>
        <router-link to="/login">
          <i class="fas fa-sign-out-alt"></i> 退出
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isCollapsed = ref(false)

const menuItems = [
  { path: '/', name: '仪表盘', icon: 'fas fa-tachometer-alt' },
  { path: '/users', name: '用户管理', icon: 'fas fa-users' },
  { path: '/projects', name: '项目管理', icon: 'fas fa-project-diagram' },
  { path: '/versions', name: '版本管理', icon: 'fas fa-tags' },
  { path: '/vulnerabilities', name: '安全漏洞', icon: 'fas fa-shield-alt' },
  { path: '/cicd', name: 'CI/CD', icon: 'fas fa-cogs' },
  { path: '/risk', name: '风险看板', icon: 'fas fa-exclamation-triangle' },
  { path: '/system', name: '系统管理', icon: 'fas fa-sliders-h' },
]
</script>

<style scoped>
#sidebar {
  min-width: 260px;
  max-width: 260px;
  background: #1a2639;
  color: #fff;
  transition: all 0.3s;
}
#sidebar.active {
  margin-left: -260px;
}
.sidebar-header {
  padding: 20px;
  background: #0e1a2b;
  border-bottom: 1px solid #2d3a4f;
}
.sidebar-header h3 {
  color: #fff;
  font-weight: 600;
}
.components {
  padding: 20px 0;
}
.components li {
  padding: 8px 20px;
  margin: 4px 8px;
  border-radius: 8px;
}
.components li:hover {
  background: #2d3a4f;
  cursor: pointer;
}
.components li.active {
  background: #0d6efd;
}
.components li a {
  color: #ddd;
  text-decoration: none;
  display: block;
}
.components li a i {
  margin-right: 12px;
  width: 20px;
}
.components li.active a {
  color: white;
}
</style>
