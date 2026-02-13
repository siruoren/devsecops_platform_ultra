<template>
  <nav class="navbar navbar-custom">
    <div class="container-fluid">
      <button type="button" class="toggle-sidebar" @click="toggleSidebar">
        <i class="fas fa-bars"></i>
      </button>
      <div class="ms-auto d-flex align-items-center">
        <!-- 通知下拉菜单（真实未读消息数） -->
        <div class="dropdown me-3">
          <a class="nav-link position-relative" href="#" role="button" data-bs-toggle="dropdown">
            <i class="fas fa-bell"></i>
            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
              {{ unreadCount }}
            </span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li v-if="notifications.length === 0">
              <span class="dropdown-item text-secondary">暂无新通知</span>
            </li>
            <li v-for="notif in notifications.slice(0, 3)" :key="notif.id">
              <a class="dropdown-item" href="#">{{ notif.title }}</a>
            </li>
            <li v-if="notifications.length > 3">
              <hr class="dropdown-divider">
              <a class="dropdown-item text-center" href="/system/notifications">查看全部</a>
            </li>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const username = computed(() => authStore.user?.username || 'admin')
const userInitials = computed(() => username.value.substring(0, 2).toUpperCase())

const unreadCount = ref(0)
const notifications = ref([])

// 获取未读消息数
const fetchUnreadCount = async () => {
  try {
    const res = await api.getUnreadCount()
    unreadCount.value = res.data.unread_count || 0
  } catch (error) {
    console.error('获取未读消息数失败', error)
  }
}

// 获取最近通知
const fetchRecentNotifications = async () => {
  try {
    const res = await api.getNotifications({ page_size: 3, is_read: false })
    notifications.value = res.data.results || res.data
  } catch (error) {
    console.error('获取通知失败', error)
  }
}

// 退出登录
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

// 侧边栏折叠
const toggleSidebar = () => {
  const sidebar = document.getElementById('sidebar')
  if (sidebar) sidebar.classList.toggle('active')
}

onMounted(() => {
  fetchUnreadCount()
  fetchRecentNotifications()
})
</script>

<style scoped>
/* 样式保持不变 */
</style>