<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="报告名称" prop="report_name">
        <el-input v-model="queryParams.report_name" placeholder="请输入报告名称" clearable @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="报告类型" prop="report_type">
        <el-select v-model="queryParams.report_type" placeholder="请选择" clearable>
          <el-option label="HTML" value="html" />
          <el-option label="PDF" value="pdf" />
          <el-option label="JSON" value="json" />
          <el-option label="Allure" value="allure" />
        </el-select>
      </el-form-item>
      <el-form-item label="执行ID" prop="execution_id">
        <el-input v-model="queryParams.execution_id" placeholder="请输入执行ID" clearable @keyup.enter="handleQuery" style="width: 150px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Histogram" :disabled="selectedIds.length < 2" @click="handleCompare" v-hasPermi="['testing:report:compare']">报告对比</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="reportList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="报告ID" align="center" prop="report_id" width="80" />
      <el-table-column label="报告名称" align="center" prop="report_name" :show-overflow-tooltip="true" />
      <el-table-column label="脚本名称" align="center" prop="script_name" width="150" />
      <el-table-column label="所属项目" align="center" prop="project_name" width="120" />
      <el-table-column label="报告类型" align="center" prop="report_type" width="80">
        <template #default="scope">
          <el-tag :type="getReportTypeTag(scope.row.report_type)">{{ scope.row.report_type.toUpperCase() }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="报告大小" align="center" prop="report_size" width="100">
        <template #default="scope">
          {{ formatFileSize(scope.row.report_size) }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="create_time" width="160">
        <template #default="scope">
          <span>{{ parseTime(scope.row.create_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="200">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看</el-button>
          <el-button link type="success" icon="Download" @click="handleDownload(scope.row)" v-hasPermi="['testing:report:download']">下载</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['testing:report:remove']">删除</el-button>
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

    <!-- 报告详情对话框 -->
    <el-dialog title="报告详情" v-model="viewOpen" width="1000px" append-to-body>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="报告名称">{{ viewData.report_name }}</el-descriptions-item>
        <el-descriptions-item label="报告类型">
          <el-tag :type="getReportTypeTag(viewData.report_type)">{{ (viewData.report_type || '').toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="报告大小">{{ formatFileSize(viewData.report_size) }}</el-descriptions-item>
        <el-descriptions-item label="脚本名称">{{ viewData.script_name }}</el-descriptions-item>
        <el-descriptions-item label="脚本类型">{{ getScriptTypeName(viewData.script_type) }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ viewData.project_name }}</el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <el-tag :type="getStatusTag(viewData.execution_status)">{{ getStatusName(viewData.execution_status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行时长">{{ viewData.duration ? viewData.duration + '秒' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(viewData.create_time) }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left" v-if="viewData.summary">报告摘要</el-divider>
      <el-descriptions v-if="viewData.summary" :column="2" border size="small">
        <el-descriptions-item v-for="(value, key) in viewData.summary" :key="key" :label="key">{{ value }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left" v-if="viewData.metrics">关键指标</el-divider>
      <el-row v-if="viewData.metrics" :gutter="20">
        <el-col :span="6" v-for="(value, key) in viewData.metrics" :key="key">
          <el-card shadow="never" class="metric-card">
            <div class="metric-value">{{ value }}</div>
            <div class="metric-label">{{ key }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-divider content-position="left" v-if="viewData.report_content">报告内容</el-divider>
      <div v-if="viewData.report_content && viewData.report_type === 'html'" class="report-preview" v-html="viewData.report_content"></div>
      <el-input v-else-if="viewData.report_content" :model-value="viewData.report_content" type="textarea" :rows="15" readonly style="font-family: monospace;" />

      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" icon="Download" @click="handleDownload(viewData)">下载报告</el-button>
          <el-button @click="viewOpen = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 报告对比对话框 -->
    <el-dialog title="报告对比" v-model="compareOpen" width="1200px" append-to-body>
      <el-table :data="compareData.reports" border>
        <el-table-column label="报告名称" prop="report_name" />
        <el-table-column label="脚本名称" prop="script_name" width="150" />
        <el-table-column label="执行状态" prop="execution_status" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.execution_status)">{{ getStatusName(scope.row.execution_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="执行时长" prop="duration" width="100">
          <template #default="scope">{{ scope.row.duration ? scope.row.duration + 's' : '-' }}</template>
        </el-table-column>
        <el-table-column label="创建时间" prop="create_time" width="160">
          <template #default="scope">{{ parseTime(scope.row.create_time) }}</template>
        </el-table-column>
      </el-table>

      <el-divider content-position="left">执行时长对比</el-divider>
      <el-row :gutter="10">
        <el-col :span="12">
          <div class="compare-chart">
            <div v-for="item in compareData.comparison?.execution_time || []" :key="item.report_id" class="compare-bar-item">
              <span class="bar-label">{{ item.report_name }}</span>
              <div class="bar-container">
                <div class="bar-fill" :style="{ width: getBarWidth(item.duration) + '%' }"></div>
                <span class="bar-value">{{ item.duration }}s</span>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <el-descriptions title="指标对比" :column="1" border v-if="compareData.comparison?.metrics_comparison">
            <el-descriptions-item v-for="(values, key) in compareData.comparison.metrics_comparison" :key="key" :label="key">
              <span v-for="(item, idx) in values" :key="idx" class="metric-compare-item">
                报告{{ item.report_id }}: {{ item.value }}
                <span v-if="idx < values.length - 1"> | </span>
              </span>
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
    </el-dialog>
  </div>
</template>

<script setup name="TestingReport">
import { listReport, getReport, delReport, downloadReport, compareReports } from "@/api/testing/report";

const { proxy } = getCurrentInstance();
const route = useRoute();

const reportList = ref([]);
const viewOpen = ref(false);
const compareOpen = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const selectedIds = ref([]);
const total = ref(0);
const viewData = ref({});
const compareData = ref({ reports: [], comparison: {} });

const data = reactive({
  queryParams: {
    page_num: 1,
    page_size: 10,
    report_name: undefined,
    report_type: undefined,
    execution_id: undefined
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

function getReportTypeTag(type) {
  const map = { 'html': '', 'pdf': 'danger', 'json': 'warning', 'allure': 'success' };
  return map[type] || 'info';
}

function formatFileSize(bytes) {
  if (!bytes) return '-';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
  return (bytes / 1024 / 1024).toFixed(2) + ' MB';
}

function getBarWidth(duration) {
  const maxDuration = Math.max(...(compareData.value.comparison?.execution_time?.map(i => i.duration) || [1]));
  return (duration / maxDuration) * 100;
}

function getList() {
  loading.value = true;
  listReport(queryParams.value).then(response => {
    reportList.value = response.rows;
    total.value = response.total;
    loading.value = false;
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

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.report_id);
}

function handleView(row) {
  getReport(row.report_id).then(response => {
    viewData.value = response.data;
    viewOpen.value = true;
  });
}

function handleDownload(row) {
  window.open(`/dev-api/api/testing/report/${row.report_id}/download`, '_blank');
}

function handleDelete(row) {
  proxy.$modal.confirm('是否确认删除报告"' + row.report_name + '"?').then(function() {
    return delReport(row.report_id);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

function handleCompare() {
  if (selectedIds.value.length < 2) {
    proxy.$modal.msgWarning("请至少选择2个报告进行对比");
    return;
  }
  compareReports({ report_ids: selectedIds.value }).then(response => {
    compareData.value = response.data;
    compareOpen.value = true;
  });
}

onMounted(() => {
  if (route.query.report_id) {
    getReport(route.query.report_id).then(response => {
      viewData.value = response.data;
      viewOpen.value = true;
    });
  }
});

getList();
</script>

<style scoped>
.metric-card {
  text-align: center;
  margin-bottom: 15px;
}

.metric-card .metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.metric-card .metric-label {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
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
}

.compare-bar-item .bar-label {
  display: block;
  margin-bottom: 5px;
  font-size: 12px;
  color: #606266;
}

.compare-bar-item .bar-container {
  display: flex;
  align-items: center;
  background: #f0f0f0;
  border-radius: 4px;
  height: 24px;
  position: relative;
}

.compare-bar-item .bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  border-radius: 4px;
  transition: width 0.3s;
}

.compare-bar-item .bar-value {
  position: absolute;
  right: 10px;
  font-size: 12px;
  font-weight: bold;
}

.metric-compare-item {
  margin-right: 10px;
}
</style>

