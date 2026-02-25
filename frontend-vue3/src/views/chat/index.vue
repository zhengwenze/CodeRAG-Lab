<template>
  <div class="chat-page">
    <div class="chat-container">
      <div class="chat-messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="empty-state">
          <img src="/logo.svg" alt="CodeRAG" />
          <h2>CodeRAG Lab</h2>
          <p>可溯源代码库助手 - 开始您的智能问答之旅</p>
        </div>
        <div v-else class="message-list">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-avatar">
              <img v-if="msg.role === 'assistant'" src="/logo.svg" alt="AI" />
              <div v-else class="user-avatar">U</div>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(msg.content)"></div>
              <div v-if="msg.references && msg.references.length > 0" class="references">
                <div class="references-title">参考资料:</div>
                <div
                  v-for="(ref, refIndex) in msg.references"
                  :key="refIndex"
                  class="reference-item"
                >
                  <div class="ref-file">{{ ref.file_path }}</div>
                  <div class="ref-content">{{ ref.content }}</div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="loading" class="loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>AI 正在思考...</span>
          </div>
        </div>
      </div>
      <div class="chat-input">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题..."
            resize="none"
            @keydown.enter.ctrl="sendMessage"
          />
          <el-button
            type="primary"
            :loading="loading"
            @click="sendMessage"
            :disabled="!inputMessage.trim()"
          >
            <el-icon><Promotion /></el-icon>
            发送
          </el-button>
        </div>
        <div class="input-tips">
          <span>Ctrl + Enter 发送</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Promotion } from '@element-plus/icons-vue'
import { chat } from '@/api/chat'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesRef = ref(null)

const formatMessage = (content) => {
  return content.replace(/\n/g, '<br>')
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  messages.value.push({
    role: 'user',
    content: userMessage,
  })

  messages.value.push({
    role: 'assistant',
    content: '',
    references: [],
  })

  loading.value = true
  scrollToBottom()

  try {
    const response = await chat({
      messages: messages.value
        .filter((m) => m.role === 'user')
        .map((m) => ({ role: m.role, content: m.content })),
      stream: false,
      top_k: 5,
    })

    const lastMsg = messages.value[messages.value.length - 1]
    lastMsg.content = response.message || response.answer || '暂无回复'
    lastMsg.references = response.references || []
  } catch (error) {
    ElMessage.error(error.message || '请求失败')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}
</script>

<style scoped lang="scss">
.chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;

  img {
    width: 80px;
    height: 80px;
    margin-bottom: 20px;
  }

  h2 {
    font-size: 24px;
    margin-bottom: 10px;
    color: #303133;
  }
}

.message-list {
  max-width: 900px;
  margin: 0 auto;
}

.message {
  display: flex;
  margin-bottom: 20px;

  &.user {
    flex-direction: row-reverse;

    .message-content {
      background-color: #e6f4ff;
      border-color: #91d5ff;
    }

    .message-avatar {
      margin-left: 12px;
      margin-right: 0;
    }
  }
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  margin-right: 12px;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .user-avatar {
    width: 100%;
    height: 100%;
    background-color: #409eff;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }
}

.message-content {
  flex: 1;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  background-color: #fafafa;
}

.message-text {
  line-height: 1.6;
  word-break: break-word;
}

.references {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;

  .references-title {
    font-size: 12px;
    color: #909399;
    margin-bottom: 8px;
  }
}

.reference-item {
  padding: 8px;
  margin-bottom: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;

  .ref-file {
    color: #409eff;
    margin-bottom: 4px;
    font-weight: 500;
  }

  .ref-content {
    color: #606266;
    line-height: 1.5;
    max-height: 60px;
    overflow: hidden;
  }
}

.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  padding: 12px;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #ebeef5;
  background-color: #fff;
}

.input-container {
  display: flex;
  gap: 12px;

  :deep(.el-textarea) {
    flex: 1;
  }
}

.input-tips {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  text-align: right;
}
</style>
