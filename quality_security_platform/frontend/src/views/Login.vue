<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-4">
      <div class="card p-4">
        <div class="text-center mb-4">
          <h2 class="fw-bold">质量安全平台</h2>
          <p class="text-secondary">QSP v5.0</p>
        </div>
        <form @submit.prevent="handleLogin">
          <div class="mb-3"><label class="form-label">用户名</label><input type="text" v-model="username" class="form-control" placeholder="请输入用户名"></div>
          <div class="mb-3"><label class="form-label">密码</label><input type="password" v-model="password" class="form-control" placeholder="请输入密码"></div>
          <div class="mb-3 form-check"><input type="checkbox" class="form-check-input" id="remember"><label class="form-check-label" for="remember">记住密码</label></div>
          <button type="submit" class="btn btn-primary w-100">登录</button>
        </form>
        <div class="mt-3 text-center"><small class="text-secondary">默认账号: admin / admin123</small></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const username = ref('')
const password = ref('')
const router = useRouter()
const handleLogin = () => {
  // 模拟登录成功
  router.push('/')
}
</script>
