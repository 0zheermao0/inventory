import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import ProductList from './views/ProductList.vue'
import InventoryTransaction from './views/InventoryTransaction.vue'
import ProductForm from './components/ProductForm.vue'

const routes = [
  { path: '/', redirect: '/products' },
  { path: '/products', component: ProductList },
  { path: '/products/new', component: ProductForm },
  { path: '/products/:id/edit', component: ProductForm, props: true },
  { path: '/inventory', component: InventoryTransaction }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')