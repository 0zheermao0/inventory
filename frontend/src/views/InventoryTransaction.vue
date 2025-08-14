<template>
  <div>
    <el-row :gutter="20">
      <!-- In/Out Form -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>{{ transactionForm.transaction_type === 'IN' ? '入库' : '出库' }}</h3>
          </template>
          
          <el-form :model="transactionForm" :rules="rules" ref="formRef" label-width="120px">
            <el-form-item label="操作类型" prop="transaction_type">
              <el-radio-group v-model="transactionForm.transaction_type">
                <el-radio label="IN">入库</el-radio>
                <el-radio label="OUT">出库</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="选择商品" prop="product">
              <el-select 
                v-model="transactionForm.product" 
                filterable 
                remote 
                :remote-method="searchProducts" 
                :loading="productLoading" 
                placeholder="请输入商品编号或名称搜索"
                style="width: 100%;"
                @focus="loadPopularProducts"
              >
                <el-option-group label="热门商品">
                  <el-option
                    v-for="item in popularProducts"
                    :key="item.id"
                    :label="`${item.product_id} - ${item.name}`"
                    :value="item.id"
                  />
                </el-option-group>
                <el-option-group label="搜索结果">
                  <el-option
                    v-for="item in searchResults"
                    :key="item.id"
                    :label="`${item.product_id} - ${item.name}`"
                    :value="item.id"
                  />
                </el-option-group>
              </el-select>
            </el-form-item>
            
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="transactionForm.quantity" :min="1" controls-position="right" style="width: 100%;" />
            </el-form-item>
            
            <el-form-item label="单价" prop="unit_price">
              <el-input-number v-model="transactionForm.unit_price" :min="0" :step="0.01" controls-position="right" style="width: 100%;" />
            </el-form-item>
            
            <el-form-item label="备注">
              <el-input v-model="transactionForm.remarks" type="textarea" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitTransaction" :loading="submitting">提交</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- Transaction List -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>出入库记录</h3>
              <div>
                <el-select v-model="filterType" placeholder="类型筛选" style="width: 120px; margin-right: 10px;" @change="fetchTransactions">
                  <el-option label="全部" value="" />
                  <el-option label="入库" value="IN" />
                  <el-option label="出库" value="OUT" />
                </el-select>
                <el-input v-model="searchKeyword" placeholder="搜索商品" style="width: 200px; margin-right: 10px;" @keyup.enter="fetchTransactions" />
                <el-button type="primary" @click="fetchTransactions">搜索</el-button>
                <el-button type="success" @click="printSelected" :disabled="selectedTransactions.length === 0" style="margin-left: 10px;">打印选中</el-button>
              </div>
            </div>
          </template>
          
          <el-table :data="transactions" stripe style="width: 100%" v-loading="loading" height="400" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="product_id" label="商品编号" width="120" />
            <el-table-column prop="product_name" label="商品名称" width="150" />
            <el-table-column label="操作类型" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.transaction_type === 'IN' ? 'success' : 'danger'">
                  {{ scope.row.transaction_type === 'IN' ? '入库' : '出库' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="unit_price" label="单价" width="80">
              <template #default="scope">
                ¥{{ scope.row.unit_price }}
              </template>
            </el-table-column>
            <el-table-column prop="total_price" label="总价" width="80">
              <template #default="scope">
                ¥{{ scope.row.total_price }}
              </template>
            </el-table-column>
            <el-table-column prop="transaction_date" label="操作时间" width="160">
              <template #default="scope">
                {{ formatDate(scope.row.transaction_date) }}
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
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const formRef = ref()
const submitting = ref(false)
const loading = ref(false)
const productLoading = ref(false)
const popularProducts = ref([])
const searchResults = ref([])
const transactions = ref([])
const searchKeyword = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedTransactions = ref([])

// 定义emits
const emit = defineEmits(['selection-change'])

const transactionForm = ref({
  product: null,
  transaction_type: 'IN',
  quantity: 1,
  unit_price: 0,
  remarks: ''
})

const rules = {
  product: [
    { required: true, message: '请选择商品', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' }
  ],
  unit_price: [
    { required: true, message: '请输入单价', trigger: 'blur' }
  ]
}

// Watch product selection to auto-fill price
watch(() => transactionForm.value.product, (newVal) => {
  if (newVal) {
    const allProducts = [...popularProducts.value, ...searchResults.value]
    const selectedProduct = allProducts.find(p => p.id === newVal)
    if (selectedProduct) {
      // 只有在单价为0时才自动填充，允许用户手动修改
      if (transactionForm.value.unit_price === 0) {
        transactionForm.value.unit_price = selectedProduct.price
      }
    }
  }
})

// 移除会导致问题的watcher
// watch(() => transactionForm.value.transaction_type, () => {
//   resetForm() // 这里会导致选择出库时被重置为入库
// })

onMounted(() => {
  fetchTransactions()
})

// 加载热门商品
const loadPopularProducts = async () => {
  if (popularProducts.value.length > 0) return // 避免重复加载
  
  try {
    const response = await axios.get('http://localhost:8000/api/products/', {
      params: { page_size: 10 }
    })
    popularProducts.value = response.data.results
  } catch (error) {
    ElMessage.error('加载热门商品失败：' + error.message)
  }
}

const searchProducts = async (query) => {
  if (!query) {
    searchResults.value = []
    return
  }
  
  try {
    productLoading.value = true
    const response = await axios.get('http://localhost:8000/api/products/', {
      params: { search: query, page_size: 20 }
    })
    searchResults.value = response.data.results
  } catch (error) {
    ElMessage.error('搜索商品失败：' + error.message)
  } finally {
    productLoading.value = false
  }
}

const fetchTransactions = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    if (filterType.value) {
      params.transaction_type = filterType.value
    }
    
    const response = await axios.get('http://localhost:8000/api/inventory-transactions/', { params })
    transactions.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('获取交易记录失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchTransactions()
}

const handleSelectionChange = (selection) => {
  selectedTransactions.value = selection
  // 向父组件传递选中的记录ID
  emit('selection-change', selection.map(item => item.id))
}

const submitTransaction = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    // 检查出库时库存是否足够
    if (transactionForm.value.transaction_type === 'OUT') {
      const selectedProduct = [...popularProducts.value, ...searchResults.value].find(
        p => p.id === transactionForm.value.product
      )
      if (selectedProduct && selectedProduct.stock_quantity < transactionForm.value.quantity) {
        ElMessage.error(`库存不足！当前库存：${selectedProduct.stock_quantity}`)
        submitting.value = false
        return
      }
    }
    
    const formData = {
      product: transactionForm.value.product,
      transaction_type: transactionForm.value.transaction_type,
      quantity: transactionForm.value.quantity,
      unit_price: transactionForm.value.unit_price,
      remarks: transactionForm.value.remarks
    }
    
    await axios.post('http://localhost:8000/api/inventory-transactions/', formData)
    ElMessage.success('操作成功')
    resetForm()
    fetchTransactions()
  } catch (error) {
    if (error.response && error.response.data) {
      const errorMsg = Object.values(error.response.data).flat().join('; ')
      ElMessage.error('操作失败：' + errorMsg)
    } else {
      ElMessage.error('操作失败：' + error.message)
    }
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  // 重置表单时保持当前的操作类型
  const currentType = transactionForm.value.transaction_type
  transactionForm.value = {
    product: null,
    transaction_type: currentType, // 保持当前选择的操作类型
    quantity: 1,
    unit_price: 0,
    remarks: ''
  }
}

const printSelected = async () => {
  try {
    const ids = selectedTransactions.value.map(item => item.id).join(',')
    const response = await axios.get(`http://localhost:8000/api/inventory-transactions/print_report/?ids=${ids}`, {
      responseType: 'blob'
    })
    
    // 创建blob URL并触发下载
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'selected_inventory_report.pdf')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('选中记录报表生成成功！')
  } catch (error) {
    ElMessage.error('报表生成失败：' + error.message)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>