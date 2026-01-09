/**
 * LangGraph SDK Composable
 * 完全复用 ai-test-management 项目的实现思路
 * 直接使用 LangGraph SDK 连接 LangGraph API
 * 
 * 参照: ai-test-management/ui/hooks/useChat.ts
 */
import { ref, computed, onUnmounted, watch } from 'vue'
import { Client } from '@langchain/langgraph-sdk'
import { v4 as uuidv4 } from 'uuid'

// LangGraph 配置
const LANGGRAPH_CONFIG = {
  // LangGraph API 地址（本地开发环境，端口 2027）
  apiUrl: import.meta.env?.VITE_LANGGRAPH_API_URL || 'http://localhost:2027',
  // API Key（如果需要）
  apiKey: import.meta.env?.VITE_LANGGRAPH_API_KEY || '',
  // 默认的智能体配置
  agents: {
    testcase_generator_agent: {
      name: 'testcase_generator_agent',
      graphId: 'testcase_generator_agent',
      description: '智能生成测试用例'
    },
    requirement_analyzer_agent: {
      name: 'requirement_analyzer_agent',
      graphId: 'requirement_analyzer_agent',
      description: '智能分析需求文档'
    },
    defect_analyzer_agent: {
      name: 'defect_analyzer_agent',
      graphId: 'defect_analyzer_agent',
      description: '智能分析缺陷报告'
    }
  }
}

/**
 * 创建 LangGraph Client
 */
function createLangGraphClient() {
  return new Client({
    apiUrl: LANGGRAPH_CONFIG.apiUrl,
    defaultHeaders: {
      'Content-Type': 'application/json',
      ...(LANGGRAPH_CONFIG.apiKey ? { 'X-Api-Key': LANGGRAPH_CONFIG.apiKey } : {})
    }
  })
}

/**
 * LangGraph SDK Chat Composable
 * 直接使用 LangGraph SDK 与 Agent 通信
 * 
 * @param {Object} options 配置选项
 * @param {string} options.assistantId - Assistant ID
 * @param {number} options.projectId - 项目 ID
 * @param {number} options.folderId - 文件夹 ID
 * @param {string} options.templateType - 模板类型
 * @param {Function} options.onTestCaseCreated - 测试用例创建回调
 * @param {Function} options.onHistoryRevalidate - 历史更新回调
 */
