<template>
  <div class="app-container ui-script-generate">
    <el-page-header @back="$router.back()" content="AI生成Playwright测试脚本">
      <template #extra>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon> 重置
        </el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20" class="mt-4">
      <!-- 左侧：生成表单 -->
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><MagicStick /></el-icon> 配置生成参数</span>
            </div>
          </template>

          <el-form ref="generateFormRef" :model="form" :rules="rules" label-width="120px">
            <el-form-item label="项目" prop="project_id">
              <el-select v-model="form.project_id" placeholder="请选择项目" style="width: 100%">
                <el-option
                  v-for="project in projectList"
                  :key="project.projectId"
                  :label="project.projectName"
                  :value="project.projectId"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="脚本名称" prop="script_name">
              <el-input
                v-model="form.script_name"
                placeholder="例如：login_test"
                clearable
              >
                <template #append>.spec.{{ form.language === 'typescript' ? 'ts' : 'js' }}</template>
              </el-input>
            </el-form-item>

            <el-form-item label="测试需求" prop="generation_prompt">
              <el-input
                v-model="form.generation_prompt"
                type="textarea"
                :rows="8"
                placeholder="请详细描述需要测试的功能和场景&#10;&#10;示例：&#10;测试用户登录功能：&#10;1. 输入正确的用户名和密码，点击登录按钮&#10;2. 验证登录成功后跳转到首页&#10;3. 测试错误密码的情况&#10;4. 测试空用户名的情况"
                show-word-limit
                maxlength="2000"
              />
            </el-form-item>

            <el-form-item label="脚本语言" prop="language">
              <el-radio-group v-model="form.language">
                <el-radio value="typescript">
                  <el-icon><Document /></el-icon> TypeScript
                </el-radio>
                <el-radio value="javascript">
                  <el-icon><Document /></el-icon> JavaScript
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="目标浏览器" prop="browser">
              <el-select v-model="form.browser" placeholder="选择浏览器">
                <el-option label="Chromium" value="chromium">
                  <span><el-icon><ChromeFilled /></el-icon> Chromium</span>
                </el-option>
                <el-option label="Firefox" value="firefox">
                  <span><el-icon><Firefox /></el-icon> Firefox</span>
                </el-option>
                <el-option label="WebKit" value="webkit">
                  <span><el-icon><Apple /></el-icon> WebKit (Safari)</span>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="使用RAG增强">
              <el-switch v-model="form.use_rag" />
              <el-tooltip effect="dark" content="启用后将使用知识库增强AI生成效果" placement="top">
                <el-icon class="ml-2"><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="generating" @click="handleGenerate" style="width: 100%">
                <el-icon><MagicStick /></el-icon>
                {{ generating ? '生成中...' : 'AI生成脚本' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：生成结果 -->
      <el-col :span="14">
        <el-card shadow="hover" class="result-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><DocumentCopy /></el-icon> 
                生成结果
                <el-tag v-if="scriptId" type="success" class="ml-2">Script ID: {{ scriptId }}</el-tag>
              </span>
              <el-button-group v-if="generatedScript">
                <el-button size="small" @click="handleCopy">
                  <el-icon><CopyDocument /></el-icon> 复制
                </el-button>
                <el-button size="small" @click="handleDownload">
                  <el-icon><Download /></el-icon> 下载
                </el-button>
              </el-button-group>
            </div>
          </template>

          <div v-if="!generatedScript && !generating" class="empty-state">
            <el-empty description="请在左侧配置参数并点击生成按钮">
              <el-icon :size="100" color="#909399"><Document /></el-icon>
            </el-empty>
          </div>

          <div v-else-if="generating" class="loading-state">
            <el-icon class="is-loading" :size="50" color="#409eff"><Loading /></el-icon>
            <p class="mt-4">AI正在生成Playwright测试脚本，请稍候...</p>
          </div>

          <div v-else class="script-editor">
            <div class="editor-header">
              <span class="filename">
                <el-icon><DocumentCopy /></el-icon>
                {{ form.script_name || 'test' }}.spec.{{ form.language === 'typescript' ? 'ts' : 'js' }}
              </span>
              <el-tag size="small" type="primary">{{ form.language }}</el-tag>
            </div>
            <div class="code-content">
              <pre><code>{{ generatedScript }}</code></pre>
            </div>
          </div>

          <div v-if="generatedScript" class="action-buttons">
            <el-button type="success" size="large" @click="handleSaveAndExecute">
              <el-icon><VideoPlay /></el-icon> 保存并执行
            </el-button>
            <el-button type="primary" size="large" plain @click="handleViewScript">
              <el-icon><View /></el-icon> 查看详情
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup name="UIScriptGenerate">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { generateUIScript } from '@/api/testing/uiAutomation'
import { listProject } from '@/api/testing/project'

const router = useRouter()

const generateFormRef = ref(null)
const projectList = ref([])
const generating = ref(false)
const generatedScript = ref('')
const scriptId = ref(null)

const form = reactive({
  project_id: null,
  script_name: '',
  generation_prompt: '',
  language: 'typescript',
  browser: 'chromium',
  use_rag: false
})

const rules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  script_name: [
    { required: true, message: '请输入脚本名称', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '脚本名称只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  generation_prompt: [
    { required: true, message: '请输入测试需求描述', trigger: 'blur' },
    { min: 20, message: '测试需求描述至少20个字符', trigger: 'blur' }
  ]
}

// 加载项目列表
async function loadProjects() {
  try {
    const response = await listProject({ projectType: 'ui', status: '0', pageNum: 1, pageSize: 100 })
    projectList.value = response.data?.rows || []
    if (projectList.value.length > 0) {
      form.project_id = projectList.value[0].projectId
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
  a.download = `${form.script_name || 'test'}.spec.${form.language === 'typescript' ? 'ts' : 'js'}`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
  ElMessage.success('✅ 下载成功')
}

// 保存并执行
function handleSaveAndExecute() {
  ElMessageBox.confirm(
    '脚本已自动保存到数据库，是否立即执行该脚本？',
    '确认执行',
    {
      confirmButtonText: '立即执行',
      cancelButtonText: '稍后执行',
      type: 'success'
    }
  ).then(() => {
    router.push({
      path: '/testing/ui-automation/execution',
      query: { scriptId: scriptId.value }
    })
  }).catch(() => {
    router.push({ path: '/testing/ui-automation' })
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
.ui-script-generate {
  padding: 20px;

  .mt-4 {
    margin-top: 16px;
  }

  .ml-2 {
    margin-left: 8px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 500;
  }

  .result-card {
    min-height: 700px;
  }

  .empty-state,
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 500px;
    color: #909399;
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
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
    display: flex;
    gap: 12px;
    justify-content: center;
  }
}
</style>

