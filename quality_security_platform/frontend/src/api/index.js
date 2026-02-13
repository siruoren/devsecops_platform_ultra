import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' }
})

export default {
  // 用户
  getUsers() { return apiClient.get('/users/') },
  createUser(data) { return apiClient.post('/users/', data) },
  updateUser(id, data) { return apiClient.put(`/users/${id}/`, data) },
  deleteUser(id) { return apiClient.delete(`/users/${id}/`) },
  // 项目
  getProjects() { return apiClient.get('/projects/') },
  // ... 其他 API
}
