<template>
  <div>
    <el-row :gutter="20">
      <!-- In/Out Form -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>{{ form.transaction_type === 'IN' ? '入库' : '出库' }}</h3>
          </template>
          
          <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
            <el-form-item label="操作类型" prop="transaction_type">
              <el-radio-group v-model="form.transaction_type">
                <el-radio label="IN">入库</el-radio>
                <el-radio label="OUT">出库</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="选择客户">
              <el-select 
                v-model="form.customer" 
                filterable 
                remote 
                :remote-method="searchCustomers" 
                :loading="customerLoading" 
                placeholder="请输入客户名称搜索"
                style="width: 100%;"
                clearable
              >
                <el-option
                  v-for="item in customerOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="备注">
              <el-input v-model="form.remarks" type="textarea" />
            </el-form-item>
            
            <el-form-item label="制单人">
              <el-input v-model="form.preparer" />
            </el-form-item>
            
            <el-form-item label="审核人">
              <el-input v-model="form.auditor" />
            </el-form-item>
            
            <el-form-item label="经手人">
              <el-input v-model="form.handler" />
            </el-form-item>
            
            <el-form-item label="收货人">
              <el-input v-model="form.receiver" />
            </el-form-item>
            
            <!-- 商品项列表 -->
            <el-form-item label="商品列表">
              <el-table :data="form.items" style="width: 100%;">
                <el-table-column label="商品">
                  <template #default="{ row, $index }">
                    <el-select 
                      v-model="row.product" 
                      filterable 
                      remote 
                      :remote-method="(query) => searchProducts(query, $index)"
                      :loading="productLoading[$index]" 
                      placeholder="选择商品"
                      style="width: 100%;"
                      @change="(value) => handleProductChange(value, $index)"
                    >
                      <el-option-group label="热门商品">
                        <el-option
                          v-for="item in popularProducts[$index] || []"
                          :key="item.id"
                          :label="`${item.product_id} - ${item.name}`"
                          :value="item.id"
                        />
                      </el-option-group>
                      <el-option-group label="搜索结果">
                        <el-option
                          v-for="item in searchResults[$index] || []"
                          :key="item.id"
                          :label="`${item.product_id} - ${item.name}`"
                          :value="item.id"
                        />
                      </el-option-group>
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="数量" width="100">
                  <template #default="{ row }">
                    <el-input-number v-model="row.quantity" :min="1" controls-position="right" style="width: 100%;" />
                  </template>
                </el-table-column>
                <el-table-column label="单价" width="100">
                  <template #default="{ row }">
                    <el-input-number v-model="row.unit_price" :min="0" :step="0.01" controls-position="right" style="width: 100%;" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="{ $index }">
                    <el-button type="danger" size="small" @click="removeItem($index)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-button type="primary" @click="addItem" style="margin-top: 10px;">添加商品</el-button>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitForm" :loading="submitting">提交</el-button>
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
                <el-button type="success" @click="exportTransactions" style="margin-right: 10px;">导出订单</el-button>
                <el-button type="primary" @click="importTransactionsDialogVisible = true" style="margin-right: 10px;">导入订单</el-button>
                <el-select v-model="filterType" placeholder="类型筛选" style="width: 120px; margin-right: 10px;" @change="fetchTransactions">
                  <el-option label="全部" value="" />
                  <el-option label="入库" value="IN" />
                  <el-option label="出库" value="OUT" />
                </el-select>
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  style="width: 240px; margin-right: 10px;"
                  @change="fetchTransactions"
                />
                <el-select 
                  v-model="filterCustomer" 
                  filterable 
                  remote 
                  :remote-method="searchCustomersForFilter" 
                  :loading="customerLoading" 
                  placeholder="选择客户"
                  style="width: 150px; margin-right: 10px;"
                  clearable
                  @change="fetchTransactions"
                >
                  <el-option
                    v-for="item in customerOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
                <el-input v-model="searchKeyword" placeholder="搜索单据" style="width: 200px; margin-right: 10px;" @keyup.enter="fetchTransactions" />
                <el-button type="primary" @click="fetchTransactions">搜索</el-button>
                <el-button type="success" @click="printSelected" :disabled="selectedTransactions.length === 0" style="margin-left: 10px;">打印选中</el-button>
              </div>
            </div>
          </template>
          
          <el-table :data="transactions" stripe style="width: 100%" v-loading="loading" height="400" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="document_number" label="单据号码" width="150" />
            <el-table-column prop="customer_name" label="客户" width="120" />
            <el-table-column label="操作类型" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.transaction_type === 'IN' ? 'success' : 'danger'">
                  {{ scope.row.transaction_type === 'IN' ? '入库' : '出库' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_amount" label="总金额" width="80">
              <template #default="scope">
                ¥{{ scope.row.total_amount }}
              </template>
            </el-table-column>
            <el-table-column prop="transaction_date" label="操作时间" width="160">
              <template #default="scope">
                {{ formatDate(scope.row.transaction_date) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="viewTransaction(scope.row)">查看</el-button>
                <el-button size="small" type="danger" @click="deleteTransaction(scope.row)">删除</el-button>
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
    
    <!-- 查看单据详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="`单据详情 - ${currentTransaction.document_number}`" width="800px">
      <el-table :data="currentTransaction.items" style="width: 100%;">
        <el-table-column prop="product_id" label="商品编码" width="120" />
        <el-table-column prop="product_name" label="商品名称" width="150" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="unit_price" label="单价" width="80">
          <template #default="scope">
            ¥{{ scope.row.unit_price }}
          </template>
        </el-table-column>
        <el-table-column prop="total_price" label="金额" width="80">
          <template #default="scope">
            ¥{{ scope.row.total_price }}
          </template>
        </el-table-column>
        <el-table-column prop="remarks" label="备注" />
      </el-table>
      
      <div style="margin-top: 20px; text-align: right;">
        <strong>总金额: ¥{{ currentTransaction.total_amount }}</strong>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 导入订单对话框 -->
    <el-dialog v-model="importTransactionsDialogVisible" title="导入订单" width="500px">
      <el-form label-width="100px">
        <el-form-item label="选择Excel文件">
          <el-upload
            class="upload-demo"
            action="#"
            :auto-upload="false"
            :show-file-list="true"
            :on-change="handleTransactionFileChange"
            accept=".xlsx,.xls"
          >
            <el-button size="small" type="primary">选择文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importTransactionsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="importTransactions" :loading="importing">导入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const formRef = ref()
const submitting = ref(false)
const loading = ref(false)
const customerLoading = ref(false)
const productLoading = ref([])
const popularProducts = ref([])
const searchResults = ref([])
const customerOptions = ref([])
const transactions = ref([])
const searchKeyword = ref('')
const filterType = ref('')
const filterCustomer = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedTransactions = ref([])
const importing = ref(false)
const importTransactionsDialogVisible = ref(false)
const selectedTransactionFile = ref(null)

// 详情对话框相关
const detailDialogVisible = ref(false)
const currentTransaction = ref({})

// 表单数据
const form = ref({
  transaction_type: 'IN',
  customer: null,
  remarks: '',
  preparer: '',
  auditor: '',
  handler: '',
  receiver: '',
  items: [
    {
      product: null,
      quantity: 1,
      unit_price: 0,
      remarks: ''
    }
  ]
})

const rules = {
  'items.0.product': [
    { required: true, message: '请选择商品', trigger: 'change' }
  ],
  'items.0.quantity': [
    { required: true, message: '请输入数量', trigger: 'blur' }
  ]
}

onMounted(() => {
  fetchTransactions()
  loadCustomerOptions()
  loadPopularProducts(0)
})

// 加载客户选项
const loadCustomerOptions = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/customers/', {
      params: { page_size: 100 }
    })
    customerOptions.value = response.data.results
  } catch (error) {
    ElMessage.error('加载客户选项失败：' + error.message)
  }
}

