<template>
  <div class="app-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><VideoPlay /></el-icon> Playwright脚本执行监控</h2>
          <p class="subtitle">Playwright Execution Monitoring</p>
        </div>
      </div>
    </el-card>

    <el-card>
      <el-form :model="queryParams" ref="queryForm" :inline="true">
        <el-form-item label="脚本名称" prop="scriptName">
          <el-input v-model="queryParams.scriptName" placeholder="请输入脚本名称" clearable />
        </el-form-item>
        <el-form-item label="执行状态" prop="status">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
            <el-option label="待执行" value="0" />
            <el-option label="执行中" value="1" />
            <el-option label="已完成" value="2" />
            <el-option label="失败" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="executionList">
        <el-table-column label="执行ID" prop="executionId" width="100" />
        <el-table-column label="脚本名称" prop="scriptName" show-overflow-tooltip />
        <el-table-column label="浏览器" prop="browser" width="100" />
        <el-table-column label="执行状态" prop="status" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.status === '0'" type="info">待执行</el-tag>
            <el-tag v-else-if="scope.row.status === '1'" type="primary">执行中</el-tag>
            <el-tag v-else-if="scope.row.status === '2'" type="success">已完成</el-tag>
            <el-tag v-else type="danger">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" prop="startTime" width="160" />
        <el-table-column label="结束时间" prop="endTime" width="160" />
        <el-table-column label="操作" align="center" width="250" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看日志</el-button>
            <el-button link type="success" icon="Document" @click="handleReport(scope.row)" v-if="scope.row.status === '2'">查看报告</el-button>
            <el-button link type="danger" icon="Close" @click="handleCancel(scope.row)" v-if="scope.row.status === '1'">取消执行</el-button>
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

<script setup name="UIAutomationExecution">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { listUIExecutions } from '@/api/testing/uiAutomation'

const router = useRouter()

const loading = ref(false)
const total = ref(0)
const executionList = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  scriptName: undefined,
  executionType: 'ui',
  status: undefined
})

async function getList() {
  loading.value = true
  try {
    const response = await listUIExecutions(queryParams)
    console.log('[Execution] API响应:', response)
    
    // 后端返回格式: { code: 200, data: { rows: [...], total: ... } } 或 { code: 200, rows: [...], total: ... }
    const data = response.data || response
    
    if (response.code === 200 || !response.code) {
      executionList.value = (data.rows || data.list || []).map(item => ({
        executionId: item.execution_id || item.executionId,
        scriptId: item.script_id || item.scriptId,
        scriptName: item.script_name || item.scriptName,
        executionType: item.execution_type || item.executionType,
        status: String(item.status || item.execution_status || ''),
        browser: item.browser,
        headless: item.headless,
        startTime: item.start_time || item.startTime,
        endTime: item.end_time || item.endTime,
        duration: item.duration,
        result: item.result,
        errorMessage: item.error_message || item.errorMessage,
        executor: item.executor,
        createTime: item.create_time || item.createTime
      }))
      total.value = data.total || 0
      console.log('[Execution] 加载成功:', executionList.value.length, '条记录，总数:', total.value)
    } else {
      console.error('[Execution] API返回错误:', response)
      ElMessage.error(response.msg || '获取执行列表失败')
      executionList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('[Execution] 获取执行列表失败:', error)
    ElMessage.error('获取执行列表失败: ' + (error.msg || error.message || '未知错误'))
    executionList.value = []
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
  queryParams.scriptName = undefined
  queryParams.status = undefined
  handleQuery()
}

function handleView(row) {
  router.push({
    path: '/testing/ui-automation/execution',
    query: { executionId: row.executionId }
  })
}

function handleReport(row) {
  router.push({
    path: '/testing/ui-automation/report',
    query: { executionId: row.executionId }
  })
}

function handleCancel(row) {
  ElMessage.info('取消执行功能开发中...')
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

