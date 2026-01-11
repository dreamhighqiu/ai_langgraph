<template>
  <div class="app-container">
    <!-- 搜索栏 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true" label-width="68px">
      <el-form-item label="项目" prop="projectId">
        <el-select
          v-model="queryParams.projectId"
          placeholder="请选择项目"
          clearable
          style="width: 200px"
          @change="handleQuery"
        >
          <el-option
            v-for="project in projectList"
            :key="project.project_id"
            :label="project.project_name"
            :value="project.project_id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="知识库名称" prop="knowledgeName">
        <el-input
          v-model="queryParams.knowledgeName"
          placeholder="请输入知识库名称"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      
      <el-form-item label="状态" prop="status">
        <el-select
          v-model="queryParams.status"
          placeholder="请选择状态"
          clearable
          style="width: 120px"
        >
          <el-option label="启用" value="0" />
          <el-option label="停用" value="1" />
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['testing:knowledge:add']"
        >新建知识库</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="Upload"
          @click="handleBatchUpload"
          v-hasPermi="['testing:knowledge:upload']"
        >批量上传文档</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Refresh"
          @click="checkProcessorStatus"
        >处理器状态</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-dropdown trigger="click" @command="handleRagCommand">
          <el-button type="info" plain icon="Link">
            RAG工具<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="webui" icon="Monitor">
                <span>RAG Web UI</span>
              </el-dropdown-item>
              <el-dropdown-item command="docs" icon="Document">
                <span>API文档</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="knowledgeList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="知识库ID" align="center" prop="knowledge_id" width="80" />
      <el-table-column label="知识库名称" align="center" prop="knowledge_name" :show-overflow-tooltip="true" />
      <el-table-column label="项目名称" align="center" prop="project_name" :show-overflow-tooltip="true" />
      <el-table-column label="Workspace" align="center" prop="collection_name" width="150" />
      <el-table-column label="查询模式" align="center" prop="query_mode" width="110">
        <template #default="scope">
          <el-tag :type="getQueryModeType(scope.row.query_mode)" size="small">
            {{ getQueryModeLabel(scope.row.query_mode) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="文件数" align="center" prop="file_count" width="80" />
      <el-table-column label="向量数" align="center" prop="vector_count" width="100" />
      <el-table-column label="状态" align="center" prop="status" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
            {{ scope.row.status === '0' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="create_time" width="160">
        <template #default="scope">
          <span>{{ parseTime(scope.row.create_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="280">
        <template #default="scope">
          <el-button
            link
            type="primary"
            icon="Upload"
            @click="handleUpload(scope.row)"
            v-hasPermi="['testing:knowledge:upload']"
          >上传文档</el-button>
          <el-button
            link
            type="primary"
            icon="Document"
            @click="handleViewFiles(scope.row)"
            v-hasPermi="['testing:knowledge:list']"
          >查看文档</el-button>
          <el-button
            link
            type="primary"
            icon="Search"
            @click="handleKnowledgeQuery(scope.row)"
            v-hasPermi="['testing:knowledge:query']"
          >知识查询</el-button>
          <el-button
            link
            type="danger"
            icon="Delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['testing:knowledge:remove']"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
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
        <el-form-item label="项目" prop="projectId">
          <el-select
            v-model="form.projectId"
            placeholder="请选择项目"
            style="width: 100%"
            :disabled="form.knowledge_id !== undefined"
            filterable
            clearable
          >
            <el-option
              v-for="(project, index) in projectList"
              :key="`project-${project.project_id}-${index}`"
              :label="project.project_name"
              :value="project.project_id"
            />
          </el-select>
          <div style="margin-top: 5px; font-size: 12px; color: #909399;">
            当前项目列表: {{ projectList.length }} 个项目
            <span v-if="projectList.length > 0" style="color: #67c23a;">✓ 已加载</span>
          </div>
          <div class="el-form-item-msg" v-if="form.knowledge_id">
            <el-alert
              title="提示：项目与知识库一对一，创建后不可修改"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </el-form-item>
        <el-form-item label="知识库名称" prop="knowledgeName">
          <el-input v-model="form.knowledgeName" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="查询模式" prop="queryMode">
          <el-select v-model="form.queryMode" placeholder="请选择查询模式" style="width: 100%">
            <el-option label="Mix - 混合模式（推荐）" value="mix">
              <div style="display: flex; align-items: center;">
                <el-icon style="margin-right: 5px;"><Connection /></el-icon>
                <span>Mix - 混合模式</span>
                <el-tag size="small" type="success" style="margin-left: 10px;">推荐</el-tag>
              </div>
            </el-option>
            <el-option label="Hybrid - 综合模式" value="hybrid">
              <div style="display: flex; align-items: center;">
                <el-icon style="margin-right: 5px;"><Grid /></el-icon>
                <span>Hybrid - 综合模式</span>
              </div>
            </el-option>
            <el-option label="Local - 实体关系模式" value="local">
              <div style="display: flex; align-items: center;">
                <el-icon style="margin-right: 5px;"><Location /></el-icon>
                <span>Local - 实体关系模式</span>
              </div>
            </el-option>
            <el-option label="Global - 全局模式" value="global">
              <div style="display: flex; align-items: center;">
                <el-icon style="margin-right: 5px;"><Promotion /></el-icon>
                <span>Global - 全局模式</span>
              </div>
            </el-option>
            <el-option label="Naive - 向量搜索" value="naive">
              <div style="display: flex; align-items: center;">
                <el-icon style="margin-right: 5px;"><Search /></el-icon>
                <span>Naive - 向量搜索</span>
              </div>
            </el-option>
          </el-select>
          <div style="margin-top: 5px; font-size: 12px; color: #909399;">
            <div>• Mix: 知识图谱+向量检索，适合大多数场景</div>
            <div>• Hybrid: 结合Local和Global策略</div>
            <div>• Local: 关注特定实体及其关系</div>
            <div>• Global: 分析知识图谱中的广泛模式</div>
            <div>• Naive: 仅使用向量相似度搜索</div>
          </div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="0">启用</el-radio>
            <el-radio label="1">停用</el-radio>
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

    <!-- 文档上传对话框 -->
    <el-dialog title="上传文档" v-model="uploadDialogVisible" width="600px" append-to-body>
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :data="uploadData"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :on-change="handleFileListChange"
        :before-upload="beforeUpload"
        v-model:file-list="fileList"
        :auto-upload="false"
        multiple
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、Word、Excel、PPT、图片、Markdown 等格式，单个文件不超过10MB
          </div>
        </template>
      </el-upload>
      <div style="margin-top: 10px; font-size: 12px; color: #909399;">
        已选择文件: {{ fileList.length }} 个
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取 消</el-button>
          <el-button 
            type="primary" 
            @click="submitUpload" 
            :disabled="!fileList || fileList.length === 0"
            :loading="uploadLoading"
          >
            {{ uploadLoading ? '上传中...' : '确认上传' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 文档列表对话框 -->
    <el-dialog title="知识库文档" v-model="filesDialogVisible" width="80%" append-to-body>
      <el-table v-loading="filesLoading" :data="filesList">
        <el-table-column label="文件名" align="center" prop="file_name" :show-overflow-tooltip="true" />
        <el-table-column label="文件类型" align="center" prop="file_type" width="100" />
        <el-table-column label="文件大小" align="center" prop="file_size" width="100">
          <template #default="scope">
            {{ formatFileSize(scope.row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column label="处理状态" align="center" prop="process_status" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.process_status)">
              {{ getStatusLabel(scope.row.process_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="向量数" align="center" prop="vector_count" width="80" />
        <el-table-column label="上传时间" align="center" prop="create_time" width="160">
          <template #default="scope">
            <span>{{ parseTime(scope.row.create_time) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="180">
          <template #default="scope">
            <el-button
              link
              type="primary"
              icon="View"
              @click="handlePreview(scope.row)"
            >预览</el-button>
            <el-button
              link
              type="primary"
              icon="Download"
              @click="handleDownload(scope.row)"
            >下载</el-button>
            <el-button
              link
              type="danger"
              icon="Delete"
              @click="handleDeleteFile(scope.row)"
              v-hasPermi="['testing:knowledge:remove']"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <pagination
        v-show="filesTotal > 0"
        :total="filesTotal"
        v-model:page="filesQueryParams.pageNum"
        v-model:limit="filesQueryParams.pageSize"
        @pagination="getFilesList"
      />
    </el-dialog>

    <!-- 知识查询对话框 -->
    <el-dialog title="知识库查询" v-model="queryDialogVisible" width="70%" append-to-body>
      <el-form :model="queryForm" label-width="80px">
        <el-form-item label="查询内容">
          <el-input
            v-model="queryForm.query"
            type="textarea"
            :rows="3"
            placeholder="请输入要查询的内容"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="查询模式" label-width="80px">
              <el-select v-model="queryForm.mode" style="width: 100%">
                <el-option label="Mix - 混合模式（推荐）" value="mix">
                  <span>Mix - 混合模式</span>
                  <el-tag size="small" type="success" style="margin-left: 10px;">推荐</el-tag>
                </el-option>
                <el-option label="Hybrid - 综合模式" value="hybrid">Hybrid - 综合模式</el-option>
                <el-option label="Local - 实体关系" value="local">Local - 实体关系</el-option>
                <el-option label="Global - 全局模式" value="global">Global - 全局模式</el-option>
                <el-option label="Naive - 向量搜索" value="naive">Naive - 向量搜索</el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="返回数量" label-width="80px">
              <el-input-number v-model="queryForm.topK" :min="1" :max="20" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="executeQuery" :loading="queryLoading">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-divider content-position="left">查询结果</el-divider>
      
      <div v-if="queryResult" class="query-result">
        <el-alert
          :title="`查询模式: ${queryForm.mode} | 知识库: ${currentKnowledge?.knowledge_name} | 项目: ${queryResult.project_id ? 'project_' + queryResult.project_id : 'N/A'}`"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <div style="margin-top: 8px; font-size: 12px; color: #606266;">
              <el-icon><InfoFilled /></el-icon>
              <span style="margin-left: 4px;">查询范围：仅在当前项目（{{ queryResult.project_id ? 'project_' + queryResult.project_id : 'N/A' }}）的知识库中检索</span>
            </div>
          </template>
        </el-alert>
        <div class="result-content" v-html="renderMarkdown(queryResult.answer || queryResult.response || '暂无答案')"></div>
        
        <el-divider content-position="left">参考文档</el-divider>
        <el-table :data="queryResult.references || []" v-if="queryResult.references && queryResult.references.length > 0">
          <el-table-column label="文档" width="300">
            <template #default="scope">
              {{ scope.row.file_name || scope.row.filename || scope.row.document || '未知文档' }}
            </template>
          </el-table-column>
          <el-table-column label="相关度" width="100">
            <template #default="scope">
              <span v-if="scope.row.relevance !== undefined && scope.row.relevance !== null">
                {{ (parseFloat(scope.row.relevance) * 100).toFixed(1) }}%
              </span>
              <span v-else-if="scope.row.score !== undefined && scope.row.score !== null">
                {{ (parseFloat(scope.row.score) * 100).toFixed(1) }}%
              </span>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column label="内容片段" show-overflow-tooltip>
            <template #default="scope">
              {{ scope.row.content || scope.row.text || scope.row.chunk || '无内容预览' }}
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="无参考文档" :image-size="80" />
      </div>
      <el-empty v-else description="暂无查询结果" />
    </el-dialog>

    <!-- 批量上传项目选择对话框 -->
    <el-dialog title="选择项目" v-model="batchUploadProjectDialogVisible" width="500px" append-to-body>
      <el-form label-width="80px">
        <el-form-item label="选择项目">
          <el-select
            v-model="batchUploadProjectId"
            placeholder="请选择要上传文档的项目"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="project in projectList"
              :key="project.project_id"
              :label="project.project_name"
              :value="project.project_id"
            >
              <span>{{ project.project_name }}</span>
            </el-option>
          </el-select>
          <div style="margin-top: 5px; font-size: 12px; color: #909399;">
            可选项目: {{ projectList.length }} 个
          </div>
        </el-form-item>
        <el-alert
          title="系统会自动为该项目创建或使用已有的知识库"
          type="info"
          :closable="false"
          show-icon
          style="margin-top: 10px;"
        />
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="confirmBatchUploadProject" :disabled="!batchUploadProjectId">
            确定并上传
          </el-button>
          <el-button @click="batchUploadProjectDialogVisible = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Knowledge">
import { ref, reactive, onMounted, getCurrentInstance, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, InfoFilled, Search } from '@element-plus/icons-vue'
import { marked } from 'marked'
import {
  listKnowledge,
  getKnowledge,
  addKnowledge,
  updateKnowledge,
  delKnowledge,
  getFileList,
  deleteFile,
  queryKnowledge,
  getProcessorStatus
} from '@/api/testing/knowledge'
import { listAllProject } from '@/api/testing/project'
import { getToken } from '@/utils/auth'
import { parseTime } from '@/utils/ruoyi'

const { proxy } = getCurrentInstance()

// 数据
const knowledgeList = ref([])
const projectList = ref([])
const filesList = ref([])
const loading = ref(true)
const filesLoading = ref(false)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const filesTotal = ref(0)
const title = ref('')
const open = ref(false)
const uploadDialogVisible = ref(false)
const filesDialogVisible = ref(false)
const queryDialogVisible = ref(false)
const queryLoading = ref(false)
const queryResult = ref(null)
const currentKnowledge = ref(null)
const fileList = ref([])
const uploadLoading = ref(false)
const uploadRef = ref(null)  // 上传组件引用
const batchUploadProjectDialogVisible = ref(false)
const batchUploadProjectId = ref(null)

// 查询参数
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  projectId: null,
  knowledgeName: null,
  status: null
})

// 文件查询参数
const filesQueryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  knowledgeId: null
})

// 表单参数
const form = ref({})

// 知识查询表单
const queryForm = reactive({
  query: '',
  mode: 'hybrid',
  topK: 5
})

// 表单校验
const rules = {
  projectId: [
    { required: true, message: '项目不能为空', trigger: 'change' }
  ],
  knowledgeName: [
    { required: true, message: '知识库名称不能为空', trigger: 'blur' }
  ]
}

// 上传配置
const uploadUrl = ref(import.meta.env.VITE_APP_BASE_API + '/api/testing/knowledge/1/files/upload')
const uploadHeaders = ref({ Authorization: 'Bearer ' + getToken() })
const uploadData = ref({})

/** 查询知识库列表 */
async function getList() {
  loading.value = true
  try {
    const response = await listKnowledge(queryParams)
    knowledgeList.value = response.rows || []
    total.value = response.total || 0
    console.log('知识库列表加载成功:', knowledgeList.value.length, '条记录')
  } catch (error) {
    console.error('查询知识库列表失败:', error)
    ElMessage.error('查询失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

/** 查询项目列表 */
async function getProjectList() {
  try {
    const response = await listAllProject('0')  // 只获取启用的项目
    // 打印完整响应
    console.log('API响应:', response)
    console.log('response.data:', response.data)
    console.log('response.rows:', response.rows)
    
    // 兼容两种返回格式
    projectList.value = response.data || response.rows || []
    console.log('项目列表加载成功:', projectList.value.length, '个项目', projectList.value)
  } catch (error) {
    console.error('查询项目列表失败:', error)
    ElMessage.error('查询项目列表失败: ' + error.message)
  }
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
}

/** 表单重置 */
function reset() {
  form.value = {
    projectId: null,
    knowledgeName: null,
    queryMode: 'mix',
    description: null,
    status: '0',
    remark: null
  }
  proxy.resetForm('knowledgeRef')
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm('queryRef')
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.knowledge_id)
  single.value = selection.length !== 1
  multiple.value = !selection.length
}

/** 新增按钮操作 */
async function handleAdd() {
  reset()
  // 每次都重新加载项目列表，确保数据最新
  console.log('开始加载项目列表...')
  await getProjectList()
  console.log('项目列表加载完成，打开对话框')
  console.log('当前projectList:', projectList.value)
  console.log('projectList长度:', projectList.value?.length)
  console.log('projectList第一项:', projectList.value?.[0])
  console.log('当前form:', form.value)
  console.log('form.knowledge_id:', form.value.knowledge_id)
  console.log('是否禁用:', form.value.knowledge_id !== undefined)
  
  open.value = true
  title.value = '添加知识库'
  
  // 强制刷新一次
  await nextTick()
  console.log('对话框已打开，再次检查projectList:', projectList.value?.length)
  console.log('对话框打开后，form.knowledge_id:', form.value.knowledge_id)
}

/** 修改按钮操作 */
async function handleUpdate(row) {
  reset()
  const knowledgeId = row.knowledge_id || ids.value[0]
  try {
    const response = await getKnowledge(knowledgeId)
    form.value = response.data
    open.value = true
    title.value = '修改知识库'
  } catch (error) {
    ElMessage.error('查询失败')
  }
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs['knowledgeRef'].validate(async valid => {
    if (valid) {
      try {
        if (form.value.knowledge_id) {
          await updateKnowledge(form.value)
          ElMessage.success('修改成功')
        } else {
          await addKnowledge(form.value)
          ElMessage.success('新增成功')
        }
        open.value = false
        getList()
      } catch (error) {
        ElMessage.error(error.message || '操作失败')
      }
    }
  })
}

/** 删除按钮操作 */
async function handleDelete(row) {
  const knowledgeIds = row.knowledge_id || ids.value.join(',')
  try {
    await ElMessageBox.confirm('是否确认删除知识库？删除后将清空所有文档和向量数据！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await delKnowledge(knowledgeIds)
    ElMessage.success('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

/** 处理RAG工具下拉菜单 */
function handleRagCommand(command) {
  const ragBaseUrl = 'http://localhost:9621'
  if (command === 'webui') {
    window.open(`${ragBaseUrl}/webui/`, '_blank')
  } else if (command === 'docs') {
    window.open(`${ragBaseUrl}/docs`, '_blank')
  }
}

/** 上传文档 */
function handleUpload(row) {
  currentKnowledge.value = row
  uploadUrl.value = import.meta.env.VITE_APP_BASE_API + `/api/testing/knowledge/${row.knowledge_id}/files/upload`
  uploadDialogVisible.value = true
  fileList.value = []
}

/** 批量上传 */
async function handleBatchUpload() {
  // 每次都重新加载项目列表
  console.log('批量上传：开始加载项目列表...')
  await getProjectList()
  console.log('批量上传：项目列表加载完成，数量:', projectList.value?.length)
  
  // 如果顶部已选择项目，直接使用
  if (queryParams.projectId) {
    console.log('使用顶部选择的项目:', queryParams.projectId)
    batchUploadProjectId.value = queryParams.projectId
    uploadUrl.value = import.meta.env.VITE_APP_BASE_API + `/api/testing/knowledge/project/${queryParams.projectId}/files/upload`
    uploadDialogVisible.value = true
    fileList.value = []
    return
  }
  
  // 否则弹出项目选择对话框
  console.log('打开项目选择对话框')
  batchUploadProjectId.value = null
  batchUploadProjectDialogVisible.value = true
  
  await nextTick()
  console.log('项目选择对话框已打开，projectList:', projectList.value?.length)
}

/** 确认批量上传项目选择 */
function confirmBatchUploadProject() {
  if (!batchUploadProjectId.value) {
    ElMessage.warning('请选择项目')
    return
  }
  
  // 设置上传URL
  uploadUrl.value = import.meta.env.VITE_APP_BASE_API + `/api/testing/knowledge/project/${batchUploadProjectId.value}/files/upload`
  
  // 关闭项目选择对话框，打开上传对话框
  batchUploadProjectDialogVisible.value = false
  uploadDialogVisible.value = true
  fileList.value = []
}

/** 上传前检查 */
function beforeUpload(file) {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

/** 文件列表变化 */
function handleFileListChange(file, fileListParam) {
  console.log('文件列表变化:', fileListParam.length, '个文件')
  // fileList会自动更新，这里只是打印日志
}

/** 提交上传 */
function submitUpload() {
  if (!uploadRef.value) {
    ElMessage.warning('上传组件未初始化')
    return
  }
  
  if (!fileList.value || fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  console.log('开始上传，文件数量:', fileList.value.length)
  uploadLoading.value = true
  uploadRef.value.submit()
}

/** 上传成功 */
function handleUploadSuccess(response, file) {
  uploadLoading.value = false
  if (response.code === 200) {
    ElMessage.success(`${file.name} 上传成功`)
    getList()
  } else {
    ElMessage.error(response.msg || '上传失败')
  }
}

/** 上传失败 */
function handleUploadError(error) {
  uploadLoading.value = false
  ElMessage.error('上传失败: ' + error.message)
}

/** 查看文档列表 */
async function handleViewFiles(row) {
  currentKnowledge.value = row
  filesQueryParams.knowledgeId = row.knowledge_id
  filesQueryParams.pageNum = 1
  filesDialogVisible.value = true
  await getFilesList()
}

/** 获取文件列表 */
async function getFilesList() {
  filesLoading.value = true
  try {
    const response = await getFileList(filesQueryParams.knowledgeId, filesQueryParams)
    // 后端返回格式: {code: 200, data: {rows: [...], total: ...}}
    filesList.value = response.data?.rows || []
    filesTotal.value = response.data?.total || 0
    console.log('文件列表加载成功:', filesList.value.length, '个文件')
  } catch (error) {
    console.error('查询文件列表失败:', error)
    ElMessage.error('查询文件列表失败')
  } finally {
    filesLoading.value = false
  }
}

/** 预览文件 */
function handlePreview(row) {
  if (row.file_url) {
    window.open(row.file_url, '_blank')
  } else {
    ElMessage.warning('文件URL不存在')
  }
}

/** 下载文件 */
function handleDownload(row) {
  const url = `${import.meta.env.VITE_APP_BASE_API}/api/testing/knowledge/files/${row.file_id}/download`
  window.open(url, '_blank')
}

/** 删除文件 */
async function handleDeleteFile(row) {
  try {
    await ElMessageBox.confirm('是否确认删除该文件？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteFile(row.file_id)
    ElMessage.success('删除成功')
    getFilesList()
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

/** 知识查询 */
function handleKnowledgeQuery(row) {
  currentKnowledge.value = row
  queryForm.query = ''
  queryForm.mode = row.query_mode || 'mix'  // 使用知识库设置的查询模式
  queryResult.value = null
  queryDialogVisible.value = true
}

/** 执行查询 */
async function executeQuery() {
  if (!queryForm.query.trim()) {
    ElMessage.warning('请输入查询内容')
    return
  }
  
  queryLoading.value = true
  try {
    console.log('开始查询知识库:', {
      knowledge_id: currentKnowledge.value.knowledge_id,
      knowledge_name: currentKnowledge.value.knowledge_name,
      collection_name: currentKnowledge.value.collection_name,
      project_id: currentKnowledge.value.project_id,
      query: queryForm.query,
      mode: queryForm.mode,
      top_k: queryForm.topK
    })
    
    const response = await queryKnowledge(currentKnowledge.value.knowledge_id, {
      query: queryForm.query,
      mode: queryForm.mode,
      top_k: queryForm.topK
    })
    
    console.log('查询响应:', response)
    queryResult.value = response.data
    console.log('查询结果:', queryResult.value)
    
    ElMessage.success('查询成功')
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败: ' + (error.message || '未知错误'))
  } finally {
    queryLoading.value = false
  }
}

/** 检查处理器状态 */
async function checkProcessorStatus() {
  try {
    const response = await getProcessorStatus()
    const status = response.data
    ElMessageBox.alert(
      `处理器状态: ${status.processor_running ? '运行中' : '已停止'}\n` +
      `待处理文件: ${status.pending_files_count}\n` +
      `处理中文件: ${status.processing_files_count}\n` +
      `失败文件: ${status.failed_files_count}`,
      '处理器状态',
      { confirmButtonText: '确定' }
    )
  } catch (error) {
    ElMessage.error('查询失败')
  }
}

/** 格式化文件大小 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/** 获取状态类型 */
function getStatusType(status) {
  const map = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

/** 获取状态标签 */
function getStatusLabel(status) {
  const map = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

/** 获取查询模式标签 */
function getQueryModeLabel(mode) {
  const map = {
    mix: 'Mix',
    hybrid: 'Hybrid',
    local: 'Local',
    global: 'Global',
    naive: 'Naive',
    bypass: 'Bypass'
  }
  return map[mode] || mode
}

/** 获取查询模式类型 */
function getQueryModeType(mode) {
  const map = {
    mix: 'success',
    hybrid: 'primary',
    local: 'warning',
    global: 'info',
    naive: '',
    bypass: 'danger'
  }
  return map[mode] || ''
}

/** 渲染Markdown */
function renderMarkdown(text) {
  if (!text) return ''
  try {
    return marked(text, { breaks: true, gfm: true })
  } catch (e) {
    return text.replace(/\n/g, '<br>')
  }
}

onMounted(() => {
  getList()
  getProjectList()
})
</script>

<style scoped lang="scss">
.query-result {
  margin-top: 20px;
  
  .result-content {
    margin-top: 16px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 4px;
    line-height: 1.8;
    
    :deep(p) {
      margin: 8px 0;
    }
    
    :deep(h1), :deep(h2), :deep(h3) {
      margin: 12px 0 8px;
    }
    
    :deep(ul), :deep(ol) {
      padding-left: 20px;
    }
    
    :deep(code) {
      background: #e6e6e6;
      padding: 2px 6px;
      border-radius: 3px;
    }
    
    :deep(pre) {
      background: #2d2d2d;
      color: #f8f8f2;
      padding: 12px;
      border-radius: 4px;
      overflow-x: auto;
    }
  }
}

.el-form-item-msg {
  margin-top: 8px;
}
</style>
