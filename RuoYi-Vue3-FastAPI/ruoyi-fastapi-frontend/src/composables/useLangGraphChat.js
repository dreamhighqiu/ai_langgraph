/**
 * LangGraph Chat Composable
 * 参照 ai-test-management 的 useChat.ts 实现
 * 提供与 LangGraph Agent 的流式通信能力
 * 
 * 使用 HTTP/SSE 通信方式，兼容性更好
 */
import { ref, computed, onUnmounted } from 'vue'

// LangGraph 配置
const LANGGRAPH_CONFIG = {
  baseUrl: import.meta.env?.VITE_LANGGRAPH_API_URL || 'http://localhost:2024',
  agents: {
    testcase_generator_agent: {
      name: 'testcase_generator_agent',
      description: '智能生成测试用例'
    },
    requirement_analyzer_agent: {
      name: 'requirement_analyzer_agent',
      description: '智能分析需求文档'
    },
    defect_analyzer_agent: {
      name: 'defect_analyzer_agent',
      description: '智能分析缺陷报告'
    }
  }
}

/**
 * 获取认证 token
 */
function getAuthToken() {
  return localStorage.getItem('token') || ''
}

/**
 * LangGraph Chat Composable
 * @param {Object} options 配置选项
 */
export function useLangGraphChat(options = {}) {
  const { assistantId, projectId, folderId, onTestCaseCreated } = options
  
  // 状态
  const threadId = ref(null)
  const messages = ref([])
  const todos = ref([])
  const files = ref({})
  const isLoading = ref(false)
  const isThreadLoading = ref(false)
  const interrupt = ref(null)
  const error = ref(null)
  const streamController = ref(null)
  
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
   * 创建新的对话线程
   */
  async function createThread() {
    threadId.value = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    messages.value = []
    todos.value = []
    files.value = {}
    interrupt.value = null
    error.value = null
    return threadId.value
  }
  
  /**
   * 发送消息（流式）
   * @param {string} content 消息内容
   */
  async function sendMessage(content) {
    if (!content?.trim() || isLoading.value) return
    
    // 如果没有 threadId，创建一个
    if (!threadId.value) {
      await createThread()
    }
    
    // 添加用户消息
    const userMessage = {
      id: `msg_${Date.now()}`,
      type: 'human',
      content: content.trim(),
      timestamp: new Date().toISOString()
    }
    messages.value.push(userMessage)
    
    isLoading.value = true
    error.value = null
    
    try {
      await streamWithHTTP(content)
      onTestCaseCreated?.()
    } catch (e) {
      console.error('发送消息失败:', e)
      error.value = e.message
      
      // 添加错误消息
      messages.value.push({
        id: `msg_${Date.now()}`,
        type: 'error',
        content: `发送失败: ${e.message}`,
        timestamp: new Date().toISOString()
      })
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 使用 HTTP SSE 进行流式通信
   */
  async function streamWithHTTP(content) {
    const token = getAuthToken()
    
    // 添加 AI 消息占位
    const aiMessage = {
      id: `msg_${Date.now()}`,
      type: 'ai',
      content: '',
      toolCalls: [],
      timestamp: new Date().toISOString()
    }
    messages.value.push(aiMessage)
    
    const response = await fetch('/api/testing/ai-chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        assistant_id: assistantId,
        message: content,
        thread_id: threadId.value,
        project_id: projectId,
        folder_id: folderId,
        stream: true
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    streamController.value = { reader }
    
    try {
      let buffer = ''
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim()
            if (dataStr === '[DONE]') continue
            if (!dataStr) continue
            
            try {
              const data = JSON.parse(dataStr)
              handleStreamData(data, aiMessage)
            } catch (parseError) {
              // 忽略解析错误，可能是不完整的 JSON
            }
          }
        }
      }
      
      // 处理缓冲区中剩余的数据
      if (buffer.startsWith('data: ')) {
        const dataStr = buffer.slice(6).trim()
        if (dataStr && dataStr !== '[DONE]') {
          try {
            const data = JSON.parse(dataStr)
            handleStreamData(data, aiMessage)
          } catch (e) {
            // 忽略
          }
        }
      }
    } finally {
      streamController.value = null
    }
  }
  
  /**
   * 处理流式数据
   */
  function handleStreamData(data, aiMessage) {
    if (data.type === 'content') {
      aiMessage.content += data.content || ''
    } else if (data.type === 'thread_id') {
      threadId.value = data.thread_id
    } else if (data.type === 'tool_call') {
      aiMessage.toolCalls.push({
        id: data.id || `tc_${Date.now()}`,
        name: data.name,
        args: data.args || {},
        status: 'running'
      })
    } else if (data.type === 'tool_result') {
      const toolCall = aiMessage.toolCalls.find(t => t.name === data.name)
      if (toolCall) {
        toolCall.status = 'completed'
        toolCall.result = data.result
      }
    } else if (data.type === 'todos') {
      todos.value = data.todos || []
    } else if (data.type === 'files') {
      files.value = data.files || {}
    } else if (data.type === 'interrupt') {
      interrupt.value = data.value
    } else if (data.type === 'error') {
      throw new Error(data.error || '未知错误')
    } else if (data.content) {
      // 兼容直接返回 content 的情况
      aiMessage.content += data.content
    } else if (data.messages) {
      // 兼容返回 messages 数组的情况
      const lastMsg = data.messages[data.messages.length - 1]
      if (lastMsg?.content) {
        aiMessage.content = typeof lastMsg.content === 'string' 
          ? lastMsg.content 
          : lastMsg.content.map(c => c.text || '').join('')
      }
    }
  }
  
  /**
   * 停止流式响应
   */
  function stopStream() {
    if (streamController.value?.reader) {
      try {
        streamController.value.reader.cancel()
      } catch (e) {
        // 忽略取消错误
      }
      streamController.value = null
    }
    isLoading.value = false
  }
  
  /**
   * 恢复中断
   * @param {Object} value 恢复值
   */
  async function resumeInterrupt(value) {
    if (!interrupt.value) return
    
    try {
      isLoading.value = true
      
      const response = await fetch('/api/testing/ai-chat/resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
          thread_id: threadId.value,
          assistant_id: assistantId,
          resume_value: value
        })
      })
      
      if (response.ok) {
        interrupt.value = null
      }
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
    threadId.value = id
    isThreadLoading.value = true
    
    try {
      const response = await fetch(`/api/testing/ai-chat/threads/${id}/history`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        const history = result.data || []
        
        // 转换消息格式
        messages.value = history.map(msg => ({
          id: msg.id || `msg_${Math.random().toString(36).substr(2, 9)}`,
          type: msg.type,
          content: typeof msg.content === 'string' 
            ? msg.content 
            : msg.content?.map(c => c.text || '').join('') || '',
          toolCalls: msg.tool_calls || [],
          timestamp: msg.timestamp || new Date().toISOString()
        }))
      }
    } catch (e) {
      console.error('加载线程失败:', e)
    } finally {
      isThreadLoading.value = false
    }
  }
  
  /**
   * 更新文件
   */
  function updateFiles(newFiles) {
    files.value = newFiles
  }
  
  // 清理
  onUnmounted(() => {
    stopStream()
  })
  
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
    
    // 计算属性
    hasInterrupt,
    hasTodos,
    hasFiles,
    groupedTodos,
    
    // 方法
    createThread,
    sendMessage,
    stopStream,
    resumeInterrupt,
    loadThread,
    updateFiles
  }
}

/**
 * Thread 列表 Composable
 */
export function useLangGraphThreads(options = {}) {
  const { assistantId } = options
  
  const threads = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  
  /**
   * 获取线程列表
   */
  async function fetchThreads() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await fetch('/api/testing/ai-chat/threads', {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        threads.value = (result.data || []).map(t => ({
          id: t.thread_id || t.id,
          title: t.title || t.metadata?.title || '新对话',
          createdAt: new Date(t.created_at || t.createdAt),
          updatedAt: new Date(t.updated_at || t.updatedAt),
          hasInterrupt: t.has_interrupt || t.metadata?.has_interrupt || false
        }))
      }
    } catch (e) {
      console.error('获取线程列表失败:', e)
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 删除线程
   */
  async function deleteThread(id) {
    try {
      await fetch(`/api/testing/ai-chat/threads/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      })
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

export { LANGGRAPH_CONFIG }
