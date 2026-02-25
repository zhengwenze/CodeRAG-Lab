<template>
  <div class="dataset-page">
    <div class="page-header">
      <div class="page-title">知识库</div>
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-input
            v-model="searchForm.title"
            placeholder="知识库名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" icon="Search">查询</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-card shadow="never">
      <div class="dataset-list">
        <div class="dataset-item add-box" @click="handleCreate">
          <div class="add-icon">
            <el-icon :size="40"><Plus /></el-icon>
          </div>
          <div class="add-text">创建知识库</div>
        </div>

        <div
          v-for="item in datasetList"
          :key="item.id"
          class="dataset-item"
        >
          <el-card shadow="never" class="dataset-card">
            <div class="dataset-info" @click="goDetail(item.id)">
              <div class="dataset-icon">
                {{ item.name ? item.name.substring(0, 1).toUpperCase() : 'D' }}
              </div>
              <div class="dataset-meta">
                <div class="dataset-name">{{ item.name || '未命名' }}</div>
                <div class="dataset-desc">{{ item.description || '暂无描述' }}</div>
              </div>
            </div>
            <div class="dataset-stats">
              <div class="stat-item">
                <span class="stat-value">{{ item.document_count || 0 }}</span>
                <span class="stat-label">文档</span>
              </div>
              <el-divider direction="vertical" />
              <div class="stat-item">
                <span class="stat-value">{{ item.chunk_count || 0 }}</span>
                <span class="stat-label">切片</span>
              </div>
            </div>
            <div class="dataset-actions">
              <el-button type="primary" link @click="goDetail(item.id)">管理</el-button>
              <el-dropdown @command="(cmd) => handleCommand(cmd, item)">
                <el-button type="primary" link>
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="reindex">
                      <el-icon><Refresh /></el-icon>
                      重新索引
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      title="创建知识库"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MoreFilled, Refresh, Delete, Search } from '@element-plus/icons-vue'
import { getDatasets, createDataset, deleteDataset } from '@/api/dataset'

const router = useRouter()

const searchForm = reactive({
  title: '',
})

const datasetList = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)

const form = reactive({
  name: '',
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入知识库名称', trigger: 'blur' }],
}

const formRef = ref(null)

const loadDatasets = async () => {
  try {
    const res = await getDatasets()
    datasetList.value = res.data || res || []
  } catch (error) {
    console.error('加载知识库失败:', error)
    datasetList.value = []
  }
}

const handleSearch = () => {
  loadDatasets()
}

const handleCreate = () => {
  form.name = ''
  form.description = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    await createDataset(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadDatasets()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const goDetail = (id) => {
  router.push(`/datasets/${id}`)
}

const handleCommand = async (command, item) => {
  if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除该知识库吗？', '提示', {
        type: 'warning',
      })
      await deleteDataset(item.id)
      ElMessage.success('删除成功')
      loadDatasets()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error(error.message || '删除失败')
      }
    }
  } else if (command === 'reindex') {
    ElMessage.info('重新索引功能开发中')
  }
}

onMounted(() => {
  loadDatasets()
})
</script>

<style scoped lang="scss">
.dataset-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }

    .search-form {
      float: right;
    }
  }
}

.dataset-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.dataset-item {
  width: calc(25% - 16px);
  min-width: 280px;

  &.add-box {
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 180px;
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
      background-color: #f5f7fa;
    }

    .add-icon {
      color: #909399;
      margin-bottom: 12px;
    }

    .add-text {
      font-size: 14px;
      color: #606266;
    }
  }
}

.dataset-card {
  min-height: 180px;
  display: flex;
  flex-direction: column;

  .dataset-info {
    display: flex;
    cursor: pointer;
    margin-bottom: 12px;

    .dataset-icon {
      width: 48px;
      height: 48px;
      border-radius: 8px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      font-weight: bold;
      margin-right: 12px;
      flex-shrink: 0;
    }

    .dataset-meta {
      flex: 1;
      overflow: hidden;

      .dataset-name {
        font-size: 16px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .dataset-desc {
        font-size: 12px;
        color: #909399;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
    }
  }

  .dataset-stats {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-top: 1px solid #ebeef5;
    border-bottom: 1px solid #ebeef5;
    margin-bottom: 12px;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0 16px;

      .stat-value {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }

      .stat-label {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .dataset-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
}
</style>
