<template>
  <el-drawer
    v-model="visible"
    :title="assistantName"
    direction="rtl"
    :size="drawerWidth"
    :before-close="handleClose"
    :destroy-on-close="true"
    class="ai-chat-drawer"
  >
    <div class="ai-chat-container">
      <!-- 头部信息 -->
      <div class="chat-header">
        <div class="assistant-info">
          <el-avatar :size="32" class="assistant-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </el-avatar>
          <div class="assistant-meta">
            <span class="assistant-name">{{ assistantName }}</span>
            <span class="assistant-status" :class="{ connected: !chat.isLoading.value }">
              {{ chat.isLoading.value ? '处理中...' : '已连接' }}
            </span>
          </div>
        </div>
        <div class="thread-actions">
          <el-button
            v-if="showThreadList"
            text
            @click="toggleThreadPanel"
          >
            <el-icon><List /></el-icon>
            对话列表
          </el-button>
          <el-button
            type="primary"
            size="small"
            :icon="Edit"
            @click="handleNewThread"
            :disabled="chat.isLoading.value"
          >
            新建对话
          </el-button>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="chat-main">
        <!-- 对话列表侧边栏 -->
        <div v-if="threadPanelVisible" class="thread-panel">
          <div class="thread-panel-header">
            <span>历史对话</span>
            <el-button text @click="threadPanelVisible = false">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          <div class="thread-list">
            <div
              v-for="thread in threads.threads.value"
              :key="thread.id"
              :class="['thread-item', { active: thread.id === chat.threadId.value }]"
              @click="handleSelectThread(thread)"
            >
              <div class="thread-title">{{ thread.title || '新对话' }}</div>
              <div class="thread-time">{{ formatTime(thread.updatedAt) }}</div>
              <el-badge v-if="thread.hasInterrupt" is-dot class="interrupt-badge" />
            </div>
            <el-empty v-if="!threads.threads.value.length" description="暂无历史对话" :image-size="60" />
          </div>
        </div>

        <!-- 消息区域 -->
        <div class="messages-area">
          <!-- 消息列表 -->
          <div class="messages-container" ref="messagesContainer">
            <div v-if="chat.messages.value.length === 0" class="empty-state">
              <div class="empty-icon">
                <el-icon :size="48"><ChatDotRound /></el-icon>
              </div>
              <h3>开始与 AI 对话</h3>
              <p>输入您的需求，AI 将帮助您生成测试用例、分析需求或缺陷</p>
              <div class="quick-actions" v-if="quickPrompts.length">
                <p class="quick-title">快速开始：</p>
                <div class="quick-buttons">
                  <el-button
                    v-for="(prompt, index) in quickPrompts"
                    :key="index"
                    size="small"
                    @click="sendQuickPrompt(prompt)"
                  >
                    {{ prompt.label }}
                  </el-button>
                </div>
              </div>
            </div>
            
            <!-- 消息列表 -->
            <template v-for="(message, index) in chat.messages.value" :key="message.id">
              <div :class="['message-item', message.type]">
                <div class="message-avatar">
                  <el-avatar v-if="message.type === 'human'" :icon="User" :size="32" />
                  <el-avatar v-else-if="message.type === 'ai'" class="ai-avatar" :size="32">
                    <el-icon><MagicStick /></el-icon>
                  </el-avatar>
                  <el-avatar v-else class="error-avatar" :size="32">
                    <el-icon><Warning /></el-icon>
                  </el-avatar>
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">{{ getSenderName(message.type) }}</span>
                    <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                  </div>
                  <div class="message-text" v-html="renderMarkdown(message.content)"></div>
                  
                  <!-- 工具调用展示 -->
                  <div v-if="message.toolCalls?.length" class="tool-calls">
                    <div v-for="(tool, ti) in message.toolCalls" :key="ti" class="tool-call-item">
                      <div class="tool-header">
                        <el-icon><Operation /></el-icon>
                        <span class="tool-name">{{ formatToolName(tool.name) }}</span>
                        <el-tag :type="getToolStatusType(tool.status)" size="small">
                          {{ getToolStatusLabel(tool.status) }}
                        </el-tag>
                      </div>
                      <div v-if="tool.args && Object.keys(tool.args).length" class="tool-args">
                        <details>
                          <summary>参数</summary>
                          <pre>{{ formatToolArgs(tool.args) }}</pre>
                        </details>
                      </div>
                      <div v-if="tool.result" class="tool-result">
                        <details>
                          <summary>结果</summary>
                          <pre>{{ formatToolResult(tool.result) }}</pre>
                        </details>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <!-- 加载中指示器 -->
            <div v-if="chat.isLoading.value" class="loading-indicator">
              <div class="typing-animation">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span class="loading-text">AI 正在思考中...</span>
            </div>
          </div>

          <!-- 任务/文件面板 -->
          <div v-if="chat.hasTodos.value || chat.hasFiles.value" class="meta-panel">
            <el-tabs v-model="activeMetaTab" type="border-card">
              <el-tab-pane v-if="chat.hasTodos.value" label="任务" name="tasks">
                <div class="todos-list">
                  <div v-for="status in ['in_progress', 'pending', 'completed']" :key="status" class="todo-group">
                    <template v-if="chat.groupedTodos.value[status]?.length">
                      <h4 class="todo-status-title">{{ getTodoStatusLabel(status) }}</h4>
                      <div v-for="todo in chat.groupedTodos.value[status]" :key="todo.id" class="todo-item">
                        <el-icon :class="['todo-icon', status]">
                          <component :is="getTodoIcon(status)" />
                        </el-icon>
                        <span>{{ todo.content }}</span>
                      </div>
                    </template>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane v-if="chat.hasFiles.value" label="文件" name="files">
                <div class="files-list">
                  <div v-for="(content, path) in chat.files.value" :key="path" class="file-item">
                    <el-icon><Document /></el-icon>
                    <span class="file-path">{{ path }}</span>
                    <el-button text size="small" @click="viewFile(path, content)">查看</el-button>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- 输入区域 -->
          <div class="input-container">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              placeholder="输入您的问题或需求... (Ctrl+Enter 发送)"
              :disabled="chat.isLoading.value"
              @keydown="handleKeydown"
              resize="none"
            />
            <div class="input-actions">
              <div class="input-tips">
                <el-checkbox v-model="useRag" size="small">使用知识库增强</el-checkbox>
              </div>
              <div class="input-buttons">
                <el-button
                  v-if="chat.isLoading.value"
                  type="danger"
                  :icon="VideoPause"
                  @click="chat.stopStream"
                >
                  停止
                </el-button>
                <el-button
                  v-else
                  type="primary"
                  :icon="Promotion"
                  @click="handleSend"
                  :disabled="!inputMessage.trim()"
                >
                  发送
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件查看对话框 -->
    <el-dialog v-model="fileDialogVisible" title="文件内容" width="70%">
      <div class="file-content">
        <div class="file-path-header">{{ currentFile.path }}</div>
        <pre class="file-code">{{ currentFile.content }}</pre>
      </div>
    </el-dialog>
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  ChatDotRound, User, MagicStick, Edit, Promotion, VideoPause, 
  Operation, Warning, List, Close, Document, Check, Loading, Clock
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useLangGraphChat, useLangGraphThreads } from '@/composables/useLangGraphChat'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  assistantId: { type: String, required: true },
  assistantName: { type: String, default: 'AI 助手' },
  initialPrompt: { type: String, default: '' },
  projectId: { type: Number, default: null },
  folderId: { type: Number, default: null },
  drawerWidth: { type: String, default: '65%' },
  showThreadList: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'message-sent', 'thread-created'])

