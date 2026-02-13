<template>
  <nav class="navbar navbar-custom">
    <div class="container-fluid">
      <button 
        type="button" 
        class="toggle-sidebar" 
        @click="toggleSidebar"
        :style="{ zIndex: 1050 }"
      >
        <i class="fas fa-bars"></i>
      </button>
      <div class="ms-auto d-flex align-items-center">
        <!-- 通知下拉菜单 -->
        <div class="dropdown me-3">
          <a class="nav-link position-relative" href="#" role="button" data-bs-toggle="dropdown">
            <i class="fas fa-bell"></i>
            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
              {{ unreadCount }}
            </span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#">漏洞扫描完成</a></li>
            <li><a class="dropdown-item" href="#">构建 #245 失败</a></li>
            <li><a class="dropdown-item" href="#">版本 V2.3.0 已封板</a></li>
          </ul>
        </div>
        <!-- 用户下拉菜单 -->
        <div class="dropdown">
          <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown">
            <span class="avatar me-2">{{ userInitials }}</span>
            <span>{{ username }}</span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#"><i class="fas fa-user me-2"></i>个人中心</a></li>
            <li><a class="dropdown-item" href="#"><i class="fas fa-cog me-2"></i>账号设置</a></li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item" href="#" @click.prevent="handleLogout">
                <i class="fas fa-sign-out-alt me-2"></i>退出
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'  // 引入 API 客户端

const router = useRouter()
const unreadCount = ref(0)
const username = ref('admin')
const userInitials = ref('AD')

// 获取未读消息数（示例）
const fetchUnreadCount = async () => {
  try {
    const res = await api.getUnreadCount()
    unreadCount.value = res.data.unread_count
  } catch (error) {
    console.error('获取未读消息数失败', error)
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await api.logout()
    // 清除本地存储的用户信息（如果有）
    localStorage.removeItem('user')
    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    console.error('退出失败', error)
    // 即使接口失败，也强制跳转登录页（前端退出）
    router.push('/login')
  }
}

// 侧边栏折叠切换
const toggleSidebar = () => {
  const sidebar = document.getElementById('sidebar')
  if (sidebar) {
    sidebar.classList.toggle('active')
  }
}

onMounted(() => {
  fetchUnreadCount()
})
</script>

<style scoped>
.navbar-custom {
  background-color: white;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.02);
  margin-bottom: 25px;
}
.toggle-sidebar {
  background: none;
  border: none;
  color: #4a5b6e;
  font-size: 1.3rem;
  cursor: pointer;
  position: relative;
  z-index: 1050;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #0d6efd;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}
</style>