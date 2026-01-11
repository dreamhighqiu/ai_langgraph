<template>
  <div class="app-container execute-detail">
    <el-page-header @back="$router.back()" content="执行UI自动化测试脚本">
      <template #extra>
        <el-button @click="$router.push({ path: '/testing/ui-automation', query: { tab: 'scripts' } })">
          <el-icon><Back /></el-icon> 返回脚本列表
        </el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20" class="mt-4">
      <!-- 左侧：脚本信息 -->
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <span><el-icon><Document /></el-icon> 脚本信息</span>
          </template>

          <el-descriptions v-if="scriptInfo" :column="1" border>
            <el-descriptions-item label="脚本ID">{{ scriptInfo.scriptId }}</el-descriptions-item>
            <el-descriptions-item label="脚本名称">{{ scriptInfo.scriptName }}</el-descriptions-item>
            <el-descriptions-item label="项目">{{ scriptInfo.projectName }}</el-descriptions-item>
            <el-descriptions-item label="语言">
              <el-tag v-if="scriptInfo.language === 'typescript'" type="primary" size="small">TypeScript</el-tag>
              <el-tag v-else type="success" size="small">JavaScript</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="默认浏览器">{{ scriptInfo.browser }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ scriptInfo.createTime }}</el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">执行配置</el-divider>

          <el-form ref="executeFormRef" :model="executeForm" :rules="executeRules" label-width="120px">
            <el-form-item label="浏览器" prop="browser">
              <el-select v-model="executeForm.browser" placeholder="选择浏览器" style="width: 100%">
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

            <el-form-item label="无头模式">
              <el-switch v-model="executeForm.headless" />
              <el-tooltip effect="dark" content="无头模式下浏览器在后台运行，不显示界面" placement="top">
                <el-icon class="ml-2"><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-form-item>

            <el-form-item label="超时时间">
              <el-input-number
                v-model="executeForm.timeout"
                :min="10000"
                :max="600000"
                :step="10000"
                style="width: 100%"
              />
              <span class="form-tip">毫秒（10000ms = 10秒）</span>
            </el-form-item>

            <el-form-item label="执行类型">
              <el-radio-group v-model="executeForm.execution_type">
                <el-radio value="manual">手动执行</el-radio>
                <el-radio value="scheduled">定时执行</el-radio>
                <el-radio value="ci">CI触发</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="executing"
                @click="handleExecute"
                style="width: 100%"
                size="large"
              >
                <el-icon><VideoPlay /></el-icon>
                {{ executing ? '执行中...' : '开始执行' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：执行状态和日志 -->
      <el-col :span="14">
        <el-card shadow="hover" class="result-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Monitor /></el-icon> 执行状态监控
                <el-tag v-if="executionId" type="success" class="ml-2">Execution ID: {{ executionId }}</el-tag>
              </span>
              <el-button v-if="completed" size="small" type="success" @click="handleViewReport">
                <el-icon><Document /></el-icon> 查看报告
              </el-button>
            </div>
          </template>

          <div v-if="!executionId && !executing" class="empty-state">
            <el-empty description="点击"开始执行"按钮开始测试">
              <el-icon :size="100" color="#909399"><VideoCamera /></el-icon>
            </el-empty>
          </div>

          <div v-else>
            <!-- 执行进度 -->
            <el-steps :active="currentStep" finish-status="success" align-center class="mb-4">
              <el-step title="准备中" icon="Setting" />
              <el-step title="执行中" icon="Loading" />
              <el-step title="完成" icon="CircleCheck" />
            </el-steps>

            <!-- 执行信息 -->
            <el-descriptions :column="2" border class="mb-4">
              <el-descriptions-item label="执行ID">{{ executionId || '-' }}</el-descriptions-item>
              <el-descriptions-item label="运行ID">{{ runId || '-' }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="statusType">{{ statusText }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="执行类型">{{ executeForm.execution_type }}</el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ executionInfo.startTime || '-' }}</el-descriptions-item>
              <el-descriptions-item label="结束时间">{{ executionInfo.endTime || '-' }}</el-descriptions-item>
              <el-descriptions-item label="耗时" :span="2">
                <span v-if="executionInfo.duration">{{ Math.round(executionInfo.duration / 1000) }}秒</span>
                <span v-else>-</span>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 执行结果统计 -->
            <div v-if="executionInfo.result" class="result-stats">
              <el-divider content-position="left">执行结果</el-divider>
              <el-row :gutter="16">
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ executionInfo.result.total || 0 }}</div>
                    <div class="stat-label">总用例数</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card success">
                    <div class="stat-value">{{ executionInfo.result.passed || 0 }}</div>
                    <div class="stat-label">通过</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card danger">
                    <div class="stat-value">{{ executionInfo.result.failed || 0 }}</div>
                    <div class="stat-label">失败</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card warning">
                    <div class="stat-value">{{ executionInfo.result.skipped || 0 }}</div>
                    <div class="stat-label">跳过</div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 错误信息 -->
            <div v-if="executionInfo.errorMessage" class="error-message">
              <el-alert
                title="执行失败"
                type="error"
                :description="executionInfo.errorMessage"
                show-icon
                :closable="false"
              />
            </div>

            <!-- 操作按钮 -->
            <div v-if="completed" class="action-buttons">
              <el-button type="success" @click="handleViewReport">
                <el-icon><Document /></el-icon> 查看完整报告
              </el-button>
              <el-button @click="handleReExecute">
                <el-icon><Refresh /></el-icon> 重新执行
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup name="UIScriptExecuteDetail">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { getUIScript, executeUIScript, getUIExecution } from '@/api/testing/uiAutomation'

