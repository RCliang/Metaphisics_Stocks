import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
import { router } from "./common/router"
// import axios from 'axios'

// categorylist
// axios.defaults.baseURL = "http://localhost:8000"

const app = createApp(App)
// app.provide("axios", axios)
app.use(ElementPlus)
app.use(createPinia());
app.use(router);
app.mount('#app')
