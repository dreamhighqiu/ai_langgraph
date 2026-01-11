<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span><el-icon><DataAnalysis /></el-icon> 测试报告详情</span>
          <el-button-group>
            <el-button @click="handleRefresh">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
            <el-button @click="handleDownloadAll" type="primary">
              <el-icon><Download /></el-icon> 下载全部报告
            </el-button>
          </el-button-group>
        </div>
      </template>

      <div v-loading="loading">
        <!-- 测试摘要卡片 -->
        <el-card shadow="hover" class="summary-card" v-if="summary">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataAnalysis /></el-icon> 测试摘要</span>
              <el-tag :type="summary.passed === summary.total ? 'success' : 'danger'" size="large">
                {{ summary.passed === summary.total ? '✓ 全部通过' : '✗ 存在失败' }}
              </el-tag>
            </div>
          </template>

          <div class="summary-content">
            <el-row :gutter="20">
              <el-col :span="4">
                <div class="stat-card">
                  <div class="stat-value">{{ summary.total }}</div>
                  <div class="stat-label">总用例数</div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="stat-card success">
                  <div class="stat-value">{{ summary.passed }}</div>
                  <div class="stat-label">通过</div>
                  <div class="stat-percent">{{ getPercent(summary.passed, summary.total) }}%</div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="stat-card danger">
                  <div class="stat-value">{{ summary.failed }}</div>
                  <div class="stat-label">失败</div>
                  <div class="stat-percent">{{ getPercent(summary.failed, summary.total) }}%</div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="stat-card warning">
                  <div class="stat-value">{{ summary.skipped }}</div>
                  <div class="stat-label">跳过</div>
                  <div class="stat-percent">{{ getPercent(summary.skipped, summary.total) }}%</div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="stat-card info">
                  <div class="stat-value">{{ formatDuration(summary.duration_ms) }}</div>
                  <div class="stat-label">总耗时</div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="stat-card">
                  <div class="stat-value">{{ formatTime(summary.start_time) }}</div>
                  <div class="stat-label">执行时间</div>
                </div>
              </el-col>
            </el-row>

            <!-- 进度条 -->
            <div class="progress-section mt-4">
              <el-progress
                :percentage="getPercent(summary.passed, summary.total)"
                :color="summary.passed === summary.total ? '#67c23a' : '#f56c6c'"
                :stroke-width="20"
                :text-inside="true"
              >
                <span class="progress-text">
                  {{ summary.passed }} / {{ summary.total }} 通过
                </span>
              </el-progress>
            </div>
          </div>
        </el-card>

        <!-- 报告列表 -->
        <el-card shadow="hover" class="mt-4">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> 测试报告文件</span>
              <el-tag type="info">共 {{ reportList.length }} 个报告</el-tag>
            </div>
          </template>

          <el-table :data="reportList" style="width: 100%">
            <el-table-column label="报告ID" prop="reportId" width="100" align="center" />
            <el-table-column label="报告名称" prop="reportName" show-overflow-tooltip min-width="200" />
            <el-table-column label="报告类型" prop="reportType" width="150" align="center">
              <template #default="scope">
                <el-tag v-if="scope.row.reportType === 'html'" type="success">
                  <el-icon><Document /></el-icon> HTML摘要
                </el-tag>
                <el-tag v-else-if="scope.row.reportType === 'json'" type="primary">
                  <el-icon><DataLine /></el-icon> JSON数据
                </el-tag>
                <el-tag v-else type="warning">
                  <el-icon><FolderOpened /></el-icon> 完整报告(ZIP)
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="文件大小" prop="fileSize" width="120" align="center">
              <template #default="scope">
                {{ formatFileSize(scope.row.fileSize) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" prop="status" width="100" align="center">
              <template #default="scope">
                <el-tag v-if="scope.row.status === '0'" type="success" size="small">正常</el-tag>
                <el-tag v-else type="danger" size="small">异常</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" prop="createTime" width="160" align="center" />
            <el-table-column label="操作" align="center" width="200" fixed="right">
              <template #default="scope">
                <el-button
                  v-if="scope.row.reportType === 'html'"
                  link
                  type="primary"
                  icon="View"
                  @click="handleViewReport(scope.row)"
                  size="small"
                >
                  在线查看
                </el-button>
                <el-button
                  link
                  type="success"
                  icon="Download"
                  @click="handleDownload(scope.row)"
                  size="small"
                >
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-card>

    <!-- 查看HTML报告对话框 -->
    <el-dialog
      v-model="viewReportDialogVisible"
      title="测试报告"
      width="90%"
      top="5vh"
      :close-on-click-modal="false"
      fullscreen
    >
      <div v-if="reportContent" v-html="reportContent" class="report-content"></div>
      <div v-else class="loading-content">
        <el-icon class="is-loading" :size="50"><Loading /></el-icon>
        <p>加载报告中...</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup name="UIReportDetail">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { getUIExecutionReports, downloadUIReport } from '@/api/testing/uiAutomation'

const route = useRoute()

const loading = ref(false)
const reportList = ref([])
const summary = ref(null)
const viewReportDialogVisible = ref(false)
const reportContent = ref('')

// 加载报告列表
async function loadReports() {
  const executionId = route.query.executionId
  if (!executionId) {
    ElMessage.error('缺少执行ID参数')
    return
  }

  loading.value = true
  try {
    const response = await getUIExecutionReports(executionId)
    const data = response.data || response
    reportList.value = (data || []).map(item => ({
      reportId: item.report_id || item.reportId,
      executionId: item.execution_id || item.executionId,
      reportName: item.report_name || item.reportName,
      reportType: item.report_type || item.reportType,
      filePath: item.file_path || item.filePath,
      fileSize: item.file_size || item.fileSize,
      status: item.status,
      createTime: item.create_time || item.createTime,
      summary: item.summary,
      metrics: item.metrics
    }))

    // 提取摘要信息（从第一个报告中）
    if (reportList.value.length > 0 && reportList.value[0].summary) {
      summary.value = reportList.value[0].summary
    }
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败')
  } finally {
    loading.value = false
  }
}

// 查看报告
async function handleViewReport(row) {
  viewReportDialogVisible.value = true
  reportContent.value = ''

  try {
    const blob = await downloadUIReport(row.reportId)
    const reader = new FileReader()
    reader.onload = (e) => {
      reportContent.value = e.target.result
    }
    reader.readAsText(blob)
  } catch (error) {
    ElMessage.error('加载报告内容失败')
    viewReportDialogVisible.value = false
  }
}

// 下载报告
async function handleDownload(row) {
  try {
    const blob = await downloadUIReport(row.reportId)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    
    const extension = row.reportType === 'html' ? 'html' : row.reportType === 'json' ? 'json' : 'zip'
    a.download = `${row.reportName || `report_${row.reportId}`}.${extension}`
    
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 下载全部报告
function handleDownloadAll() {
  reportList.value.forEach(report => {
    handleDownload(report)
  })
}

// 刷新
function handleRefresh() {
  loadReports()
  ElMessage.success('已刷新')
}

// 格式化百分比
function getPercent(value, total) {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

// 格式化时长
function formatDuration(ms) {
  if (!ms) return '-'
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`
  return `${(ms / 60000).toFixed(2)}min`
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)}MB`
}

// 格式化时间
function formatTime(time) {
  if (!time) return '-'
  const date = new Date(time)
  return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.mt-4 {
  margin-top: 16px;
}

.summary-card {
  .summary-content {
    .stat-card {
      padding: 24px;
      background: #f4f4f5;
      border-radius: 8px;
      text-align: center;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
      }

      &.success {
        background: linear-gradient(135deg, #f0f9ff 0%, #e8f5e9 100%);
        .stat-value {
          color: #67c23a;
        }
      }

      &.danger {
        background: linear-gradient(135deg, #fef0f0 0%, #ffebee 100%);
        .stat-value {
          color: #f56c6c;
        }
      }

      &.warning {
        background: linear-gradient(135deg, #fdf6ec 0%, #fff3e0 100%);
        .stat-value {
          color: #e6a23c;
        }
      }

      &.info {
        background: linear-gradient(135deg, #f0f9ff 0%, #e3f2fd 100%);
        .stat-value {
          color: #409eff;
        }
      }

      .stat-value {
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 8px;
        line-height: 1;
      }

      .stat-label {
        font-size: 14px;
        color: #606266;
        margin-bottom: 4px;
      }

      .stat-percent {
        font-size: 12px;
        color: #909399;
      }
    }

    .progress-section {
      :deep(.el-progress__text) {
        font-size: 16px !important;
        font-weight: bold;
      }
    }
  }
}

.report-content {
  height: calc(100vh - 150px);
  overflow-y: auto;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
}
</style>
