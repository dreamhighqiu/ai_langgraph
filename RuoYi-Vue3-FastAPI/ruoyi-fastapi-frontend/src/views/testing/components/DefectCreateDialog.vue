<template>
  <el-dialog
    v-model="visible"
    :title="isAIMode ? 'AI 智能缺陷分析' : (editData ? '编辑缺陷分析' : '新建缺陷分析')"
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

        <!-- 缺陷描述输入 -->
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

          <el-form-item label="缺陷标题" prop="title" required>
            <el-input v-model="aiForm.title" placeholder="简要描述缺陷现象" />
          </el-form-item>

          <el-form-item label="缺陷描述" prop="description" required>
            <el-input
              v-model="aiForm.description"
              type="textarea"
              :rows="6"
              placeholder="请详细描述缺陷情况，包括：
- 缺陷现象
- 复现步骤
- 期望行为
- 实际行为
- 相关日志或截图描述

AI 将分析缺陷根因并提供修复建议..."
              :maxlength="5000"
              show-word-limit
            />
          </el-form-item>

          <!-- 快捷示例 -->
          <div class="quick-examples mb-4">
            <span class="label">试试这些：</span>
            <el-button size="small" @click="applyExample('crash')">
              <el-icon><MagicStick /></el-icon>
              应用崩溃缺陷
            </el-button>
            <el-button size="small" @click="applyExample('performance')">
              <el-icon><MagicStick /></el-icon>
              性能问题缺陷
            </el-button>
          </div>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="严重程度" prop="severity">
                <el-select v-model="aiForm.severity" style="width: 100%">
                  <el-option label="致命" value="critical" />
                  <el-option label="严重" value="high" />
                  <el-option label="一般" value="medium" />
                  <el-option label="轻微" value="low" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="优先级" prop="priority">
                <el-select v-model="aiForm.priority" style="width: 100%">
                  <el-option label="紧急" value="urgent" />
                  <el-option label="高" value="high" />
                  <el-option label="中" value="medium" />
                  <el-option label="低" value="low" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="缺陷类型" prop="defectType">
                <el-select v-model="aiForm.defectType" style="width: 100%">
                  <el-option label="功能缺陷" value="functional" />
                  <el-option label="性能问题" value="performance" />
                  <el-option label="安全漏洞" value="security" />
                  <el-option label="UI问题" value="ui" />
                  <el-option label="兼容性" value="compatibility" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 分析类型选择 -->
          <el-form-item label="分析内容">
            <el-checkbox-group v-model="aiForm.analysisTypes">
              <el-checkbox label="root_cause">根因分析</el-checkbox>
              <el-checkbox label="impact">影响分析</el-checkbox>
              <el-checkbox label="fix">修复建议</el-checkbox>
              <el-checkbox label="prevention">预防措施</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <!-- RAG 检索 -->
          <el-form-item label="知识库增强">
            <el-switch v-model="aiForm.useRag" />
            <span class="form-tip ml-2">启用后，AI 会检索相关代码和历史缺陷来增强分析结果</span>
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
            <el-form-item label="分析名称" prop="analysisName" required>
              <el-input v-model="manualForm.analysisName" placeholder="请输入分析名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="缺陷标题" prop="defectTitle" required>
          <el-input v-model="manualForm.defectTitle" placeholder="请输入缺陷标题" />
        </el-form-item>

        <el-form-item label="缺陷描述" prop="defectDescription">
          <el-input
            v-model="manualForm.defectDescription"
            type="textarea"
            :rows="4"
            placeholder="请详细描述缺陷现象..."
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="严重程度" prop="severity">
              <el-select v-model="manualForm.severity" style="width: 100%">
                <el-option label="致命" value="critical" />
                <el-option label="严重" value="high" />
                <el-option label="一般" value="medium" />
                <el-option label="轻微" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="manualForm.priority" style="width: 100%">
                <el-option label="紧急" value="urgent" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="缺陷类型" prop="defectType">
              <el-select v-model="manualForm.defectType" style="width: 100%">
                <el-option label="功能缺陷" value="functional" />
                <el-option label="性能问题" value="performance" />
                <el-option label="安全漏洞" value="security" />
                <el-option label="UI问题" value="ui" />
                <el-option label="兼容性" value="compatibility" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="根因分析" prop="rootCauseAnalysis">
          <el-input
            v-model="manualForm.rootCauseAnalysis"
            type="textarea"
            :rows="3"
            placeholder="分析缺陷产生的根本原因..."
          />
        </el-form-item>

        <el-form-item label="影响分析" prop="impactAnalysis">
          <el-input
            v-model="manualForm.impactAnalysis"
            type="textarea"
            :rows="3"
            placeholder="分析缺陷的影响范围和严重程度..."
          />
        </el-form-item>

        <el-form-item label="修复建议" prop="fixSuggestions">
          <el-input
            v-model="manualForm.fixSuggestions"
            type="textarea"
            :rows="3"
            placeholder="提供修复建议..."
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
        :disabled="!aiForm.title.trim() || !aiForm.description.trim()"
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
import { addDefectAnalysis, updateDefectAnalysis } from '@/api/testing/defectAnalysis'
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
  title: '',
  description: '',
  severity: 'medium',
  priority: 'medium',
  defectType: 'functional',
  analysisTypes: ['root_cause', 'fix'],
  useRag: false
})

// 手动模式表单
const manualForm = reactive({
  projectId: null,
  analysisName: '',
  defectTitle: '',
  defectDescription: '',
  severity: 'medium',
  priority: 'medium',
  defectType: 'functional',
  rootCauseAnalysis: '',
  impactAnalysis: '',
  fixSuggestions: ''
})

