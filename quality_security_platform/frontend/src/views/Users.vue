<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">用户管理</h1>
      <button class="btn btn-primary" @click="openCreateModal">
        <i class="fas fa-plus me-2"></i>新建用户
      </button>
    </div>

    <!-- 搜索栏 -->
    <div class="card p-3 mb-4">
      <div class="row g-3">
        <div class="col-md-4">
          <div class="input-group">
            <span class="input-group-text bg-white"><i class="fas fa-search"></i></span>
            <input type="text" v-model="filters.search" class="form-control" placeholder="用户名/邮箱/部门" @keyup.enter="fetchUsers">
          </div>
        </div>
        <div class="col-md-2">
          <select v-model="filters.is_active" class="form-select">
            <option value="">全部状态</option>
            <option value="true">激活</option>
            <option value="false">未激活</option>
          </select>
        </div>
        <div class="col-md-2">
          <button class="btn btn-outline-primary" @click="fetchUsers">查询</button>
          <button class="btn btn-outline-secondary ms-2" @click="resetFilters">重置</button>
        </div>
      </div>
    </div>

    <!-- 批量操作栏 -->
    <div class="card p-3 mb-3" v-if="selectedIds.length > 0">
      <div class="d-flex align-items-center">
        <span class="me-3">已选择 {{ selectedIds.length }} 项</span>
        <button class="btn btn-sm btn-outline-danger" @click="bulkDelete">
          <i class="fas fa-trash me-1"></i>批量删除
        </button>
        <button class="btn btn-sm btn-outline-secondary ms-2" @click="selectedIds = []">取消选择</button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="card p-0">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th style="width: 40px;">
                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll">
              </th>
              <th>用户</th>
              <th>邮箱</th>
              <th>部门</th>
              <th>职位</th>
              <th>角色</th>
              <th>状态</th>
              <th style="width: 120px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>
                <input type="checkbox" :value="user.id" v-model="selectedIds">
              </td>
              <td>
                <div class="d-flex align-items-center">
                  <span class="avatar me-2" :style="{ backgroundColor: getAvatarColor(user.username) }">
                    {{ getInitials(user.username) }}
                  </span>
                  <span>{{ user.username }}</span>
                </div>
              </td>
              <td>{{ user.email }}</td>
              <td>{{ user.department || '—' }}</td>
              <td>{{ user.position || '—' }}</td>
              <td>
                <span v-if="user.is_superuser" class="badge bg-primary">超级管理员</span>
                <span v-else class="badge bg-secondary">普通用户</span>
              </td>
              <td>
                <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-warning text-dark'">
                  {{ user.is_active ? '激活' : '未激活' }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-secondary me-1" @click="openEditModal(user)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteUser(user.id)">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="8" class="text-center py-4 text-secondary">暂无用户数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页 -->
    <div class="d-flex justify-content-between align-items-center mt-4">
      <span class="text-secondary">共 {{ total }} 条记录</span>
      <nav>
        <ul class="pagination mb-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">上一页</a>
          </li>
          <li class="page-item" v-for="page in pageRange" :key="page" :class="{ active: page === currentPage }">
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">下一页</a>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 用户表单模态框（新增/编辑） -->
    <div class="modal fade" id="userModal" tabindex="-1" ref="userModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ modalTitle }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveUser">
              <div class="mb-3">
                <label class="form-label">用户名</label>
                <input type="text" v-model="form.username" class="form-control" :disabled="!!form.id" required>
              </div>
              <div class="mb-3">
                <label class="form-label">邮箱</label>
                <input type="email" v-model="form.email" class="form-control" required>
              </div>
              <div class="mb-3" v-if="!form.id">
                <label class="form-label">密码</label>
                <input type="password" v-model="form.password" class="form-control" minlength="8" required>
              </div>
              <div class="row mb-3">
                <div class="col">
                  <label class="form-label">姓</label>
                  <input type="text" v-model="form.last_name" class="form-control">
                </div>
                <div class="col">
                  <label class="form-label">名</label>
                  <input type="text" v-model="form.first_name" class="form-control">
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">部门</label>
                <input type="text" v-model="form.department" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">职位</label>
                <input type="text" v-model="form.position" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">手机号</label>
                <input type="text" v-model="form.phone" class="form-control">
              </div>
              <div class="mb-3 form-check" v-if="form.id && isSuperAdmin">
                <input type="checkbox" v-model="form.is_active" class="form-check-input" id="isActive">
                <label class="form-check-label" for="isActive">激活</label>
              </div>
              <div class="mb-3 form-check" v-if="isSuperAdmin">
                <input type="checkbox" v-model="form.is_superuser" class="form-check-input" id="isSuperuser">
                <label class="form-check-label" for="isSuperuser">超级管理员</label>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
            <button type="button" class="btn btn-primary" @click="saveUser">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Modal } from 'bootstrap'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'  // 如需轻量提示，可使用 sweetalert2 或自定义

