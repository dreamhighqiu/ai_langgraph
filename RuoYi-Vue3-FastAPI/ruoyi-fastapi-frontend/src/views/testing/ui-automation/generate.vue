<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span><el-icon><MagicStick /></el-icon> AI生成Playwright测试脚本</span>
        </div>
      </template>

      <el-form ref="generateFormRef" :model="form" :rules="rules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目" prop="projectId">
              <el-select v-model="form.projectId" placeholder="请选择项目" style="width: 100%" filterable>
                <el-option
                  v-for="project in projectList"
                  :key="project.projectId"
                  :label="project.projectName"
                  :value="project.projectId"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="脚本名称" prop="scriptName">
              <el-input
                v-model="form.scriptName"
                placeholder="例如：login_test"
                clearable
              >
                <template #append>.spec.{{ form.language === 'typescript' ? 'ts' : 'js' }}</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="测试需求" prop="generationPrompt">
          <el-input
            v-model="form.generationPrompt"
            type="textarea"
            :rows="8"
            placeholder="请详细描述需要测试的功能和场景&#10;&#10;示例：&#10;测试用户登录功能：&#10;1. 打开登录页面 http://example.com/login&#10;2. 输入用户名 admin&#10;3. 输入密码 admin123&#10;4. 点击登录按钮&#10;5. 验证页面跳转到 /dashboard&#10;6. 验证页面包含"欢迎"文字"
            show-word-limit
            maxlength="2000"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="脚本语言" prop="language">
              <el-radio-group v-model="form.language">
                <el-radio value="typescript">TypeScript</el-radio>
                <el-radio value="javascript">JavaScript</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="目标浏览器" prop="browser">
              <el-select v-model="form.browser" placeholder="选择浏览器" style="width: 100%">
                <el-option label="Chromium" value="chromium" />
                <el-option label="Firefox" value="firefox" />
                <el-option label="WebKit" value="webkit" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="使用RAG增强">
              <el-switch v-model="form.useRag" />
              <el-tooltip effect="dark" content="启用后将使用知识库增强AI生成效果" placement="top">
                <el-icon class="ml-2"><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" :loading="generating" @click="handleGenerate">
            <el-icon><MagicStick /></el-icon>
            {{ generating ? '生成中...' : 'AI生成脚本' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 生成结果 -->
      <div v-if="generatedScript" class="result-section">
        <el-divider content-position="left">
          <span>生成结果 <el-tag v-if="scriptId" type="success" class="ml-2">Script ID: {{ scriptId }}</el-tag></span>
        </el-divider>

        <div class="script-editor">
          <div class="editor-header">
            <span class="filename">
              <el-icon><DocumentCopy /></el-icon>
              {{ form.scriptName || 'test' }}.spec.{{ form.language === 'typescript' ? 'ts' : 'js' }}
            </span>
            <el-button-group>
              <el-button size="small" @click="handleCopy">
                <el-icon><CopyDocument /></el-icon> 复制
              </el-button>
              <el-button size="small" @click="handleDownload">
                <el-icon><Download /></el-icon> 下载
              </el-button>
            </el-button-group>
          </div>
          <div class="code-content">
            <pre><code>{{ generatedScript }}</code></pre>
          </div>
        </div>

        <div class="action-buttons">
          <el-button type="success" size="large" @click="handleSaveAndExecute">
            <el-icon><VideoPlay /></el-icon> 保存并执行
          </el-button>
          <el-button type="primary" size="large" plain @click="handleViewScript">
            <el-icon><View /></el-icon> 查看详情
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup name="UIScriptGenerate">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { generateUIScript } from '@/api/testing/uiAutomation'
import { listAllProject } from '@/api/testing/project'

const router = useRouter()

const generateFormRef = ref(null)
const projectList = ref([])
const generating = ref(false)
const generatedScript = ref('')
const scriptId = ref(null)

const form = reactive({
  projectId: null,
  scriptName: '',
  generationPrompt: '',
  language: 'typescript',
  browser: 'chromium',
  useRag: false
})

const rules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  scriptName: [
    { required: true, message: '请输入脚本名称', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '脚本名称只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  generationPrompt: [
    { required: true, message: '请输入测试需求描述', trigger: 'blur' },
    { min: 20, message: '测试需求描述至少20个字符', trigger: 'blur' }
  ]
}

// 加载项目列表
async function loadProjects() {
  try {
    const response = await listAllProject('0')
    // 兼容不同的返回格式
    projectList.value = (response.data || response.rows || []).map(item => ({
      projectId: item.project_id || item.projectId,
      projectName: item.project_name || item.projectName
    }))
    if (projectList.value.length > 0) {
      form.projectId = projectList.value[0].projectId
    }
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  }
}

// 生成脚本
async function handleGenerate() {
  if (!generateFormRef.value) return
  
  try {
    await generateFormRef.value.validate()
  } catch {
    return
  }

  generating.value = true
  generatedScript.value = ''
  scriptId.value = null

  try {
    const response = await generateUIScript(form)
    
    // 后端返回格式: { code: 200, msg: "...", data: {...} }
    if (response.code === 200 && response.data) {
      const data = response.data
      if (data.success) {
        generatedScript.value = data.script_content || ''
        scriptId.value = data.script_id
        ElMessage.success('🎉 Playwright脚本生成成功！')
      } else {
        ElMessage.error(data.error || '生成失败')
      }
    } else {
      ElMessage.error(response.msg || '生成失败')
    }
  } catch (error) {
    console.error('生成脚本失败:', error)
    ElMessage.error('生成脚本失败: ' + (error.message || '未知错误'))
  } finally {
    generating.value = false
  }
}

// 复制脚本
function handleCopy() {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(generatedScript.value).then(() => {
      ElMessage.success('✅ 已复制到剪贴板')
    }).catch(() => {
      fallbackCopy()
    })
  } else {
    fallbackCopy()
  }
}

function fallbackCopy() {
  const textarea = document.createElement('textarea')
  textarea.value = generatedScript.value
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  try {
    document.execCommand('copy')
    ElMessage.success('✅ 已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败，请手动复制')
  }
  document.body.removeChild(textarea)
}

// 下载脚本
function handleDownload() {
  const blob = new Blob([generatedScript.value], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${form.scriptName || 'test'}.spec.${form.language === 'typescript' ? 'ts' : 'js'}`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
  ElMessage.success('✅ 下载成功')
}

// 保存并执行
function handleSaveAndExecute() {
  router.push({
    path: '/testing/ui-automation/execution',
    query: { scriptId: scriptId.value }
  })
}

// 查看详情
function handleViewScript() {
  router.push({
    path: '/testing/ui-automation',
    query: { tab: 'scripts', highlightId: scriptId.value }
  })
}

// 重置表单
function handleReset() {
  generateFormRef.value?.resetFields()
  generatedScript.value = ''
  scriptId.value = null
  ElMessage.info('已重置')
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.ml-2 {
  margin-left: 8px;
}

.result-section {
  margin-top: 20px;
}

.script-editor {
  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #f5f7fa;
    border: 1px solid #dcdfe6;
    border-bottom: none;
    border-radius: 4px 4px 0 0;

    .filename {
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: 'Consolas', 'Monaco', monospace;
      font-weight: 500;
      color: #303133;
    }
  }

  .code-content {
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid #dcdfe6;
    border-radius: 0 0 4px 4px;
    background: #282c34;

    pre {
      margin: 0;
      padding: 16px;

      code {
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
        line-height: 1.6;
        color: #abb2bf;
        white-space: pre;
        word-wrap: normal;
      }
    }
  }
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
