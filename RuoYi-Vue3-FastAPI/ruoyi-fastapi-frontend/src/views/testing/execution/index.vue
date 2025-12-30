<template>
  <div class="app-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="mb20">
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

    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="脚本ID" prop="script_id">
        <el-input v-model="queryParams.script_id" placeholder="请输入脚本ID" clearable @keyup.enter="handleQuery" style="width: 150px" />
      </el-form-item>
      <el-form-item label="执行状态" prop="execution_status">
        <el-select v-model="queryParams.execution_status" placeholder="请选择" clearable>
          <el-option label="待执行" value="pending" />
          <el-option label="运行中" value="running" />
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
      <el-form-item label="执行者" prop="executor">
        <el-input v-model="queryParams.executor" placeholder="请输入执行者" clearable @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="info" plain icon="Refresh" @click="getList">刷新</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="executionList">
      <el-table-column label="执行ID" align="center" prop="execution_id" width="80" />
      <el-table-column label="脚本名称" align="center" prop="script_name" :show-overflow-tooltip="true" />
      <el-table-column label="脚本类型" align="center" prop="script_type" width="100">
        <template #default="scope">
          <el-tag size="small">{{ getScriptTypeName(scope.row.script_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="所属项目" align="center" prop="project_name" width="120" />
      <el-table-column label="执行状态" align="center" prop="execution_status" width="100">
        <template #default="scope">
          <el-tag :type="getStatusTag(scope.row.execution_status)">
            <el-icon v-if="scope.row.execution_status === 'running'" class="is-loading"><Loading /></el-icon>
            {{ getStatusName(scope.row.execution_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行时长" align="center" prop="duration" width="100">
        <template #default="scope">
          {{ scope.row.duration ? scope.row.duration + 's' : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="执行者" align="center" prop="executor" width="100" />
      <el-table-column label="开始时间" align="center" prop="start_time" width="160">
        <template #default="scope">
          <span>{{ parseTime(scope.row.start_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="240">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleView(scope.row)">详情</el-button>
          <el-button link type="success" icon="Document" @click="handleReport(scope.row)" v-if="scope.row.execution_status === 'success'" v-hasPermi="['testing:report:add']">报告</el-button>
          <el-button link type="warning" icon="RefreshRight" @click="handleRetry(scope.row)" v-if="['failed', 'cancelled'].includes(scope.row.execution_status)">重试</el-button>
          <el-button link type="danger" icon="Close" @click="handleCancel(scope.row)" v-if="['pending', 'running'].includes(scope.row.execution_status)" v-hasPermi="['testing:execution:cancel']">取消</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.page_num"
      v-model:limit="queryParams.page_size"
      @pagination="getList"
    />

    <!-- 执行详情对话框 -->
    <el-dialog title="执行详情" v-model="viewOpen" width="900px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="执行ID">{{ viewData.execution_id }}</el-descriptions-item>
        <el-descriptions-item label="脚本名称">{{ viewData.script_name }}</el-descriptions-item>
        <el-descriptions-item label="脚本类型">{{ getScriptTypeName(viewData.script_type) }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ viewData.project_name }}</el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <el-tag :type="getStatusTag(viewData.execution_status)">{{ getStatusName(viewData.execution_status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行类型">{{ viewData.execution_type === 'manual' ? '手动执行' : '定时执行' }}</el-descriptions-item>
        <el-descriptions-item label="执行者">{{ viewData.executor }}</el-descriptions-item>
        <el-descriptions-item label="执行时长">{{ viewData.duration ? viewData.duration + '秒' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ parseTime(viewData.start_time) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ parseTime(viewData.end_time) }}</el-descriptions-item>
        <el-descriptions-item label="Thread ID" v-if="viewData.thread_id">{{ viewData.thread_id }}</el-descriptions-item>
        <el-descriptions-item label="Agent ID" v-if="viewData.agent_id">{{ viewData.agent_id }}</el-descriptions-item>
      </el-descriptions>
      
      <el-divider content-position="left" v-if="viewData.error_msg">错误信息</el-divider>
      <el-alert v-if="viewData.error_msg" :title="viewData.error_msg" type="error" show-icon :closable="false" />

      <el-divider content-position="left">执行配置</el-divider>
      <el-input :model-value="JSON.stringify(viewData.config || {}, null, 2)" type="textarea" :rows="4" readonly />

      <el-divider content-position="left" v-if="viewData.result">执行结果</el-divider>
      <el-input v-if="viewData.result" :model-value="JSON.stringify(viewData.result, null, 2)" type="textarea" :rows="8" readonly />

      <el-divider content-position="left" v-if="viewData.reports && viewData.reports.length">关联报告</el-divider>
      <el-table v-if="viewData.reports && viewData.reports.length" :data="viewData.reports" size="small">
        <el-table-column label="报告名称" prop="report_name" />
        <el-table-column label="报告类型" prop="report_type" width="100" />
        <el-table-column label="创建时间" prop="create_time" width="160">
          <template #default="scope">{{ parseTime(scope.row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button link type="primary" @click="goToReport(scope.row.report_id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-divider content-position="left">测试脚本</el-divider>
      <el-input v-model="viewData.script_content" type="textarea" :rows="10" readonly style="font-family: monospace;" />
    </el-dialog>
  </div>
</template>

<script setup name="TestingExecution">
import { listExecution, getExecution, getExecutionStatistics, cancelExecution, retryExecution } from "@/api/testing/execution";
import { generateHtmlReport } from "@/api/testing/report";

const { proxy } = getCurrentInstance();
const router = useRouter();
const route = useRoute();

const executionList = ref([]);
const viewOpen = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const total = ref(0);
const viewData = ref({});
const statistics = ref({ total: 0, success: 0, failed: 0, running: 0, success_rate: 0 });

const data = reactive({
  queryParams: {
    page_num: 1,
    page_size: 10,
    script_id: undefined,
    execution_status: undefined,
    executor: undefined
  }
});

const { queryParams } = toRefs(data);

function getScriptTypeName(type) {
  const typeMap = { 'k6': 'K6性能测试', 'playwright': 'Playwright', 'api': 'API测试' };
  return typeMap[type] || type;
}

function getStatusName(status) {
  const map = { 'pending': '待执行', 'running': '运行中', 'success': '成功', 'failed': '失败', 'cancelled': '已取消' };
  return map[status] || status;
}

function getStatusTag(status) {
  const map = { 'pending': 'info', 'running': 'warning', 'success': 'success', 'failed': 'danger', 'cancelled': '' };
  return map[status] || 'info';
}

function getList() {
  loading.value = true;
  listExecution(queryParams.value).then(response => {
    executionList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

function loadStatistics() {
  getExecutionStatistics(7).then(response => {
    statistics.value = response.data;
  });
}

function handleQuery() {
  queryParams.value.page_num = 1;
  getList();
}

function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

function handleView(row) {
  getExecution(row.execution_id).then(response => {
    viewData.value = response.data;
    viewOpen.value = true;
  });
}

function handleReport(row) {
  generateHtmlReport(row.execution_id).then(response => {
    proxy.$modal.msgSuccess("报告生成成功");
    router.push({ path: '/testing/report', query: { report_id: response.data.report_id } });
  });
}

function handleRetry(row) {
  proxy.$modal.confirm('是否确认重新执行?').then(function() {
    return retryExecution(row.execution_id);
  }).then(response => {
    proxy.$modal.msgSuccess("重试已启动");
    getList();
    loadStatistics();
  }).catch(() => {});
}

function handleCancel(row) {
  proxy.$modal.confirm('是否确认取消执行?').then(function() {
    return cancelExecution({ execution_id: row.execution_id });
  }).then(() => {
    proxy.$modal.msgSuccess("取消成功");
    getList();
    loadStatistics();
  }).catch(() => {});
}

function goToReport(reportId) {
  viewOpen.value = false;
  router.push({ path: '/testing/report', query: { report_id: reportId } });
}

// 自动刷新运行中的执行
let refreshTimer = null;
onMounted(() => {
  // 检查URL参数
  if (route.query.execution_id) {
    getExecution(route.query.execution_id).then(response => {
      viewData.value = response.data;
      viewOpen.value = true;
    });
  }
  
  refreshTimer = setInterval(() => {
    if (statistics.value.running > 0) {
      getList();
      loadStatistics();
    }
  }, 5000);
});

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});

loadStatistics();
getList();
</script>

<style scoped>
.mb20 {
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-card .stat-content {
  position: relative;
  z-index: 1;
}

.stat-card .stat-value {
  font-size: 28px;
  font-weight: bold;
  line-height: 1.2;
}

.stat-card .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.stat-card .stat-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 50px;
  opacity: 0.15;
}

.stat-card-total .stat-value { color: #409EFF; }
.stat-card-total .stat-icon { color: #409EFF; }

.stat-card-success .stat-value { color: #67C23A; }
.stat-card-success .stat-icon { color: #67C23A; }

.stat-card-failed .stat-value { color: #F56C6C; }
.stat-card-failed .stat-icon { color: #F56C6C; }

.stat-card-running .stat-value { color: #E6A23C; }
.stat-card-running .stat-icon { color: #E6A23C; }
</style>