const authStore = useAuthStore()
const isSuperAdmin = computed(() => authStore.user?.is_superuser)

// 数据列表
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 筛选条件
const filters = reactive({
  search: '',
  is_active: '',
  ordering: '-id',
})

// 选中项
const selectedIds = ref([])
const isAllSelected = computed({
  get: () => users.value.length > 0 && selectedIds.value.length === users.value.length,
  set: (value) => {
    if (value) {
      selectedIds.value = users.value.map(u => u.id)
    } else {
      selectedIds.value = []
    }
  }
})

// 模态框
let modalInstance = null
const userModal = ref(null)
const form = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  department: '',
  position: '',
  phone: '',
  is_active: true,
  is_superuser: false,
})
const modalTitle = computed(() => form.id ? '编辑用户' : '新建用户')

// 获取用户列表
const fetchUsers = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
      is_active: filters.is_active || undefined,
      ordering: filters.ordering,
    }
    const response = await api.getUsers(params)
    users.value = response.data.results || response.data
    total.value = response.data.count || response.data.length
  } catch (error) {
    console.error('获取用户列表失败', error)
  }
}

// 重置筛选
const resetFilters = () => {
  filters.search = ''
  filters.is_active = ''
  filters.ordering = '-id'
  currentPage.value = 1
  fetchUsers()
}

// 翻页
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchUsers()
  }
}

// 分页范围
const pageRange = computed(() => {
  const range = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  for (let i = start; i <= end; i++) range.push(i)
  return range
})

// 打开新增模态框
const openCreateModal = () => {
  resetForm()
  modalInstance.show()
}

// 打开编辑模态框
const openEditModal = (user) => {
  resetForm()
  form.id = user.id
  form.username = user.username
  form.email = user.email
  form.first_name = user.first_name || ''
  form.last_name = user.last_name || ''
  form.department = user.department || ''
  form.position = user.position || ''
  form.phone = user.phone || ''
  form.is_active = user.is_active
  form.is_superuser = user.is_superuser
  modalInstance.show()
}

// 重置表单
const resetForm = () => {
  form.id = null
  form.username = ''
  form.email = ''
  form.password = ''
  form.first_name = ''
  form.last_name = ''
  form.department = ''
  form.position = ''
  form.phone = ''
  form.is_active = true
  form.is_superuser = false
}

// 保存用户
const saveUser = async () => {
  try {
    if (form.id) {
      await api.updateUser(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await api.createUser(form)
      ElMessage.success('创建成功')
    }
    modalInstance.hide()
    fetchUsers()
  } catch (error) {
    console.error('保存用户失败', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 删除单个用户
const deleteUser = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该用户吗？', '提示', { type: 'warning' })
    await api.deleteUser(id)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败', error)
  }
}

// 批量删除
const bulkDelete = async () => {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 个用户吗？`, '提示', { type: 'warning' })
    await api.bulkDeleteUsers(selectedIds.value)
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') console.error('批量删除失败', error)
  }
}

// 辅助函数
const getInitials = (username) => {
  return username.substring(0, 2).toUpperCase()
}
const getAvatarColor = (username) => {
  const colors = ['#0d6efd', '#6f42c1', '#20c997', '#fd7e14', '#dc3545', '#198754']
  const hash = username.split('').reduce((a, b) => a + b.charCodeAt(0), 0)
  return colors[hash % colors.length]
}

onMounted(() => {
  modalInstance = new Modal(userModal.value)
  fetchUsers()
})

// 监听筛选条件变化（防抖）
watch([filters], () => {
  currentPage.value = 1
  fetchUsers()
}, { deep: true, debounce: 500 })
</script>

<style scoped>
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}
</style>