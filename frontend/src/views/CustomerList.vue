<template>
  <div>
    <el-card>
      <template #header>
        <div class="clearfix">
          <span>客户管理</span>
          <el-button type="primary" style="float: right;" @click="openCustomerForm()">新增客户</el-button>
        </div>
      </template>
      
      <el-table :data="customers" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="客户名称" />
        <el-table-column prop="contact_person" label="联系人" />
        <el-table-column prop="phone" label="联系电话" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="openCustomerForm(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCustomer(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        v-model:current-page="currentPage"
        @current-change="handlePageChange"
        style="margin-top: 20px; text-align: center;"
      />
    </el-card>
    
    <!-- 客户表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingCustomer ? '编辑客户' : '新增客户'" width="500px">
      <el-form :model="customerForm" :rules="customerRules" ref="customerFormRef" label-width="100px">
        <el-form-item label="客户名称" prop="name">
          <el-input v-model="customerForm.name" />
        </el-form-item>
        
        <el-form-item label="联系人">
          <el-input v-model="customerForm.contact_person" />
        </el-form-item>
        
        <el-form-item label="联系电话">
          <el-input v-model="customerForm.phone" />
        </el-form-item>
        
        <el-form-item label="邮箱">
          <el-input v-model="customerForm.email" />
        </el-form-item>
        
        <el-form-item label="地址">
          <el-input v-model="customerForm.address" type="textarea" />
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input v-model="customerForm.remarks" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCustomerForm" :loading="submitting">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const customers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingCustomer = ref(null)
const submitting = ref(false)
const customerFormRef = ref()

// 分页相关
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const customerForm = ref({
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  remarks: ''
})

const customerRules = {
  name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ]
}

onMounted(() => {
  fetchCustomers()
})

const fetchCustomers = async (page = 1) => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/customers/', {
      params: {
        page: page,
        page_size: pageSize.value
      }
    })
    
    if (response.data.results) {
      customers.value = response.data.results
      total.value = response.data.count
    } else {
      customers.value = response.data
      total.value = response.data.length
    }
  } catch (error) {
    ElMessage.error('获取客户列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchCustomers(page)
}

const openCustomerForm = (customer = null) => {
  editingCustomer.value = customer
  if (customer) {
    customerForm.value = { ...customer }
  } else {
    customerForm.value = {
      name: '',
      contact_person: '',
      phone: '',
      email: '',
      address: '',
      remarks: ''
    }
  }
  dialogVisible.value = true
}

const submitCustomerForm = async () => {
  try {
    await customerFormRef.value.validate()
    
    submitting.value = true
    
    if (editingCustomer.value) {
      // 更新客户
      await axios.put(`http://localhost:8000/api/customers/${editingCustomer.value.id}/`, customerForm.value)
      ElMessage.success('客户更新成功')
    } else {
      // 创建新客户
      await axios.post('http://localhost:8000/api/customers/', customerForm.value)
      ElMessage.success('客户创建成功')
    }
    
    dialogVisible.value = false
    fetchCustomers(currentPage.value)
  } catch (error) {
    if (error.response && error.response.data) {
      const errorMsg = Object.values(error.response.data).flat().join('; ')
      ElMessage.error('保存失败：' + errorMsg)
    } else {
      ElMessage.error('保存失败：' + error.message)
    }
  } finally {
    submitting.value = false
  }
}

const deleteCustomer = (customer) => {
  ElMessageBox.confirm(
    `确定要删除客户 "${customer.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await axios.delete(`http://localhost:8000/api/customers/${customer.id}/`)
      ElMessage.success('客户删除成功')
      fetchCustomers(currentPage.value)
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  }).catch(() => {
    // 用户取消删除
  })
}
</script>