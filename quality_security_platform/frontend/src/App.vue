<template>
  <div class="wrapper">
    <Sidebar />
    <div id="content">
      <Navbar />
      <div class="container-fluid mt-4">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
</script>

<style>
.wrapper {
  display: flex;
  width: 100%;
  align-items: stretch;
}
#content {
  width: 100%;
  padding: 20px;
  min-height: 100vh;
  background-color: #f8fafc;
}
</style>
