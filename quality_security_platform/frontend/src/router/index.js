import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 页面组件
import Dashboard from '../views/Dashboard.vue'
import Users from '../views/Users.vue'
import Projects from '../views/Projects.vue'
import Versions from '../views/Versions.vue'
import Vulnerabilities from '../views/Vulnerabilities.vue'
import Cicd from '../views/Cicd.vue'
import Risk from '../views/Risk.vue'
import System from '../views/System.vue'
import Login from '../views/Login.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/users', name: 'Users', component: Users, meta: { requiresAuth: true } },
  { path: '/projects', name: 'Projects', component: Projects, meta: { requiresAuth: true } },
  { path: '/versions', name: 'Versions', component: Versions, meta: { requiresAuth: true } },
  { path: '/vulnerabilities', name: 'Vulnerabilities', component: Vulnerabilities, meta: { requiresAuth: true } },
  { path: '/cicd', name: 'Cicd', component: Cicd, meta: { requiresAuth: true } },
  { path: '/risk', name: 'Risk', component: Risk, meta: { requiresAuth: true } },
  { path: '/system', name: 'System', component: System, meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: Login, meta: { requiresAuth: false } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：检查认证状态
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 尝试获取当前用户（如果还没获取过）
  if (!authStore.isAuthenticated) {
    await authStore.fetchCurrentUser()
  }

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isAuthenticated) {
      next({ path: '/login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  } else {
    // 登录页：如果已登录则跳转首页
    if (to.path === '/login' && authStore.isAuthenticated) {
      next('/')
    } else {
      next()
    }
  }
})

export default router