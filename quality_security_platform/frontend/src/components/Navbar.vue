<template>
  <nav class="navbar navbar-custom">
    <div class="container-fluid">
      <button type="button" class="toggle-sidebar" @click="toggleSidebar">
        <i class="fas fa-bars"></i>
      </button>
      <div class="ms-auto d-flex align-items-center">
        <div class="dropdown me-3">
          <a class="nav-link position-relative" href="#" role="button" data-bs-toggle="dropdown">
            <i class="fas fa-bell"></i>
            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
              3
            </span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#">漏洞扫描完成</a></li>
            <li><a class="dropdown-item" href="#">构建 #245 失败</a></li>
            <li><a class="dropdown-item" href="#">版本 V2.3.0 已封板</a></li>
          </ul>
        </div>
        <div class="dropdown">
          <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown">
            <span class="avatar me-2">AD</span>
            <span>admin</span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#"><i class="fas fa-user me-2"></i>个人中心</a></li>
            <li><a class="dropdown-item" href="#"><i class="fas fa-cog me-2"></i>账号设置</a></li>
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item" href="/login"><i class="fas fa-sign-out-alt me-2"></i>退出</a></li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
const toggleSidebar = () => {
  const sidebar = document.getElementById('sidebar')
  sidebar.classList.toggle('active')
}
</script>

<style scoped>
.navbar-custom {
  background-color: white;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.02);
  margin-bottom: 25px;
}
.toggle-sidebar {
  background: none;
  border: none;
  color: #4a5b6e;
  font-size: 1.3rem;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #0d6efd;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}
</style>