export function useLangGraphSDK(options = {}) {
  const { 
    assistantId, 
    projectId, 
    folderId, 
    templateType = 'test_case',
    onTestCaseCreated, 
    onHistoryRevalidate 
  } = options
  
  // LangGraph Client
  const client = createLangGraphClient()
  
  // 状态
  const threadId = ref(null)
  const messages = ref([])
  const todos = ref([])
  const files = ref({})
  const isLoading = ref(false)
  const isThreadLoading = ref(false)
  const interrupt = ref(null)
  const error = ref(null)
  const currentAssistant = ref(null)
  
  // 用于取消流式请求
  let abortController = null
  
  // 计算属性
  const hasInterrupt = computed(() => interrupt.value !== null)
  const hasTodos = computed(() => todos.value.length > 0)
  const hasFiles = computed(() => Object.keys(files.value).length > 0)
  
  // 分组的 todos
  const groupedTodos = computed(() => ({
    in_progress: todos.value.filter(t => t.status === 'in_progress'),
    pending: todos.value.filter(t => t.status === 'pending'),
    completed: todos.value.filter(t => t.status === 'completed')
  }))
  
  /**
   * 初始化 Assistant
   */
  async function initAssistant() {
    if (!assistantId) return null
    
    try {
      // 尝试获取或创建 Assistant
      const assistants = await client.assistants.search({ graphId: assistantId })
      
      if (assistants && assistants.length > 0) {
        currentAssistant.value = assistants[0]
        return assistants[0]
      }
      
      // 如果不存在，创建一个
      const newAssistant = await client.assistants.create({
        graphId: assistantId,
        config: {
          configurable: {
            project_identifier: String(projectId || ''),
            folder_id: String(folderId || ''),
            template_type: templateType
          }
        }
      })
      
      currentAssistant.value = newAssistant
      return newAssistant
    } catch (e) {
      console.error('初始化 Assistant 失败:', e)
      // 使用默认配置
      currentAssistant.value = {
        assistant_id: assistantId,
        graph_id: assistantId,
        config: {
          configurable: {
            project_identifier: String(projectId || ''),
            folder_id: String(folderId || ''),
            template_type: templateType
          }
        }
      }
      return currentAssistant.value
    }
  }
  
  /**
   * 创建新的对话线程
   */
  async function createThread(metadata = {}) {
    try {
      const thread = await client.threads.create({
        metadata: {
          assistantId,
          projectId,
          folderId,
          ...metadata
        }
      })
      
      threadId.value = thread.thread_id
      messages.value = []
      todos.value = []
      files.value = {}
      interrupt.value = null
      error.value = null
      
      onHistoryRevalidate?.()
      
      return thread.thread_id
    } catch (e) {
      console.error('创建线程失败:', e)
      // 使用本地生成的 ID
      const localId = `thread_${uuidv4()}`
      threadId.value = localId
      messages.value = []
      todos.value = []
      files.value = {}
      interrupt.value = null
      error.value = null
      return localId
    }
  }
  
  /**
   * 发送消息（流式响应）
   * @param {string} content 消息内容
   */
  async function sendMessage(content) {
    if (!content?.trim() || isLoading.value) return
    
    // 确保有 threadId
    if (!threadId.value) {
      await createThread()
    }
    
    // 确保有 assistant
    if (!currentAssistant.value) {
      await initAssistant()
    }
    
    // 添加用户消息
    const userMessage = {
      id: uuidv4(),
      type: 'human',
      content: content.trim(),
      timestamp: new Date().toISOString()
    }
    messages.value.push(userMessage)
    
    isLoading.value = true
    error.value = null
    
    // 创建 AbortController
    abortController = new AbortController()
    
    // 添加 AI 消息占位
    const aiMessage = {
      id: uuidv4(),
      type: 'ai',
      content: '',
      toolCalls: [],
      timestamp: new Date().toISOString()
    }
    messages.value.push(aiMessage)
    
    try {
      // 构建输入
      const input = {
        messages: [{
          id: uuidv4(),
          type: 'human',
          content: content.trim()
        }],
        context: {
          project_identifier: String(projectId || ''),
          folder_id: String(folderId || ''),
          template_type: templateType
        }
      }
      
      // 使用流式 API
      const streamResponse = client.runs.stream(
        threadId.value,
        currentAssistant.value?.assistant_id || assistantId,
        {
          input,
          config: {
            ...(currentAssistant.value?.config || {}),
            recursion_limit: 100
          },
          streamMode: 'messages'
        }
      )
      
      // 处理流式响应
      for await (const chunk of streamResponse) {
        if (abortController?.signal.aborted) break
        
        handleStreamChunk(chunk, aiMessage)
      }
      
      // 完成后触发回调
      onTestCaseCreated?.()
      onHistoryRevalidate?.()
      
    } catch (e) {
      if (e.name !== 'AbortError') {
        console.error('发送消息失败:', e)
        error.value = e.message
        
        // 更新 AI 消息为错误状态
        aiMessage.content = `发送失败: ${e.message}`
        aiMessage.type = 'error'
      }
    } finally {
      isLoading.value = false
      abortController = null
    }
  }
  
  /**
   * 处理流式数据块
   * 参照 ai-test-management 项目的数据格式
   */
  function handleStreamChunk(chunk, aiMessage) {
    try {
      // chunk 可能是不同格式：{ event, data } 或直接是数据对象
      let event = chunk.event || chunk.type
      let data = chunk.data || chunk
      
      console.log('[Stream] 收到数据:', event, data)
      
      // 处理消息事件
      if (event === 'messages/partial' || event === 'messages/complete' || event === 'messages') {
        processMessageData(data, aiMessage)
        return
      }
      
      // 处理 metadata 事件
      if (event === 'metadata') {
        // metadata 事件通常包含 thread_id 等信息，可以忽略
        return
      }
      
      // 处理 values 事件
      if (event === 'values') {
        if (data) {
          if (data.todos) todos.value = data.todos
          if (data.files) files.value = data.files
          // 也可能包含消息
          if (data.messages) {
            processMessageData(data.messages, aiMessage)
          }
        }
        return
      }
      
      // 处理 error 事件
      if (event === 'error') {
        error.value = data?.message || data?.error || '未知错误'
        return
      }
      
      // 处理 interrupt 事件
      if (event === 'interrupt') {
        interrupt.value = data
        return
      }
      
      // 处理 end 事件
      if (event === 'end' || event === 'done') {
        return
      }
      
      // 如果没有 event，尝试直接解析 data
      if (!event && data) {
        // 可能是直接的消息数组
        if (Array.isArray(data)) {
          processMessageData(data, aiMessage)
        } else if (data.messages) {
          processMessageData(data.messages, aiMessage)
        } else if (data.content !== undefined) {
          processMessageData([data], aiMessage)
        }
      }
      
    } catch (e) {
      console.error('处理流式数据失败:', e, chunk)
    }
  }
  
  /**
   * 处理消息数据
   */
  function processMessageData(data, aiMessage) {
    if (!data) return
    
    const msgArray = Array.isArray(data) ? data : [data]
    
    for (const msg of msgArray) {
      if (!msg) continue
      
      // 跳过 human 消息
      if (msg.type === 'human' || msg.role === 'user') continue
      
      // 提取内容
      let content = ''
      if (typeof msg.content === 'string') {
        content = msg.content
      } else if (Array.isArray(msg.content)) {
        // 可能是 [{ type: 'text', text: '...' }] 格式
        content = msg.content
          .filter(c => c.type === 'text' || !c.type)
          .map(c => c.text || c.content || '')
          .join('')
        
        // 处理工具调用块
        const toolUseBlocks = msg.content.filter(c => c.type === 'tool_use')
        toolUseBlocks.forEach(tb => {
          const existingTC = aiMessage.toolCalls.find(tc => tc.id === tb.id)
          if (!existingTC) {
            aiMessage.toolCalls.push({
              id: tb.id || `tool_${Date.now()}`,
              name: tb.name,
              args: tb.input || {},
              status: 'running'
            })
          }
        })
      }
      
      // 更新 AI 消息内容
      if (content && msg.type !== 'tool') {
        aiMessage.content = content
      }
      
      // 处理 tool_calls
      if (msg.tool_calls && Array.isArray(msg.tool_calls)) {
        msg.tool_calls.forEach(tc => {
          const existingTC = aiMessage.toolCalls.find(t => t.id === tc.id)
          if (existingTC) {
            existingTC.args = tc.args || existingTC.args
            existingTC.name = tc.name || existingTC.name
          } else {
            aiMessage.toolCalls.push({
              id: tc.id || `tool_${Date.now()}`,
              name: tc.name,
              args: tc.args || {},
              status: 'running'
            })
          }
        })
      }
      
      // 处理 additional_kwargs 中的 tool_calls
      if (msg.additional_kwargs?.tool_calls) {
        msg.additional_kwargs.tool_calls.forEach(tc => {
          const existingTC = aiMessage.toolCalls.find(t => t.id === tc.id)
          if (existingTC) {
            existingTC.args = tc.function?.arguments 
              ? JSON.parse(tc.function.arguments) 
              : existingTC.args
          } else {
            aiMessage.toolCalls.push({
              id: tc.id || `tool_${Date.now()}`,
              name: tc.function?.name || tc.name,
              args: tc.function?.arguments 
                ? JSON.parse(tc.function.arguments) 
                : (tc.args || {}),
              status: 'running'
            })
          }
        })
      }
      
      // 处理工具结果消息
      if (msg.type === 'tool') {
        const toolCallId = msg.tool_call_id
        const tc = aiMessage.toolCalls.find(t => t.id === toolCallId)
        if (tc) {
          tc.status = 'completed'
          tc.result = msg.content
        }
      }
      
      // 处理 response_metadata
      if (msg.response_metadata) {
        // 可以从这里获取 token 使用信息等
        console.log('[Stream] response_metadata:', msg.response_metadata)
      }
    }
  }
  
  /**
   * 停止流式响应
   */
  function stopStream() {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    isLoading.value = false
  }
  
  /**
   * 恢复中断
   * @param {Object} value 恢复值
   */
  async function resumeInterrupt(value) {
    if (!interrupt.value || !threadId.value) return
    
    try {
      isLoading.value = true
      
      await client.runs.create(
        threadId.value,
        currentAssistant.value?.assistant_id || assistantId,
        {
          command: { resume: value }
        }
      )
      
      interrupt.value = null
      onHistoryRevalidate?.()
      
    } catch (e) {
      console.error('恢复中断失败:', e)
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 加载线程历史
   * @param {string} id 线程ID
   */
  async function loadThread(id) {
    if (!id) return
    
    threadId.value = id
    isThreadLoading.value = true
    
    try {
      // 获取线程状态
      const state = await client.threads.getState(id)
      
      if (state) {
        // 转换消息格式
        if (state.values?.messages) {
          messages.value = state.values.messages.map(msg => ({
            id: msg.id || uuidv4(),
            type: msg.type || (msg.role === 'assistant' ? 'ai' : 'human'),
            content: typeof msg.content === 'string' 
              ? msg.content 
              : (Array.isArray(msg.content) 
                  ? msg.content.filter(c => c.type === 'text').map(c => c.text).join('') 
                  : ''),
            toolCalls: msg.tool_calls || [],
            timestamp: msg.timestamp || new Date().toISOString()
          }))
        }
        
        // 更新 todos 和 files
        if (state.values?.todos) {
          todos.value = state.values.todos
        }
        if (state.values?.files) {
          files.value = state.values.files
        }
        
        // 检查中断
        if (state.next && state.next.length > 0) {
          interrupt.value = state.tasks?.[0]?.interrupts?.[0] || null
        }
      }
    } catch (e) {
      console.error('加载线程失败:', e)
      error.value = e.message
    } finally {
      isThreadLoading.value = false
    }
  }
  
  /**
   * 获取线程列表
   */
  async function listThreads(limit = 20) {
    try {
      const response = await client.threads.search({
        limit,
        metadata: { assistantId }
      })
      
      return (response || []).map(t => ({
        id: t.thread_id,
        title: t.metadata?.title || '新对话',
        createdAt: new Date(t.created_at),
        updatedAt: new Date(t.updated_at),
        hasInterrupt: t.metadata?.has_interrupt || false
      }))
    } catch (e) {
      console.error('获取线程列表失败:', e)
      return []
    }
  }
  
  /**
   * 删除线程
   */
  async function deleteThread(id) {
    try {
      await client.threads.delete(id)
      if (threadId.value === id) {
        threadId.value = null
        messages.value = []
      }
      onHistoryRevalidate?.()
    } catch (e) {
      console.error('删除线程失败:', e)
    }
  }
  
  /**
   * 更新文件状态
   */
  async function updateFiles(newFiles) {
    if (!threadId.value) return
    
    try {
      await client.threads.updateState(threadId.value, {
        values: { files: newFiles }
      })
      files.value = newFiles
    } catch (e) {
      console.error('更新文件失败:', e)
    }
  }
  
  // 清理
  onUnmounted(() => {
    stopStream()
  })
  
  // 初始化
  initAssistant()
  
  return {
    // 状态
    threadId,
    messages,
    todos,
    files,
    isLoading,
    isThreadLoading,
    interrupt,
    error,
    currentAssistant,
    
    // 计算属性
    hasInterrupt,
    hasTodos,
    hasFiles,
    groupedTodos,
    
    // Client 方法
    client,
    
    // 方法
    initAssistant,
    createThread,
    sendMessage,
    stopStream,
    resumeInterrupt,
    loadThread,
    listThreads,
    deleteThread,
    updateFiles
  }
}

/**
 * Thread 列表 Composable
 */
export function useLangGraphThreads(options = {}) {
  const { assistantId } = options
  
  const client = createLangGraphClient()
  const threads = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  
  /**
   * 获取线程列表
   */
  async function fetchThreads(limit = 20) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await client.threads.search({
        limit,
        metadata: assistantId ? { assistantId } : undefined
      })
      
      threads.value = (response || []).map(t => ({
        id: t.thread_id,
        title: t.metadata?.title || '新对话',
        createdAt: new Date(t.created_at),
        updatedAt: new Date(t.updated_at),
        hasInterrupt: t.metadata?.has_interrupt || false
      }))
      
      return threads.value
    } catch (e) {
      console.error('获取线程列表失败:', e)
      error.value = e.message
      return []
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 删除线程
   */
  async function deleteThread(id) {
    try {
      await client.threads.delete(id)
      threads.value = threads.value.filter(t => t.id !== id)
    } catch (e) {
      console.error('删除线程失败:', e)
    }
  }
  
  return {
    threads,
    isLoading,
    error,
    fetchThreads,
    deleteThread
  }
}

export { LANGGRAPH_CONFIG, createLangGraphClient }