const searchCustomers = async (query) => {
  if (!query) {
    loadCustomerOptions()
    return
  }
  
  try {
    customerLoading.value = true
    const response = await axios.get('http://localhost:8000/api/customers/', {
      params: { search: query, page_size: 20 }
    })
    customerOptions.value = response.data.results
  } catch (error) {
    ElMessage.error('搜索客户失败：' + error.message)
  } finally {
    customerLoading.value = false
  }
}

const searchCustomersForFilter = async (query) => {
  await searchCustomers(query)
}

// 加载热门商品
const loadPopularProducts = async (index) => {
  // 初始化数组
  if (!popularProducts.value[index]) {
    popularProducts.value[index] = []
  }
  
  if (popularProducts.value[index].length > 0) return // 避免重复加载
  
  try {
    const response = await axios.get('http://localhost:8000/api/products/', {
      params: { page_size: 10 }
    })
    popularProducts.value[index] = response.data.results
  } catch (error) {
    ElMessage.error('加载热门商品失败：' + error.message)
  }
}

const searchProducts = async (query, index) => {
  // 初始化数组
  if (!searchResults.value[index]) {
    searchResults.value[index] = []
  }
  if (!productLoading.value[index]) {
    productLoading.value[index] = false
  }
  
  if (!query) {
    searchResults.value[index] = []
    return
  }
  
  try {
    productLoading.value[index] = true
    const response = await axios.get('http://localhost:8000/api/products/', {
      params: { search: query, page_size: 20 }
    })
    searchResults.value[index] = response.data.results
  } catch (error) {
    ElMessage.error('搜索商品失败：' + error.message)
  } finally {
    productLoading.value[index] = false
  }
}

// 添加商品项
const addItem = () => {
  form.value.items.push({
    product: null,
    quantity: 1,
    unit_price: 0,
    remarks: ''
  })
  
  // 为新项加载热门商品
  const newIndex = form.value.items.length - 1
  loadPopularProducts(newIndex)
}