// 抽屉可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 使用 LangGraph Chat Composable
const chat = useLangGraphChat({
  assistantId: props.assistantId,
  projectId: props.projectId,
  folderId: props.folderId,
  onTestCaseCreated: () => emit('message-sent', { created: true })
})

// 使用 Thread 列表 Composable
const threads = useLangGraphThreads({
  assistantId: props.assistantId
})

// 本地状态
const inputMessage = ref('')
const useRag = ref(false)
const messagesContainer = ref(null)
const threadPanelVisible = ref(false)
const activeMetaTab = ref('tasks')
const fileDialogVisible = ref(false)
const currentFile = ref({ path: '', content: '' })

// 快捷提示
const quickPrompts = computed(() => {
  const prompts = []
  if (props.assistantId.includes('testcase')) {
    prompts.push(
      { label: '生成登录功能测试用例', prompt: '请帮我生成用户登录功能的测试用例' },
      { label: '生成 BDD 测试用例', prompt: '请用 BDD 格式生成用户注册功能的测试用例' },
      { label: '批量生成用例', prompt: '请分析以下需求并生成完整的测试用例集' }
    )
  } else if (props.assistantId.includes('requirement')) {
    prompts.push(
      { label: '分析需求文档', prompt: '请分析以下需求文档，提取功能需求和非功能需求' },
      { label: '生成用户故事', prompt: '请将以下需求转换为用户故事格式' },
      { label: '评估需求质量', prompt: '请评估以下需求的完整性、清晰度和可测试性' }
    )
  } else if (props.assistantId.includes('defect')) {
    prompts.push(
      { label: '分析缺陷根因', prompt: '请分析以下缺陷的根本原因' },
      { label: '提供修复建议', prompt: '请针对以下缺陷提供修复建议和预防措施' },
      { label: '评估缺陷影响', prompt: '请分析以下缺陷的影响范围和严重程度' }
    )
  }
  return prompts
})

