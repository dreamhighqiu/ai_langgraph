<template>
  <div class="app-container">
    <el-card class="header-card mb-4">
      <div class="header-content">
        <div>
          <h2><el-icon><Folder /></el-icon> 文件管理</h2>
          <p class="subtitle">File Management - 按项目查看文件，支持预览原始文件和RAG处理后的文档</p>
        </div>
      </div>
    </el-card>

    <!-- 项目选择 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="项目" prop="projectId">
        <el-select
          v-model="queryParams.projectId"
          placeholder="请选择项目"
          clearable
          style="width: 200px"
          @change="handleProjectChange"
        >
          <el-option
            v-for="project in projectList"
            :key="project.projectId"
            :label="project.projectName"
            :value="project.projectId"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- Tab切换：原始文件 / RAG处理后的文档 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="原始文件" name="original">
        <el-table v-loading="loading" :data="originalFileList">
          <el-table-column label="文件名" align="center" prop="fileName" :show-overflow-tooltip="true" min-width="200">
            <template #default="scope">
              <div style="display: flex; align-items: center; gap: 8px;">
                <el-icon><Document /></el-icon>
                <span>{{ scope.row.fileName }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="文件格式" align="center" prop="fileType" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.fileType" type="info" size="small">{{ scope.row.fileType }}</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="文件大小" align="center" prop="fileSize" width="120">
            <template #default="scope">
              {{ formatFileSize(scope.row.fileSize) }}
            </template>
          </el-table-column>
          <el-table-column label="处理状态" align="center" prop="processStatus" width="120">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.processStatus)">
                {{ getStatusText(scope.row.processStatus) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="上传时间" align="center" prop="createTime" width="160">
            <template #default="scope">
              {{ parseTime(scope.row.createTime) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="200" fixed="right">
            <template #default="scope">
              <el-button
                link
                type="primary"
                icon="View"
                @click="handlePreview(scope.row)"
                :disabled="!scope.row.fileUrl"
                v-if="scope.row.processStatus === 'completed'"
              >
                预览
              </el-button>
              <el-button
                link
                type="primary"
                icon="Download"
                @click="handleDownload(scope.row)"
                :disabled="!scope.row.fileUrl"
                v-if="scope.row.processStatus === 'completed'"
              >
                下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="originalTotal > 0"
          :total="originalTotal"
          v-model:page="originalQueryParams.pageNum"
          v-model:limit="originalQueryParams.pageSize"
          @pagination="getOriginalFileList"
        />
      </el-tab-pane>

      <el-tab-pane label="RAG处理后的文档" name="rag">
        <el-form :model="ragQueryParams" ref="ragQueryRef" :inline="true" label-width="68px" class="mb-4">
          <el-form-item label="状态" prop="statusFilter">
            <el-select v-model="ragQueryParams.statusFilter" placeholder="请选择状态" clearable style="width: 200px">
              <el-option label="全部" value="" />
              <el-option label="等待处理" value="PENDING" />
              <el-option label="处理中" value="PROCESSING" />
              <el-option label="预处理完成" value="PREPROCESSED" />
              <el-option label="处理完成" value="PROCESSED" />
              <el-option label="失败" value="FAILED" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleRagQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetRagQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-table v-loading="ragLoading" :data="ragDocumentList">
          <el-table-column label="文件路径" align="center" prop="file_path" :show-overflow-tooltip="true" min-width="250">
            <template #default="scope">
              <div style="display: flex; align-items: center; gap: 8px;">
                <el-icon><Document /></el-icon>
                <span>{{ scope.row.file_path }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="文档ID" align="center" prop="id" width="150" :show-overflow-tooltip="true">
            <template #default="scope">
              <el-tag v-if="scope.row.id" type="info" size="small">{{ scope.row.id }}</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" align="center" prop="status" width="120">
            <template #default="scope">
              <el-tag :type="getRagStatusType(scope.row.status)">
                {{ getRagStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" align="center" prop="created_at" width="160">
            <template #default="scope">
              {{ formatRagTime(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="更新时间" align="center" prop="updated_at" width="160">
            <template #default="scope">
              {{ formatRagTime(scope.row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="150" fixed="right">
            <template #default="scope">
              <el-button
                link
                type="primary"
                icon="View"
                @click="handleViewRagDocument(scope.row)"
                v-if="scope.row.status === 'PROCESSED'"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="ragTotal > 0"
          :total="ragTotal"
          v-model:page="ragQueryParams.page"
          v-model:limit="ragQueryParams.pageSize"
          @pagination="getRagDocumentList"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 文件预览对话框 -->
    <el-dialog title="文件预览" v-model="previewVisible" width="80%" append-to-body>
      <iframe
        v-if="previewUrl"
        :src="previewUrl"
        style="width: 100%; height: 70vh; border: none;"
      ></iframe>
      <div v-else style="text-align: center; padding: 40px;">
        <el-icon :size="60" color="#ccc"><Document /></el-icon>
        <p>无法预览此文件</p>
      </div>
    </el-dialog>

    <!-- RAG文档详情对话框 -->
    <el-dialog title="RAG文档详情" v-model="ragDetailVisible" width="80%" append-to-body>
      <el-descriptions :column="2" border v-if="currentRagDocument">
        <el-descriptions-item label="文件路径">{{ currentRagDocument.file_path }}</el-descriptions-item>
        <el-descriptions-item label="文档ID">{{ currentRagDocument.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getRagStatusType(currentRagDocument.status)">
            {{ getRagStatusText(currentRagDocument.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatRagTime(currentRagDocument.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间" :span="2">{{ formatRagTime(currentRagDocument.updated_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup name="KnowledgeFilesManage">
import { listAllProject } from "@/api/testing/project";
import { listKnowledgeFiles, listKnowledge, getProjectRagDocuments } from "@/api/testing/knowledge";
import { Folder, Document } from '@element-plus/icons-vue';

const { proxy } = getCurrentInstance();

const projectList = ref([]);
const loading = ref(false);
const ragLoading = ref(false);
const showSearch = ref(true);
const activeTab = ref('original');
const previewVisible = ref(false);
const previewUrl = ref('');
const ragDetailVisible = ref(false);
const currentRagDocument = ref(null);

const originalFileList = ref([]);
const originalTotal = ref(0);
const originalQueryParams = ref({
  pageNum: 1,
  pageSize: 10
});

const ragDocumentList = ref([]);
const ragTotal = ref(0);
const ragQueryParams = ref({
  page: 1,
  pageSize: 50,
  statusFilter: ''
});

const queryParams = ref({
  projectId: undefined
});

/** 查询项目列表 */
function getProjectList() {
  listAllProject('0').then(response => {
    if (response.code === 200 && response.data) {
      projectList.value = (response.data || []).map(item => ({
        projectId: item.project_id,
        projectName: item.project_name
      }));
    }
  });
}

/** 项目改变 */
function handleProjectChange() {
  if (queryParams.value.projectId) {
    getOriginalFileList();
    if (activeTab.value === 'rag') {
      getRagDocumentList();
    }
  }
}

/** 获取原始文件列表 */
function getOriginalFileList() {
  if (!queryParams.value.projectId) {
    originalFileList.value = [];
    originalTotal.value = 0;
    return;
  }

  loading.value = true;
  // 先获取项目的知识库ID
  listKnowledge({ project_id: queryParams.value.projectId, page_num: 1, page_size: 1 }).then(response => {
    if (response.code === 200 && response.data && response.data.rows && response.data.rows.length > 0) {
      const knowledgeId = response.data.rows[0].knowledge_id;
      const query = {
        page_num: originalQueryParams.value.pageNum,
        page_size: originalQueryParams.value.pageSize
      };
      listKnowledgeFiles(knowledgeId, query).then(fileResponse => {
        if (fileResponse.code === 200 && fileResponse.data) {
          originalFileList.value = (fileResponse.data.rows || []).map(item => ({
            fileId: item.file_id,
            fileName: item.file_name,
            fileType: item.file_type,
            fileSize: item.file_size,
            fileUrl: item.file_url,
            processStatus: item.process_status,
            createTime: item.create_time
          }));
          originalTotal.value = fileResponse.data.total || 0;
        }
        loading.value = false;
      }).catch(() => {
        loading.value = false;
      });
    } else {
      loading.value = false;
      originalFileList.value = [];
      originalTotal.value = 0;
    }
  }).catch(() => {
    loading.value = false;
  });
}

/** 获取RAG处理后的文档列表 */
function getRagDocumentList() {
  if (!queryParams.value.projectId) {
    ragDocumentList.value = [];
    ragTotal.value = 0;
    return;
  }

  ragLoading.value = true;
  const params = {
    status_filter: ragQueryParams.value.statusFilter || undefined,
    page: ragQueryParams.value.page,
    page_size: ragQueryParams.value.pageSize
  };
  getProjectRagDocuments(queryParams.value.projectId, params).then(response => {
    if (response.code === 200 && response.data) {
      ragDocumentList.value = response.data.documents || [];
      ragTotal.value = response.data.total || 0;
    }
    ragLoading.value = false;
  }).catch(() => {
    ragLoading.value = false;
  });
}

/** Tab切换 */
function handleTabChange(tab) {
  if (tab === 'rag' && queryParams.value.projectId) {
    getRagDocumentList();
  }
}

/** 搜索 */
function handleQuery() {
  originalQueryParams.value.pageNum = 1;
  getOriginalFileList();
}

/** 重置 */
function resetQuery() {
  proxy.resetForm("queryRef");
  originalFileList.value = [];
  originalTotal.value = 0;
}

/** RAG搜索 */
function handleRagQuery() {
  ragQueryParams.value.page = 1;
  getRagDocumentList();
}

/** RAG重置 */
function resetRagQuery() {
  proxy.resetForm("ragQueryRef");
  ragQueryParams.value.statusFilter = '';
  handleRagQuery();
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

/** 获取RAG状态类型 */
function getRagStatusType(status) {
  const statusMap = {
    'PENDING': 'info',
    'PROCESSING': 'warning',
    'PREPROCESSED': 'primary',
    'PROCESSED': 'success',
    'FAILED': 'danger'
  };
  return statusMap[status] || 'info';
}

/** 获取RAG状态文本 */
function getRagStatusText(status) {
  const textMap = {
    'PENDING': '等待处理',
    'PROCESSING': '处理中',
    'PREPROCESSED': '预处理完成',
    'PROCESSED': '处理完成',
    'FAILED': '失败'
  };
  return textMap[status] || status;
}

/** 格式化RAG时间 */
function formatRagTime(timeStr) {
  if (!timeStr) return '-';
  try {
    return parseTime(timeStr);
  } catch {
    return timeStr;
  }
}

/** 预览文件 */
function handlePreview(row) {
  if (row.fileUrl) {
    // 如果是后端API URL，添加preview参数
    let url = row.fileUrl;
    if (url.includes('/files/') && url.includes('/download')) {
      url = url + (url.includes('?') ? '&' : '?') + 'preview=true';
    }
    previewUrl.value = url;
    previewVisible.value = true;
  } else {
    proxy.$modal.msgWarning('文件URL不可用，无法预览');
  }
}

/** 下载文件 */
function handleDownload(row) {
  if (row.fileUrl) {
    window.open(row.fileUrl, '_blank');
  } else {
    proxy.$modal.msgWarning('文件URL不可用，无法下载');
  }
}

/** 查看RAG文档详情 */
function handleViewRagDocument(row) {
  currentRagDocument.value = row;
  ragDetailVisible.value = true;
}

onMounted(() => {
  getProjectList();
});
</script>

<style scoped>
.header-card {
  margin-bottom: 16px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.mb-4 {
  margin-bottom: 16px;
}
</style>

