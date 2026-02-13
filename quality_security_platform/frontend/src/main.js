import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// ✅ 必须按此顺序导入 Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'  // 这会自动导入所有 Bootstrap 的 JavaScript 插件

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')