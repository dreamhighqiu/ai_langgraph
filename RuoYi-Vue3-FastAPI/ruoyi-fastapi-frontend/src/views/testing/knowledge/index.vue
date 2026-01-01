<template>
  <div class="app-container">
    <!-- 页面标题卡片 -->
    <el-card class="header-card mb-4">
      <div class="header-content">
        <div>
          <h2><el-icon><Collection /></el-icon> 知识库管理</h2>
          <p class="subtitle">Knowledge Base Management - 管理测试项目的知识库，支持文档上传和RAG智能问答</p>
        </div>
      </div>
    </el-card>

    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="项目" prop="projectId">
        <el-select
          v-model="queryParams.projectId"
          placeholder="请选择项目"
          clearable
          style="width: 200px"
        >
          <el-option
            v-for="project in projectList"
            :key="project.projectId"
            :label="project.projectName"
            :value="project.projectId"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="知识库名称" prop="knowledgeName">
        <el-input
          v-model="queryParams.knowledgeName"
          placeholder="请输入知识库名称"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
          <el-option label="正常" value="0" />
          <el-option label="停用" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['testing:knowledge:add']">新增知识库</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['testing:knowledge:remove']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="knowledgeList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="知识库ID" align="center" prop="knowledgeId" width="100" />
      <el-table-column label="知识库名称" align="center" prop="knowledgeName" :show-overflow-tooltip="true" width="180" />
      <el-table-column label="Collection" align="center" prop="collectionName" :show-overflow-tooltip="true" width="200">
        <template #default="scope">
          <el-tag type="info" size="small">{{ scope.row.collectionName }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="文件数" align="center" prop="fileCount" width="100">
        <template #default="scope">
          <el-tag>{{ scope.row.fileCount }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="向量数" align="center" prop="vectorCount" width="100">
        <template #default="scope">
          <el-tag type="success">{{ scope.row.vectorCount }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="描述" align="center" prop="description" :show-overflow-tooltip="true" min-width="150" />
      <el-table-column label="状态" align="center" prop="status" width="80">
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            active-value="0"
            inactive-value="1"
            @change="handleStatusChange(scope.row)"
            v-hasPermi="['testing:knowledge:edit']"
          />
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="160">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="360" fixed="right">
        <template #default="scope">
          <el-button link type="primary" icon="Upload" @click="handleUpload(scope.row)" v-hasPermi="['testing:knowledge:upload']">上传</el-button>
          <el-button link type="primary" icon="Document" @click="handleFiles(scope.row)" v-hasPermi="['testing:knowledge:list']">文件</el-button>
          <el-button link type="primary" icon="ChatLineRound" @click="handleChat(scope.row)" v-hasPermi="['testing:knowledge:query']">问答</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['testing:knowledge:edit']">修改</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['testing:knowledge:remove']">删除</el-button>
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

    <!-- 添加或修改知识库对话框 -->
    <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form ref="knowledgeRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="所属项目" prop="projectId">
          <el-select v-model="form.projectId" placeholder="请选择项目" style="width: 100%" :disabled="form.knowledgeId">
            <el-option
              v-for="project in projectList"
              :key="project.projectId"
              :label="project.projectName"
              :value="project.projectId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="知识库名称" prop="knowledgeName">
          <el-input v-model="form.knowledgeName" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="form.knowledgeId">
          <el-radio-group v-model="form.status">
            <el-radio value="0">正常</el-radio>
            <el-radio value="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 上传文件对话框 -->
    <el-dialog title="上传文件" v-model="uploadOpen" width="600px" append-to-body>
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="handleBeforeUpload"
        :file-list="fileList"
        :auto-upload="false"
        drag
        multiple
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、TXT、DOCX、MD、HTML 等格式，单个文件不超过 50MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitUpload">确 定</el-button>
          <el-button @click="uploadOpen = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Knowledge">
import { listKnowledge, getKnowledge, createKnowledge, updateKnowledge, deleteKnowledge } from "@/api/testing/knowledge";
import { listAllProject } from "@/api/testing/project";
import { getToken } from '@/utils/auth';
import { Collection } from '@element-plus/icons-vue';

const { proxy } = getCurrentInstance();
const router = useRouter();

const knowledgeList = ref([]);
const projectList = ref([]);
const open = ref(false);
const uploadOpen = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const fileList = ref([]);

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    projectId: undefined,
    knowledgeName: undefined,
    status: undefined
  },
  rules: {
    projectId: [{ required: true, message: "所属项目不能为空", trigger: "change" }],
    knowledgeName: [{ required: true, message: "知识库名称不能为空", trigger: "blur" }]
  }
});

const { queryParams, form, rules } = toRefs(data);

// 计算上传地址和请求头
const uploadUrl = computed(() => {
  return import.meta.env.VITE_APP_BASE_API + `/testing/knowledge/${form.value.knowledgeId}/files/upload`;
});

const uploadHeaders = computed(() => {
  return {
    'Authorization': 'Bearer ' + getToken()
  };
});

