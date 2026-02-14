<template>
  <nav id="sidebar" :class="{ active: isCollapsed }">
    <div class="sidebar-header">
      <h3>QSP</h3>
      <small>质量安全平台 v0.0.1</small>
    </div>
    <ul class="components list-unstyled">
      <li v-for="item in menuItems" :key="item.path" :class="{ active: $route.path === item.path }">
        <router-link :to="item.path">
          <i :class="item.icon"></i> {{ item.name }}
        </router-link>
      </li>
      <hr style="border-color:#2d3a4f; margin:20px 10px;">
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
// isCollapsed 由 Navbar 的 toggleSidebar 切换类名控制，此处只需监听类名变化
const isCollapsed = ref(false)

// 可选：监听 sidebar 类名变化，同步 isCollapsed 状态
// 但此处不需要，因为样式切换直接基于类名

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
  font-size: 1.5rem;
  margin-bottom: 0;
  letter-spacing: 1px;
}
.sidebar-header small {
  color: #b0c4ce;
  font-size: 0.8rem;
}
.components {
  padding: 20px 0;
}
.components li {
  padding: 8px 20px;
  margin: 4px 8px;
  border-radius: 8px;
  transition: 0.2s;
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
  font-size: 1rem;
}
.components li a i {
  margin-right: 12px;
  width: 20px;
  text-align: center;
}
.components li.active a {
  color: white;
}
</style>