// AI 表单验证规则
const aiRules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  title: [{ required: true, message: '请输入缺陷标题', trigger: 'blur' }],
  description: [
    { required: true, message: '请输入缺陷描述', trigger: 'blur' },
    { min: 20, message: '描述至少需要20个字符', trigger: 'blur' }
  ]
}

// 手动表单验证规则
const manualRules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  analysisName: [{ required: true, message: '请输入分析名称', trigger: 'blur' }],
  defectTitle: [{ required: true, message: '请输入缺陷标题', trigger: 'blur' }]
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
  if (type === 'crash') {
    aiForm.title = '用户登录时应用崩溃'
    aiForm.description = `缺陷描述：
用户在登录页面点击"登录"按钮后，应用闪退并返回到手机桌面

复现步骤：
1. 打开应用
2. 在登录页面输入用户名和密码
3. 点击"登录"按钮
4. 应用立即崩溃

期望行为：
点击登录按钮后，应进行身份验证并跳转到首页

实际行为：
应用崩溃，显示"应用程序已停止运行"

测试环境：
- 设备：iPhone 13
- 系统版本：iOS 16.1
- 应用版本：2.3.1

日志信息：
Uncaught Exception: nil is not an object (evaluating 'user.id')`
    aiForm.severity = 'critical'
    aiForm.defectType = 'functional'
  } else if (type === 'performance') {
    aiForm.title = '列表加载耗时过长'
    aiForm.description = `缺陷描述：
订单列表页面加载时间超过10秒，用户体验差

复现步骤：
1. 登录系统
2. 进入"我的订单"页面
3. 等待页面加载

期望行为：
页面加载时间应在2秒以内

实际行为：
页面加载需要10-15秒，期间显示空白页面

测试环境：
- 网络：4G
- 测试账号：有1000+历史订单
- 服务器：生产环境

性能数据：
- 接口响应时间：8.5秒
- 前端渲染时间：3.2秒
- 首屏加载：11.7秒`
    aiForm.severity = 'high'
    aiForm.defectType = 'performance'
  }
}

// AI 分析
const handleAIAnalyze = async () => {
  const valid = await aiFormRef.value?.validate()
  if (!valid) return

  // 构建AI聊天提示词
  const analysisTypesText = aiForm.analysisTypes.map(t => {
    const map = {
      root_cause: '根因分析',
      impact: '影响分析',
      fix: '修复建议',
      prevention: '预防措施'
    }
    return map[t]
  }).join('、')

  const severityText = {
    critical: '致命',
    high: '严重',
    medium: '一般',
    low: '轻微'
  }[aiForm.severity]

  const chatPrompt = `请帮我分析以下缺陷，并提供专业的分析报告。

缺陷标题：${aiForm.title}

缺陷描述：
${aiForm.description.trim()}

严重程度：${severityText}
缺陷类型：${aiForm.defectType}

分析要求：
- 需要分析的内容：${analysisTypesText}
- 请深入分析缺陷产生的根本原因
- 评估缺陷对系统和用户的影响
- 提供具体可行的修复方案
- 建议预防措施避免类似问题
${aiForm.useRag ? '\n请先使用 rag_query_tool 从知识库检索相关的代码和历史缺陷信息来增强分析结果。' : ''}

请按照以下格式输出分析结果：
1. 缺陷概述
2. 根本原因分析
3. 影响范围评估
4. 修复建议
5. 测试建议
6. 预防措施

分析完成后，请使用 save_defect_analysis_tool 工具保存分析结果。`

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
      analysis_name: manualForm.analysisName,
      defect_title: manualForm.defectTitle,
      defect_description: manualForm.defectDescription,
      severity: manualForm.severity,
      priority: manualForm.priority,
      defect_type: manualForm.defectType,
      root_cause_analysis: manualForm.rootCauseAnalysis,
      impact_analysis: manualForm.impactAnalysis,
      fix_suggestions: manualForm.fixSuggestions
    }

    if (props.editData) {
      await updateDefectAnalysis(props.editData.analysis_id, submitData)
      ElMessage.success('更新成功')
    } else {
      await addDefectAnalysis(submitData)
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
  aiForm.title = ''
  aiForm.description = ''
  aiForm.severity = 'medium'
  aiForm.priority = 'medium'
  aiForm.defectType = 'functional'
  aiForm.analysisTypes = ['root_cause', 'fix']
  aiForm.useRag = false

  manualForm.projectId = props.defaultProjectId
  manualForm.analysisName = ''
  manualForm.defectTitle = ''
  manualForm.defectDescription = ''
  manualForm.severity = 'medium'
  manualForm.priority = 'medium'
  manualForm.defectType = 'functional'
  manualForm.rootCauseAnalysis = ''
  manualForm.impactAnalysis = ''
  manualForm.fixSuggestions = ''
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
      manualForm.analysisName = props.editData.analysis_name
      manualForm.defectTitle = props.editData.defect_title
      manualForm.defectDescription = props.editData.defect_description || ''
      manualForm.severity = props.editData.severity || 'medium'
      manualForm.priority = props.editData.priority || 'medium'
      manualForm.defectType = props.editData.defect_type || 'functional'
      manualForm.rootCauseAnalysis = props.editData.root_cause_analysis || ''
      manualForm.impactAnalysis = props.editData.impact_analysis || ''
      manualForm.fixSuggestions = props.editData.fix_suggestions || ''
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