/** 查询项目列表 */
function getProjectList() {
  listAllProject('0').then(response => {
    if (response.code === 200 && response.data) {
      projectList.value = (response.data || []).map(item => ({
        projectId: item.project_id,
        projectName: item.project_name
      }));
    } else {
      console.warn('查询项目列表失败:', response);
      projectList.value = [];
    }
  }).catch(error => {
    console.error('查询项目列表失败:', error);
    projectList.value = [];
  });
}

/** 查询知识库列表 */
function getList() {
  loading.value = true;
  const query = {
    page_num: queryParams.value.pageNum,
    page_size: queryParams.value.pageSize,
    project_id: queryParams.value.projectId,
    knowledge_name: queryParams.value.knowledgeName,
    status: queryParams.value.status
  };
  listKnowledge(query).then(response => {
    console.log('知识库列表响应:', response);
    if (response.code === 200 && response.data) {
      knowledgeList.value = (response.data.rows || []).map(item => ({
        knowledgeId: item.knowledge_id,
        projectId: item.project_id,
        knowledgeName: item.knowledge_name,
        collectionName: item.collection_name || item.milvus_collection_name || '',
        description: item.description,
        fileCount: item.file_count || 0,
        vectorCount: item.vector_count || 0,
        status: item.status,
        createTime: item.create_time,
        updateTime: item.update_time,
        remark: item.remark
      }));
      total.value = response.data.total || 0;
    } else {
      proxy.$modal.msgError(response.msg || '查询失败');
      knowledgeList.value = [];
      total.value = 0;
    }
    loading.value = false;
  }).catch(error => {
    console.error('查询知识库列表失败:', error);
    proxy.$modal.msgError('查询失败，请检查网络连接');
    loading.value = false;
  });
}

/** 取消按钮 */
function cancel() {
  open.value = false;
  reset();
}

/** 表单重置 */
function reset() {
  form.value = {
    knowledgeId: undefined,
    projectId: undefined,
    knowledgeName: undefined,
    description: undefined,
    status: "0",
    remark: undefined
  };
  proxy.resetForm("knowledgeRef");
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

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.knowledgeId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加知识库";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const knowledgeId = row.knowledgeId || ids.value[0];
  getKnowledge(knowledgeId).then(response => {
    form.value = {
      knowledgeId: response.data.knowledge_id,
      projectId: response.data.project_id,
      knowledgeName: response.data.knowledge_name,
      description: response.data.description,
      status: response.data.status,
      remark: response.data.remark
    };
    open.value = true;
    title.value = "修改知识库";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["knowledgeRef"].validate(valid => {
    if (valid) {
      if (form.value.knowledgeId != undefined) {
        updateKnowledge(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        createKnowledge(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const knowledgeIds = row.knowledgeId || ids.value;
  proxy.$modal.confirm('是否确认删除知识库编号为"' + knowledgeIds + '"的数据项？此操作将删除所有相关文件和向量数据！').then(function() {
    return deleteKnowledge(knowledgeIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 状态修改 */
function handleStatusChange(row) {
  let text = row.status === "0" ? "启用" : "停用";
  proxy.$modal.confirm('确认要"' + text + '""' + row.knowledgeName + '"知识库吗？').then(function() {
    return updateKnowledge(row);
  }).then(() => {
    proxy.$modal.msgSuccess(text + "成功");
  }).catch(function() {
    row.status = row.status === "0" ? "1" : "0";
  });
}

/** 上传文件 */
function handleUpload(row) {
  reset();
  form.value.knowledgeId = row.knowledgeId;
  fileList.value = [];
  uploadOpen.value = true;
}

/** 上传前校验 */
function handleBeforeUpload(file) {
  const isLt50M = file.size / 1024 / 1024 < 50;
  if (!isLt50M) {
    proxy.$modal.msgError("上传文件大小不能超过 50MB!");
    return false;
  }
  return true;
}

/** 提交上传 */
function submitUpload() {
  proxy.$refs.uploadRef.submit();
}

/** 上传成功回调 */
function handleUploadSuccess(response, file) {
  if (response.code === 200) {
    proxy.$modal.msgSuccess("上传成功：" + file.name);
    uploadOpen.value = false;
    getList();
  } else {
    proxy.$modal.msgError("上传失败：" + response.msg);
  }
}

/** 上传失败回调 */
function handleUploadError() {
  proxy.$modal.msgError("上传失败，请重试");
}

/** 查看文件列表 */
function handleFiles(row) {
  router.push({ 
    path: "/knowledge/files/" + row.knowledgeId, 
    query: { 
      knowledgeName: row.knowledgeName
    } 
  });
}

/** RAG 问答 */
function handleChat(row) {
  router.push({ 
    path: "/knowledge/chat/" + row.knowledgeId, 
    query: { 
      knowledgeName: row.knowledgeName
    } 
  });
}

onMounted(() => {
  getList();
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
</style>

