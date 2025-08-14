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
                <el-dropdown-item divided command="print-settings">打印设置</el-dropdown-item>
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
            <el-menu-item index="/customers">
              <el-icon><User /></el-icon>
              <span>客户管理</span>
            </el-menu-item>
            <el-menu-item index="/store-info">
              <el-icon><Shop /></el-icon>
              <span>店铺信息</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main>
          <router-view @selection-change="handleTransactionSelection" />
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 打印设置对话框 -->
    <el-dialog v-model="printSettingsDialogVisible" title="打印设置" width="400px">
      <el-form label-width="100px">
        <el-form-item label="纸张规格">
          <el-select v-model="selectedPaperSize" style="width: 100%;">
            <el-option label="A4" value="A4" />
            <el-option label="A5" value="A5" />
            <el-option label="A3" value="A3" />
            <el-option label="Letter" value="Letter" />
            <el-option label="Legal" value="Legal" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="printSettingsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="savePrintSettings">保存设置</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Goods, Tickets, User, Shop } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const activeMenu = ref('/products')
const printing = ref(false)
const selectedTransactionIds = ref([])
const printSettingsDialogVisible = ref(false)
const selectedPaperSize = ref('A4')

// 从本地存储获取打印设置
onMounted(() => {
  activeMenu.value = route.path
  const savedPaperSize = localStorage.getItem('printPaperSize')
  if (savedPaperSize) {
    selectedPaperSize.value = savedPaperSize
  }
})

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleTransactionSelection = (ids) => {
  selectedTransactionIds.value = ids
}

const handlePrintCommand = (command) => {
  if (command === 'print-settings') {
    printSettingsDialogVisible.value = true
  } else {
    printReport(command)
  }
}

const savePrintSettings = () => {
  localStorage.setItem('printPaperSize', selectedPaperSize.value)
  ElMessage.success('打印设置已保存')
  printSettingsDialogVisible.value = false
}

const printReport = async (command) => {
  try {
    printing.value = true
    
    let url
    if (command === 'all') {
      url = `http://localhost:8000/api/inventory-transactions/print_report/?paper_size=${selectedPaperSize.value}`
    } else if (command === 'selected' && selectedTransactionIds.value.length > 0) {
      const ids = selectedTransactionIds.value.join(',')
      url = `http://localhost:8000/api/inventory-transactions/print_report/?ids=${ids}&paper_size=${selectedPaperSize.value}`
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
    link.setAttribute('download', `inventory_report_${selectedPaperSize.value}.pdf`)
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