<template>
  <div class="layout-container">
    <div class="sidebar">
      <div class="logo">
        <img src="@/assets/logo.png" alt="CodeRAG" />
        <span>CodeRAG Lab</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
      >
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 对话</span>
        </el-menu-item>
        <el-menu-item index="/datasets">
          <el-icon><FolderOpened /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
      </el-menu>
    </div>
    <div class="main-container">
      <div class="header">
        <div class="header-title">{{ pageTitle }}</div>
        <div class="header-actions">
          <el-button text>
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChatDotRound, FolderOpened, DataAnalysis, Setting } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/chat': 'AI 对话',
    '/datasets': '知识库管理',
    '/dashboard': '数据概览',
  }
  return titles[route.path] || 'CodeRAG Lab'
})
</script>

<style scoped lang="scss">
.layout-container {
  display: flex;
  height: 100vh;
  background-color: #f0f2f5;
}

.sidebar {
  width: 220px;
  background-color: #001529;
  display: flex;
  flex-direction: column;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    img {
      width: 32px;
      height: 32px;
      margin-right: 8px;
    }
  }

  .sidebar-menu {
    border-right: none;
    background-color: #001529;

    :deep(.el-menu-item) {
      color: rgba(255, 255, 255, 0.65);

      &:hover,
      &.is-active {
        color: #fff;
        background-color: #1890ff;
      }
    }
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 60px;
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);

  .header-title {
    font-size: 16px;
    font-weight: 500;
    color: #303133;
  }

  .header-actions {
    display: flex;
    align-items: center;
  }
}

.content {
  flex: 1;
  overflow: auto;
  padding: 24px;
}
</style>
