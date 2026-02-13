import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,  // 允许跨域携带 Cookie
})

// 请求拦截器（可添加 Token）
apiClient.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// 响应拦截器（全局处理 401）
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 未认证，跳转到登录页
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  // ========== 用户认证 ==========
  login(credentials) { return apiClient.post('/users/login/', credentials) },
  logout() { return apiClient.post('/users/logout/') },
  getCurrentUser() { return apiClient.get('/users/me/') },
  changePassword(data) { return apiClient.post('/users/change_password/', data) },

  // ========== 用户管理 ==========
  getUsers(params) { return apiClient.get('/users/', { params }) },
  getUser(id) { return apiClient.get(`/users/${id}/`) },
  createUser(data) { return apiClient.post('/users/', data) },
  updateUser(id, data) { return apiClient.put(`/users/${id}/`, data) },
  deleteUser(id) { return apiClient.delete(`/users/${id}/`) },
  bulkDeleteUsers(ids) { return apiClient.delete('/users/bulk_delete/', { data: { ids } }) },

  // ========== 项目管理 ==========
  getProjects(params) { return apiClient.get('/projects/', { params }) },
  getProject(id) { return apiClient.get(`/projects/${id}/`) },
  createProject(data) { return apiClient.post('/projects/', data) },
  updateProject(id, data) { return apiClient.put(`/projects/${id}/`, data) },
  deleteProject(id) { return apiClient.delete(`/projects/${id}/`) },
  bulkDeleteProjects(ids) { return apiClient.delete('/projects/bulk_delete/', { data: { ids } }) },

  getEnvironments(params) { return apiClient.get('/environments/', { params }) },

  // ========== 角色权限 ==========
  getRoles(params) { return apiClient.get('/roles/', { params }) },
  getPermissions(params) { return apiClient.get('/permissions/', { params }) },

  // ========== CI/CD ==========
  getPipelines(params) { return apiClient.get('/pipelines/', { params }) },
  getBuilds(params) { return apiClient.get('/builds/', { params }) },
  triggerPipeline(id, data) { return apiClient.post(`/pipelines/${id}/trigger/`, data) },
  cancelBuild(id) { return apiClient.post(`/builds/${id}/cancel/`) },

  // ========== 风险 ==========
  getRiskProfiles(params) { return apiClient.get('/risk/profiles/', { params }) },
  getRiskAlerts(params) { return apiClient.get('/risk/alerts/', { params }) },

  // ========== 系统通知 ==========
  getNotifications(params) { return apiClient.get('/system/notifications/', { params }) },
  markNotificationAsRead(id) { return apiClient.post(`/system/notifications/${id}/mark_as_read/`) },
  getUnreadCount() { return apiClient.get('/system/notifications/unread_count/') },
  bulkDeleteNotifications(ids) { return apiClient.delete('/system/notifications/bulk_delete/', { data: { ids } }) },
}