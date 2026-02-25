<template>
  <div class="dataset-detail-page">
    <div class="page-header">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <div class="page-title">{{ datasetName }}</div>
      <div class="header-actions">
        <el-button type="primary" @click="handleUpload">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="文档管理" name="documents">
        <el-card shadow="never">
          <el-table :data="documentList" stripe>
            <el-table-column prop="filename" label="文件名" min-width="200" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="大小" width="100">
              <template #default="{ row }">
                {{ formatBytes(row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="上传时间" width="180" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="viewChunks(row)">查看切片</el-button>
                <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="切片预览" name="chunks">
        <el-card shadow="never">
          <el-empty v-if="!selectedDocument" description="请选择文档查看切片" />
          <div v-else>
            <div class="chunk-header">
              <span>{{ selectedDocument.filename }} - 切片列表</span>
            </div>
            <el-table :data="chunkList" stripe>
              <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
              <el-table-column prop="index" label="序号" width="80" />
            </el-table>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="uploadDialogVisible"
      title="上传文档"
      width="500px"
    >
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        :auto-upload="false"
        :limit="10"
        :on-change="handleFileChange"
        :file-list="fileList"
        accept=".pdf,.md,.txt,.docx,.py,.js,.ts,.java"
      >
        <el-button type="primary">
          <el-icon><Upload /></el-icon>
          选择文件
        </el-button>
        <template #tip>
          <div class="upload-tip">
            支持 PDF、Markdown、Text、Word、代码文件，单个文件不超过 10MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Upload, Delete } from '@element-plus/icons-vue'
import {
  getDataset,
  getDocuments,
  deleteDocument,
  uploadDocument,
  getChunks,
} from '@/api/dataset'

const route = useRoute()
const router = useRouter()

const datasetId = route.params.id
const datasetName = ref('知识库详情')
const activeTab = ref('documents')
const documentList = ref([])
const chunkList = ref([])
const selectedDocument = ref(null)
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const fileList = ref([])
const uploadRef = ref(null)

const goBack = () => {
  router.push('/datasets')
}

const loadDataset = async () => {
  try {
    const res = await getDataset(datasetId)
    datasetName.value = res.name || '知识库详情'
  } catch (error) {
    console.error('加载知识库失败:', error)
  }
}

const loadDocuments = async () => {
  try {
    const res = await getDocuments(datasetId)
    documentList.value = res.data || res || []
  } catch (error) {
    console.error('加载文档失败:', error)
    documentList.value = []
  }
}

const getStatusType = (status) => {
  const map = {
    completed: 'success',
    pending: 'warning',
    processing: 'info',
    failed: 'danger',
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    completed: '已完成',
    pending: '等待中',
    processing: '处理中',
    failed: '失败',
  }
  return map[status] || status
}

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleUpload = () => {
  fileList.value = []
  uploadDialogVisible.value = true
}

const handleFileChange = (file, files) => {
  fileList.value = files
}

const handleSubmitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    for (const file of fileList.value) {
      const formData = new FormData()
      formData.append('file', file.raw)
      await uploadDocument(datasetId, formData)
    }
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    loadDocuments()
  } catch (error) {
    ElMessage.error(error.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

const viewChunks = async (row) => {
  selectedDocument.value = row
  activeTab.value = 'chunks'
  try {
    const res = await getChunks(datasetId, row.id)
    chunkList.value = res.data || res || []
  } catch (error) {
    console.error('加载切片失败:', error)
    chunkList.value = []
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该文档吗？', '提示', {
      type: 'warning',
    })
    await deleteDocument(datasetId, row.id)
    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  loadDataset()
  loadDocuments()
})
</script>

<style scoped lang="scss">
.dataset-detail-page {
  .page-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      flex: 1;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
      margin: 0 20px;
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
}

.detail-tabs {
  :deep(.el-tabs__content) {
    padding-top: 16px;
  }
}

.chunk-header {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
}

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
