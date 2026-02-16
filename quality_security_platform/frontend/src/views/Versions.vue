<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">版本管理</h1>
      <button class="btn btn-primary"><i class="fas fa-plus me-2"></i>新建发布版本</button>
    </div>
    <div class="card p-4">
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr><th>版本号</th><th>创建时间</th><th>封板时间</th><th>状态</th><th>代码质量</th><th>登记应用数</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="(v, idx) in versions" :key="idx">
              <td class="fw-semibold"><a href="#" class="text-decoration-none" @click="showVersionDetail(v.id)"><i class="fas fa-info-circle me-1"></i>{{ v.version }}</a></td>
              <td>{{ v.created }}</td>
              <td>{{ v.released || '--' }}</td>
              <td><span class="badge" :class="v.statusBadge">{{ v.status }}</span></td>
              <td><span class="badge bg-success">⩾ {{ v.quality }}%</span></td>
              <td>{{ v.count }}</td>
              <td>
                <button class="btn btn-sm btn-outline-secondary"><i class="fas fa-edit"></i></button>
                <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 版本详情模态框 -->
    <div class="modal fade" id="versionDetailModal" tabindex="-1" aria-labelledby="versionDetailModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="versionDetailModalLabel">版本详情</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-4">
              <h6 class="fw-semibold">版本信息</h6>
              <div class="row">
                <div class="col-md-6">
                  <p><strong>版本号：</strong>{{ currentVersion.version }}</p>
                  <p><strong>创建时间：</strong>{{ currentVersion.createdAt }}</p>
                </div>
                <div class="col-md-6">
                  <p><strong>封板时间：</strong>{{ currentVersion.releasedAt || '--' }}</p>
                  <p><strong>状态：</strong>{{ currentVersion.status }}</p>
                </div>
              </div>
            </div>
            
            <div>
              <h6 class="fw-semibold">登记的应用版本</h6>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>应用名称</th>
                      <th>应用版本号</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(reg, idx) in currentVersion.registrations" :key="idx">
                      <td>{{ reg.project }}</td>
                      <td>{{ reg.app_version }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-if="currentVersion.registrations.length === 0" class="text-center text-muted mt-4">
                暂无应用版本登记
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const versions = ref([
  { id: 1, version: 'V2.3.0', created: '2026-02-10', released: null, status: '开发中', statusBadge: 'bg-warning text-dark', quality: 85, count: 3 },
  { id: 2, version: 'V2.2.1', created: '2026-01-25', released: '2026-02-01', status: '已封板', statusBadge: 'bg-secondary', quality: 92, count: 5 },
])

const currentVersion = ref({
  version: '',
  createdAt: '',
  releasedAt: '',
  status: '',
  registrations: []
})

async function showVersionDetail(versionId) {
  try {
    const res = await fetch(`/api/versions/${versionId}/`, { credentials: 'include' })
    const data = await res.json()
    
    if (data.status === 'success') {
      const version = data.data
      currentVersion.value = {
        version: version.version,
        createdAt: new Date(version.created_at).toLocaleString(),
        releasedAt: version.released_at ? new Date(version.released_at).toLocaleString() : null,
        status: version.status === 'developing' ? '开发中' : '已封板',
        registrations: version.registrations || []
      }
      
      // 显示模态框
      const modal = new bootstrap.Modal(document.getElementById('versionDetailModal'))
      modal.show()
    } else {
      alert('获取版本详情失败')
    }
  } catch (error) {
    console.error('获取版本详情失败:', error)
    alert('获取版本详情失败')
  }
}
</script>
