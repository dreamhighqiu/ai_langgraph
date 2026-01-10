<template>
  <el-dialog
    v-model="visible"
    title="从文档/图片生成需求分析"
    width="750px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 头部信息 -->
    <div class="dialog-header">
      <div class="header-icon">
        <el-icon :size="24"><Document /></el-icon>
      </div>
      <div class="header-text">
        <h3>从文档/图片生成需求分析</h3>
        <p>上传需求文档、规格说明或界面截图，AI 将自动分析内容并生成结构化的需求分析报告</p>
      </div>
    </div>

    <!-- 安全提示 -->
    <el-alert type="success" :closable="false" class="mb-4">
      <template #title>
        <el-icon><CircleCheck /></el-icon>
        您的数据是安全的，不会用于 AI 训练
      </template>
    </el-alert>

    <!-- 表单 -->
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <!-- 文件上传 -->
      <el-form-item label="上传文件" prop="files" required>
        <el-upload
          ref="uploadRef"
          v-model:file-list="form.files"
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

      <!-- 附加说明 -->
      <el-form-item label="附加说明">
        <el-input
          v-model="form.additionalNotes"
          type="textarea"
          :rows="3"
          placeholder="例如：重点关注功能需求和非功能需求、需要包含用户故事、关注验收标准等..."
        />
        <div class="form-tip">提供额外的上下文信息，帮助 AI 更好地理解您的需求</div>
      </el-form-item>

      <!-- RAG 检索选项 -->
      <el-form-item label="启用 RAG 检索">
        <el-switch v-model="form.useRag" />
        <div class="form-tip" style="margin-top: 8px">
          <el-icon><InfoFilled /></el-icon>
          启用后，AI 会先从知识库检索相关的历史需求、技术文档等信息，然后结合文档内容生成更准确的需求分析。
        </div>
      </el-form-item>
    </el-form>

    <!-- 底部操作 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="generating"
          @click="handleGenerate"
        >
          {{ generating ? '生成中...' : '开始生成' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Document, CircleCheck, UploadFilled, InfoFilled } from '@element-plus/icons-vue'
import { uploadDocumentForAI } from '@/api/testing/document'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'open-chat'])

const visible = ref(props.modelValue)
const generating = ref(false)
const uploading = ref(false)
const uploadedFiles = ref([])

const acceptTypes = '.jpg,.jpeg,.png,.gif,.webp,.bmp,.pdf,.doc,.docx,.txt'

const form = reactive({
  files: [],
  additionalNotes: '',
  useRag: false
})

const rules = {
  files: [
    { required: true, message: '请上传至少一个文件', trigger: 'change' }
  ]
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

// 上传文件到 MinIO
const uploadFilesToMinIO = async () => {
  if (form.files.length === 0) return false
  
  uploading.value = true
  uploadedFiles.value = []
  
  try {
    for (const fileItem of form.files) {
      const file = fileItem.raw || fileItem
      
      ElMessage.info(`正在上传文件: ${file.name}...`)
      
      const result = await uploadDocumentForAI(props.projectId, file)
      
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

// 构建 AI 提示词
const buildAIPrompt = () => {
  if (uploadedFiles.value.length === 0) return ''
  
  // 构建文件信息描述
  const filesInfo = uploadedFiles.value.map((f, index) => {
    return `文件 ${index + 1}:
- 文件名: ${f.file_name}
- 文件类型: ${f.content_type}
- 文件大小: ${(f.file_size / 1024).toFixed(2)} KB
- 文件URL: ${f.url}`
  }).join('\n\n')
  
  // 构建完整提示词
  let prompt = `请帮我从文档/图片生成需求分析。

上传的文件信息：
${filesInfo}

`

  if (form.additionalNotes) {
    prompt += `附加说明：
${form.additionalNotes}

`
  }

  prompt += `项目ID：${props.projectId}
使用 RAG 检索：${form.useRag ? '是' : '否'}

请先使用 parse_document_from_url 工具解析文档内容，提取关键功能点和需求信息。${form.useRag ? '然后使用 rag_query_tool 从知识库检索相关的历史需求、技术文档等信息，结合文档内容和检索结果生成完整的需求分析报告。' : '然后基于解析的文档内容生成完整的需求分析报告。'}`

  return prompt
}

// 生成需求分析
const handleGenerate = async () => {
  if (form.files.length === 0) {
    ElMessage.error('请上传至少一个文件')
    return
  }

  generating.value = true

  try {
    // 1. 先上传文件到 MinIO
    const uploadSuccess = await uploadFilesToMinIO()
    
    if (!uploadSuccess) {
      generating.value = false
      return
    }
    
    // 2. 构建 AI 提示词
    const chatPrompt = buildAIPrompt()
    
    if (!chatPrompt) {
      ElMessage.error('生成提示词失败')
      generating.value = false
      return
    }
    
    // 3. 触发打开 AI 聊天对话框
    emit('open-chat', chatPrompt)
    
    // 4. 重置表单并关闭对话框
    resetForm()
    visible.value = false
    
    ElMessage.success('文件已上传，正在启动 AI 分析...')

  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成需求分析失败')
  } finally {
    generating.value = false
  }
}

// 重置表单
const resetForm = () => {
  form.files = []
  form.additionalNotes = ''
  form.useRag = false
  uploadedFiles.value = []
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 监听对话框打开
watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    resetForm()
  }
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
    flex-shrink: 0;
  }

  .header-text {
    flex: 1;

    h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    p {
      margin: 0;
      font-size: 14px;
      color: #606266;
      line-height: 1.5;
    }
  }
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

.form-tip {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

