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
          
          <!-- 状态筛选 -->
          <div class="thread-filters">
            <el-select v-model="threadStatusFilter" placeholder="筛选状态" size="small" style="width: 100%">
              <el-option label="全部对话" value="all">
                <span class="filter-option">全部对话</span>
              </el-option>
              <el-option label="进行中" value="busy">
                <span class="filter-option">
                  <span class="status-dot busy"></span>
                  进行中
                </span>
              </el-option>
              <el-option label="已完成" value="idle">
                <span class="filter-option">
                  <span class="status-dot idle"></span>
                  已完成
                </span>
              </el-option>
              <el-option label="需要关注" value="interrupted">
                <span class="filter-option">
                  <span class="status-dot interrupted"></span>
                  需要关注
                  <el-badge v-if="interruptedCount > 0" :value="interruptedCount" class="filter-badge" />
                </span>
              </el-option>
              <el-option label="错误" value="error">
                <span class="filter-option">
                  <span class="status-dot error"></span>
                  错误
                </span>
              </el-option>
            </el-select>
          </div>
          
          <div class="thread-list">
            <div
              v-for="thread in filteredThreadList"
              :key="thread.id"
              :class="['thread-item', { active: thread.id === chat.threadId.value }]"
              @click="handleSelectThread(thread)"
            >
              <div class="thread-header">
                <span :class="['status-indicator', thread.status]"></span>
                <div class="thread-title">{{ thread.title || '新对话' }}</div>
                <el-dropdown trigger="click" @command="(cmd) => handleThreadAction(cmd, thread)">
                  <el-button text size="small" class="thread-menu">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="delete">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              <div class="thread-meta">
                <span class="thread-time">{{ formatThreadTime(thread.updatedAt) }}</span>
                <el-tag v-if="thread.status" :type="getStatusTagType(thread.status)" size="small">
                  {{ getStatusLabel(thread.status) }}
                </el-tag>
              </div>
              <el-badge v-if="thread.hasInterrupt" is-dot class="interrupt-badge" />
            </div>
            <el-empty v-if="!filteredThreadList.length" description="暂无对话" :image-size="60" />
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
            <!-- 已上传文件预览 -->
            <div v-if="uploadedFiles.length > 0" class="uploaded-files-preview">
              <div v-for="(file, index) in uploadedFiles" :key="index" class="uploaded-file-item">
                <el-icon class="file-icon"><Document /></el-icon>
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
                <el-button text size="small" @click="removeFile(index)" class="remove-file">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </div>
            
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
                <!-- 文件上传按钮 - 优化版 -->
                <el-upload
                  ref="uploadRef"
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleFileChange"
                  :accept="acceptedFileTypes"
                  multiple
                  class="file-upload-btn"
                >
                  <el-button text size="small" class="upload-trigger">
                    <el-icon><Paperclip /></el-icon>
                    <span>上传文件</span>
                  </el-button>
                </el-upload>
                
                <!-- RAG知识库选择 - 优化版 -->
                <el-select 
                  v-model="selectedKnowledgeBase" 
                  placeholder="选择知识库" 
                  size="small" 
                  clearable
                  filterable
                  :loading="knowledgeBasesLoading"
                  class="knowledge-base-select"
                >
                  <template #prefix>
                    <el-icon><FolderOpened /></el-icon>
                  </template>
                  <el-option
                    v-for="kb in knowledgeBases"
                    :key="kb.id"
                    :label="kb.name"
                    :value="kb.id"
                    class="knowledge-base-option"
                  >
                    <div class="kb-option-content">
                      <div class="kb-option-header">
                        <el-icon class="kb-icon"><Collection /></el-icon>
                        <span class="kb-name">{{ kb.name }}</span>
                        <el-tag :type="getQueryModeTagType(kb.queryMode)" size="small">
                          {{ kb.queryMode || 'mix' }}
                        </el-tag>
                      </div>
                      <div class="kb-option-footer">
                        <span class="kb-project">{{ kb.projectName || '未知项目' }}</span>
                        <span class="kb-stats">
                          <el-icon><Document /></el-icon>
                          {{ kb.docCount }} 文档
                        </span>
                      </div>
                    </div>
                  </el-option>
                  <template #empty>
                    <div class="kb-empty">
                      <el-icon :size="32"><FolderDelete /></el-icon>
                      <p>暂无可用知识库</p>
                      <el-button text type="primary" size="small" @click="goToKnowledgeManagement">
                        去创建知识库
                      </el-button>
                    </div>
                  </template>
                </el-select>
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
                  :disabled="!inputMessage.trim() && uploadedFiles.length === 0"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ChatDotRound, User, MagicStick, Edit, Promotion, VideoPause, 
  Operation, Warning, List, Close, Document, Check, Loading, Clock,
  Paperclip, Delete, MoreFilled, FolderOpened, Collection, FolderDelete
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useLangGraphSDK } from '@/composables/useLangGraphSDK'

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

