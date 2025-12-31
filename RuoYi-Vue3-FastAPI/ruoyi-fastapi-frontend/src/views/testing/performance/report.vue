<template>
  <div class="app-container">
    <!-- 头部标题 -->
    <el-card class="box-card header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><DataAnalysis /></el-icon> 性能测试报告</h2>
          <p class="subtitle">K6 Performance Test Reports</p>
        </div>
        <el-button type="primary" :disabled="selectedIds.length < 2" @click="handleCompare" v-hasPermi="['performance:report:compare']">
          <el-icon><Histogram /></el-icon> 报告对比
        </el-button>
      </div>
    </el-card>

    <!-- 查询区域 -->
    <el-card class="box-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="报告名称" prop="reportName">
          <el-input v-model="queryParams.reportName" placeholder="请输入报告名称" clearable style="width: 200px" @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="报告类型" prop="reportType">
          <el-select v-model="queryParams.reportType" placeholder="请选择类型" clearable style="width: 120px">
            <el-option label="HTML" value="html" />
            <el-option label="JSON" value="json" />
            <el-option label="PDF" value="pdf" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表区域 -->
    <el-card class="box-card">
      <el-table v-loading="loading" :data="reportList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="报告ID" prop="reportId" width="80" align="center" />
        <el-table-column label="报告名称" prop="reportName" min-width="200" show-overflow-tooltip />
        <el-table-column label="脚本名称" prop="scriptName" width="150" show-overflow-tooltip />
        <el-table-column label="项目" prop="projectName" width="120" show-overflow-tooltip />
        <el-table-column label="报告类型" prop="reportType" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getReportTypeTag(scope.row.reportType)">{{ (scope.row.reportType || '').toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="报告大小" prop="reportSize" width="100" align="center">
          <template #default="scope">
            {{ formatFileSize(scope.row.reportSize) }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="createTime" width="160" align="center">
          <template #default="scope">
            <span>{{ parseTime(scope.row.createTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="200" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看</el-button>
            <el-button link type="success" icon="Download" @click="handleDownload(scope.row)" v-hasPermi="['performance:report:download']">下载</el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['performance:report:remove']">删除</el-button>
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

    <!-- 报告详情对话框 -->
    <el-dialog title="性能测试报告详情" v-model="viewVisible" width="1000px" append-to-body>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="报告名称">{{ viewData.reportName }}</el-descriptions-item>
        <el-descriptions-item label="报告类型">
          <el-tag :type="getReportTypeTag(viewData.reportType)">{{ (viewData.reportType || '').toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="报告大小">{{ formatFileSize(viewData.reportSize) }}</el-descriptions-item>
        <el-descriptions-item label="脚本名称">{{ viewData.scriptName }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ viewData.projectName }}</el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <el-tag :type="getStatusTag(viewData.executionStatus)">{{ getStatusName(viewData.executionStatus) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行时长">{{ viewData.duration ? viewData.duration + '秒' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ parseTime(viewData.createTime) }}</el-descriptions-item>
      </el-descriptions>

      <!-- 性能指标卡片 -->
      <el-divider content-position="left" v-if="viewData.metrics">关键性能指标</el-divider>
      <el-row v-if="viewData.metrics" :gutter="20" class="metrics-row">
        <el-col :span="6" v-for="(value, key) in viewData.metrics" :key="key">
          <el-card shadow="never" class="metric-card">
            <div class="metric-value">{{ value }}</div>
            <div class="metric-label">{{ formatMetricLabel(key) }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 报告摘要 -->
      <el-divider content-position="left" v-if="viewData.summary">报告摘要</el-divider>
      <el-descriptions v-if="viewData.summary" :column="2" border size="small">
        <el-descriptions-item v-for="(value, key) in viewData.summary" :key="key" :label="formatMetricLabel(key)">{{ value }}</el-descriptions-item>
      </el-descriptions>

      <!-- 报告内容预览 -->
      <el-divider content-position="left" v-if="viewData.reportContent">报告内容</el-divider>
      <div v-if="viewData.reportContent && viewData.reportType === 'html'" class="report-preview" v-html="viewData.reportContent"></div>
      <el-input v-else-if="viewData.reportContent" :model-value="viewData.reportContent" type="textarea" :rows="15" readonly style="font-family: monospace;" />

      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" icon="Download" @click="handleDownload(viewData)">下载报告</el-button>
          <el-button @click="viewVisible = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 报告对比对话框 -->
    <el-dialog title="性能报告对比" v-model="compareVisible" width="1200px" append-to-body>
      <el-table :data="compareData.reports" border>
        <el-table-column label="报告名称" prop="reportName" />
        <el-table-column label="脚本名称" prop="scriptName" width="150" />
        <el-table-column label="执行时长" prop="duration" width="100">
          <template #default="scope">{{ scope.row.duration ? scope.row.duration + 's' : '-' }}</template>
        </el-table-column>
        <el-table-column label="创建时间" prop="createTime" width="160">
          <template #default="scope">{{ parseTime(scope.row.createTime) }}</template>
        </el-table-column>
      </el-table>

      <el-divider content-position="left">执行时长对比</el-divider>
      <div class="compare-chart">
        <div v-for="item in compareData.comparison?.execution_time || []" :key="item.report_id" class="compare-bar-item">
          <span class="bar-label">{{ item.report_name }}</span>
          <div class="bar-container">
            <div class="bar-fill" :style="{ width: getBarWidth(item.duration) + '%' }"></div>
            <span class="bar-value">{{ item.duration }}s</span>
          </div>
        </div>
      </div>

      <el-divider content-position="left" v-if="compareData.comparison?.metrics_comparison">指标对比</el-divider>
      <el-descriptions :column="1" border v-if="compareData.comparison?.metrics_comparison">
        <el-descriptions-item v-for="(values, key) in compareData.comparison.metrics_comparison" :key="key" :label="formatMetricLabel(key)">
          <span v-for="(item, idx) in values" :key="idx" class="metric-compare-item">
            报告{{ item.report_id }}: {{ item.value }}
            <span v-if="idx < values.length - 1"> | </span>
          </span>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup name="PerformanceReport">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listReport, getReport, delReport, downloadReport, compareReports } from '@/api/testing/report'

const { proxy } = getCurrentInstance()
const route = useRoute()

// 数据定义
const loading = ref(false)
const total = ref(0)
const reportList = ref([])
const viewVisible = ref(false)
const compareVisible = ref(false)
const viewData = ref({})
const compareData = ref({ reports: [], comparison: {} })
const selectedIds = ref([])

// 查询参数
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  reportName: undefined,
  reportType: undefined,
  scriptType: 'k6'
})

function getReportTypeTag(type) {
  const map = { 'html': '', 'pdf': 'danger', 'json': 'warning' }
  return map[type] || 'info'
}

function getStatusName(status) {
  const map = { 'pending': '待执行', 'running': '运行中', 'success': '成功', 'failed': '失败', 'cancelled': '已取消' }
  return map[status] || status
}

function getStatusTag(status) {
  const map = { 'pending': 'info', 'running': 'warning', 'success': 'success', 'failed': 'danger', 'cancelled': '' }
  return map[status] || 'info'
}

function formatFileSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

function formatMetricLabel(key) {
  const labels = {
    'http_req_duration': '请求耗时',
    'http_req_failed': '请求失败率',
    'http_reqs': '请求总数',
    'vus': '虚拟用户数',
    'vus_max': '最大虚拟用户',
    'iterations': '迭代次数',
    'data_received': '接收数据',
    'data_sent': '发送数据',
    'p95': 'P95响应时间',
    'p99': 'P99响应时间',
    'avg': '平均响应时间',
    'min': '最小响应时间',
    'max': '最大响应时间'
  }
  return labels[key] || key
}

function getBarWidth(duration) {
  const maxDuration = Math.max(...(compareData.value.comparison?.execution_time?.map(i => i.duration) || [1]))
  return (duration / maxDuration) * 100
}

/** 查询报告列表 */
function getList() {
  loading.value = true
  listReport({
    report_name: queryParams.reportName,
    report_type: queryParams.reportType,
    script_type: queryParams.scriptType,
    page_num: queryParams.pageNum,
    page_size: queryParams.pageSize
  }).then(response => {
    reportList.value = response.data?.rows || response.rows || []
    total.value = response.data?.total || response.total || 0
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryParams.reportName = undefined
  queryParams.reportType = undefined
  handleQuery()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.reportId || item.report_id)
}

function handleView(row) {
  getReport(row.reportId || row.report_id).then(response => {
    viewData.value = response.data || row
    viewVisible.value = true
  })
}

function handleDownload(row) {
  window.open(`/dev-api/testing/report/${row.reportId || row.report_id}/download`, '_blank')
}

function handleDelete(row) {
  const id = row.reportId || row.report_id
  ElMessageBox.confirm('是否确认删除报告"' + row.reportName + '"?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return delReport(id)
  }).then(() => {
    getList()
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function handleCompare() {
  if (selectedIds.value.length < 2) {
    ElMessage.warning('请至少选择2个报告进行对比')
    return
  }
  compareReports({ report_ids: selectedIds.value }).then(response => {
    compareData.value = response.data || { reports: [], comparison: {} }
    compareVisible.value = true
  })
}

onMounted(() => {
  getList()
  // 检查URL参数
  if (route.query.reportId) {
    getReport(route.query.reportId).then(response => {
      viewData.value = response.data
      viewVisible.value = true
    })
  }
})
</script>

<style scoped lang="scss">
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

.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
  margin-bottom: 15px;
  .metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #409EFF;
  }
  .metric-label {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
}

.report-preview {
  max-height: 500px;
  overflow: auto;
  border: 1px solid #ebeef5;
  padding: 15px;
  border-radius: 4px;
  background: #fafafa;
}

.compare-chart {
  padding: 20px;
}

.compare-bar-item {
  margin-bottom: 15px;
  .bar-label {
    display: block;
    margin-bottom: 5px;
    font-size: 12px;
    color: #606266;
  }
  .bar-container {
    display: flex;
    align-items: center;
    background: #f0f0f0;
    border-radius: 4px;
    height: 24px;
    position: relative;
  }
  .bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #409EFF, #67C23A);
    border-radius: 4px;
    transition: width 0.3s;
  }
  .bar-value {
    position: absolute;
    right: 10px;
    font-size: 12px;
    font-weight: bold;
  }
}

.metric-compare-item {
  margin-right: 10px;
}
</style>
