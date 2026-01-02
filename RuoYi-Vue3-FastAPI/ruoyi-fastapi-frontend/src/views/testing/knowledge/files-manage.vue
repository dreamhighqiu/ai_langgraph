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
          <el-table-column label="项目" align="center" prop="projectName" width="150" v-if="!queryParams.projectId">
            <template #default="scope">
              <el-tag v-if="scope.row.projectName" type="info" size="small">{{ scope.row.projectName }}</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
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
                v-if="canPreviewOrDownload(scope.row)"
                link
                type="primary"
                icon="View"
                @click="handlePreview(scope.row)"
              >
                预览
              </el-button>
              <el-button
                v-if="canPreviewOrDownload(scope.row)"
                link
                type="primary"
                icon="Download"
                @click="handleDownload(scope.row)"
              >
                下载
              </el-button>
              <span v-if="!canPreviewOrDownload(scope.row)" style="color: #999; font-size: 12px;">
                {{ getUnavailableReason(scope.row) }}
              </span>
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
          <el-table-column label="项目" align="center" prop="knowledge_name" width="150" v-if="!queryParams.projectId">
            <template #default="scope">
              <el-tag v-if="scope.row.knowledge_name" type="info" size="small">{{ scope.row.knowledge_name }}</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="文件名" align="center" prop="file_name" :show-overflow-tooltip="true" min-width="250">
            <template #default="scope">
              <div style="display: flex; align-items: center; gap: 8px;">
                <el-icon><Document /></el-icon>
                <span>{{ scope.row.file_name || scope.row.file_path || '-' }}</span>
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
          <el-table-column label="操作" align="center" width="200" fixed="right">
            <template #default="scope">
              <el-button
                link
                type="primary"
                icon="View"
                @click="handlePreviewRagFile(scope.row)"
                v-if="scope.row.file_url"
              >
                预览文件
              </el-button>
              <el-button
                link
                type="primary"
                icon="InfoFilled"
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
    <el-dialog title="文件预览" v-model="previewVisible" width="80%" append-to-body @close="handlePreviewClose">
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
import { getAllFiles, getAllRagDocuments } from "@/api/testing/knowledge";
import { Folder, Document } from '@element-plus/icons-vue';
import request from '@/utils/request';
import axios from 'axios';
import { getToken } from '@/utils/auth';

const { proxy } = getCurrentInstance();

const projectList = ref([]);
const loading = ref(false);
const ragLoading = ref(false);
const showSearch = ref(true);
const activeTab = ref('original');
const previewVisible = ref(false);
const previewUrl = ref('');
const previewBlobUrl = ref(null); // 存储blob URL，用于释放内存
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
  projectId: undefined  // 默认不选择项目，显示所有项目的文件
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
  // 无论是否选择项目，都加载数据（如果未选择项目，显示所有项目的文件）
  getOriginalFileList();
  if (activeTab.value === 'rag') {
    getRagDocumentList();
  }
}

/** 获取原始文件列表 */
function getOriginalFileList() {
  loading.value = true;
  const query = {
    page_num: originalQueryParams.value.pageNum,
    page_size: originalQueryParams.value.pageSize,
    project_id: queryParams.value.projectId || undefined  // 如果未选择项目，传undefined显示所有
  };
  
  getAllFiles(query).then(response => {
    if (response.code === 200 && response.data) {
      originalFileList.value = (response.data.rows || []).map(item => ({
        fileId: item.file_id,
        fileName: item.file_name,
        fileType: item.file_type,
        fileSize: item.file_size,
        fileUrl: item.file_url,
        processStatus: item.process_status,
        createTime: item.create_time,
        projectId: item.project_id,
        projectName: item.project_name,
        knowledgeName: item.knowledge_name
      }));
      originalTotal.value = response.data.total || 0;
    }
    loading.value = false;
  }).catch(() => {
    loading.value = false;
  });
}

/** 获取RAG处理后的文档列表 */
function getRagDocumentList() {
  ragLoading.value = true;
  const params = {
    project_id: queryParams.value.projectId || undefined,  // 如果未选择项目，传undefined显示所有
    status_filter: ragQueryParams.value.statusFilter || undefined,
    page: ragQueryParams.value.page,
    page_size: ragQueryParams.value.pageSize
  };
  
  getAllRagDocuments(params).then(response => {
    if (response.code === 200 && response.data) {
      ragDocumentList.value = (response.data.documents || []).map(doc => ({
        id: doc[0] || doc.id,  // doc可能是[doc_id, DocProcessingStatus]元组或对象
        ...(typeof doc[1] === 'object' ? doc[1] : doc),  // 如果是元组，展开DocProcessingStatus
        project_id: doc.project_id,
        knowledge_id: doc.knowledge_id,
        knowledge_name: doc.knowledge_name
      }));
      ragTotal.value = response.data.total || response.data.pagination?.total_count || 0;
    }
    ragLoading.value = false;
  }).catch(() => {
    ragLoading.value = false;
  });
}

/** Tab切换 */
function handleTabChange(tab) {
  if (tab === 'rag') {
    getRagDocumentList();
  } else if (tab === 'original') {
    getOriginalFileList();
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
  queryParams.value.projectId = undefined;  // 重置为显示所有项目
  originalQueryParams.value.pageNum = 1;
  getOriginalFileList();
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
    'processed': '已处理',
    'failed': '失败'
  };
  return textMap[status] || status;
}

