<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-4">
      <div class="card p-4">
        <div class="text-center mb-4">
          <h2 class="fw-bold">质量安全平台</h2>
          <p class="text-secondary">QSP v0.0.1</p>
        </div>

        <!-- 认证方式选择（仅当有多个可用方式时显示） -->
        <div v-if="authConfig.available_auth_types.length > 1" class="mb-3">
          <div class="btn-group w-100" role="group">
            <button
              v-for="type in authConfig.available_auth_types"
              :key="type.type"
              :class="['btn', activeAuthType === type.type ? 'btn-primary' : 'btn-outline-secondary']"
              @click="activeAuthType = type.type"
              :disabled="!type.enabled"
            >
              {{ type.name }}
            </button>
          </div>
        </div>

        <!-- 本地认证表单 -->
        <form v-if="activeAuthType === 'local'" @submit.prevent="handleLocalLogin">
          <div class="mb-3">
            <label class="form-label">用户名</label>
            <input type="text" v-model="username" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">密码</label>
            <input type="password" v-model="password" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- LDAP 认证（使用相同表单，但后端不同） -->
        <form v-else-if="activeAuthType === 'ldap'" @submit.prevent="handleLdapLogin">
          <div class="mb-3">
            <label class="form-label">用户名</label>
            <input type="text" v-model="username" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">密码</label>
            <input type="password" v-model="password" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? '登录中...' : 'LDAP登录' }}
          </button>
        </form>

        <!-- Keycloak/OIDC 认证（跳转） -->
        <div v-else-if="activeAuthType === 'keycloak'" class="text-center">
          <p class="mb-3">使用 Keycloak 统一认证登录</p>
          <button class="btn btn-primary w-100" @click="redirectToOIDC">
            <i class="fas fa-key me-2"></i>Keycloak登录
          </button>
        </div>

        <!-- CAS 认证（跳转） -->
        <div v-else-if="activeAuthType === 'cas'" class="text-center">
          <p class="mb-3">使用 CAS 统一认证登录</p>
          <button class="btn btn-primary w-100" @click="redirectToCAS">
            <i class="fas fa-id-card me-2"></i>CAS登录
          </button>
        </div>

        <div v-if="errorMsg" class="alert alert-danger mt-3 py-2">{{ errorMsg }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')
const activeAuthType = ref('local')
const authConfig = ref({
  authenticated: false,
  auth_type: 'local',
  available_auth_types: [{ type: 'local', name: '本地认证', enabled: true }]
})

// 获取认证配置
const fetchAuthConfig = async () => {
  try {
    const res = await api.get('/auth/status/')
    authConfig.value = res.data
    activeAuthType.value = res.data.auth_type
  } catch (error) {
    console.error('获取认证配置失败', error)
  }
}

// 本地登录
const handleLocalLogin = async () => {
  loading.value = true
  errorMsg.value = ''

  const result = await authStore.login({
    username: username.value,
    password: password.value
  })

  loading.value = false
  if (result.success) {
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } else {
    errorMsg.value = result.error
  }
}

// LDAP 登录
const handleLdapLogin = async () => {
  loading.value = true
  errorMsg.value = ''

  try {
    // 调用 LDAP 认证 API（复用本地登录接口，后端会根据配置切换认证方式）
    const result = await authStore.login({
      username: username.value,
      password: password.value,
      auth_type: 'ldap'  // 可选的提示字段
    })

    if (result.success) {
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      errorMsg.value = result.error
    }
  } catch (error) {
    errorMsg.value = 'LDAP 认证失败'
  } finally {
    loading.value = false
  }
}

// 跳转到 Keycloak 登录页
const redirectToOIDC = () => {
  window.location.href = '/auth/oidc/login/'
}

// 跳转到 CAS 登录页（需要配置 django-cas-ng 的 URL）
const redirectToCAS = () => {
  window.location.href = '/accounts/login/'
}

onMounted(() => {
  fetchAuthConfig()
})
</script>