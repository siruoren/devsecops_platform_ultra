<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">项目管理</h1>
      <div>
        <button class="btn btn-outline-secondary me-2" @click="openEnvModal">
          <i class="fas fa-server me-2"></i>环境管理
        </button>
        <button class="btn btn-primary" @click="openCreateModal">
          <i class="fas fa-plus me-2"></i>新建应用
        </button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="card p-3 mb-4">
      <div class="row g-3">
        <div class="col-md-5">
          <div class="input-group">
            <span class="input-group-text bg-white"><i class="fas fa-search"></i></span>
            <input type="text" v-model="filters.search" class="form-control" placeholder="应用名 / Git仓库" @keyup.enter="fetchProjects">
          </div>
        </div>
        <div class="col-md-2">
          <select v-model="filters.environment" class="form-select">
            <option value="">全部环境</option>
            <option v-for="env in environments" :key="env.id" :value="env.id">{{ env.name }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <button class="btn btn-outline-primary" @click="fetchProjects">查询</button>
          <button class="btn btn-outline-secondary ms-2" @click="resetFilters">重置</button>
        </div>
      </div>
    </div>

    <!-- 项目列表 -->
    <div class="card p-0">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>应用名</th>
              <th>仓库地址</th>
              <th>环境</th>
              <th>负责人</th>
              <th>SonarQube</th>
              <th style="width: 100px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="proj in projects" :key="proj.id">
              <td class="fw-semibold">{{ proj.name }}</td>
              <td><code>{{ proj.git_repo }}</code></td>
              <td>
                <span class="badge" :class="getEnvBadge(proj.environment_name)">
                  {{ proj.environment_name }}
                </span>
              </td>
              <td>{{ proj.owner_username || '—' }}</td>
              <td>
                <a v-if="proj.sonarqube_url" :href="proj.sonarqube_url" target="_blank">
                  <i class="fas fa-external-link-alt me-1"></i>查看
                </a>
                <span v-else>—</span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-secondary me-1" @click="openEditModal(proj)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteProject(proj.id)">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="projects.length === 0">
              <td colspan="6" class="text-center py-4 text-secondary">暂无项目数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页（与用户管理类似，此处省略分页组件） -->
    <!-- 实际项目需添加分页，暂略 -->
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const projects = ref([])
const environments = ref([])

const filters = reactive({
  search: '',
  environment: '',
})

// 获取环境列表
const fetchEnvironments = async () => {
  try {
    const res = await api.getEnvironments()
    environments.value = res.data
  } catch (error) {
    console.error('获取环境列表失败', error)
  }
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const params = {
      search: filters.search || undefined,
      environment: filters.environment || undefined,
    }
    const res = await api.getProjects(params)
    projects.value = res.data
  } catch (error) {
    console.error('获取项目列表失败', error)
  }
}

// 重置筛选
const resetFilters = () => {
  filters.search = ''
  filters.environment = ''
  fetchProjects()
}

// 删除项目
const deleteProject = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该项目吗？', '提示', { type: 'warning' })
    await api.deleteProject(id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败', error)
  }
}

// 环境标签样式
const getEnvBadge = (envName) => {
  const map = {
    '生产': 'bg-success',
    '测试': 'bg-warning text-dark',
    '预发': 'bg-info',
  }
  return map[envName] || 'bg-secondary'
}

onMounted(() => {
  fetchEnvironments()
  fetchProjects()
})
</script>