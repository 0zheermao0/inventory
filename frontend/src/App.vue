<template>
  <div id="app">
    <el-container style="height: 100vh;">
      <el-header style="background-color: #409EFF; color: white; display: flex; align-items: center; justify-content: space-between;">
        <h2>库存管理系统</h2>
        <div>
          <el-dropdown @command="handlePrintCommand">
            <el-button type="primary" :loading="printing">
              打印报表<i class="el-icon-arrow-down el-icon--right"></i>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="all">打印所有记录</el-dropdown-item>
                <el-dropdown-item command="selected" :disabled="!selectedTransactionIds.length">打印选中记录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="200px" style="background-color: #f5f5f5;">
          <el-menu :default-active="activeMenu" class="el-menu-vertical-demo" @select="handleMenuSelect">
            <el-menu-item index="/products">
              <el-icon><Goods /></el-icon>
              <span>商品管理</span>
            </el-menu-item>
            <el-menu-item index="/inventory">
              <el-icon><Tickets /></el-icon>
              <span>出入库管理</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main>
          <router-view @selection-change="handleTransactionSelection" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Goods, Tickets } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const activeMenu = ref('/products')
const printing = ref(false)
const selectedTransactionIds = ref([])

onMounted(() => {
  activeMenu.value = route.path
})

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleTransactionSelection = (ids) => {
  selectedTransactionIds.value = ids
}

const handlePrintCommand = async (command) => {
  try {
    printing.value = true
    
    let url
    if (command === 'all') {
      url = 'http://localhost:8000/api/inventory-transactions/print_report/'
    } else if (command === 'selected' && selectedTransactionIds.value.length > 0) {
      const ids = selectedTransactionIds.value.join(',')
      url = `http://localhost:8000/api/inventory-transactions/print_report/?ids=${ids}`
    } else {
      ElMessage.warning('请先选择要打印的记录')
      return
    }
    
    const response = await axios.get(url, {
      responseType: 'blob'
    })
    
    // 创建blob URL并触发下载
    const urlBlob = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = urlBlob
    link.setAttribute('download', 'inventory_report.pdf')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('报表生成成功！')
  } catch (error) {
    ElMessage.error('报表生成失败：' + error.message)
  } finally {
    printing.value = false
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>