// 验证 projectId（对于需求分析和缺陷分析是必需的）
const requiresProjectId = computed(() => {
  return props.assistantId.includes('requirement') || props.assistantId.includes('defect') || props.assistantId.includes('testcase')
})

const validProjectId = computed(() => {
  const result = props.projectId && props.projectId !== 0 && props.projectId !== '0' && props.projectId !== null && props.projectId !== undefined
  console.log('[AIChatDrawer] validProjectId computed:', {
    'props.projectId': props.projectId,
    'result': result
  })
  return result
})

// 监听 props.projectId 的变化
watch(() => props.projectId, (newVal, oldVal) => {
  console.log('[AIChatDrawer] 🔄 props.projectId 变化:', {
    旧值: oldVal,
    新值: newVal,
    'validProjectId': validProjectId.value
  })
}, { immediate: true })

// 使用 LangGraph SDK Composable（直接连接 LangGraph API）
const chat = useLangGraphSDK({
  assistantId: props.assistantId,
  projectId: computed(() => {
    const id = validProjectId.value ? props.projectId : null
    console.log('[AIChatDrawer] projectId computed:', {
      'props.projectId': props.projectId,
      'validProjectId': validProjectId.value,
      '返回值': id
    })
    return id
  }),
  folderId: props.folderId,
  templateType: computed(() => {
    // 根据 assistantId 确定模板类型
    if (props.assistantId.includes('testcase')) {
      return 'test_case'
    } else if (props.assistantId.includes('requirement')) {
      return 'requirement_analysis'
    } else if (props.assistantId.includes('defect')) {
      return 'defect_analysis'
    }
    return null
  }),
  onTestCaseCreated: () => emit('message-sent', { created: true }),
  onHistoryRevalidate: () => fetchThreadList()
})

// 本地状态
const inputMessage = ref('')
const useRag = ref(false)
const messagesContainer = ref(null)
const threadPanelVisible = ref(false)
const activeMetaTab = ref('tasks')
const fileDialogVisible = ref(false)
const currentFile = ref({ path: '', content: '' })
const threadList = ref([])
const initialPromptSent = ref(false)

// 新增：文件上传相关
const uploadedFiles = ref([])
const uploadRef = ref(null)
const acceptedFileTypes = '.pdf,.doc,.docx,.txt,.md,.png,.jpg,.jpeg,.gif,.xlsx,.xls,.csv'

// 新增：知识库选择（真实数据）
const selectedKnowledgeBase = ref(null)
const knowledgeBases = ref([])
const knowledgeBasesLoading = ref(false)

