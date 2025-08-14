<template>
  <div>
    <el-card>
      <template #header>
        <h3>{{ isEdit ? '编辑商品' : '新增商品' }}</h3>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="商品编号" prop="product_id">
          <el-input v-model="form.product_id" :disabled="isEdit" />
        </el-form-item>
        
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        
        <el-form-item label="规格">
          <el-input v-model="form.specification" placeholder="例如：24个/件" />
        </el-form-item>
        
        <el-form-item label="单位">
          <el-input v-model="form.unit" placeholder="例如：件、箱、瓶" />
        </el-form-item>
        
        <el-form-item label="单价" prop="price">
          <el-input-number v-model="form.price" :min="0" :step="0.01" controls-position="right" style="width: 100%;" />
        </el-form-item>
        
        <el-form-item label="库存数量" prop="stock_quantity">
          <el-input-number v-model="form.stock_quantity" :min="0" controls-position="right" style="width: 100%;" />
        </el-form-item>
        
        <el-form-item label="商品描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">{{ isEdit ? '更新' : '创建' }}</el-button>
          <el-button @click="cancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const isEdit = ref(false)
const submitting = ref(false)

const form = ref({
  product_id: '',
  name: '',
  specification: '',
  unit: '',
  price: 0,
  stock_quantity: 0,
  description: ''
})

const rules = {
  product_id: [
    { required: true, message: '请输入商品编号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入单价', trigger: 'blur' }
  ],
  stock_quantity: [
    { required: true, message: '请输入库存数量', trigger: 'blur' }
  ]
}

onMounted(() => {
  const productId = route.params.id
  if (productId) {
    isEdit.value = true
    fetchProduct(productId)
  }
})

const fetchProduct = async (id) => {
  try {
    const response = await axios.get(`http://localhost:8000/api/products/${id}/`)
    form.value = response.data
  } catch (error) {
    ElMessage.error('获取商品信息失败：' + error.message)
  }
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    if (isEdit.value) {
      // Update existing product
      await axios.put(`http://localhost:8000/api/products/${route.params.id}/`, form.value)
      ElMessage.success('商品更新成功')
    } else {
      // Create new product
      await axios.post('http://localhost:8000/api/products/', form.value)
      ElMessage.success('商品创建成功')
    }
    
    router.push('/products')
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

const cancel = () => {
  router.push('/products')
}
</script>