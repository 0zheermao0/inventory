<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>商品管理</h3>
          <div>
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
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

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

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}
</script>