// 加载真实的知识库列表
async function loadKnowledgeBases() {
  knowledgeBasesLoading.value = true
  try {
    // 导入knowledge API
    const { listKnowledge } = await import('@/api/testing/knowledge')
    
    console.log('🔍 开始加载知识库列表, projectId:', props.projectId)
    
    const response = await listKnowledge({
      pageNum: 1,
      pageSize: 100,  // 获取所有启用的知识库
      status: '0',  // 只获取启用的
      projectId: props.projectId  // 如果有项目ID限制
    })
    
    console.log('📡 API响应:', response)
    
    // 后端返回格式: {code: 200, data: {rows: [...], total: ...}}
    // 经过axios拦截器后返回: {rows: [...], total: ...}
    const rows = response.rows || response.data?.rows || []
    
    console.log('📋 原始数据行数:', rows.length)
    
    knowledgeBases.value = rows.map(kb => {
      console.log('📚 处理知识库:', kb.knowledge_name, 'project:', kb.project_name)
      return {
        id: kb.knowledge_id,
        name: kb.knowledge_name,
        docCount: kb.file_count || 0,
        workspace: kb.collection_name,  // LightRAG workspace名称
        projectId: kb.project_id,
        projectName: kb.project_name || '未知项目',
        queryMode: kb.query_mode || 'mix'
      }
    })
    
    console.log('✅ 知识库列表加载成功:', knowledgeBases.value.length, '个知识库')
    if (knowledgeBases.value.length > 0) {
      console.log('📊 第一个知识库:', knowledgeBases.value[0])
    } else {
      console.warn('⚠️ 没有可用的知识库')
      ElMessage.warning('当前项目没有可用的知识库，请先在知识库管理中创建和上传文档')
    }
  } catch (error) {
    console.error('❌ 加载知识库列表失败:', error)
    ElMessage.error('加载知识库列表失败: ' + (error.message || '未知错误'))
  } finally {
    knowledgeBasesLoading.value = false
  }
}

// 新增：对话列表筛选
const threadStatusFilter = ref('all')
const interruptedCount = computed(() => {
  return threadList.value.filter(t => t.status === 'interrupted').length
})

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

// 获取线程列表
const fetchThreadList = async () => {
  try {
    const list = await chat.listThreads(20)
    // 模拟添加状态信息（实际应从后端获取）
    threadList.value = list.map(thread => ({
      ...thread,
      status: thread.hasInterrupt ? 'interrupted' : (thread.isActive ? 'busy' : 'idle')
    }))
  } catch (e) {
    console.error('获取线程列表失败:', e)
  }
}

// 筛选后的对话列表
const filteredThreadList = computed(() => {
  if (threadStatusFilter.value === 'all') {
    return threadList.value
  }
  return threadList.value.filter(t => t.status === threadStatusFilter.value)
})

// 文件上传处理
const handleFileChange = (file) => {
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.warning('文件大小不能超过10MB')
    return
  }
  uploadedFiles.value.push(file)
  ElMessage.success(`已添加文件: ${file.name}`)
}

// 移除文件
const removeFile = (index) => {
  const file = uploadedFiles.value[index]
  uploadedFiles.value.splice(index, 1)
  ElMessage.info(`已移除文件: ${file.name}`)
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 对话操作
const handleThreadAction = async (command, thread) => {
  if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确认删除此对话?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      // 调用删除API
      await chat.deleteThread(thread.id)
      ElMessage.success('已删除对话')
      await fetchThreadList()
    } catch (e) {
      if (e !== 'cancel') {
        console.error('删除对话失败:', e)
      }
    }
  }
}

// 状态标签类型
const getStatusTagType = (status) => {
  const map = {
    idle: 'success',
    busy: 'primary',
    interrupted: 'warning',
    error: 'danger'
  }
  return map[status] || 'info'
}

// 状态标签文本
const getStatusLabel = (status) => {
  const map = {
    idle: '已完成',
    busy: '进行中',
    interrupted: '需要关注',
    error: '错误'
  }
  return map[status] || status
}

// 获取查询模式标签类型
const getQueryModeTagType = (mode) => {
  const map = {
    mix: 'success',
    hybrid: 'primary',
    local: 'warning',
    global: 'info',
    naive: '',
    bypass: 'danger'
  }
  return map[mode] || ''
}

