<template>
  <div class="dashboard-page">
    <div class="page-header">
      <div class="page-title">数据概览</div>
      <el-button text @click="loadStats">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon datasets">
            <el-icon :size="24"><FolderOpened /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.dataset_count }}</div>
            <div class="stat-label">知识库数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon documents">
            <el-icon :size="24"><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.document_count }}</div>
            <div class="stat-label">文档数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon chunks">
            <el-icon :size="24"><Files /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.chunk_count }}</div>
            <div class="stat-label">切片数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon chats">
            <el-icon :size="24"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.chat_count }}</div>
            <div class="stat-label">对话次数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="never" header="最近对话">
          <el-table :data="recentChats" stripe>
            <el-table-column prop="query" label="问题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="timestamp" label="时间" width="180" />
          </el-table>
          <el-empty v-if="recentChats.length === 0" description="暂无对话记录" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" header="最近文档">
          <el-table :data="recentDocuments" stripe>
            <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
                  {{ row.status === 'completed' ? '已完成' : '处理中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
          <el-empty v-if="recentDocuments.length === 0" description="暂无文档" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { FolderOpened, Document, Files, ChatDotRound, Refresh } from '@element-plus/icons-vue'
import { getDatasets, getDocuments } from '@/api/dataset'

const stats = reactive({
  dataset_count: 0,
  document_count: 0,
  chunk_count: 0,
  chat_count: 0,
})

const recentChats = ref([])
const recentDocuments = ref([])

const loadStats = async () => {
  try {
    const datasetsRes = await getDatasets()
    const datasets = datasetsRes.data || datasetsRes || []
    stats.dataset_count = datasets.length

    let totalDocs = 0
    let totalChunks = 0
    
    for (const ds of datasets) {
      if (ds.document_count) totalDocs += ds.document_count
      if (ds.chunk_count) totalChunks += ds.chunk_count
    }
    
    stats.document_count = totalDocs
    stats.chunk_count = totalChunks
    
    const docsRes = await getDocuments()
    const docs = docsRes.data || docsRes || []
    recentDocuments.value = docs.slice(0, 5).map(d => ({
      ...d,
      created_at: d.created_at || new Date().toLocaleString()
    }))
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped lang="scss">
.dashboard-page {
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
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-right: 16px;

    &.datasets {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    &.documents {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    &.chunks {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }

    &.chats {
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
  }

  .stat-content {
    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      line-height: 1.2;
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-top: 4px;
    }
  }
}
</style>