/** 判断是否可以预览或下载 */
function canPreviewOrDownload(row) {
  // 只要有fileId就可以下载/预览
  const fileId = row.fileId || row.file_id;
  if (!fileId) {
    return false;
  }
  
  // 如果状态是pending或processing，可能文件还未准备好
  const status = row.processStatus || row.process_status;
  if (status === 'pending' || status === 'processing') {
    return false;
  }
  
  // 其他状态（completed, processed, failed等）都允许预览/下载
  return true;
}

/** 获取不可用的原因 */
function getUnavailableReason(row) {
  if (!row.fileId && !row.file_id) {
    return '文件ID缺失';
  }
  const status = row.processStatus || row.process_status;
  if (status === 'pending') {
    return '等待处理';
  }
  if (status === 'processing') {
    return '处理中';
  }
  return '暂不可用';
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
async function handlePreview(row) {
  const fileId = row.fileId || row.file_id;
  if (!fileId) {
    proxy.$modal.msgWarning('文件ID不可用，无法预览');
    return;
  }
  
  try {
    // 释放之前的blob URL（如果存在）
    if (previewBlobUrl.value) {
      URL.revokeObjectURL(previewBlobUrl.value);
      previewBlobUrl.value = null;
    }
    
    // 使用axios直接获取文件内容，这样可以获取完整的响应信息（包括响应头）
    const baseUrl = import.meta.env.VITE_APP_BASE_API || '';
    const response = await axios({
      url: `${baseUrl}/testing/knowledge/files/${fileId}/download`,
      method: 'get',
      params: { preview: true },
      responseType: 'blob',
      headers: {
        'Authorization': 'Bearer ' + getToken()
      }
    });
    
    // axios返回的blob响应，response.data是Blob对象，response.headers包含响应头
    let blob = response.data;
    let mimeType = blob.type || 'application/octet-stream';
    
    // 如果Blob没有type或type不正确，从响应头获取
    if (!mimeType || mimeType === 'application/octet-stream') {
      const contentType = response.headers['content-type'];
      if (contentType) {
        mimeType = contentType.split(';')[0].trim(); // 移除charset等参数
      }
    }
    
    // 如果还是没有，根据文件名推断MIME类型
    if (!mimeType || mimeType === 'application/octet-stream') {
      const fileName = row.fileName || row.file_name || '';
      const ext = fileName.toLowerCase().split('.').pop() || '';
      const mimeMap = {
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'md': 'text/markdown',
        'html': 'text/html',
        'htm': 'text/html',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'json': 'application/json',
        'xml': 'application/xml',
      };
      mimeType = mimeMap[ext] || 'application/octet-stream';
    }
    
    // 如果推断出的类型与Blob类型不同，创建新的Blob以确保正确的MIME类型
    if (blob.type !== mimeType) {
      blob = new Blob([blob], { type: mimeType });
    }
    
    // 创建blob URL
    const blobUrl = URL.createObjectURL(blob);
    
    previewBlobUrl.value = blobUrl;
    previewUrl.value = blobUrl;
    previewVisible.value = true;
  } catch (error) {
    console.error('预览文件失败:', error);
    // 检查是否是401错误
    if (error.response && error.response.status === 401) {
      proxy.$modal.msgError('预览文件失败：用户未登录，请先完成登录');
    } else if (error.response && error.response.status === 404) {
      proxy.$modal.msgError('预览文件失败：文件不存在');
    } else {
      proxy.$modal.msgError('预览文件失败：' + (error.message || '未知错误'));
    }
  }
}

/** 关闭预览对话框时释放blob URL */
function handlePreviewClose() {
  if (previewBlobUrl.value) {
    URL.revokeObjectURL(previewBlobUrl.value);
    previewBlobUrl.value = null;
  }
  previewUrl.value = '';
}

/** 下载文件 */
function handleDownload(row) {
  const fileId = row.fileId || row.file_id;
  if (!fileId) {
    proxy.$modal.msgWarning('文件ID不可用，无法下载');
    return;
  }
  
  let url = row.fileUrl || row.file_url;
  
  // 如果没有fileUrl，通过fileId生成URL
  if (!url) {
    const baseUrl = import.meta.env.VITE_APP_BASE_API || '';
    url = `${baseUrl}/testing/knowledge/files/${fileId}/download`;
  }
  
  // 确保是下载而不是预览
  if (url.includes('preview=true')) {
    url = url.replace('preview=true', 'preview=false');
  } else if (!url.includes('preview=')) {
    url = url + (url.includes('?') ? '&' : '?') + 'preview=false';
  }
  
  window.open(url, '_blank');
}

/** 预览RAG文档的原始文件 */
async function handlePreviewRagFile(row) {
  const fileId = row.fileId || row.file_id;
  if (fileId) {
    // 如果有fileId，使用handlePreview函数（会自动携带token）
    await handlePreview(row);
  } else if (row.file_url) {
    // 如果没有fileId但有file_url，直接使用（可能是MinIO预签名URL）
    previewUrl.value = row.file_url;
    previewVisible.value = true;
  } else {
    proxy.$modal.msgWarning('文件URL不可用，无法预览');
  }
}

/** 查看RAG文档详情 */
function handleViewRagDocument(row) {
  currentRagDocument.value = row;
  ragDetailVisible.value = true;
}

onMounted(() => {
  getProjectList();
  // 默认加载所有项目的文件
  getOriginalFileList();
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

