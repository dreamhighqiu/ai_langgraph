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

          <!-- 输入方式选择 -->
          <el-form-item label="输入方式">
            <el-radio-group v-model="aiForm.inputMode" @change="handleInputModeChange">
              <el-radio value="text">文本输入</el-radio>
              <el-radio value="document">文档上传</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 文本输入模式 -->
          <template v-if="aiForm.inputMode === 'text'">
            <el-form-item label="缺陷标题" prop="title" :required="aiForm.inputMode === 'text'">
              <el-input v-model="aiForm.title" placeholder="简要描述缺陷现象" />
            </el-form-item>

            <el-form-item label="缺陷描述" prop="description" :required="aiForm.inputMode === 'text'">
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
                placeholder="例如：重点关注根本原因分析、需要包含修复建议、关注预防措施等..."
              />
              <div class="form-tip">提供额外的上下文信息，帮助 AI 更好地理解缺陷情况</div>
            </el-form-item>
          </template>

          <!-- 报告模板选择 -->
          <el-form-item label="报告模板">
            <el-select v-model="aiForm.templateName" placeholder="选择报告模板" style="width: 100%">
              <el-option
                v-for="template in defectTemplates"
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
        :loading="generating || uploading"
        :disabled="(aiForm.inputMode === 'text' && (!aiForm.title.trim() || !aiForm.description.trim())) || (aiForm.inputMode === 'document' && aiForm.files.length === 0)"
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
import { addDefectAnalysis, updateDefectAnalysis, getReportTemplates } from '@/api/testing/defectAnalysis'
import { listAllProject } from '@/api/testing/project'
import { uploadDocumentForAI } from '@/api/testing/document'
import { marked } from 'marked'

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
const isAIMode = ref(true) // 默认显示 AI 智能分析 tab
const generating = ref(false)
const submitting = ref(false)
const uploading = ref(false)
const projectList = ref([])
const defectTemplates = ref([])
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
  title: '',
  description: '',
  files: [],
  additionalNotes: '',
  templateName: 'defect_analysis_report.md.jinja2',
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
  title: [
    { 
      required: false, 
      message: '请输入缺陷标题', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (aiForm.inputMode === 'text') {
          if (!value || value.trim().length === 0) {
            callback(new Error('请输入缺陷标题'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      }
    }
  ],
  description: [
    { 
      required: false, 
      message: '请输入缺陷描述', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (aiForm.inputMode === 'text') {
          if (!value || value.trim().length === 0) {
            callback(new Error('请输入缺陷描述'))
          } else if (value.trim().length < 1) {
            callback(new Error('描述至少需要1个字符'))
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

// 加载报告模板列表
const loadTemplates = async () => {
  try {
    const res = await getReportTemplates()
    if (res.code === 200 && res.data) {
      defectTemplates.value = res.data.defect_analysis || []
      // 设置默认模板
      if (defectTemplates.value.length > 0 && !aiForm.templateName) {
        aiForm.templateName = defectTemplates.value[0]
      }
    }
  } catch (error) {
    console.error('加载模板列表失败:', error)
    // 设置默认模板
    defectTemplates.value = ['defect_analysis_report.md.jinja2']
    aiForm.templateName = 'defect_analysis_report.md.jinja2'
  }
}

// 获取模板显示名称
const getTemplateDisplayName = (templateName) => {
  const nameMap = {
    'defect_analysis_report.md.jinja2': '标准缺陷分析报告'
  }
  return nameMap[templateName] || templateName.replace('.jinja2', '').replace(/_/g, ' ')
}

// 渲染模板预览
const renderTemplatePreview = () => {
  // 使用 Markdown 格式生成预览内容
  const markdownContent = `# 缺陷分析报告模板预览

## 模板信息

- **模板名称**: ${aiForm.templateName}
- **模板类型**: 标准缺陷分析报告

---

## 报告结构

### 1. 基本信息
- 缺陷标题
- 缺陷类型
- 严重程度
- 优先级
- 发现时间
- 分析人员

### 2. 缺陷描述
- 缺陷现象
- 复现步骤
- 期望行为
- 实际行为
- 环境信息

### 3. 缺陷概述
- 缺陷摘要
- 影响范围
- 紧急程度

### 4. 根本原因分析
- 技术原因
- 业务原因
- 流程原因
- 根本原因总结

### 5. 影响分析
- 功能影响
- 用户影响
- 业务影响
- 系统影响

### 6. 复现步骤
- 详细复现步骤
- 复现环境
- 复现概率

### 7. 受影响模块
- 代码模块
- 功能模块
- 系统模块

### 8. 修复建议
- 临时修复方案
- 长期解决方案
- 修复优先级
- 修复工作量评估

### 9. 测试建议
- 验证测试用例
- 回归测试建议
- 测试重点

### 10. 预防措施
- 代码层面预防
- 流程层面预防
- 测试层面预防

### 11. 相似缺陷
- 历史相似缺陷
- 关联缺陷
- 缺陷模式分析

### 12. RAG检索信息（如果使用）
- 检索到的相关缺陷
- 检索到的解决方案
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
    aiForm.title = ''
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
      chatPrompt = `请帮我从文档/图片生成缺陷分析。

上传的文件信息：
${filesInfo}

`

      // RAG 检索逻辑：文档上传模式，RAG 检索附加说明
      let ragQuery = ''
      if (aiForm.useRag && aiForm.additionalNotes) {
        ragQuery = `\n**重要：请先使用 rag_query_tool 从知识库检索与以下附加说明相关的内容：**
附加说明：
${aiForm.additionalNotes}

检索完成后，将检索到的 RAG 内容与文档解析内容结合，生成完整的缺陷分析报告。
RAG 检索内容将作为补充上下文，帮助生成更准确的分析结果。\n`
      } else if (aiForm.useRag) {
        ragQuery = `\n**重要：请先使用 rag_query_tool 从知识库检索与文档内容相关的历史缺陷、解决方案等信息。**
检索完成后，将检索到的 RAG 内容与文档解析内容结合，生成完整的缺陷分析报告。
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
1. 首先使用 parse_document_from_url 工具解析文档内容，提取关键缺陷信息和错误描述。
${ragQuery || ''}${!aiForm.useRag ? '2. 基于解析的文档内容生成完整的缺陷分析报告。' : '2. 将 RAG 检索内容与文档解析内容结合，生成完整的缺陷分析报告。'}
3. 使用 save_defect_analysis_tool 工具保存分析结果。
4. 使用 generate_defect_analysis_report_tool 工具生成报告（使用模板：${aiForm.templateName}）。

**注意**：${aiForm.useRag ? '生成缺陷分析时，必须结合 RAG 检索内容和文档解析内容，确保分析结果既基于文档内容，又参考了知识库中的相关信息。' : '生成缺陷分析时，完全基于文档解析内容，确保分析结果准确反映文档中的缺陷信息。'}`

    } else {
      // 文本输入模式
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

      // RAG 检索逻辑：文本输入模式，RAG 检索缺陷描述
      let ragQuery = ''
      if (aiForm.useRag && aiForm.description.trim()) {
        ragQuery = `\n**重要：请先使用 rag_query_tool 从知识库检索与以下缺陷描述相关的内容：**
缺陷描述：
${aiForm.description.trim()}

检索完成后，将检索到的 RAG 内容与缺陷描述结合，生成完整的缺陷分析报告。
RAG 检索内容将作为补充上下文，帮助生成更准确的分析结果。\n`
      }

      chatPrompt = `请帮我分析以下缺陷，并提供专业的分析报告。

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

${ragQuery || ''}**工作流程：**
${aiForm.useRag ? '1. 首先使用 rag_query_tool 从知识库检索与缺陷描述相关的内容。\n2. 将 RAG 检索内容与缺陷描述结合，生成完整的缺陷分析报告。' : '1. 基于缺陷描述生成完整的缺陷分析报告。'}
3. 使用 save_defect_analysis_tool 工具保存分析结果。
4. 使用 generate_defect_analysis_report_tool 工具生成报告（使用模板：${aiForm.templateName}）。

请按照以下格式输出分析结果：
1. 缺陷概述
2. 根本原因分析
3. 影响范围评估
4. 修复建议
5. 测试建议
6. 预防措施

**注意**：${aiForm.useRag ? '生成缺陷分析时，必须结合 RAG 检索内容和缺陷描述，确保分析结果既基于用户输入，又参考了知识库中的相关信息。' : '生成缺陷分析时，完全基于缺陷描述，确保分析结果准确反映用户的缺陷信息。'}`
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
    ElMessage.error('生成缺陷分析失败')
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
  aiForm.inputMode = 'text'
  aiForm.title = ''
  aiForm.description = ''
  aiForm.files = []
  aiForm.additionalNotes = ''
  aiForm.templateName = defectTemplates.value.length > 0 ? defectTemplates.value[0] : 'defect_analysis_report.md.jinja2'
  aiForm.severity = 'medium'
  aiForm.priority = 'medium'
  aiForm.defectType = 'functional'
  aiForm.analysisTypes = ['root_cause', 'fix']
  aiForm.useRag = false
  uploadedFiles.value = []

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
    loadTemplates()
    if (props.editData) {
      isAIMode.value = false // 编辑模式使用手动录入
      // 填充编辑数据
      manualForm.projectId = props.editData.project_id
      manualForm.analysisName = props.editData.analysis_name
      manualForm.defectTitle = props.editData.defect_title
      manualForm.defectDescription = props.editData.defect_description || ''
      manualForm.severity = props.editData.severity || 'medium'
      manualForm.priority = props.editData.priority || 'medium'
      manualForm.defectType = props.editData.defect_type || 'functional'
      // 处理对象类型字段，转换为字符串
      manualForm.rootCauseAnalysis = typeof props.editData.root_cause_analysis === 'object' 
        ? JSON.stringify(props.editData.root_cause_analysis, null, 2) 
        : (props.editData.root_cause_analysis || '')
      manualForm.impactAnalysis = typeof props.editData.impact_analysis === 'object' 
        ? JSON.stringify(props.editData.impact_analysis, null, 2) 
        : (props.editData.impact_analysis || '')
      manualForm.fixSuggestions = Array.isArray(props.editData.fix_suggestions)
        ? props.editData.fix_suggestions.map(item => 
            typeof item === 'object' ? JSON.stringify(item, null, 2) : String(item)
          ).join('\n\n')
        : (typeof props.editData.fix_suggestions === 'object' 
          ? JSON.stringify(props.editData.fix_suggestions, null, 2) 
          : (props.editData.fix_suggestions || ''))
    } else {
      isAIMode.value = true // 新建模式默认使用 AI 智能分析
      resetForms()
    }
  }
})

// 监听 defaultProjectId 的变化，自动更新表单中的项目ID
watch(() => props.defaultProjectId, (newVal, oldVal) => {
  console.log('[DefectCreateDialog] defaultProjectId 变化:', { 旧值: oldVal, 新值: newVal })
  
  // 只在 newVal 有效且不为 0 时更新
  if (newVal && newVal !== 0 && newVal !== '0') {
    if (!aiForm.projectId || aiForm.projectId === null || aiForm.projectId === 0) {
      aiForm.projectId = newVal
      console.log('[DefectCreateDialog] ✅ 设置 aiForm.projectId =', newVal)
    } else {
      console.log('[DefectCreateDialog] ⏭️ aiForm.projectId 已有值，跳过:', aiForm.projectId)
    }
    
    if (!manualForm.projectId || manualForm.projectId === null || manualForm.projectId === 0) {
      manualForm.projectId = newVal
      console.log('[DefectCreateDialog] ✅ 设置 manualForm.projectId =', newVal)
    }
  } else {
    console.warn('[DefectCreateDialog] ⚠️ defaultProjectId 无效，不更新表单:', newVal)
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
        border-bottom: 2px solid #f5576c;
      }

      :deep(h2) {
        font-size: 20px;
        font-weight: 600;
        color: #f5576c;
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
        background: #fff0f0;
        border-left: 4px solid #f5576c;
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
</style>