// 删除商品项
const removeItem = (index) => {
  if (form.value.items.length <= 1) {
    ElMessage.warning('至少需要保留一个商品项')
    return
  }
  form.value.items.splice(index, 1)
}

// 处理商品选择变化
const handleProductChange = (productId, index) => {
  if (!productId) {
    // 如果清空了商品选择，重置单价
    form.value.items[index].unit_price = 0
    return
  }
  
  // 查找选中的商品
  const allProducts = [...(popularProducts.value[index] || []), ...(searchResults.value[index] || [])]
  const selectedProduct = allProducts.find(p => p.id === productId)
  
  if (selectedProduct) {
    // 更新单价为选中商品的价格
    form.value.items[index].unit_price = selectedProduct.price
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
    
    if (filterCustomer.value) {
      params.customer = filterCustomer.value
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
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
}

const submitForm = async () => {
  try {
    // 验证表单
    let valid = true
    for (let i = 0; i < form.value.items.length; i++) {
      if (!form.value.items[i].product) {
        ElMessage.error(`第${i+1}行商品未选择`)
        valid = false
        break
      }
      if (form.value.items[i].quantity <= 0) {
        ElMessage.error(`第${i+1}行数量必须大于0`)
        valid = false
        break
      }
    }
    
    if (!valid) return
    
    submitting.value = true
    
    // 检查出库时库存是否足够
    if (form.value.transaction_type === 'OUT') {
      for (let i = 0; i < form.value.items.length; i++) {
        const item = form.value.items[i]
        const allProducts = [...(popularProducts.value[i] || []), ...(searchResults.value[i] || [])]
        const selectedProduct = allProducts.find(p => p.id === item.product)
        if (selectedProduct && selectedProduct.stock_quantity < item.quantity) {
          ElMessage.error(`商品 ${selectedProduct.name} 库存不足！当前库存：${selectedProduct.stock_quantity}`)
          submitting.value = false
          return
        }
      }
    }
    
    // 构造提交数据
    const formData = {
      transaction_type: form.value.transaction_type,
      customer: form.value.customer,
      remarks: form.value.remarks,
      preparer: form.value.preparer,
      auditor: form.value.auditor,
      handler: form.value.handler,
      receiver: form.value.receiver,
      items: form.value.items.map(item => ({
        product: item.product,
        quantity: item.quantity,
        unit_price: item.unit_price,
        remarks: item.remarks
      }))
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
  form.value = {
    transaction_type: 'IN',
    customer: null,
    remarks: '',
    preparer: '',
    auditor: '',
    handler: '',
    receiver: '',
    items: [
      {
        product: null,
        quantity: 1,
        unit_price: 0,
        remarks: ''
      }
    ]
  }
  
  // 重新加载第一个商品项的热门商品
  loadPopularProducts(0)
}

const viewTransaction = async (transaction) => {
  try {
    // 获取完整的交易详情（包含商品项）
    const response = await axios.get(`http://localhost:8000/api/inventory-transactions/${transaction.id}/`)
    currentTransaction.value = response.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取单据详情失败：' + error.message)
  }
}

const deleteTransaction = (transaction) => {
  ElMessageBox.confirm(
    `确定要删除单据 ${transaction.document_number} 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await axios.delete(`http://localhost:8000/api/inventory-transactions/${transaction.id}/`)
      ElMessage.success('单据删除成功')
      fetchTransactions()
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  }).catch(() => {
    // 用户取消删除
  })
}

const printSelected = async () => {
  try {
    const ids = selectedTransactions.value.map(item => item.id).join(',')
    // 获取纸张规格（这里使用默认的A4，实际应用中可以从设置中获取）
    const paperSize = 'A4'
    const response = await axios.get(`http://localhost:8000/api/inventory-transactions/print_report/?ids=${ids}&paper_size=${paperSize}`, {
      responseType: 'blob'
    })
    
    // 创建blob URL并触发下载
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `selected_inventory_report_${paperSize}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('选中记录报表生成成功！')
  } catch (error) {
    ElMessage.error('报表生成失败：' + error.message)
  }
}

const exportTransactions = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/inventory-transactions/export_transactions/', {
      responseType: 'blob'
    })
    
    // 创建blob URL并触发下载
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'inventory_transactions.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('出入库订单导出成功！')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

const handleTransactionFileChange = (file) => {
  selectedTransactionFile.value = file.raw
}

const importTransactions = async () => {
  if (!selectedTransactionFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  try {
    importing.value = true
    
    const formData = new FormData()
    formData.append('file', selectedTransactionFile.value)
    
    const response = await axios.post('http://localhost:8000/api/inventory-transactions/import_transactions/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    ElMessage.success(`导入成功：新增${response.data.created_count}条，更新${response.data.updated_count}条`)
    if (response.data.errors.length > 0) {
      ElMessage.warning(`部分数据导入失败：${response.data.errors.join('; ')}`)
    }
    
    importTransactionsDialogVisible.value = false
    fetchTransactions()
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
  flex-wrap: wrap;
}

.card-header > div {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}
</style>