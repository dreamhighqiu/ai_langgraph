<template>
  <el-dialog
    v-model="visible"
    title="AI 生成测试用例"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 头部信息 -->
    <div class="dialog-header">
      <div class="header-icon">
        <el-icon :size="24"><MagicStick /></el-icon>
      </div>
      <div class="header-text">
        <h3>AI 生成测试用例</h3>
        <p>使用自然语言描述功能需求，AI 将自动生成完整的测试用例</p>
      </div>
    </div>

    <!-- 安全提示 -->
    <el-alert type="success" :closable="false" class="mb-4">
      <template #title>
        <el-icon><CircleCheck /></el-icon>
        您的数据是安全的，不会用于 AI 训练
      </template>
    </el-alert>

    <!-- 快捷建议 -->
    <div class="quick-suggestions mb-4">
      <span class="label">试试这些：</span>
      <el-button
        v-for="(item, index) in quickSuggestions"
        :key="index"
        size="small"
        @click="applyQuickSuggestion(item)"
      >
        <el-icon><MagicStick /></el-icon>
        {{ item.label }}
      </el-button>
    </div>

    <!-- 表单 -->
    <el-form ref="formRef" :model="form" :rules="rules" label-width="130px">
      <el-form-item label="项目" prop="projectId" required>
        <el-select v-model="form.projectId" placeholder="选择项目" style="width: 100%">
          <el-option
            v-for="item in projectList"
            :key="item.project_id"
            :label="item.project_name"
            :value="item.project_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="功能描述" prop="prompt" required>
        <el-input
          v-model="form.prompt"
          type="textarea"
          :rows="6"
          placeholder="例如：用户登录功能，包括用户名密码验证、记住密码、忘记密码、第三方登录等场景..."
          :maxlength="2000"
          show-word-limit
        />
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          描述越详细，生成的测试用例越准确。可以包含功能描述、业务场景、边界条件等信息。
        </div>
      </el-form-item>

      <el-form-item label="启用 RAG 检索">
        <el-switch v-model="form.useRag" />
        <div class="form-tip" style="margin-top: 8px">
          <el-icon><InfoFilled /></el-icon>
          启用后，AI 会先从知识库检索相关的接口文档、测试数据等信息，然后基于这些上下文生成更准确的测试用例。适用于已有文档的 API 接口测试。
        </div>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="测试用例模板" prop="template">
            <el-select v-model="form.template" style="width: 100%">
              <el-option value="test_case">
                <div class="template-option">
                  <span class="template-name">测试步骤模板</span>
                  <span class="template-desc">传统的步骤-预期结果格式</span>
                </div>
              </el-option>
              <el-option value="test_case_bdd">
                <div class="template-option">
                  <span class="template-name">BDD 模板</span>
                  <span class="template-desc">Given-When-Then 格式</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="生成数量" prop="count">
            <el-input-number
              v-model="form.count"
              :min="1"
              :max="20"
              style="width: 100%"
            />
            <div class="form-tip">建议生成 3-10 个测试用例</div>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        type="primary"
        :loading="generating"
        :disabled="!form.prompt.trim()"
        @click="handleGenerate"
      >
        <el-icon v-if="!generating"><MagicStick /></el-icon>
        {{ generating ? 'AI 生成中...' : '生成测试用例' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, CircleCheck, InfoFilled } from '@element-plus/icons-vue'
import { listAllProject } from '@/api/testing/project'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  projectId: { type: Number, default: null },
  folderId: { type: Number, default: null }
})

const emit = defineEmits(['update:modelValue', 'open-chat', 'success'])

// 对话框可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 表单引用
const formRef = ref(null)

// 状态
const generating = ref(false)
const projectList = ref([])

// 表单数据
const form = reactive({
  projectId: null,
  prompt: '',
  template: 'test_case',
  count: 5,
  useRag: false
})

// 表单验证规则
const rules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  prompt: [
    { required: true, message: '请输入功能描述', trigger: 'blur' },
    { min: 5, message: '描述至少需要5个字符', trigger: 'blur' }
  ]
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await listAllProject('0')
    projectList.value = res.data || []
    // 如果props中有projectId，设置为默认值
    if (props.projectId && !form.projectId) {
      form.projectId = props.projectId
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 快捷建议
const quickSuggestions = [
  {
    label: '为用户登录生成测试用例',
    prompt: '为用户登录功能生成测试用例，包括用户名密码验证、记住密码、忘记密码、第三方登录等场景'
  },
  {
    label: '为密码重置生成测试用例',
    prompt: '为密码重置功能生成测试用例，包括邮箱验证、验证码验证、密码强度检查、重置成功后的登录等场景'
  }
]

// 应用快捷建议
const applyQuickSuggestion = (item) => {
  form.prompt = item.prompt
}

  // 生成测试用例
  const handleGenerate = async () => {
    const valid = await formRef.value?.validate()
    if (!valid) return

    // 构建聊天提示词，交给AI对话界面处理
    // 如果启用了 RAG，在 prompt 中明确要求使用 RAG 检索
    const ragInstruction = form.useRag 
      ? '\n\n⚠️ 重要：用户已明确要求使用 RAG 检索功能。请务必先调用 rag_query_tool 从知识库检索相关信息，然后基于检索结果生成测试用例。'
      : ''
    
    const chatPrompt = `请帮我生成测试用例。

需求描述：
${form.prompt.trim()}

生成数量：${form.count} 个
模板类型：${form.template === 'test_case' ? '标准测试用例' : 'BDD测试用例'}
使用 RAG 检索：${form.useRag ? '是' : '否'}${ragInstruction}

请根据以上需求生成测试用例。`

    // 触发打开AI聊天，传递 prompt、projectId 和 useRag
    emit('open-chat', {
      prompt: chatPrompt,
      projectId: form.projectId,
      useRag: form.useRag
    })
    
    // 重置表单
    resetForm()
    
    // 关闭对话框
    visible.value = false
  }

// 重置表单
const resetForm = () => {
  form.projectId = props.projectId || null
  form.prompt = ''
  form.template = 'test_case'
  form.count = 5
  form.useRag = false
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 监听对话框打开
watch(visible, (val) => {
  if (val) {
    loadProjects()
  } else {
    resetForm()
  }
})

// 组件挂载时加载项目列表
onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.dialog-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;

  .header-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .header-text {
    flex: 1;

    h3 {
      margin: 0 0 4px 0;
      font-size: 18px;
      font-weight: 600;
    }

    p {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }
}

.quick-suggestions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;

  .label {
    font-size: 14px;
    color: #606266;
    font-weight: 500;
  }

  .el-button {
    border-radius: 16px;
  }
}

.form-tip {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;

  .el-icon {
    margin-top: 2px;
    color: #409eff;
  }
}

.template-option {
  display: flex;
  flex-direction: column;

  .template-name {
    font-weight: 500;
  }

  .template-desc {
    font-size: 12px;
    color: #909399;
  }
}

:deep(.el-alert__content) {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>

