<template>
  <div class="app-container">
    <el-page-header @back="goBack">
      <template #content>
        <span class="text-large font-600 mr-3">文件管理 - {{ knowledgeName }}</span>
      </template>
    </el-page-header>

    <el-divider />

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="mb20">
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <el-statistic title="文件总数" :value="stats.fileCount">
            <template #suffix>
              <el-icon style="vertical-align: -0.125em"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <el-statistic title="向量总数" :value="stats.vectorCount">
            <template #suffix>
              <el-icon style="vertical-align: -0.125em"><DataAnalysis /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <el-statistic title="处理中" :value="stats.processingCount">
            <template #suffix>
              <el-icon style="vertical-align: -0.125em"><Loading /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <el-statistic title="已完成" :value="stats.completedCount">
            <template #suffix>
              <el-icon style="vertical-align: -0.125em"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索栏 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true" label-width="68px">
      <el-form-item label="文件名" prop="fileName">
        <el-input
          v-model="queryParams.fileName"
          placeholder="请输入文件名"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="处理状态" prop="processStatus">
        <el-select v-model="queryParams.processStatus" placeholder="请选择状态" clearable>
          <el-option label="等待处理" value="pending" />
          <el-option label="处理中" value="processing" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        <el-button type="primary" icon="Refresh" @click="refreshStats">刷新统计</el-button>
      </el-form-item>
    </el-form>

    <!-- 表格 -->
    <el-table v-loading="loading" :data="fileList">
      <el-table-column label="文件ID" align="center" prop="fileId" width="80" />
      <el-table-column label="文件名" align="center" prop="fileName" :show-overflow-tooltip="true" min-width="200" />
      <el-table-column label="文件大小" align="center" prop="fileSize" width="120">
        <template #default="scope">
          {{ formatFileSize(scope.row.fileSize) }}
        </template>
      </el-table-column>
      <el-table-column label="文档ID" align="center" prop="docId" width="150" :show-overflow-tooltip="true">
        <template #default="scope">
          <el-tag v-if="scope.row.docId" type="info" size="small">{{ scope.row.docId }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="处理状态" align="center" prop="processStatus" width="120">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.processStatus)">
            {{ getStatusText(scope.row.processStatus) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="处理进度" align="center" prop="processProgress" width="200">
        <template #default="scope">
          <el-progress
            :percentage="scope.row.processProgress"
            :status="scope.row.processStatus === 'failed' ? 'exception' : (scope.row.processStatus === 'completed' ? 'success' : undefined)"
          />
        </template>
      </el-table-column>
      <el-table-column label="向量数" align="center" prop="vectorCount" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.vectorCount > 0" type="success">{{ scope.row.vectorCount }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="上传时间" align="center" prop="createTime" width="160">
        <template #default="scope">
          {{ parseTime(scope.row.createTime) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="150">
        <template #default="scope">
          <el-tooltip content="查看错误信息" placement="top" v-if="scope.row.processStatus === 'failed' && scope.row.errorMsg">
            <el-button link type="warning" icon="Warning" @click="showError(scope.row)">错误</el-button>
          </el-tooltip>
          <el-button
            link
            type="danger"
            icon="Delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['testing:knowledge:remove']"
          >
            删除
          </el-button>
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

    <!-- 错误信息对话框 -->
    <el-dialog title="错误信息" v-model="errorDialogVisible" width="600px" append-to-body>
      <el-alert
        type="error"
        :closable="false"
        show-icon
      >
        <template #default>
          <pre style="white-space: pre-wrap; word-wrap: break-word;">{{ currentError }}</pre>
        </template>
      </el-alert>
      <template #footer>
        <el-button @click="errorDialogVisible = false">关 闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="KnowledgeFiles">
import { listKnowledgeFiles, deleteKnowledgeFile, getKnowledgeStats } from "@/api/testing/knowledge";

const { proxy } = getCurrentInstance();
const router = useRouter();
const route = useRoute();

const fileList = ref([]);
const loading = ref(true);
const total = ref(0);
const knowledgeId = ref(null);
const knowledgeName = ref("");
const errorDialogVisible = ref(false);
const currentError = ref("");
const refreshTimer = ref(null);

const stats = ref({
  fileCount: 0,
  vectorCount: 0,
  pendingCount: 0,
  processingCount: 0,
  completedCount: 0,
  failedCount: 0
});

const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  fileName: undefined,
  processStatus: undefined
});

/** 获取文件列表 */
function getList() {
  if (!knowledgeId.value) return;
  
  loading.value = true;
  const query = {
    page_num: queryParams.value.pageNum,
    page_size: queryParams.value.pageSize,
    file_name: queryParams.value.fileName,
    process_status: queryParams.value.processStatus
  };
  
  listKnowledgeFiles(knowledgeId.value, query).then(response => {
    fileList.value = (response.data.rows || []).map(item => ({
      fileId: item.file_id,
      knowledgeId: item.knowledge_id,
      fileName: item.file_name,
      filePath: item.file_path,
      fileSize: item.file_size,
      docId: item.doc_id,
      processStatus: item.process_status,
      processProgress: item.process_progress,
      processStartTime: item.process_start_time,
      processEndTime: item.process_end_time,
      errorMsg: item.error_msg,
      vectorCount: item.vector_count,
      createTime: item.create_time,
      updateTime: item.update_time
    }));
    total.value = response.data.total || 0;
    loading.value = false;
  }).catch(() => {
    loading.value = false;
  });
}

/** 获取统计信息 */
function getStats() {
  if (!knowledgeId.value) return;
  
  getKnowledgeStats(knowledgeId.value).then(response => {
    stats.value = {
      fileCount: response.data.file_count || 0,
      vectorCount: response.data.vector_count || 0,
      pendingCount: response.data.pending_count || 0,
      processingCount: response.data.processing_count || 0,
      completedCount: response.data.completed_count || 0,
      failedCount: response.data.failed_count || 0
    };
  });
}

/** 格式化文件大小 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/** 获取状态类型 */
function getStatusType(status) {
  const statusMap = {
    'pending': 'info',
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  };
  return statusMap[status] || 'info';
}

/** 获取状态文本 */
function getStatusText(status) {
  const textMap = {
    'pending': '等待处理',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  };
  return textMap[status] || status;
}

/** 显示错误信息 */
function showError(row) {
  currentError.value = row.errorMsg;
  errorDialogVisible.value = true;
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

/** 刷新统计 */
function refreshStats() {
  getStats();
  getList();
}

/** 删除文件 */
function handleDelete(row) {
  proxy.$modal.confirm('是否确认删除文件"' + row.fileName + '"？').then(function() {
    return deleteKnowledgeFile(row.fileId);
  }).then(() => {
    getList();
    getStats();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 返回 */
function goBack() {
  router.back();
}

/** 自动刷新 */
function startAutoRefresh() {
  // 每10秒刷新一次统计信息
  refreshTimer.value = setInterval(() => {
    getStats();
    // 如果有处理中的文件，也刷新列表
    if (stats.value.processingCount > 0 || stats.value.pendingCount > 0) {
      getList();
    }
  }, 10000);
}

function stopAutoRefresh() {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value);
    refreshTimer.value = null;
  }
}

onMounted(() => {
  // 从路由参数中获取 knowledgeId（路径参数）
  knowledgeId.value = route.params.knowledgeId || route.query.knowledgeId;
  knowledgeName.value = route.query.knowledgeName || "未知";
  
  if (knowledgeId.value) {
    getList();
    getStats();
    startAutoRefresh();
  } else {
    proxy.$modal.msgError("缺少知识库ID参数");
    router.back();
  }
});

onBeforeUnmount(() => {
  stopAutoRefresh();
});
</script>

<style scoped>
.mb20 {
  margin-bottom: 20px;
}

.stats-card {
  text-align: center;
}

.text-large {
  font-size: 18px;
}

.font-600 {
  font-weight: 600;
}

.mr-3 {
  margin-right: 12px;
}
</style>

