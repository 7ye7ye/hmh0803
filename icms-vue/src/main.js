import { createApp } from 'vue'
import App from './App.vue'
import router from "./router"
import Antd from 'ant-design-vue';
import { createPinia } from 'pinia'
import 'ant-design-vue/dist/reset.css';
import 'animate.css';

const pinia = createPinia()
createApp(App).use(Antd).use(router).use(pinia).mount('#app')

  