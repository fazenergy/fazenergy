import { createApp } from 'vue'
import App from './App.vue'
import VueTheMask from 'vue-the-mask'

import './index.css'
import { createPinia } from 'pinia'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(VueTheMask) // registra as diretivas globalmente
app.mount('#app')