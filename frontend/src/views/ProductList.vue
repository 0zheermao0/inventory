<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>商品管理</h3>
          <div>
            <el-dropdown @command="handleProductDropdownCommand" style="margin-right: 10px;">
              <el-button type="primary">
                Excel操作<i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="export">导出商品</el-dropdown-item>
                  <el-dropdown-item command="import">导入商品</el-dropdown-item>
                  <el-dropdown-item command="download-template">下载模板</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-input v-model="searchKeyword" placeholder="搜索商品编号或名称" style="width: 300px; margin-right: 10px;" @keyup.enter="fetchProducts" />
            <el-button type="primary" @click="fetchProducts">搜索</el-button>
            <el-button type="success" @click="addProduct" style="margin-left: 10px;">新增商品</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="products" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="product_id" label="商品编号" width="150" />
        <el-table-column prop="name" label="商品名称" width="200" />
        <el-table-column prop="specification" label="规格" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price" label="单价" width="120">
          <template #default="scope">
            ¥{{ scope.row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存数量" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="200">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editProduct(scope.row)">编辑</el-button>
            <el-popconfirm title="确定要删除这个商品吗？" @confirm="deleteProduct(scope.row)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div style="margin-top: 20px; text-align: right;">
        <el-pagination
          @current-change="handlePageChange"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
        />
      </div>
    </el-card>
    
    <!-- 导入商品对话框 -->
    <el-dialog v-model="importProductsDialogVisible" title="导入商品" width="500px">
      <el-form label-width="100px">
        <el-form-item label="选择Excel文件">
          <el-upload
            class="upload-demo"
            action="#"
            :auto-upload="false"
            :show-file-list="true"
            :on-change="handleProductFileChange"
            accept=".xlsx,.xls"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <div slot="tip" class="el-upload__tip">只能上传xls/xlsx文件</div>
          </el-upload>
        </el-form-item>
        <el-alert
          title="注意：请确保Excel文件格式正确，第一列应为'型号'，第二列应为'单价元/个'等"
          type="info"
          show-icon
          :closable="false"
        />
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importProductsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="importProducts" :loading="importing">导入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const products = ref([])
const loading = ref(false)
const importing = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const importProductsDialogVisible = ref(false)
const selectedProductFile = ref(null)

// 定义emits
const emit = defineEmits(['selection-change'])

onMounted(() => {
  fetchProducts()
})

const fetchProducts = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    const response = await axios.get('http://localhost:8000/api/products/', { params })
    products.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('获取商品列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchProducts()
}

const addProduct = () => {
  router.push('/products/new')
}

const editProduct = (product) => {
  router.push(`/products/${product.id}/edit`)
}

const deleteProduct = async (product) => {
  try {
    await axios.delete(`http://localhost:8000/api/products/${product.id}/`)
    ElMessage.success('删除成功')
    fetchProducts()
  } catch (error) {
    ElMessage.error('删除失败：' + error.message)
  }
}

const handleProductDropdownCommand = (command) => {
  switch (command) {
    case 'export':
      exportProducts()
      break
    case 'import':
      importProductsDialogVisible.value = true
      break
    case 'download-template':
      downloadProductTemplate()
      break
  }
}

const exportProducts = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/inventory-transactions/export_products/', {
      responseType: 'blob'
    })
    
    // 创建blob URL并触发下载
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'products.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('商品信息导出成功！')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

const downloadProductTemplate = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/inventory-transactions/download_product_template/', {
      responseType: 'blob'
    })
    
    // 创建blob URL并触发下载
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'products_template.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('商品信息模板下载成功！')
  } catch (error) {
    ElMessage.error('下载失败：' + error.message)
  }
}

const handleProductFileChange = (file) => {
  selectedProductFile.value = file.raw
}

const importProducts = async () => {
  if (!selectedProductFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  try {
    importing.value = true
    
    const formData = new FormData()
    formData.append('file', selectedProductFile.value)
    
    const response = await axios.post('http://localhost:8000/api/inventory-transactions/import_products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    ElMessage.success(`导入成功：新增${response.data.created_count}条，更新${response.data.updated_count}条`)
    if (response.data.errors.length > 0) {
      ElMessage.warning(`部分数据导入失败：${response.data.errors.join('; ')}`)
    }
    
    importProductsDialogVisible.value = false
    fetchProducts()
  } catch (error) {
    if (error.response && error.response.data) {
      ElMessage.error('导入失败：' + error.response.data.error)
    } else {
      ElMessage.error('导入失败：' + error.message)
    }
  } finally {
    importing.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}
</script>