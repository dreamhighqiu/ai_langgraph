<template>
  <div class="app-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><DataAnalysis /></el-icon> UI自动化测试报告</h2>
          <p class="subtitle">Playwright/Allure Test Reports</p>
        </div>
      </div>
    </el-card>

    <el-card>
      <el-form :model="queryParams" ref="queryForm" :inline="true">
        <el-form-item label="报告名称" prop="reportName">
          <el-input v-model="queryParams.reportName" placeholder="请输入报告名称" clearable />
        </el-form-item>
        <el-form-item label="生成时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="reportList">
        <el-table-column label="报告名称" prop="reportName" show-overflow-tooltip />
        <el-table-column label="关联脚本" prop="scriptName" show-overflow-tooltip />
        <el-table-column label="浏览器" prop="browser" width="100" />
        <el-table-column label="测试结果" prop="result" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.result === 'passed'" type="success">通过</el-tag>
            <el-tag v-else type="danger">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="生成时间" prop="createTime" width="160" />
        <el-table-column label="操作" align="center" width="250" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看详情</el-button>
            <el-button link type="success" icon="Download" @click="handleDownload(scope.row)">下载报告</el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)">删除</el-button>
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
  </div>
</template>

<script setup name="UIAutomationReport">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { listUIReports, deleteUIReport, downloadUIReport } from '@/api/testing/uiAutomation'

const router = useRouter()

const loading = ref(false)
const total = ref(0)
const reportList = ref([])
const dateRange = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  reportName: undefined,
  reportType: 'ui',
  beginTime: undefined,
  endTime: undefined
})

// 监听日期范围变化
watch(dateRange, (val) => {
  if (val && val.length === 2) {
    queryParams.beginTime = val[0]
    queryParams.endTime = val[1]
  } else {
    queryParams.beginTime = undefined
    queryParams.endTime = undefined
  }
})

async function getList() {
  loading.value = true
  try {
    // 处理日期范围参数
    const params = { ...queryParams }
    if (dateRange.value && dateRange.value.length === 2) {
      params.beginTime = dateRange.value[0]
      params.endTime = dateRange.value[1]
    }
    
    const response = await listUIReports(params)
    console.log('[Report] API响应:', response)
    
    // 后端返回格式: { code: 200, data: { rows: [...], total: ... } } 或 { code: 200, rows: [...], total: ... }
    const data = response.data || response
    
    if (response.code === 200 || !response.code) {
      reportList.value = (data.rows || data.list || []).map(item => ({
        reportId: item.report_id || item.reportId,
        executionId: item.execution_id || item.executionId,
        reportName: item.report_name || item.reportName,
        reportType: item.report_type || item.reportType,
        scriptId: item.script_id || item.scriptId,
        scriptName: item.script_name || item.scriptName,
        browser: item.browser,
        result: item.result,
        summary: item.summary,
        metrics: item.metrics,
        createTime: item.create_time || item.createTime,
        filePath: item.file_path || item.filePath,
        fileSize: item.file_size || item.fileSize
      }))
      total.value = data.total || 0
      console.log('[Report] 加载成功:', reportList.value.length, '条记录，总数:', total.value)
    } else {
      console.error('[Report] API返回错误:', response)
      ElMessage.error(response.msg || '获取报告列表失败')
      reportList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('[Report] 获取报告列表失败:', error)
    ElMessage.error('获取报告列表失败: ' + (error.msg || error.message || '未知错误'))
    reportList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryParams.reportName = undefined
  dateRange.value = []
  handleQuery()
}

function handleView(row) {
  router.push({
    path: '/testing/ui-automation/report',
    query: { reportId: row.reportId }
  })
}

async function handleDownload(row) {
  try {
    const response = await downloadUIReport(row.reportId)
    const blob = new Blob([response], { type: 'application/zip' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${row.reportName || 'report'}.zip`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载报告失败:', error)
    ElMessage.error('下载报告失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(
    `确认删除报告"${row.reportName}"吗？此操作不可恢复。`,
    '警告',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteUIReport(row.reportId)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  getList()
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
    }
    .subtitle {
      color: #909399;
      margin: 0;
    }
  }
}
</style>