// 跳转到知识库管理
const goToKnowledgeManagement = () => {
  window.open('/#/testing/knowledge/index', '_blank')
  visible.value = false
}

// 格式化对话时间
const formatThreadTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }
}

// 发送消息
const handleSend = async () => {
  const message = inputMessage.value.trim()
  if (!message && uploadedFiles.value.length === 0) return
  
  // 验证 projectId（对于需求分析和缺陷分析是必需的）
  if (requiresProjectId.value && !validProjectId.value) {
    ElMessage.warning('请先选择项目！需求分析和缺陷分析功能需要指定项目ID。')
    return
  }
  
  // 构建消息内容
  let messageContent = message
  
  // 如果有上传文件，添加文件信息
  if (uploadedFiles.value.length > 0) {
    const fileInfo = uploadedFiles.value.map(f => `[文件: ${f.name}]`).join('\n')
    messageContent = `${fileInfo}\n\n${message}`
  }
  
  // 如果选择了知识库，添加RAG标记
  if (selectedKnowledgeBase.value) {
    const kb = knowledgeBases.value.find(k => k.id === selectedKnowledgeBase.value)
    messageContent = `[使用知识库: ${kb?.name}]\n\n${messageContent}`
  }
  
  inputMessage.value = ''
  const files = [...uploadedFiles.value]
  uploadedFiles.value = []
  
  try {
    // 发送消息（包含文件和RAG信息）
    await chat.sendMessage(messageContent, {
      files: files,
      knowledgeBaseId: selectedKnowledgeBase.value
    })
    scrollToBottom()
  } catch (err) {
    console.error('发送消息失败:', err)
    ElMessage.error(err.message || '发送消息失败，请检查项目ID是否正确')
    // 恢复文件列表
    uploadedFiles.value = files
  }
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
    fetchThreadList()
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
    'generate_mindmap': '生成思维导图',
    'parse_document_from_url': '解析文档内容'
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
watch(visible, async (val) => {
  if (val) {
    // 加载知识库列表
    await loadKnowledgeBases()
    
    // 验证 projectId（对于需求分析和缺陷分析是必需的）
    if (requiresProjectId.value && !validProjectId.value) {
      ElMessage.warning('请先选择项目！需求分析和缺陷分析功能需要指定项目ID。')
      // 延迟关闭抽屉，让用户看到提示
      setTimeout(() => {
        visible.value = false
      }, 2000)
      return
    }
    
    // 等待一个 tick，确保 props.initialPrompt 已经更新
    await nextTick()
    
    // 如果有新的初始提示词，强制创建新线程
    if (props.initialPrompt && props.initialPrompt.trim()) {
      console.log('[AIChatDrawer] 检测到初始提示词，准备发送:', props.initialPrompt.substring(0, 100) + '...')
      // 创建新线程，确保每次从文档生成都是新对话
      await chat.createThread()
      initialPromptSent.value = false
      
      // 发送初始提示词
      await nextTick()
      inputMessage.value = props.initialPrompt
      initialPromptSent.value = true
      // 延迟发送，确保组件完全初始化
      setTimeout(() => {
        console.log('[AIChatDrawer] 发送初始提示词')
        handleSend()
      }, 300)
    } else {
      // 没有初始提示词时，如果还没有线程，创建新线程
      if (!chat.threadId.value) {
        await chat.createThread()
      }
    }
  } else {
    // 关闭时重置状态
    initialPromptSent.value = false
  }
})

// 监听初始提示词变化（当从外部传入新的提示词时）
watch(() => props.initialPrompt, async (newVal, oldVal) => {
  console.log('[AIChatDrawer] initialPrompt 变化:', {
    oldVal: oldVal?.substring(0, 50) + '...',
    newVal: newVal?.substring(0, 50) + '...',
    visible: visible.value,
    hasContent: newVal && newVal.trim(),
    isDifferent: newVal !== oldVal
  })
  
  // 如果抽屉已打开，且有新的提示词（且与旧的不同），创建新线程并发送
  if (visible.value && newVal && newVal.trim() && newVal !== oldVal) {
    // 验证 projectId（对于需求分析和缺陷分析是必需的）
    if (requiresProjectId.value && !validProjectId.value) {
      ElMessage.warning('请先选择项目！需求分析和缺陷分析功能需要指定项目ID。')
      return
    }
    
    console.log('[AIChatDrawer] 抽屉已打开且有新提示词，创建新线程并发送')
    await chat.createThread()
    initialPromptSent.value = false
    await nextTick()
    inputMessage.value = newVal
    initialPromptSent.value = true
    setTimeout(() => {
      console.log('[AIChatDrawer] 发送更新的初始提示词')
      handleSend()
    }, 300)
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

      .thread-filters {
        padding: 8px 12px;
        border-bottom: 1px solid #ebeef5;
        
        .filter-option {
          display: flex;
          align-items: center;
          gap: 6px;
          
          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            
            &.idle { background: #67c23a; }
            &.busy { background: #409eff; }
            &.interrupted { background: #e6a23c; }
            &.error { background: #f56c6c; }
          }
          
          .filter-badge {
            margin-left: auto;
          }
        }
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
          border: 1px solid transparent;

          &:hover { 
            background: #f5f7fa;
            .thread-menu {
              opacity: 1;
            }
          }
          &.active { background: #ecf5ff; border-color: #409eff; }

          .thread-header {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 6px;
            
            .status-indicator {
              width: 8px;
              height: 8px;
              border-radius: 50%;
              margin-top: 4px;
              flex-shrink: 0;
              
              &.idle { background: #67c23a; }
              &.busy { background: #409eff; }
              &.interrupted { background: #e6a23c; }
              &.error { background: #f56c6c; }
            }
            
            .thread-title {
              flex: 1;
              font-size: 14px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
              line-height: 1.4;
            }
            
            .thread-menu {
              opacity: 0;
              transition: opacity 0.2s;
              padding: 2px;
            }
          }

          .thread-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-left: 16px;
            
            .thread-time {
              font-size: 12px;
              color: #909399;
            }
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
          padding: 10px 14px;
          line-height: 1.6;
          word-break: break-word;
          font-size: 14px;

          :deep(p) { 
            margin: 0 0 6px; 
            font-size: 14px;
            &:last-child { margin-bottom: 0; } 
          }
          :deep(h1) { font-size: 20px; margin: 12px 0 8px; font-weight: 600; }
          :deep(h2) { font-size: 18px; margin: 10px 0 6px; font-weight: 600; }
          :deep(h3) { font-size: 16px; margin: 8px 0 4px; font-weight: 600; }
          :deep(h4) { font-size: 15px; margin: 6px 0 4px; font-weight: 500; }
          :deep(pre) { 
            background: #f5f7fa; 
            padding: 10px; 
            border-radius: 4px; 
            overflow-x: auto; 
            margin: 6px 0; 
            font-size: 13px;
          }
          :deep(code) { 
            background: rgba(0, 0, 0, 0.06); 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-size: 13px; 
            font-family: 'Courier New', monospace;
          }
          :deep(ul), :deep(ol) { 
            padding-left: 20px; 
            margin: 6px 0; 
            font-size: 14px;
          }
          :deep(li) {
            margin: 4px 0;
            font-size: 14px;
          }
          :deep(blockquote) {
            border-left: 3px solid #409eff;
            padding-left: 12px;
            margin: 8px 0;
            color: #606266;
            font-style: italic;
          }
          :deep(strong) {
            font-weight: 600;
            color: #303133;
          }
          :deep(em) {
            font-style: italic;
            color: #606266;
          }
          :deep(a) {
            color: #409eff;
            text-decoration: none;
            &:hover {
              text-decoration: underline;
            }
          }
          :deep(table) {
            width: 100%;
            border-collapse: collapse;
            margin: 8px 0;
            font-size: 13px;
            th, td {
              border: 1px solid #ebeef5;
              padding: 6px 10px;
              text-align: left;
            }
            th {
              background: #f5f7fa;
              font-weight: 600;
            }
          }
          :deep(img) {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin: 8px 0;
          }
          // 支持emoji和特殊字符
          :deep(.emoji) {
            font-size: 18px;
            vertical-align: middle;
            margin: 0 2px;
          }
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

    .uploaded-files-preview {
      margin-bottom: 12px;
      padding: 8px;
      background: #f5f7fa;
      border-radius: 6px;
      max-height: 120px;
      overflow-y: auto;
      
      .uploaded-file-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 8px;
        background: white;
        border-radius: 4px;
        margin-bottom: 4px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .file-icon {
          color: #409eff;
          font-size: 16px;
        }
        
        .file-name {
          flex: 1;
          font-size: 13px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .file-size {
          font-size: 12px;
          color: #909399;
        }
        
        .remove-file {
          padding: 2px;
          &:hover {
            color: #f56c6c;
          }
        }
      }
    }

    .el-textarea {
      margin-bottom: 12px;
      :deep(.el-textarea__inner) { border-radius: 8px; resize: none; }
    }

    .input-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .input-tips { 
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #909399;
      }
      
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

// 知识库选择器样式优化
.knowledge-base-select {
  width: 240px !important;
  margin-left: 8px;
  
  :deep(.el-input__wrapper) {
    border-radius: 6px;
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 0 0 1px #409eff inset;
    }
  }
  
  :deep(.el-input__prefix) {
    color: #409eff;
  }
}

.knowledge-base-option {
  height: auto !important;
  padding: 0 !important;
  
  .kb-option-content {
    padding: 10px 12px;
    
    .kb-option-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
      
      .kb-icon {
        color: #409eff;
        font-size: 16px;
      }
      
      .kb-name {
        flex: 1;
        font-weight: 500;
        font-size: 14px;
        color: #303133;
      }
      
      .el-tag {
        font-size: 11px;
        height: 20px;
        line-height: 18px;
        padding: 0 6px;
        text-transform: uppercase;
      }
    }
    
    .kb-option-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: #909399;
      
      .kb-project {
        display: flex;
        align-items: center;
        gap: 4px;
        
        &:before {
          content: '📁';
          font-size: 12px;
        }
      }
      
      .kb-stats {
        display: flex;
        align-items: center;
        gap: 4px;
        
        .el-icon {
          font-size: 12px;
        }
      }
    }
  }
  
  &:hover .kb-option-content {
    background: #f5f7fa;
  }
}

.kb-empty {
  text-align: center;
  padding: 30px 20px;
  
  .el-icon {
    color: #c0c4cc;
    margin-bottom: 12px;
  }
  
  p {
    color: #909399;
    font-size: 14px;
    margin: 8px 0 16px;
  }
}

// 文件上传按钮优化
.file-upload-btn {
  .upload-trigger {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border-radius: 6px;
    transition: all 0.3s ease;
    
    &:hover {
      background: #ecf5ff;
      color: #409eff;
    }
    
    .el-icon {
      font-size: 14px;
    }
    
    span {
      font-size: 13px;
    }
  }
}

// 已上传文件预览优化
.uploaded-files-preview {
  margin-bottom: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  
  .uploaded-file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    background: white;
    border-radius: 4px;
    margin-bottom: 6px;
    transition: all 0.2s ease;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .file-icon {
      color: #409eff;
      font-size: 16px;
    }
    
    .file-name {
      flex: 1;
      font-size: 13px;
      color: #303133;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .file-size {
      font-size: 12px;
      color: #909399;
    }
    
    .remove-file {
      padding: 4px;
      
      .el-icon {
        font-size: 14px;
        color: #f56c6c;
      }
      
      &:hover .el-icon {
        color: #f56c6c;
      }
    }
  }
}
</style>
