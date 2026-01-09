<template>
  <div 
    v-if="interrupts.length > 0" 
    class="interrupt-actions w-full space-y-4 rounded-lg border-2 border-orange-300 bg-orange-50/80 p-4 dark:border-orange-700 dark:bg-orange-950/30"
  >
    <div 
      v-for="(humanInterrupt, idx) in interrupts" 
      :key="idx"
      :class="[
        'rounded-lg border-2 bg-white p-4 shadow-sm transition-colors',
        decisions[idx]?.mode === 'edit' && 'border-blue-500 bg-blue-50/50',
        decisions[idx]?.mode === 'reject' && 'border-red-500 bg-red-50/50',
        !decisions[idx]?.mode && 'border-orange-500 bg-orange-50/50'
      ]"
    >
      <!-- 头部 -->
      <div class="mb-4 flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <span class="rounded-md bg-orange-100 px-2 py-1 text-xs font-semibold text-orange-800">
              需要批准
            </span>
            <span 
              v-if="interrupts.length > 1" 
              class="text-xs font-medium text-gray-600"
            >
              第 {{ idx + 1 }} 个，共 {{ interrupts.length }} 个
            </span>
          </div>
          <h3 class="mt-3 text-xl font-bold text-gray-900">
            {{ getActionName(humanInterrupt) }}
          </h3>
          <p class="mt-1 text-sm font-medium text-gray-700">
            请查看以下工具参数并选择操作
          </p>
        </div>
      </div>

      <!-- 工具参数 -->
      <div class="mb-4 space-y-2">
        <h4 class="mb-1 text-xs font-bold uppercase tracking-wider text-gray-600">
          参数
        </h4>
        
        <!-- 编辑模式 -->
        <div v-if="decisions[idx]?.mode === 'edit'" class="space-y-2">
          <div 
            v-for="(value, key) in getActionArgs(humanInterrupt)" 
            :key="key"
            class="rounded-sm border border-gray-200"
          >
            <div class="bg-gray-100/30 p-2">
              <label class="font-mono text-xs font-semibold text-gray-900">
                {{ key }}
              </label>
            </div>
            <div class="p-2">
              <el-input
                type="textarea"
                :model-value="getEditedArgValue(idx, key, value)"
                @update:model-value="val => updateEditedArgs(idx, key, val)"
                :autosize="{ minRows: 2, maxRows: 6 }"
                class="font-mono text-xs"
                :placeholder="`输入 ${key}...`"
              />
            </div>
          </div>
        </div>
        
        <!-- 查看模式 -->
        <div v-else class="space-y-2">
          <div 
            v-for="(value, key) in getActionArgs(humanInterrupt)" 
            :key="key"
            class="rounded-md border border-gray-200 bg-white"
          >
            <button
              @click="toggleArgExpanded(idx, key)"
              class="flex w-full items-center justify-between bg-gray-100 p-3 text-left transition-colors hover:bg-gray-200"
            >
              <span class="font-mono text-sm font-semibold">{{ key }}</span>
              <el-icon>
                <component :is="expandedArgs[idx]?.[key] ? 'ArrowUp' : 'ArrowDown'" />
              </el-icon>
            </button>
            <div 
              v-if="expandedArgs[idx]?.[key]" 
              class="border-t border-gray-200 p-3"
            >
              <pre class="m-0 max-h-96 overflow-auto whitespace-pre-wrap break-words font-mono text-xs">{{ formatValue(value) }}</pre>
            </div>
            <div v-else class="border-t border-gray-200 p-3">
              <p class="m-0 truncate font-mono text-sm">
                {{ getPreview(value) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 拒绝消息输入 -->
      <div v-if="decisions[idx]?.mode === 'reject'" class="mb-4">
        <label class="mb-2 block text-xs font-bold uppercase tracking-wider text-gray-600">
          反馈给 AI（可选）
        </label>
        <el-input
          type="textarea"
          :model-value="decisions[idx]?.rejectMessage"
          @update:model-value="val => updateRejectMessage(idx, val)"
          :autosize="{ minRows: 2, maxRows: 4 }"
          placeholder="解释为什么不应执行此操作以及 AI 应该怎么做..."
        />
        <p class="mt-1 text-xs font-medium text-gray-600">
          此反馈将添加到对话中以帮助引导 AI。
        </p>
      </div>

      <!-- 操作按钮 -->
      <div class="flex flex-wrap gap-2">
        <!-- 批准按钮 -->
        <el-button
          v-if="canApprove(humanInterrupt) && decisions[idx]?.mode !== 'edit' && decisions[idx]?.mode !== 'reject'"
          type="success"
          size="small"
          @click="interrupts.length === 1 ? handleSubmit() : setDecisionMode(idx, 'idle')"
          :loading="isLoading"
        >
          <el-icon><Check /></el-icon>
          <span class="font-semibold">批准</span>
        </el-button>

        <!-- 编辑按钮 -->
        <el-button
          v-if="canEdit(humanInterrupt) && decisions[idx]?.mode !== 'reject'"
          :type="decisions[idx]?.mode === 'edit' ? 'primary' : 'default'"
          size="small"
          @click="handleEditClick(idx, humanInterrupt)"
          :loading="isLoading"
        >
          <el-icon><Edit /></el-icon>
          <span class="font-semibold">
            {{ decisions[idx]?.mode === 'edit' 
              ? (interrupts.length === 1 ? '提交编辑' : '完成编辑')
              : '编辑' 
            }}
          </span>
        </el-button>

        <!-- 拒绝按钮 -->
        <el-button
          v-if="canReject(humanInterrupt) && decisions[idx]?.mode !== 'edit'"
          :type="decisions[idx]?.mode === 'reject' ? 'danger' : 'default'"
          size="small"
          @click="handleRejectClick(idx)"
          :loading="isLoading"
        >
          <el-icon><Close /></el-icon>
          <span class="font-semibold">
            {{ decisions[idx]?.mode === 'reject' 
              ? (interrupts.length === 1 ? '提交拒绝' : '确认拒绝')
              : '拒绝' 
            }}
          </span>
        </el-button>

        <!-- 取消按钮 -->
        <el-button
          v-if="decisions[idx]?.mode === 'edit' || decisions[idx]?.mode === 'reject'"
          size="small"
          @click="setDecisionMode(idx, 'idle')"
          :loading="isLoading"
        >
          <span class="font-semibold">取消</span>
        </el-button>
      </div>
    </div>

    <!-- 提交全部按钮（多个中断时） -->
    <div v-if="interrupts.length > 1" class="flex justify-end pt-2">
      <el-button
        type="primary"
        size="large"
        @click="handleSubmit"
        :loading="isLoading"
      >
        {{ isLoading ? '提交中...' : `提交全部决策 (${interrupts.length})` }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Check, Close, Edit, ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  interrupt: {
    type: Object,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit'])

// 状态
const decisions = ref({})
const expandedArgs = ref({})

// 解析中断
const interrupts = computed(() => {
  try {
    const value = props.interrupt?.value
    if (!value) return []

    // 处理 Deep Agents/LangGraph 格式
    if (typeof value === 'object' && !Array.isArray(value) && 
        Array.isArray(value.action_requests) && Array.isArray(value.review_configs)) {
      return value.action_requests.map((actionReq, idx) => {
        const reviewConfig = value.review_configs[idx] || {}
        const allowedDecisions = reviewConfig.allowed_decisions || ['approve', 'edit', 'reject']
        
        return {
          action_request: {
            action: actionReq.name || actionReq.action || '未知操作',
            args: actionReq.args || actionReq.arguments || {}
          },
          config: {
            allow_accept: allowedDecisions.includes('approve'),
            allow_edit: allowedDecisions.includes('edit'),
            allow_respond: allowedDecisions.includes('reject')
          },
          description: actionReq.description
        }
      })
    }

    // 标准格式中断数组
    if (Array.isArray(value)) {
      return value.filter(item => item?.action_request)
    }

    // 单个中断对象
    if (value?.action_request) {
      return [value]
    }

    return []
  } catch (error) {
    console.error('解析中断时出错:', error)
    return []
  }
})

// 辅助函数
function getActionName(humanInterrupt) {
  return humanInterrupt?.action_request?.action || 
         humanInterrupt?.action_request?.name || 
         '未知操作'
}

function getActionArgs(humanInterrupt) {
  return humanInterrupt?.action_request?.args || {}
}

function canApprove(humanInterrupt) {
  return humanInterrupt?.config?.allow_accept !== false
}

function canEdit(humanInterrupt) {
  return humanInterrupt?.config?.allow_edit !== false
}

function canReject(humanInterrupt) {
  return humanInterrupt?.config?.allow_respond !== false
}

function formatValue(value) {
  return typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

function getPreview(value) {
  const str = formatValue(value)
  return str.length > 200 ? str.slice(0, 100) + '...' : str
}

function getEditedArgValue(idx, key, originalValue) {
  const edited = decisions.value[idx]?.editedArgs?.[key]
  if (edited !== undefined) {
    return typeof edited === 'string' ? edited : JSON.stringify(edited, null, 2)
  }
  return formatValue(originalValue)
}

// 操作函数
function toggleArgExpanded(idx, key) {
  if (!expandedArgs.value[idx]) {
    expandedArgs.value[idx] = {}
  }
  expandedArgs.value[idx][key] = !expandedArgs.value[idx][key]
}

function setDecisionMode(idx, mode, initialArgs) {
  decisions.value[idx] = {
    mode,
    editedArgs: mode === 'edit' ? (initialArgs || {}) : undefined,
    rejectMessage: mode === 'reject' ? '' : undefined
  }
}

function updateRejectMessage(idx, message) {
  if (!decisions.value[idx]) {
    decisions.value[idx] = { mode: 'reject' }
  }
  decisions.value[idx].rejectMessage = message
}

function updateEditedArgs(idx, key, value) {
  if (!decisions.value[idx]) {
    decisions.value[idx] = { mode: 'edit', editedArgs: {} }
  }
  if (!decisions.value[idx].editedArgs) {
    decisions.value[idx].editedArgs = {}
  }
  
  // 尝试解析 JSON
  let parsedValue = value
  try {
    if (value.trim().startsWith('{') || value.trim().startsWith('[')) {
      parsedValue = JSON.parse(value)
    }
  } catch {
    // 保持为字符串
  }
  
  decisions.value[idx].editedArgs[key] = parsedValue
}

function handleEditClick(idx, humanInterrupt) {
  if (decisions.value[idx]?.mode === 'edit') {
    // 提交编辑
    if (interrupts.value.length === 1) {
      handleSubmit()
    } else {
      setDecisionMode(idx, 'idle')
    }
  } else {
    // 进入编辑模式
    setDecisionMode(idx, 'edit', getActionArgs(humanInterrupt))
  }
}

function handleRejectClick(idx) {
  if (decisions.value[idx]?.mode === 'reject') {
    // 提交拒绝
    if (interrupts.value.length === 1) {
      handleSubmit()
    } else {
      setDecisionMode(idx, 'idle')
    }
  } else {
    // 进入拒绝模式
    setDecisionMode(idx, 'reject')
  }
}

function handleSubmit() {
  const responses = interrupts.value.map((interrupt, idx) => {
    if (!interrupt?.action_request) {
      return { type: 'approve' }
    }

    const decision = decisions.value[idx]

    if (!decision || decision.mode === 'idle') {
      return { type: 'approve' }
    }

    if (decision.mode === 'edit') {
      return {
        type: 'edit',
        edited_action: {
          name: interrupt.action_request.action || interrupt.action_request.name,
          args: decision.editedArgs || interrupt.action_request.args
        }
      }
    }

    if (decision.mode === 'reject') {
      const message = decision.rejectMessage?.trim() || ''
      return {
        type: 'reject',
        message: message ? `用户拒绝：${message}` : '用户拒绝'
      }
    }

    return { type: 'approve' }
  })

  emit('submit', responses)
}

// 重置状态
watch(() => props.interrupt, () => {
  decisions.value = {}
  expandedArgs.value = {}
})
</script>

<style scoped>
.interrupt-actions {
  font-family: system-ui, -apple-system, sans-serif;
}
</style>

