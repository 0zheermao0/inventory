<template>
  <div>
    <el-card>
      <template #header>
        <div class="clearfix">
          <span>店铺信息管理</span>
        </div>
      </template>
      
      <el-form :model="storeForm" ref="storeFormRef" label-width="120px" v-loading="loading">
        <el-form-item label="店铺名称" prop="name">
          <el-input v-model="storeForm.name" />
        </el-form-item>
        
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="storeForm.phone" />
        </el-form-item>
        
        <el-form-item label="地址" prop="address">
          <el-input v-model="storeForm.address" type="textarea" />
        </el-form-item>
        
        <el-form-item label="店铺Logo" prop="logo">
          <el-upload
            class="avatar-uploader"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleLogoChange"
          >
            <img v-if="storeForm.logoPreview" :src="storeForm.logoPreview" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="备注" prop="remarks">
          <el-input v-model="storeForm.remarks" type="textarea" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Plus } from '@element-plus/icons-vue'

const storeFormRef = ref()
const loading = ref(false)
const submitting = ref(false)
const logoFile = ref(null)

const storeForm = ref({
  id: null,
  name: '',
  phone: '',
  address: '',
  logo: null,
  logoPreview: null,
  remarks: ''
})

onMounted(() => {
  fetchStoreInfo()
})

const fetchStoreInfo = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/store-info/')
    if (response.data.results && response.data.results.length > 0) {
      const store = response.data.results[0]
      storeForm.value = {
        ...store,
        logoPreview: store.logo ? `http://localhost:8000${store.logo}` : null
      }
    }
  } catch (error) {
    ElMessage.error('获取店铺信息失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const handleLogoChange = (file) => {
  logoFile.value = file.raw
  storeForm.value.logoPreview = URL.createObjectURL(file.raw)
}

const submitForm = async () => {
  try {
    submitting.value = true
    
    const formData = new FormData()
    formData.append('name', storeForm.value.name)
    formData.append('phone', storeForm.value.phone)
    formData.append('address', storeForm.value.address)
    formData.append('remarks', storeForm.value.remarks)
    
    if (logoFile.value) {
      formData.append('logo', logoFile.value)
    }
    
    if (storeForm.value.id) {
      // 更新店铺信息
      await axios.put(`http://localhost:8000/api/store-info/${storeForm.value.id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      ElMessage.success('店铺信息更新成功')
    } else {
      // 创建店铺信息
      await axios.post('http://localhost:8000/api/store-info/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      ElMessage.success('店铺信息创建成功')
    }
    
    fetchStoreInfo()
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
</script>

<style scoped>
.avatar-uploader .avatar {
  width: 178px;
  height: 178px;
  display: block;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}
</style>