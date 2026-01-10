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

          <!-- 输入方式选择 -->
          <el-form-item label="输入方式">
            <el-radio-group v-model="aiForm.inputMode" @change="handleInputModeChange">
              <el-radio value="text">文本输入</el-radio>
              <el-radio value="document">文档上传</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 文本输入模式 -->
          <template v-if="aiForm.inputMode === 'text'">
            <el-form-item label="需求描述" prop="description" :required="aiForm.inputMode === 'text'">
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
          </template>

          <!-- 文档上传模式 -->
          <template v-else>
            <el-form-item label="上传文档" prop="files" :required="aiForm.inputMode === 'document'">
              <el-upload
                ref="uploadRef"
                v-model:file-list="aiForm.files"
                class="upload-area"
                drag
                :auto-upload="false"
                :limit="5"
                :accept="acceptTypes"
                :on-exceed="handleExceed"
                :before-upload="beforeUpload"
              >
                <div class="upload-content">
                  <el-icon class="upload-icon"><UploadFilled /></el-icon>
                  <div class="upload-text">
                    <span class="upload-primary">点击上传文件</span>
                    <span class="upload-secondary">或拖拽文件到此处</span>
                  </div>
                  <div class="upload-tips">
                    支持图片 (JPG, PNG, GIF, WebP)、文档 (PDF, Word, TXT)<br />
                    文件大小限制：10MB
                  </div>
                </div>
              </el-upload>
              
              <!-- 已上传的文件列表 -->
              <div v-if="uploadedFiles.length > 0" class="uploaded-files">
                <div v-for="(file, index) in uploadedFiles" :key="index" class="uploaded-file-item">
                  <el-icon class="file-icon"><Document /></el-icon>
                  <span class="file-name">{{ file.file_name }}</span>
                  <el-tag type="success" size="small">已上传</el-tag>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="附加说明">
              <el-input
                v-model="aiForm.additionalNotes"
                type="textarea"
                :rows="3"
                placeholder="例如：重点关注功能需求和非功能需求、需要包含用户故事、关注验收标准等..."
              />
              <div class="form-tip">提供额外的上下文信息，帮助 AI 更好地理解您的需求</div>
            </el-form-item>
          </template>

          <!-- 报告模板选择 -->
          <el-form-item label="报告模板">
            <el-select v-model="aiForm.templateName" placeholder="选择报告模板" style="width: 100%">
              <el-option
                v-for="template in requirementTemplates"
                :key="template"
                :label="getTemplateDisplayName(template)"
                :value="template"
              />
            </el-select>
            <div class="form-tip">
              <el-button text size="small" @click="showTemplatePreview = true">
                <el-icon><View /></el-icon>
                预览模板
              </el-button>
            </div>
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
        :loading="generating || uploading"
        :disabled="(aiForm.inputMode === 'text' && !aiForm.description.trim()) || (aiForm.inputMode === 'document' && aiForm.files.length === 0)"
        @click="handleAIAnalyze"
      >
        <el-icon v-if="!generating && !uploading"><MagicStick /></el-icon>
        {{ uploading ? '上传中...' : generating ? 'AI 分析中...' : '开始 AI 分析' }}
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

    <!-- 模板预览对话框 -->
    <el-dialog
      v-model="showTemplatePreview"
      title="报告模板预览"
      width="800px"
      append-to-body
    >
      <div class="template-preview">
        <el-alert type="info" :closable="false" class="mb-4">
          <template #title>
            当前选择的模板：{{ getTemplateDisplayName(aiForm.templateName) }}
          </template>
        </el-alert>
        <div class="preview-content">
          <el-scrollbar height="500px">
            <div class="markdown-preview" v-html="renderTemplatePreview()"></div>
          </el-scrollbar>
        </div>
      </div>
      <template #footer>
        <el-button @click="showTemplatePreview = false">关闭</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, MagicStick, CircleCheck, UploadFilled, Document, View } from '@element-plus/icons-vue'