// 发送消息
const handleSend = async () => {
  const message = inputMessage.value.trim()
  if (!message) return
  
  inputMessage.value = ''
  await chat.sendMessage(message)
  scrollToBottom()
}

// 发送快捷提示
const sendQuickPrompt = (prompt) => {
  inputMessage.value = prompt.prompt
  handleSend()
}

// 新建对话
const handleNewThread = async () => {
  await chat.createThread()
  emit('thread-created', chat.threadId.value)
  ElMessage.success('已创建新对话')
}

// 切换对话列表面板
const toggleThreadPanel = () => {
  threadPanelVisible.value = !threadPanelVisible.value
  if (threadPanelVisible.value) {
    threads.fetchThreads()
  }
}

// 选择对话
const handleSelectThread = async (thread) => {
  await chat.loadThread(thread.id)
  threadPanelVisible.value = false
}

// 键盘事件
const handleKeydown = (e) => {
  if (e.key === 'Enter' && e.ctrlKey) {
    e.preventDefault()
    handleSend()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 关闭抽屉
const handleClose = (done) => {
  chat.stopStream()
  done()
}

// 查看文件
const viewFile = (path, content) => {
  currentFile.value = { path, content }
  fileDialogVisible.value = true
}

// 渲染 Markdown
const renderMarkdown = (text) => {
  if (!text) return ''
  try {
    return marked(text, { breaks: true, gfm: true })
  } catch (e) {
    return text.replace(/\n/g, '<br>')
  }
}

// 格式化工具名称
const formatToolName = (name) => {
  const nameMap = {
    'create_test_case': '创建测试用例',
    'update_test_case': '更新测试用例',
    'batch_create_test_cases': '批量创建测试用例',
    'rag_query': 'RAG 知识检索',
    'save_requirement_analysis': '保存需求分析',
    'save_defect_analysis': '保存缺陷分析',
    'generate_mindmap': '生成思维导图'
  }
  return nameMap[name] || name
}

// 格式化工具参数
const formatToolArgs = (args) => {
  try {
    return JSON.stringify(args, null, 2)
  } catch {
    return String(args)
  }
}

// 格式化工具结果
const formatToolResult = (result) => {
  if (typeof result === 'string') {
    try {
      return JSON.stringify(JSON.parse(result), null, 2)
    } catch {
      return result.length > 500 ? result.substring(0, 500) + '...' : result
    }
  }
  return JSON.stringify(result, null, 2)
}

// 工具状态
const getToolStatusType = (status) => {
  const map = { pending: 'info', running: 'warning', completed: 'success', error: 'danger', interrupted: 'warning' }
  return map[status] || 'info'
}

const getToolStatusLabel = (status) => {
  const map = { pending: '等待', running: '执行中', completed: '已完成', error: '失败', interrupted: '已中断' }
  return map[status] || status
}

// 消息发送者名称
const getSenderName = (type) => {
  const map = { human: '你', ai: 'AI 助手', error: '系统' }
  return map[type] || type
}

// TODO 状态
const getTodoStatusLabel = (status) => {
  const map = { in_progress: '进行中', pending: '待处理', completed: '已完成' }
  return map[status] || status
}

const getTodoIcon = (status) => {
  const map = { in_progress: Loading, pending: Clock, completed: Check }
  return map[status] || Clock
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 监听打开
watch(visible, (val) => {
  if (val) {
    if (!chat.threadId.value) {
      chat.createThread()
    }
    if (props.initialPrompt) {
      nextTick(() => {
        inputMessage.value = props.initialPrompt
        handleSend()
      })
    }
  }
})

// 监听消息变化，自动滚动
watch(() => chat.messages.value.length, scrollToBottom)
</script>

<style scoped lang="scss">
.ai-chat-drawer {
  :deep(.el-drawer__header) {
    margin-bottom: 0;
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
  }

  :deep(.el-drawer__body) {
    padding: 0;
    display: flex;
    flex-direction: column;
    height: calc(100% - 60px);
  }
}

.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f7fa;

  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: white;
    border-bottom: 1px solid #ebeef5;

    .assistant-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .assistant-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      .assistant-meta {
        display: flex;
        flex-direction: column;
        gap: 2px;

        .assistant-name { font-weight: 600; font-size: 14px; }
        .assistant-status {
          font-size: 12px;
          color: #909399;
          &.connected { color: #67c23a; }
        }
      }
    }

    .thread-actions {
      display: flex;
      gap: 8px;
    }
  }

  .chat-main {
    display: flex;
    flex: 1;
    overflow: hidden;

    .thread-panel {
      width: 260px;
      background: white;
      border-right: 1px solid #ebeef5;
      display: flex;
      flex-direction: column;

      .thread-panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid #ebeef5;
        font-weight: 500;
      }

      .thread-list {
        flex: 1;
        overflow-y: auto;
        padding: 8px;

        .thread-item {
          padding: 12px;
          border-radius: 6px;
          cursor: pointer;
          position: relative;
          margin-bottom: 4px;

          &:hover { background: #f5f7fa; }
          &.active { background: #ecf5ff; border: 1px solid #409eff; }

          .thread-title {
            font-size: 14px;
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .thread-time {
            font-size: 12px;
            color: #909399;
          }

          .interrupt-badge {
            position: absolute;
            top: 8px;
            right: 8px;
          }
        }
      }
    }

    .messages-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px;

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
      color: #909399;

      .empty-icon { margin-bottom: 16px; color: #c0c4cc; }
      h3 { margin: 0 0 8px; font-size: 18px; color: #606266; }
      p { margin: 0 0 24px; max-width: 400px; }

      .quick-actions {
        .quick-title { margin: 0 0 12px; font-size: 13px; }
        .quick-buttons { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
      }
    }

    .message-item {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;

      &.human {
        flex-direction: row-reverse;
        .message-content {
          align-items: flex-end;
          .message-text {
            background: #409eff;
            color: white;
            border-radius: 16px 16px 4px 16px;
          }
        }
      }

      &.ai {
        .message-content .message-text {
          background: white;
          border-radius: 16px 16px 16px 4px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        .ai-avatar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
      }

      &.error {
        .message-content .message-text {
          background: #fef0f0;
          color: #f56c6c;
          border-radius: 16px;
        }
        .error-avatar { background: #f56c6c; }
      }

      .message-content {
        display: flex;
        flex-direction: column;
        max-width: 75%;

        .message-header {
          display: flex;
          gap: 8px;
          margin-bottom: 4px;
          font-size: 12px;
          color: #909399;
          .sender-name { font-weight: 500; }
        }

        .message-text {
          padding: 12px 16px;
          line-height: 1.6;
          word-break: break-word;

          :deep(p) { margin: 0 0 8px; &:last-child { margin-bottom: 0; } }
          :deep(pre) { background: #f5f7fa; padding: 12px; border-radius: 4px; overflow-x: auto; margin: 8px 0; }
          :deep(code) { background: rgba(0, 0, 0, 0.06); padding: 2px 6px; border-radius: 4px; font-size: 13px; }
          :deep(ul), :deep(ol) { padding-left: 20px; margin: 8px 0; }
        }

        .tool-calls {
          margin-top: 12px;

          .tool-call-item {
            background: white;
            border: 1px solid #ebeef5;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;

            .tool-header {
              display: flex;
              align-items: center;
              gap: 8px;
              margin-bottom: 8px;
              .el-icon { color: #409eff; }
              .tool-name { font-weight: 500; flex: 1; }
            }

            .tool-args, .tool-result {
              margin-top: 8px;
              details {
                summary {
                  cursor: pointer;
                  font-size: 12px;
                  color: #909399;
                  margin-bottom: 4px;
                }
                pre {
                  background: #f5f7fa;
                  border-radius: 4px;
                  padding: 8px;
                  margin: 0;
                  font-size: 12px;
                  white-space: pre-wrap;
                  max-height: 150px;
                  overflow: auto;
                }
              }
            }
          }
        }
      }
    }

    .loading-indicator {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;

      .typing-animation {
        display: flex;
        gap: 4px;
        span {
          width: 8px;
          height: 8px;
          background: #409eff;
          border-radius: 50%;
          animation: typing 1.4s infinite ease-in-out both;
          &:nth-child(1) { animation-delay: -0.32s; }
          &:nth-child(2) { animation-delay: -0.16s; }
        }
      }
      .loading-text { color: #909399; font-size: 14px; }
    }
  }

  .meta-panel {
    padding: 0 16px 16px;
    max-height: 200px;

    .todos-list {
      .todo-group {
        margin-bottom: 12px;
        .todo-status-title { font-size: 12px; color: #909399; margin-bottom: 6px; }
        .todo-item {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          padding: 4px 0;
          font-size: 13px;
          .todo-icon {
            margin-top: 2px;
            &.in_progress { color: #e6a23c; }
            &.completed { color: #67c23a; }
            &.pending { color: #909399; }
          }
        }
      }
    }

    .files-list {
      .file-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px;
        border-radius: 4px;
        &:hover { background: #f5f7fa; }
        .file-path { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; }
      }
    }
  }

  .input-container {
    padding: 16px 20px;
    background: white;
    border-top: 1px solid #ebeef5;

    .el-textarea {
      margin-bottom: 12px;
      :deep(.el-textarea__inner) { border-radius: 8px; resize: none; }
    }

    .input-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      .input-tips { font-size: 12px; color: #909399; }
      .input-buttons { display: flex; gap: 8px; }
    }
  }
}

.file-content {
  .file-path-header {
    padding: 8px 12px;
    background: #f5f7fa;
    border-radius: 4px;
    font-family: monospace;
    margin-bottom: 12px;
  }
  .file-code {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 4px;
    overflow: auto;
    max-height: 500px;
    font-size: 13px;
  }
}

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
