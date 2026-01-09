<template>
  <el-dialog
    v-model="visible"
    :title="isAIMode ? 'AI 智能需求分析' : (editData ? '编辑需求' : '新建需求')"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- AI 模式切换 -->
    <div class="mode-switch mb-4">
      <el-radio-group v-model="isAIMode" size="default">
        <el-radio-button :label="false">
          <el-icon><Edit /></el-icon>
          手动录入
        </el-radio-button>
        <el-radio-button :label="true">
          <el-icon><MagicStick /></el-icon>
          AI 智能分析
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- AI 模式 -->
    <template v-if="isAIMode">
      <div class="ai-mode-content">
        <!-- 安全提示 -->
        <el-alert type="success" :closable="false" class="mb-4">
          <template #title>
            <el-icon><CircleCheck /></el-icon>
            您的数据是安全的，不会用于 AI 训练
          </template>
        </el-alert>

        <!-- 需求描述输入 -->
        <el-form ref="aiFormRef" :model="aiForm" :rules="aiRules" label-width="100px">
          <el-form-item label="项目" prop="projectId" required>
            <el-select v-model="aiForm.projectId" placeholder="选择项目" style="width: 100%">
              <el-option
                v-for="item in projectList"
                :key="item.projectId"
                :label="item.projectName"
                :value="item.projectId"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="需求描述" prop="description" required>
            <el-input
              v-model="aiForm.description"
              type="textarea"
              :rows="8"
              placeholder="请详细描述您的需求，AI 将自动分析并提取关键信息...

例如：
- 用户可以通过邮箱或手机号注册账号
- 注册时需要设置密码，密码长度至少8位，包含数字和字母
- 注册成功后发送欢迎邮件
- 支持第三方账号（微信、QQ）快捷注册"
              :maxlength="5000"
              show-word-limit
            />
          </el-form-item>

          <!-- 快捷示例 -->
          <div class="quick-examples mb-4">
            <span class="label">试试这些：</span>
            <el-button size="small" @click="applyExample('login')">
              <el-icon><MagicStick /></el-icon>
              用户登录需求
            </el-button>
            <el-button size="small" @click="applyExample('order')">
              <el-icon><MagicStick /></el-icon>
              订单管理需求
            </el-button>
          </div>

          <!-- 分析类型选择 -->
          <el-form-item label="分析类型">
            <el-checkbox-group v-model="aiForm.analysisTypes">
              <el-checkbox label="functional">功能需求</el-checkbox>
              <el-checkbox label="nonfunctional">非功能需求</el-checkbox>
              <el-checkbox label="user_story">用户故事</el-checkbox>
              <el-checkbox label="acceptance">验收标准</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <!-- RAG 检索 -->
          <el-form-item label="知识库增强">
            <el-switch v-model="aiForm.useRag" />
            <span class="form-tip ml-2">启用后，AI 会先检索相关文档来增强分析结果</span>
          </el-form-item>
        </el-form>
      </div>
    </template>

    <!-- 手动模式 -->
    <template v-else>
      <el-form ref="manualFormRef" :model="manualForm" :rules="manualRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目" prop="projectId" required>
              <el-select v-model="manualForm.projectId" placeholder="选择项目" style="width: 100%">
                <el-option
                  v-for="item in projectList"
                  :key="item.projectId"
                  :label="item.projectName"
                  :value="item.projectId"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="需求类型" prop="requirementType">
              <el-select v-model="manualForm.requirementType" placeholder="选择类型" style="width: 100%">
                <el-option label="功能需求" value="functional" />
                <el-option label="性能需求" value="performance" />
                <el-option label="安全需求" value="security" />
                <el-option label="接口需求" value="interface" />
                <el-option label="业务需求" value="business" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="需求名称" prop="requirementName" required>
              <el-input v-model="manualForm.requirementName" placeholder="请输入需求名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="manualForm.priority" placeholder="选择优先级" style="width: 100%">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="所属模块" prop="module">
          <el-input v-model="manualForm.module" placeholder="请输入所属模块（如：用户模块、订单模块）" />
        </el-form-item>

        <el-form-item label="需求描述" prop="description">
          <el-input
            v-model="manualForm.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述需求内容..."
          />
        </el-form-item>

        <el-form-item label="功能需求" prop="functionalRequirements">
          <el-input
            v-model="manualForm.functionalRequirements"
            type="textarea"
            :rows="4"
            placeholder="列出主要功能需求点..."
          />
        </el-form-item>

        <el-form-item label="验收标准" prop="acceptanceCriteria">
          <el-input
            v-model="manualForm.acceptanceCriteria"
            type="textarea"
            :rows="3"
            placeholder="请输入验收标准..."
          />
        </el-form-item>
      </el-form>
    </template>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        v-if="isAIMode"
        type="primary"
        :loading="generating"
        :disabled="!aiForm.description.trim()"
        @click="handleAIAnalyze"
      >
        <el-icon v-if="!generating"><MagicStick /></el-icon>
        {{ generating ? 'AI 分析中...' : '开始 AI 分析' }}
      </el-button>
      <el-button
        v-else
        type="primary"
        :loading="submitting"
        @click="handleManualSubmit"
      >
        {{ editData ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, MagicStick, CircleCheck } from '@element-plus/icons-vue'
import { addRequirementAnalysis, updateRequirementAnalysis } from '@/api/testing/requirementAnalysis'
import { listAllProject } from '@/api/testing/project'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  editData: { type: Object, default: null },
  defaultProjectId: { type: Number, default: null }
})

const emit = defineEmits(['update:modelValue', 'open-chat', 'success'])

// 对话框可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 状态
const isAIMode = ref(false)
const generating = ref(false)
const submitting = ref(false)
const projectList = ref([])