const router = useRouter()
const route = useRoute()

const executeFormRef = ref(null)
const scriptInfo = ref(null)
const executing = ref(false)
const executionId = ref(null)
const runId = ref(null)
const currentStep = ref(0)
const completed = ref(false)
const pollingTimer = ref(null)

const executeForm = reactive({
  script_id: null,
  browser: 'chromium',
  headless: true,
  timeout: 60000,
  execution_type: 'manual'
})

const executeRules = {
  browser: [{ required: true, message: '请选择浏览器', trigger: 'change' }]
}

const executionInfo = ref({
  status: '',
  startTime: null,
  endTime: null,
  duration: null,
  result: null,
  errorMessage: null
})

const statusType = computed(() => {
  const map = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger'
  }
  return map[executionInfo.value.status] || 'info'
})

const statusText = computed(() => {
  const map = {
    pending: '等待中',
    running: '执行中',
    success: '成功',
    failed: '失败'
  }
  return map[executionInfo.value.status] || executionInfo.value.status
})

// 加载脚本信息
async function loadScriptInfo() {
  const scriptId = route.query.scriptId
  if (!scriptId) {
    ElMessage.error('缺少脚本ID参数')
    router.back()
    return
  }

  executeForm.script_id = Number(scriptId)

  try {
    const response = await getUIScript(scriptId)
    scriptInfo.value = response.data
    // 使用脚本默认配置
    if (scriptInfo.value.browser) {
      executeForm.browser = scriptInfo.value.browser
    }
  } catch (error) {
    ElMessage.error('加载脚本信息失败')
    router.back()
  }
}

// 执行脚本
async function handleExecute() {
  if (!executeFormRef.value) return

  try {
    await executeFormRef.value.validate()
  } catch {
    return
  }

  executing.value = true
  executionInfo.value = {
    status: '',
    startTime: null,
    endTime: null,
    duration: null,
    result: null,
    errorMessage: null
  }

  try {
    const response = await executeUIScript(executeForm)

    if (response.code === 200 && response.data) {
      const data = response.data
      if (data.success) {
        executionId.value = data.execution_id
        runId.value = data.run_id
        executionInfo.value.status = data.status || 'running'
        currentStep.value = 1

        ElMessage.success('✅ 测试脚本开始执行！')

        // 开始轮询执行状态
        startPolling()
      } else {
        ElMessage.error(data.error || '执行失败')
      }
    } else {
      ElMessage.error(response.msg || '执行失败')
    }
  } catch (error) {
    console.error('执行脚本失败:', error)
    ElMessage.error('执行失败: ' + (error.message || '未知错误'))
  } finally {
    executing.value = false
  }
}

// 轮询执行状态
function startPolling() {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
  }

  pollingTimer.value = setInterval(async () => {
    if (!executionId.value) return

    try {
      const response = await getUIExecution(executionId.value)
      const data = response.data

      executionInfo.value = {
        status: data.status,
        startTime: data.start_time,
        endTime: data.end_time,
        duration: data.duration,
        result: data.result ? JSON.parse(data.result) : null,
        errorMessage: data.error_message
      }

      if (data.status === 'running') {
        currentStep.value = 1
      } else if (data.status === 'success' || data.status === 'failed') {
        currentStep.value = 2
        completed.value = true
        stopPolling()

        if (data.status === 'success') {
          ElMessage.success('🎉 测试执行成功！')
        } else {
          ElMessage.error('❌ 测试执行失败')
        }
      }
    } catch (error) {
      console.error('获取执行状态失败:', error)
    }
  }, 3000) // 每3秒轮询一次
}

// 停止轮询
function stopPolling() {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

// 查看报告
function handleViewReport() {
  router.push({
    path: '/testing/ui-automation/report',
    query: { executionId: executionId.value }
  })
}

// 重新执行
function handleReExecute() {
  executionId.value = null
  runId.value = null
  currentStep.value = 0
  completed.value = false
  executionInfo.value = {
    status: '',
    startTime: null,
    endTime: null,
    duration: null,
    result: null,
    errorMessage: null
  }
}

onMounted(() => {
  loadScriptInfo()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.execute-detail {
  padding: 20px;

  .mt-4 {
    margin-top: 16px;
  }

  .ml-2 {
    margin-left: 8px;
  }

  .mb-4 {
    margin-bottom: 16px;
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

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 500px;
    color: #909399;
  }

  .form-tip {
    margin-left: 10px;
    font-size: 12px;
    color: #909399;
  }

  .result-stats {
    margin-top: 20px;

    .stat-card {
      padding: 20px;
      background: #f4f4f5;
      border-radius: 8px;
      text-align: center;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }

      &.success {
        background: #f0f9ff;
        color: #67c23a;
      }

      &.danger {
        background: #fef0f0;
        color: #f56c6c;
      }

      &.warning {
        background: #fdf6ec;
        color: #e6a23c;
      }

      .stat-value {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 8px;
      }

      .stat-label {
        font-size: 14px;
        color: #606266;
      }
    }
  }

  .error-message {
    margin-top: 20px;
  }

  .action-buttons {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
    display: flex;
    gap: 12px;
    justify-content: center;
  }
}
</style>

