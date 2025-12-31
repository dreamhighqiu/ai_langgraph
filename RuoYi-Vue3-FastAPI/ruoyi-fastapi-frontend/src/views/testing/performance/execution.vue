<template>
  <div class="app-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-total">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total }}</div>
            <div class="stat-label">总执行数</div>
          </div>
          <el-icon class="stat-icon"><DataAnalysis /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-success">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.success }}</div>
            <div class="stat-label">执行成功</div>
          </div>
          <el-icon class="stat-icon"><CircleCheckFilled /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-failed">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.failed }}</div>
            <div class="stat-label">执行失败</div>
          </div>
          <el-icon class="stat-icon"><CircleCloseFilled /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-running">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.running }}</div>
            <div class="stat-label">正在运行</div>
          </div>
          <el-icon class="stat-icon"><Loading /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 头部标题 -->
    <el-card class="box-card header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><VideoPlay /></el-icon> 性能测试执行监控</h2>
          <p class="subtitle">K6 Performance Test Execution</p>
        </div>
        <el-button type="info" @click="refreshList">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </el-card>

    <!-- 查询区域 -->
    <el-card class="box-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="执行状态" prop="executionStatus">
          <el-select v-model="queryParams.executionStatus" placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="待执行" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行者" prop="executor">
          <el-input v-model="queryParams.executor" placeholder="请输入执行者" clearable style="width: 150px" @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表区域 -->
    <el-card class="box-card">
      <el-table v-loading="loading" :data="executionList">
        <el-table-column label="执行ID" prop="executionId" width="80" align="center" />
        <el-table-column label="脚本名称" prop="scriptName" min-width="200" show-overflow-tooltip />
        <el-table-column label="项目" prop="projectName" width="150" show-overflow-tooltip />
        <el-table-column label="执行状态" prop="executionStatus" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.executionStatus)">
              <el-icon v-if="scope.row.executionStatus === 'running'" class="is-loading"><Loading /></el-icon>
              {{ getStatusName(scope.row.executionStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="执行时长" prop="duration" width="100" align="center">
          <template #default="scope">
            {{ scope.row.duration ? scope.row.duration + 's' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="执行者" prop="executor" width="100" align="center" />
        <el-table-column label="开始时间" prop="startTime" width="160" align="center">
          <template #default="scope">
            <span>{{ parseTime(scope.row.startTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="250" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)">详情</el-button>
            <el-button link type="success" icon="Document" @click="handleReport(scope.row)" v-if="scope.row.executionStatus === 'success'" v-hasPermi="['performance:report:query']">报告</el-button>
            <el-button link type="warning" icon="RefreshRight" @click="handleRetry(scope.row)" v-if="['failed', 'cancelled'].includes(scope.row.executionStatus)" v-hasPermi="['performance:execution:retry']">重试</el-button>
            <el-button link type="danger" icon="Close" @click="handleCancel(scope.row)" v-if="['pending', 'running'].includes(scope.row.executionStatus)" v-hasPermi="['performance:execution:cancel']">取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total > 0"
        :total="total"
        v-model:page="queryParams.pageNum"
        v-model:limit="queryParams.pageSize"
        @pagination="getList"
      />
    </el-card>

    <!-- 执行详情对话框 -->
    <el-dialog title="执行详情" v-model="viewVisible" width="900px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="执行ID">{{ viewData.executionId }}</el-descriptions-item>
        <el-descriptions-item label="脚本名称">{{ viewData.scriptName }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ viewData.projectName }}</el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <el-tag :type="getStatusTag(viewData.executionStatus)">{{ getStatusName(viewData.executionStatus) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行类型">{{ viewData.executionType === 'manual' ? '手动执行' : '定时执行' }}</el-descriptions-item>
        <el-descriptions-item label="执行者">{{ viewData.executor }}</el-descriptions-item>
        <el-descriptions-item label="执行时长">{{ viewData.duration ? viewData.duration + '秒' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="Thread ID">{{ viewData.threadId || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ parseTime(viewData.startTime) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ parseTime(viewData.endTime) }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left" v-if="viewData.errorMsg">错误信息</el-divider>
      <el-alert v-if="viewData.errorMsg" :title="viewData.errorMsg" type="error" show-icon :closable="false" />

      <el-divider content-position="left">执行配置</el-divider>
      <el-input :model-value="JSON.stringify(viewData.config || {}, null, 2)" type="textarea" :rows="4" readonly style="font-family: monospace;" />

      <el-divider content-position="left" v-if="viewData.result">执行结果</el-divider>
      <el-input v-if="viewData.result" :model-value="JSON.stringify(viewData.result, null, 2)" type="textarea" :rows="8" readonly style="font-family: monospace;" />
    </el-dialog>
  </div>
</template>

<script setup name="PerformanceExecution">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listExecution, getExecution, getExecutionStatistics, cancelExecution, retryExecution } from '@/api/testing/execution'
import { generateHtmlReport } from '@/api/testing/report'

const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

// 数据定义
const loading = ref(false)
const total = ref(0)
const executionList = ref([])
const viewVisible = ref(false)
const viewData = ref({})
const statistics = ref({ total: 0, success: 0, failed: 0, running: 0 })

// 查询参数
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  scriptType: 'k6',
  executionStatus: undefined,
  executor: undefined
})

function getStatusName(status) {
  const map = { 'pending': '待执行', 'running': '运行中', 'success': '成功', 'failed': '失败', 'cancelled': '已取消' }
  return map[status] || status
}

function getStatusTag(status) {
  const map = { 'pending': 'info', 'running': 'warning', 'success': 'success', 'failed': 'danger', 'cancelled': '' }
  return map[status] || 'info'
}

/** 查询执行列表 */
function getList() {
  loading.value = true
  listExecution({
    script_type: queryParams.scriptType,
    execution_status: queryParams.executionStatus,
    executor: queryParams.executor,
    page_num: queryParams.pageNum,
    page_size: queryParams.pageSize
  }).then(response => {
    executionList.value = response.data?.rows || response.rows || []
    total.value = response.data?.total || response.total || 0
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

/** 加载统计数据 */
function loadStatistics() {
  getExecutionStatistics(7).then(response => {
    statistics.value = response.data || { total: 0, success: 0, failed: 0, running: 0 }
  })
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryParams.executionStatus = undefined
  queryParams.executor = undefined
  handleQuery()
}

function refreshList() {
  getList()
  loadStatistics()
}

function handleView(row) {
  getExecution(row.executionId || row.execution_id).then(response => {
    viewData.value = response.data || row
    viewVisible.value = true
  })
}

function handleReport(row) {
  generateHtmlReport(row.executionId || row.execution_id).then(response => {
    ElMessage.success('报告生成成功')
    router.push({ path: '/performance/report', query: { reportId: response.data?.report_id } })
  })
}

function handleRetry(row) {
  ElMessageBox.confirm('是否确认重新执行?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return retryExecution(row.executionId || row.execution_id)
  }).then(() => {
    ElMessage.success('重试已启动')
    refreshList()
  }).catch(() => {})
}

function handleCancel(row) {
  ElMessageBox.confirm('是否确认取消执行?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return cancelExecution({ execution_id: row.executionId || row.execution_id })
  }).then(() => {
    ElMessage.success('取消成功')
    refreshList()
  }).catch(() => {})
}

// 自动刷新
let refreshTimer = null
onMounted(() => {
  getList()
  loadStatistics()
  
  // 检查URL参数
  if (route.query.executionId) {
    getExecution(route.query.executionId).then(response => {
      viewData.value = response.data
      viewVisible.value = true
    })
  }

  // 每5秒刷新一次（如果有运行中的执行）
  refreshTimer = setInterval(() => {
    if (statistics.value.running > 0) {
      refreshList()
    }
  }, 5000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped lang="scss">
.mb-4 {
  margin-bottom: 20px;
}

.header-card {
  margin-bottom: 20px;
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    h2 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 8px 0;
      font-size: 20px;
    }
    .subtitle {
      color: #909399;
      margin: 0;
      font-size: 14px;
    }
  }
}

.box-card {
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  .stat-content {
    position: relative;
    z-index: 1;
  }
  .stat-value {
    font-size: 32px;
    font-weight: bold;
    line-height: 1.2;
  }
  .stat-label {
    font-size: 14px;
    color: #909399;
    margin-top: 5px;
  }
  .stat-icon {
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 60px;
    opacity: 0.15;
  }
}

.stat-card-total .stat-value, .stat-card-total .stat-icon { color: #409EFF; }
.stat-card-success .stat-value, .stat-card-success .stat-icon { color: #67C23A; }
.stat-card-failed .stat-value, .stat-card-failed .stat-icon { color: #F56C6C; }
.stat-card-running .stat-value, .stat-card-running .stat-icon { color: #E6A23C; }
</style>
