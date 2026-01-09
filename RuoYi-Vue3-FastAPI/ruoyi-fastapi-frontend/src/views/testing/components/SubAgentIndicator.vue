<template>
  <div class="sub-agent-indicator" v-if="visible">
    <div class="indicator-header" @click="toggleExpand">
      <div class="agent-info">
        <el-icon class="agent-icon" :class="{ 'is-running': isRunning }">
          <component :is="agentIcon" />
        </el-icon>
        <span class="agent-name">{{ agentDisplayName }}</span>
        <el-tag 
          :type="statusTagType" 
          size="small" 
          class="agent-status"
        >
          {{ statusText }}
        </el-tag>
      </div>
      <el-icon class="expand-icon" :class="{ 'is-expanded': expanded }">
        <ArrowRight />
      </el-icon>
    </div>
    
    <!-- 展开内容 -->
    <transition name="expand">
      <div v-show="expanded" class="indicator-content">
        <!-- 当前任务 -->
        <div class="task-info" v-if="currentTask">
          <el-icon class="task-icon"><Loading /></el-icon>
          <span class="task-text">{{ currentTask }}</span>
        </div>
        
        <!-- 进度条 -->
        <el-progress 
          v-if="progress > 0"
          :percentage="progress" 
          :stroke-width="6"
          :show-text="false"
          class="agent-progress"
        />
        
        <!-- 工具调用列表 -->
        <div class="tool-calls" v-if="toolCalls.length > 0">
          <div class="tool-call-title">
            <el-icon><Tools /></el-icon>
            <span>工具调用 ({{ toolCalls.length }})</span>
          </div>
          <div 
            v-for="(tool, index) in toolCalls.slice(-3)" 
            :key="index"
            class="tool-call-item"
          >
            <span class="tool-name">{{ tool.name }}</span>
            <el-tag 
              :type="tool.status === 'success' ? 'success' : tool.status === 'error' ? 'danger' : 'info'"
              size="small"
            >
              {{ tool.status === 'success' ? '成功' : tool.status === 'error' ? '失败' : '执行中' }}
            </el-tag>
          </div>
        </div>
        
        <!-- 思考过程 -->
        <div class="thinking-process" v-if="thinkingSteps.length > 0">
          <div class="thinking-title">
            <el-icon><Aim /></el-icon>
            <span>思考过程</span>
          </div>
          <div 
            v-for="(step, index) in thinkingSteps.slice(-5)" 
            :key="index"
            class="thinking-step"
          >
            <span class="step-number">{{ index + 1 }}.</span>
            <span class="step-text">{{ step }}</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { 
  ArrowRight, 
  Loading, 
  Tools, 
  Aim,
  Document,
  DataAnalysis,
  Warning,
  ChatDotRound
} from '@element-plus/icons-vue'

const props = defineProps({
  // 子代理名称
  agentName: {
    type: String,
    default: ''
  },
  // 子代理状态
  status: {
    type: String,
    default: 'idle', // idle, running, completed, error
    validator: (value) => ['idle', 'running', 'completed', 'error'].includes(value)
  },
  // 当前任务描述
  currentTask: {
    type: String,
    default: ''
  },
  // 进度 (0-100)
  progress: {
    type: Number,
    default: 0
  },
  // 工具调用列表
  toolCalls: {
    type: Array,
    default: () => []
  },
  // 思考步骤
  thinkingSteps: {
    type: Array,
    default: () => []
  },
  // 是否默认展开
  defaultExpanded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle'])

// 展开状态
const expanded = ref(props.defaultExpanded)

// 是否显示
const visible = computed(() => {
  return props.agentName && props.status !== 'idle'
})

// 是否正在运行
const isRunning = computed(() => props.status === 'running')

// 代理显示名称
const agentDisplayName = computed(() => {
  const nameMap = {
    'testcase_generator': '测试用例生成器',
    'requirement_analyzer': '需求分析器',
    'defect_analyzer': '缺陷分析器',
    'rag_searcher': 'RAG 检索器',
    'document_parser': '文档解析器'
  }
  return nameMap[props.agentName] || props.agentName
})

// 代理图标
const agentIcon = computed(() => {
  const iconMap = {
    'testcase_generator': Document,
    'requirement_analyzer': DataAnalysis,
    'defect_analyzer': Warning,
    'rag_searcher': ChatDotRound,
    'document_parser': Document
  }
  return iconMap[props.agentName] || ChatDotRound
})

// 状态标签类型
const statusTagType = computed(() => {
  const typeMap = {
    'idle': 'info',
    'running': 'primary',
    'completed': 'success',
    'error': 'danger'
  }
  return typeMap[props.status] || 'info'
})

// 状态文本
const statusText = computed(() => {
  const textMap = {
    'idle': '空闲',
    'running': '运行中',
    'completed': '已完成',
    'error': '错误'
  }
  return textMap[props.status] || props.status
})

// 切换展开
const toggleExpand = () => {
  expanded.value = !expanded.value
  emit('toggle', expanded.value)
}

// 监听状态变化，自动展开
watch(() => props.status, (newStatus) => {
  if (newStatus === 'running') {
    expanded.value = true
  }
})
</script>

<style scoped>
.sub-agent-indicator {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  margin: 8px 0;
  overflow: hidden;
}

.indicator-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.indicator-header:hover {
  background: var(--el-fill-color-light);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.agent-icon {
  font-size: 18px;
  color: var(--el-color-primary);
}

.agent-icon.is-running {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.agent-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.agent-status {
  margin-left: 4px;
}

.expand-icon {
  transition: transform 0.3s;
  color: var(--el-text-color-secondary);
}

.expand-icon.is-expanded {
  transform: rotate(90deg);
}

.indicator-content {
  padding: 0 12px 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.task-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: var(--el-text-color-regular);
  font-size: 13px;
}

.task-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.agent-progress {
  margin: 8px 0;
}

.tool-calls,
.thinking-process {
  margin-top: 12px;
}

.tool-call-title,
.thinking-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.tool-call-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  background: var(--el-fill-color-lighter);
  border-radius: 4px;
  margin-bottom: 4px;
  font-size: 12px;
}

.tool-name {
  color: var(--el-text-color-regular);
}

.thinking-step {
  display: flex;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  padding: 2px 0;
}

.step-number {
  color: var(--el-color-primary);
  font-weight: 500;
}

/* 展开动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>

