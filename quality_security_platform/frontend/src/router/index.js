import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Users from '../views/Users.vue'
import Projects from '../views/Projects.vue'
import Versions from '../views/Versions.vue'
import Vulnerabilities from '../views/Vulnerabilities.vue'
import Cicd from '../views/Cicd.vue'
import Risk from '../views/Risk.vue'
import System from '../views/System.vue'
import Login from '../views/Login.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/users', name: 'Users', component: Users },
  { path: '/projects', name: 'Projects', component: Projects },
  { path: '/versions', name: 'Versions', component: Versions },
  { path: '/vulnerabilities', name: 'Vulnerabilities', component: Vulnerabilities },
  { path: '/cicd', name: 'Cicd', component: Cicd },
  { path: '/risk', name: 'Risk', component: Risk },
  { path: '/system', name: 'System', component: System },
  { path: '/login', name: 'Login', component: Login },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