// 表单引用
const aiFormRef = ref(null)
const manualFormRef = ref(null)

// AI 模式表单
const aiForm = reactive({
  projectId: null,
  description: '',
  analysisTypes: ['functional', 'acceptance'],
  useRag: false
})

// 手动模式表单
const manualForm = reactive({
  projectId: null,
  requirementName: '',
  requirementType: 'functional',
  priority: 'medium',
  module: '',
  description: '',
  functionalRequirements: '',
  acceptanceCriteria: ''
})

// AI 表单验证规则
const aiRules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  description: [
    { required: true, message: '请输入需求描述', trigger: 'blur' },
    { min: 20, message: '描述至少需要20个字符', trigger: 'blur' }
  ]
}

// 手动表单验证规则
const manualRules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  requirementName: [{ required: true, message: '请输入需求名称', trigger: 'blur' }],
  requirementType: [{ required: true, message: '请选择需求类型', trigger: 'change' }]
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await listAllProject('0')
    projectList.value = (res.data || []).map(item => ({
      projectId: item.project_id,
      projectName: item.project_name
    }))
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

// 应用示例
const applyExample = (type) => {
  if (type === 'login') {
    aiForm.description = `用户登录功能需求：

1. 用户可以通过用户名/邮箱/手机号登录系统
2. 登录时需要输入密码，支持密码可见/隐藏切换
3. 提供"记住我"选项，7天内免登录
4. 登录失败时显示友好的错误提示
5. 连续5次登录失败后锁定账号15分钟
6. 支持第三方账号（微信、QQ、钉钉）登录
7. 登录成功后跳转到用户之前访问的页面
8. 提供忘记密码功能，支持邮箱和手机验证码重置`
  } else if (type === 'order') {
    aiForm.description = `订单管理功能需求：

1. 用户可以查看订单列表，支持分页和筛选
2. 订单支持多种状态：待支付、已支付、已发货、已完成、已取消
3. 用户可以取消未支付的订单
4. 支持订单详情查看，包含商品信息、收货地址、支付方式等
5. 已完成订单支持申请退款
6. 订单状态变更时发送通知（短信/推送）
7. 支持订单导出为Excel`
  }
}

// AI 分析
const handleAIAnalyze = async () => {
  const valid = await aiFormRef.value?.validate()
  if (!valid) return

  // 构建AI聊天提示词
  const analysisTypesText = aiForm.analysisTypes.map(t => {
    const map = {
      functional: '功能需求',
      nonfunctional: '非功能需求',
      user_story: '用户故事',
      acceptance: '验收标准'
    }
    return map[t]
  }).join('、')

  const chatPrompt = `请帮我分析以下需求，并提取关键信息。

需求描述：
${aiForm.description.trim()}

分析要求：
- 提取并整理：${analysisTypesText}
- 识别潜在的技术风险和依赖
- 生成可测试的验收标准
${aiForm.useRag ? '\n请先使用 rag_query_tool 从知识库检索相关信息来增强分析结果。' : ''}

请按照以下格式输出分析结果：
1. 需求概述
2. 功能需求清单
3. 非功能需求（如性能、安全等）
4. 用户故事（采用 As a ... I want ... So that ... 格式）
5. 验收标准
6. 技术风险和依赖

分析完成后，请使用 save_requirement_analysis_tool 工具保存分析结果。`

  // 触发打开AI聊天
  emit('open-chat', chatPrompt)
  
  // 关闭对话框
  visible.value = false
}

// 手动提交
const handleManualSubmit = async () => {
  const valid = await manualFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const submitData = {
      project_id: manualForm.projectId,
      requirement_name: manualForm.requirementName,
      requirement_type: manualForm.requirementType,
      priority: manualForm.priority,
      module: manualForm.module,
      description: manualForm.description,
      functional_requirements: manualForm.functionalRequirements,
      acceptance_criteria: manualForm.acceptanceCriteria
    }

    if (props.editData) {
      await updateRequirementAnalysis(props.editData.requirement_id, submitData)
      ElMessage.success('更新成功')
    } else {
      await addRequirementAnalysis(submitData)
      ElMessage.success('创建成功')
    }

    emit('success')
    visible.value = false

  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForms = () => {
  aiForm.projectId = props.defaultProjectId
  aiForm.description = ''
  aiForm.analysisTypes = ['functional', 'acceptance']
  aiForm.useRag = false

  manualForm.projectId = props.defaultProjectId
  manualForm.requirementName = ''
  manualForm.requirementType = 'functional'
  manualForm.priority = 'medium'
  manualForm.module = ''
  manualForm.description = ''
  manualForm.functionalRequirements = ''
  manualForm.acceptanceCriteria = ''
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 监听对话框打开
watch(visible, (val) => {
  if (val) {
    loadProjects()
    if (props.editData) {
      isAIMode.value = false
      // 填充编辑数据
      manualForm.projectId = props.editData.project_id
      manualForm.requirementName = props.editData.requirement_name
      manualForm.requirementType = props.editData.requirement_type || 'functional'
      manualForm.priority = props.editData.priority || 'medium'
      manualForm.module = props.editData.module || ''
      manualForm.description = props.editData.description || ''
      manualForm.functionalRequirements = props.editData.functional_requirements || ''
      manualForm.acceptanceCriteria = props.editData.acceptance_criteria || ''
    } else {
      resetForms()
    }
  }
})
</script>

<style scoped lang="scss">
.mode-switch {
  text-align: center;

  .el-radio-button {
    :deep(.el-radio-button__inner) {
      display: flex;
      align-items: center;
      gap: 6px;
    }
  }
}

.ai-mode-content {
  .quick-examples {
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
}

.form-tip {
  font-size: 12px;
  color: #909399;
}

:deep(.el-alert__content) {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>

