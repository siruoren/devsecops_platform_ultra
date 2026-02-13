import axios from 'axios'

// 创建 Axios 实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,  // ✅ 必须：允许跨域携带 Cookie
})

// 请求拦截器（可选：添加 Token、Loading 等）
apiClient.interceptors.request.use(
  config => {
    // 可以在这里添加 JWT Token（如果使用 Token 认证）
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器（统一处理错误）
apiClient.interceptors.response.use(
  response => response,
  error => {
    // 401 未认证：跳转到登录页
    if (error.response && error.response.status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  // 用户相关
  getUsers(params) { return apiClient.get('/users/', { params }) },
  createUser(data) { return apiClient.post('/users/', data) },
  updateUser(id, data) { return apiClient.put(`/users/${id}/`, data) },
  deleteUser(id) { return apiClient.delete(`/users/${id}/`) },
  bulkDeleteUsers(ids) { return apiClient.delete('/users/bulk_delete/', { data: { ids } }) },
  login(credentials) { return apiClient.post('/users/login/', credentials) },
  logout() { return apiClient.post('/users/logout/') },
  getCurrentUser() { return apiClient.get('/users/me/') },
  changePassword(data) { return apiClient.post('/users/change_password/', data) },

  // 项目相关
  getProjects(params) { return apiClient.get('/projects/', { params }) },
  getEnvironments(params) { return apiClient.get('/environments/', { params }) },

  // 角色权限
  getRoles(params) { return apiClient.get('/roles/', { params }) },
  getPermissions(params) { return apiClient.get('/permissions/', { params }) },

  // CI/CD
  getPipelines(params) { return apiClient.get('/pipelines/', { params }) },
  getBuilds(params) { return apiClient.get('/builds/', { params }) },

  // 风险
  getRiskProfiles(params) { return apiClient.get('/risk/profiles/', { params }) },
  getRiskAlerts(params) { return apiClient.get('/risk/alerts/', { params }) },

  // 系统
  getNotifications(params) { return apiClient.get('/system/notifications/', { params }) },
  markNotificationAsRead(id) { return apiClient.post(`/system/notifications/${id}/mark_as_read/`) },
  getUnreadCount() { return apiClient.get('/system/notifications/unread_count/') },

  // ... 其他 API 可继续扩展
}