import { addRequirementAnalysis, updateRequirementAnalysis } from '@/api/testing/requirementAnalysis'
import { listAllProject } from '@/api/testing/project'
import { uploadDocumentForAI } from '@/api/testing/document'
import { getReportTemplates } from '@/api/testing/requirementAnalysis'
import { marked } from 'marked'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  editData: { type: Object, default: null },
  defaultProjectId: { type: Number, default: null }
})

const emit = defineEmits(['update:modelValue', 'open-chat', 'success'])

// 暴露 projectId 供父组件使用
defineExpose({
  getProjectId: () => aiForm.projectId
})

// 对话框可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 状态
const isAIMode = ref(true) // 默认显示 AI 智能分析 tab
const generating = ref(false)
const submitting = ref(false)
const uploading = ref(false)
const projectList = ref([])
const requirementTemplates = ref([])
const uploadedFiles = ref([])
const showTemplatePreview = ref(false)
const acceptTypes = '.jpg,.jpeg,.png,.gif,.webp,.bmp,.pdf,.doc,.docx,.txt'

// 表单引用
const aiFormRef = ref(null)
const manualFormRef = ref(null)
const uploadRef = ref(null)

// AI 模式表单
const aiForm = reactive({
  projectId: null,
  inputMode: 'text', // 'text' 或 'document'
  description: '',
  files: [],
  additionalNotes: '',
  templateName: 'requirement_analysis_report.md.jinja2',
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
    { 
      required: false,  // 改为非必填，在 validator 中根据输入模式判断
      message: '请输入需求描述', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (aiForm.inputMode === 'text') {
          if (!value || value.trim().length === 0) {
            callback(new Error('请输入需求描述'))
          } else if (value.trim().length < 5) {
            callback(new Error('描述至少需要5个字符'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      }
    }
  ],
  files: [
    {
      required: true,
      message: '请上传至少一个文件',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (aiForm.inputMode === 'document' && (!value || value.length === 0)) {
          callback(new Error('请上传至少一个文件'))
        } else {
          callback()
        }
      }
    }
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

// 加载报告模板列表
const loadTemplates = async () => {
  try {
    const res = await getReportTemplates()
    if (res.code === 200 && res.data) {
      requirementTemplates.value = res.data.requirement_analysis || []
      // 设置默认模板
      if (requirementTemplates.value.length > 0 && !aiForm.templateName) {
        aiForm.templateName = requirementTemplates.value[0]
      }
    }
  } catch (error) {
    console.error('加载模板列表失败:', error)
    // 设置默认模板
    requirementTemplates.value = ['requirement_analysis_report.md.jinja2']
    aiForm.templateName = 'requirement_analysis_report.md.jinja2'
  }
}

// 获取模板显示名称
const getTemplateDisplayName = (templateName) => {
  const nameMap = {
    'requirement_analysis_report.md.jinja2': '标准需求分析报告'
  }
  return nameMap[templateName] || templateName.replace('.jinja2', '').replace(/_/g, ' ')
}

// 渲染模板预览
const renderTemplatePreview = () => {
  // 使用 Markdown 格式生成预览内容
  const markdownContent = `# 需求分析报告模板预览

## 模板信息

- **模板名称**: ${aiForm.templateName}
- **模板类型**: 标准需求分析报告

---

## 报告结构

### 1. 基本信息
- 项目信息
- 分析时间
- 分析人员
- 分析状态

### 2. 需求概述
- 需求背景
- 需求目标
- 业务价值

### 3. 功能需求
- 核心功能点
- 功能详细描述
- 功能优先级

### 4. 非功能需求
- 性能要求
- 安全要求
- 可用性要求
- 兼容性要求

### 5. 用户故事
- 用户角色
- 用户场景
- 验收标准

### 6. 验收标准
- 功能验收标准
- 性能验收标准
- 质量验收标准

### 7. 依赖关系
- 技术依赖
- 业务依赖
- 外部系统依赖

### 8. 风险评估
- 技术风险
- 业务风险
- 进度风险
- 风险缓解措施

### 9. 改进建议
- 功能优化建议
- 架构优化建议
- 流程优化建议

### 10. 质量评分
- 完整性评分
- 清晰度评分
- 一致性评分
- 可测试性评分
- 总体评分

### 11. RAG检索信息（如果使用）
- 检索到的相关文档
- 检索到的实体信息
- 知识库上下文

---

> **注**: 实际报告内容会根据分析结果动态生成，以上仅为模板结构预览。`
  
  try {
    return marked(markdownContent, { breaks: true, gfm: true })
  } catch (e) {
    return markdownContent.replace(/\n/g, '<br>')
  }
}

// 文件上传前验证
const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  return true
}

// 超出限制处理
const handleExceed = (files) => {
  ElMessage.warning('最多只能上传 5 个文件')
}

// 输入方式切换
const handleInputModeChange = () => {
  if (aiForm.inputMode === 'text') {
    aiForm.files = []
    uploadedFiles.value = []
  } else {
    aiForm.description = ''
  }
}

// 上传文件到 MinIO
const uploadFilesToMinIO = async () => {
  if (aiForm.files.length === 0) return false
  
  uploading.value = true
  uploadedFiles.value = []
  
  try {
    for (const fileItem of aiForm.files) {
      const file = fileItem.raw || fileItem
      
      ElMessage.info(`正在上传文件: ${file.name}...`)
      
      const result = await uploadDocumentForAI(aiForm.projectId, file)
      
      if (result.success) {
        uploadedFiles.value.push(result.data)
        ElMessage.success(`文件 ${file.name} 上传成功`)
      } else {
        ElMessage.error(`文件 ${file.name} 上传失败: ${result.message}`)
        return false
      }
    }
    
    return true
  } catch (error) {
    console.error('文件上传失败:', error)
    ElMessage.error('文件上传失败')
    return false
  } finally {
    uploading.value = false
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

  generating.value = true

  try {
    let chatPrompt = ''

    if (aiForm.inputMode === 'document') {
      // 文档上传模式
      if (aiForm.files.length === 0) {
        ElMessage.error('请上传至少一个文件')
        generating.value = false
        return
      }

      // 1. 先上传文件到 MinIO
      const uploadSuccess = await uploadFilesToMinIO()
      
      if (!uploadSuccess) {
        generating.value = false
        return
      }

      // 2. 构建文件信息描述
      const filesInfo = uploadedFiles.value.map((f, index) => {
        return `文件 ${index + 1}:
- 文件名: ${f.file_name}
- 文件类型: ${f.content_type}
- 文件大小: ${(f.file_size / 1024).toFixed(2)} KB
- 文件URL: ${f.url}`
      }).join('\n\n')

      // 3. 构建完整提示词
      chatPrompt = `请帮我从文档/图片生成需求分析。

上传的文件信息：
${filesInfo}

`

      // RAG 检索逻辑：文档上传模式，RAG 检索附加说明
      let ragQuery = ''
      if (aiForm.useRag && aiForm.additionalNotes) {
        ragQuery = `\n**重要：请先使用 rag_query_tool 从知识库检索与以下附加说明相关的内容：**
附加说明：
${aiForm.additionalNotes}

检索完成后，将检索到的 RAG 内容与文档解析内容结合，生成完整的需求分析报告。
RAG 检索内容将作为补充上下文，帮助生成更准确的分析结果。\n`
      } else if (aiForm.useRag) {
        ragQuery = `\n**重要：请先使用 rag_query_tool 从知识库检索与文档内容相关的历史需求、技术文档等信息。**
检索完成后，将检索到的 RAG 内容与文档解析内容结合，生成完整的需求分析报告。
RAG 检索内容将作为补充上下文，帮助生成更准确的分析结果。\n`
      }

      if (aiForm.additionalNotes && !aiForm.useRag) {
        chatPrompt += `附加说明：
${aiForm.additionalNotes}

`
      }

      chatPrompt += `项目ID：${aiForm.projectId}
报告模板：${aiForm.templateName}
使用 RAG 检索：${aiForm.useRag ? '是' : '否'}

**工作流程：**
1. 首先使用 parse_document_from_url 工具解析文档内容，提取关键功能点和需求信息。
${ragQuery || ''}${!aiForm.useRag ? '2. 基于解析的文档内容生成完整的需求分析报告。' : '2. 将 RAG 检索内容与文档解析内容结合，生成完整的需求分析报告。'}
3. 使用 save_requirement_analysis_tool 工具保存分析结果。
4. 使用 generate_requirement_analysis_report_tool 工具生成报告（使用模板：${aiForm.templateName}）。

**注意**：${aiForm.useRag ? '生成需求分析时，必须结合 RAG 检索内容和文档解析内容，确保分析结果既基于文档内容，又参考了知识库中的相关信息。' : '生成需求分析时，完全基于文档解析内容，确保分析结果准确反映文档中的需求信息。'}`

    } else {
      // 文本输入模式
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

      // RAG 检索逻辑：文本输入模式，RAG 检索需求描述
      let ragQuery = ''
      if (aiForm.useRag && aiForm.description.trim()) {
        ragQuery = `\n**重要：请先使用 rag_query_tool 从知识库检索与以下需求描述相关的内容：**
需求描述：
${aiForm.description.trim()}

检索完成后，将检索到的 RAG 内容与需求描述结合，生成完整的需求分析报告。
RAG 检索内容将作为补充上下文，帮助生成更准确的分析结果。\n`
      }

      chatPrompt = `请帮我分析以下需求，并提取关键信息。

需求描述：
${aiForm.description.trim()}

分析要求：
- 提取并整理：${analysisTypesText}
- 识别潜在的技术风险和依赖
- 生成可测试的验收标准

${ragQuery || ''}**工作流程：**
${aiForm.useRag ? '1. 首先使用 rag_query_tool 从知识库检索与需求描述相关的内容。\n2. 将 RAG 检索内容与需求描述结合，生成完整的需求分析报告。' : '1. 基于需求描述生成完整的需求分析报告。'}
3. 使用 save_requirement_analysis_tool 工具保存分析结果。
4. 使用 generate_requirement_analysis_report_tool 工具生成报告（使用模板：${aiForm.templateName}）。

请按照以下格式输出分析结果：
1. 需求概述
2. 功能需求清单
3. 非功能需求（如性能、安全等）
4. 用户故事（采用 As a ... I want ... So that ... 格式）
5. 验收标准
6. 技术风险和依赖

**注意**：${aiForm.useRag ? '生成需求分析时，必须结合 RAG 检索内容和需求描述，确保分析结果既基于用户输入，又参考了知识库中的相关信息。' : '生成需求分析时，完全基于需求描述，确保分析结果准确反映用户的需求。'}`
    }

    // 触发打开AI聊天，传递 projectId
    emit('open-chat', {
      prompt: chatPrompt,
      projectId: aiForm.projectId
    })
    
    // 关闭对话框
    visible.value = false
    
    ElMessage.success(aiForm.inputMode === 'document' ? '文件已上传，正在启动 AI 分析...' : '正在启动 AI 分析...')

  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成需求分析失败')
  } finally {
    generating.value = false
  }
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
  aiForm.inputMode = 'text'
  aiForm.description = ''
  aiForm.files = []
  aiForm.additionalNotes = ''
  aiForm.templateName = requirementTemplates.value.length > 0 ? requirementTemplates.value[0] : 'requirement_analysis_report.md.jinja2'
  aiForm.analysisTypes = ['functional', 'acceptance']
  aiForm.useRag = false
  uploadedFiles.value = []

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
    loadTemplates()
    if (props.editData) {
      isAIMode.value = false // 编辑模式使用手动录入
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
      isAIMode.value = true // 新建模式默认使用 AI 智能分析
      resetForms()
    }
  }
})

// 监听 defaultProjectId 的变化，自动更新表单中的项目ID
watch(() => props.defaultProjectId, (newVal, oldVal) => {
  console.log('[RequirementCreateDialog] defaultProjectId 变化:', { 旧值: oldVal, 新值: newVal })
  
  // 只在 newVal 有效且不为 0 时更新
  if (newVal && newVal !== 0 && newVal !== '0') {
    if (!aiForm.projectId || aiForm.projectId === null || aiForm.projectId === 0) {
      aiForm.projectId = newVal
      console.log('[RequirementCreateDialog] ✅ 设置 aiForm.projectId =', newVal)
    } else {
      console.log('[RequirementCreateDialog] ⏭️ aiForm.projectId 已有值，跳过:', aiForm.projectId)
    }
    
    if (!manualForm.projectId || manualForm.projectId === null || manualForm.projectId === 0) {
      manualForm.projectId = newVal
      console.log('[RequirementCreateDialog] ✅ 设置 manualForm.projectId =', newVal)
    }
  } else {
    console.warn('[RequirementCreateDialog] ⚠️ defaultProjectId 无效，不更新表单:', newVal)
  }
}, { immediate: true })
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

.template-preview {
  .preview-content {
    .markdown-preview {
      padding: 24px;
      background: #ffffff;
      border-radius: 8px;
      border: 1px solid #e4e7ed;
      line-height: 1.8;
      color: #303133;
      font-size: 14px;

      :deep(h1) {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid #409eff;
      }

      :deep(h2) {
        font-size: 20px;
        font-weight: 600;
        color: #409eff;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #e4e7ed;
      }

      :deep(h3) {
        font-size: 16px;
        font-weight: 600;
        color: #606266;
        margin: 20px 0 12px 0;
      }

      :deep(p) {
        margin: 12px 0;
        line-height: 1.8;
      }

      :deep(ul), :deep(ol) {
        margin: 12px 0;
        padding-left: 24px;

        li {
          margin: 8px 0;
          line-height: 1.8;
        }
      }

      :deep(blockquote) {
        margin: 16px 0;
        padding: 12px 16px;
        background: #f0f9ff;
        border-left: 4px solid #409eff;
        border-radius: 4px;
        color: #606266;
        font-style: italic;
      }

      :deep(code) {
        background: #f5f7fa;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #e6a23c;
      }

      :deep(pre) {
        background: #2d2d2d;
        color: #f8f8f2;
        padding: 16px;
        border-radius: 6px;
        overflow-x: auto;
        margin: 16px 0;

        code {
          background: transparent;
          padding: 0;
          color: inherit;
        }
      }

      :deep(hr) {
        margin: 24px 0;
        border: none;
        border-top: 1px solid #e4e7ed;
      }

      :deep(strong) {
        font-weight: 600;
        color: #303133;
      }

      :deep(em) {
        font-style: italic;
        color: #909399;
      }

      :deep(table) {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;

        th, td {
          padding: 10px 12px;
          border: 1px solid #e4e7ed;
          text-align: left;
        }

        th {
          background: #f5f7fa;
          font-weight: 600;
          color: #303133;
        }

        tr:nth-child(even) {
          background: #fafafa;
        }
      }
    }
  }
}

:deep(.el-alert__content) {
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-area {
  width: 100%;

  :deep(.el-upload-dragger) {
    width: 100%;
    padding: 40px 20px;
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    background: #fafafa;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
      background: #f0f9ff;
    }
  }
}

.upload-content {
  text-align: center;

  .upload-icon {
    font-size: 48px;
    color: #409eff;
    margin-bottom: 16px;
  }

  .upload-text {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 12px;

    .upload-primary {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }

    .upload-secondary {
      font-size: 14px;
      color: #909399;
    }
  }

  .upload-tips {
    font-size: 12px;
    color: #909399;
    line-height: 1.5;
  }
}

.uploaded-files {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;

  .uploaded-file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    margin-bottom: 8px;
    background: white;
    border-radius: 4px;

    &:last-child {
      margin-bottom: 0;
    }

    .file-icon {
      color: #409eff;
    }

    .file-name {
      flex: 1;
      font-size: 14px;
      color: #303133;
    }
  }
}
</style>

