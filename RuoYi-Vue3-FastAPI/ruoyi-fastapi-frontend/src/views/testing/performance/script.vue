<template>
  <div class="app-container">
    <!-- 头部标题 -->
    <el-card class="box-card header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><Document /></el-icon> 性能测试脚本管理</h2>
          <p class="subtitle">K6 Performance Test Scripts</p>
        </div>
        <div class="header-actions">
          <el-button type="success" @click="handleGenerate" v-hasPermi="['performance:script:add']">
            <el-icon><MagicStick /></el-icon> AI生成脚本
          </el-button>
          <el-button type="primary" @click="handleAdd" v-hasPermi="['performance:script:add']">
            <el-icon><Plus /></el-icon> 新增脚本
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 查询区域 -->
    <el-card class="box-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="脚本名称" prop="scriptName">
          <el-input v-model="queryParams.scriptName" placeholder="请输入脚本名称" clearable style="width: 200px" @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="项目" prop="projectId">
          <el-select v-model="queryParams.projectId" placeholder="请选择项目" clearable style="width: 200px">
            <el-option v-for="project in projectList" :key="project.projectId" :label="project.projectName" :value="project.projectId" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="正常" value="0" />
            <el-option label="停用" value="1" />
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
      <el-table v-loading="loading" :data="scriptList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="ID" prop="scriptId" width="80" align="center" />
        <el-table-column label="脚本名称" prop="scriptName" min-width="200" show-overflow-tooltip />
        <el-table-column label="项目" prop="projectName" width="150" show-overflow-tooltip />
        <el-table-column label="版本" prop="version" width="80" align="center" />
        <el-table-column label="AI生成" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.aiGenerated === '1'" type="success" size="small">AI生成</el-tag>
            <el-tag v-else type="info" size="small">手动</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">{{ scope.row.status === '0' ? '正常' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="createTime" width="160" align="center">
          <template #default="scope">
            <span>{{ parseTime(scope.row.createTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="280" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看</el-button>
            <el-button link type="success" icon="VideoPlay" @click="handleExecute(scope.row)" v-hasPermi="['performance:script:execute']">执行</el-button>
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['performance:script:edit']">编辑</el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['performance:script:remove']">删除</el-button>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="900px" append-to-body destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="脚本名称" prop="scriptName">
              <el-input v-model="form.scriptName" placeholder="请输入脚本名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属项目" prop="projectId">
              <el-select v-model="form.projectId" placeholder="请选择项目" style="width: 100%">
                <el-option v-for="project in projectList" :key="project.projectId" :label="project.projectName" :value="project.projectId" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="版本号" prop="version">
              <el-input v-model="form.version" placeholder="如：1.0.0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio value="0">正常</el-radio>
                <el-radio value="1">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="脚本内容" prop="scriptContent">
              <el-input 
                v-model="form.scriptContent" 
                type="textarea" 
                :rows="18" 
                placeholder="请输入K6脚本内容" 
                style="font-family: 'Consolas', 'Monaco', monospace;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 脚本详情对话框 -->
    <el-dialog title="脚本详情" v-model="viewVisible" width="900px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="脚本名称">{{ viewData.scriptName }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ viewData.projectName }}</el-descriptions-item>
        <el-descriptions-item label="版本号">{{ viewData.version }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewData.status === '0' ? 'success' : 'danger'">{{ viewData.status === '0' ? '正常' : '停用' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建者">{{ viewData.createBy }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(viewData.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="Agent ID" v-if="viewData.agentId">{{ viewData.agentId }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider content-position="left">脚本内容</el-divider>
      <el-input :model-value="viewData.scriptContent" type="textarea" :rows="15" readonly style="font-family: 'Consolas', 'Monaco', monospace;" />
    </el-dialog>

    <!-- AI生成脚本对话框 -->
    <el-dialog title="AI生成K6性能测试脚本" v-model="generateVisible" width="800px" append-to-body destroy-on-close>
      <el-form ref="generateFormRef" :model="generateForm" :rules="generateRules" label-width="100px">
        <el-form-item label="脚本名称" prop="scriptName">
          <el-input v-model="generateForm.scriptName" placeholder="请输入脚本名称" />
        </el-form-item>
        <el-form-item label="所属项目" prop="projectId">
          <el-select v-model="generateForm.projectId" placeholder="请选择项目" style="width: 100%">
            <el-option v-for="project in projectList" :key="project.projectId" :label="project.projectName" :value="project.projectId" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试需求" prop="prompt">
          <el-input 
            v-model="generateForm.prompt" 
            type="textarea" 
            :rows="6" 
            placeholder="请详细描述您要测试的场景，例如：
生成一个登录接口的性能测试脚本，接口地址为https://api.example.com/login，
请求方法为POST，请求体为JSON格式{username, password}，
测试50个虚拟用户并发，持续30秒，
性能要求：P95响应时间<500ms，错误率<1%"
          />
        </el-form-item>
        <el-divider content-position="left">K6配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="虚拟用户数">
              <el-input-number v-model="generateForm.vus" :min="1" :max="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="测试时长">
              <el-input v-model="generateForm.duration" placeholder="如：30s, 1m" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="使用RAG">
              <el-switch v-model="generateForm.useRag" />
              <span class="ml-2 text-gray">使用知识库增强生成</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="generateVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmGenerate" :loading="generating">
            <el-icon v-if="!generating"><MagicStick /></el-icon>
            {{ generating ? '生成中...' : 'AI 生成' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 执行配置对话框 -->
    <el-dialog title="执行K6性能测试" v-model="executeVisible" width="600px" append-to-body destroy-on-close>
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="脚本名称">
          <el-input :model-value="executeForm.scriptName" disabled />
        </el-form-item>
        <el-divider content-position="left">执行配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="虚拟用户数">
              <el-input-number v-model="executeForm.vus" :min="1" :max="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="测试时长">
              <el-input v-model="executeForm.duration" placeholder="如：30s" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="环境变量">
          <el-input v-model="executeForm.envVarsText" type="textarea" :rows="3" placeholder='{"BASE_URL": "https://api.example.com"}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="executeVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmExecute" :loading="executing">
            <el-icon v-if="!executing"><VideoPlay /></el-icon>
            {{ executing ? '执行中...' : '开始执行' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="PerformanceScript">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listScript, getScript, addScript, updateScript, delScript, generateScript, executeScript } from '@/api/testing/script'
import { listProject } from '@/api/testing/project'

const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

// 数据定义
const loading = ref(false)
const total = ref(0)
const scriptList = ref([])
const projectList = ref([])
const dialogVisible = ref(false)
const viewVisible = ref(false)
const generateVisible = ref(false)
const executeVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const generating = ref(false)
const executing = ref(false)
const selectedIds = ref([])
const viewData = ref({})

// 查询参数
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  scriptName: undefined,
  scriptType: 'k6',
  projectId: undefined,
  status: undefined
})

// 表单数据
const form = ref({
  scriptId: undefined,
  scriptName: '',
  scriptType: 'k6',
  projectId: undefined,
  scriptContent: '',
  version: '1.0.0',
  status: '0',
  remark: ''
})

// 表单验证规则
const rules = {
  scriptName: [{ required: true, message: '脚本名称不能为空', trigger: 'blur' }],
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  scriptContent: [{ required: true, message: '脚本内容不能为空', trigger: 'blur' }]
}

// AI生成表单
const generateForm = reactive({
  scriptName: '',
  projectId: undefined,
  prompt: '',
  vus: 10,
  duration: '30s',
  useRag: true
})

const generateRules = {
  scriptName: [{ required: true, message: '脚本名称不能为空', trigger: 'blur' }],
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  prompt: [
    { required: true, message: '测试需求不能为空', trigger: 'blur' },
    { min: 20, message: '请详细描述测试需求（至少20个字符）', trigger: 'blur' }
  ]
}

// 执行表单
const executeForm = reactive({
  scriptId: undefined,
  scriptName: '',
  vus: 10,
  duration: '30s',
  envVarsText: ''
})

/** 查询脚本列表 */
function getList() {
  loading.value = true
  listScript({
    script_name: queryParams.scriptName,
    script_type: queryParams.scriptType,
    project_id: queryParams.projectId,
    status: queryParams.status,
    page_num: queryParams.pageNum,
    page_size: queryParams.pageSize
  }).then(response => {
    scriptList.value = response.data?.rows || response.rows || []
    total.value = response.data?.total || response.total || 0
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

/** 查询项目列表 */
function getProjectList() {
  listProject({ projectType: 'performance', status: '0', pageNum: 1, pageSize: 100 }).then(response => {
    projectList.value = response.data?.rows || []
  })
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryParams.scriptName = undefined
  queryParams.projectId = undefined
  queryParams.status = undefined
  handleQuery()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.scriptId)
}

function handleAdd() {
  resetForm()
  dialogTitle.value = '新增K6脚本'
  dialogVisible.value = true
}

function handleView(row) {
  getScript(row.scriptId || row.script_id).then(response => {
    viewData.value = response.data || row
    viewVisible.value = true
  })
}

function handleUpdate(row) {
  resetForm()
  getScript(row.scriptId || row.script_id).then(response => {
    const data = response.data
    form.value = {
      scriptId: data.script_id || data.scriptId,
      scriptName: data.script_name || data.scriptName,
      scriptType: 'k6',
      projectId: data.project_id || data.projectId,
      scriptContent: data.script_content || data.scriptContent,
      version: data.version,
      status: data.status,
      remark: data.remark
    }
    dialogTitle.value = '编辑K6脚本'
    dialogVisible.value = true
  })
}

function handleGenerate() {
  generateForm.scriptName = ''
  generateForm.projectId = undefined
  generateForm.prompt = ''
  generateForm.vus = 10
  generateForm.duration = '30s'
  generateForm.useRag = true
  generateVisible.value = true
}

function confirmGenerate() {
  proxy.$refs.generateFormRef.validate(valid => {
    if (valid) {
      generating.value = true
      generateScript({
        script_name: generateForm.scriptName,
        project_id: generateForm.projectId,
        script_type: 'k6',
        prompt: generateForm.prompt,
        config: {
          vus: generateForm.vus,
          duration: generateForm.duration
        },
        use_rag: generateForm.useRag
      }).then(response => {
        ElMessage.success('K6脚本生成成功')
        generateVisible.value = false
        getList()
      }).finally(() => {
        generating.value = false
      })
    }
  })
}

function handleExecute(row) {
  executeForm.scriptId = row.scriptId || row.script_id
  executeForm.scriptName = row.scriptName || row.script_name
  executeForm.vus = 10
  executeForm.duration = '30s'
  executeForm.envVarsText = ''
  executeVisible.value = true
}

function confirmExecute() {
  let envVars = {}
  if (executeForm.envVarsText) {
    try {
      envVars = JSON.parse(executeForm.envVarsText)
    } catch (e) {
      ElMessage.error('环境变量格式错误，请输入有效的JSON')
      return
    }
  }

  executing.value = true
  executeScript({
    script_id: executeForm.scriptId,
    config: {
      vus: executeForm.vus,
      duration: executeForm.duration,
      env_vars: envVars
    }
  }).then(response => {
    ElMessage.success('执行已启动')
    executeVisible.value = false
    router.push({ path: '/performance/execution', query: { executionId: response.data?.execution_id } })
  }).finally(() => {
    executing.value = false
  })
}

function handleDelete(row) {
  const ids = row.scriptId || row.script_id || selectedIds.value.join(',')
  ElMessageBox.confirm('是否确认删除选中的脚本?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return delScript(ids)
  }).then(() => {
    getList()
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function submitForm() {
  proxy.$refs.formRef.validate(valid => {
    if (valid) {
      submitLoading.value = true
      const submitData = {
        script_id: form.value.scriptId,
        script_name: form.value.scriptName,
        script_type: 'k6',
        project_id: form.value.projectId,
        script_content: form.value.scriptContent,
        version: form.value.version,
        status: form.value.status,
        remark: form.value.remark
      }

      const api = form.value.scriptId ? updateScript : addScript
      api(submitData).then(() => {
        ElMessage.success(form.value.scriptId ? '修改成功' : '新增成功')
        dialogVisible.value = false
        getList()
      }).finally(() => {
        submitLoading.value = false
      })
    }
  })
}

function resetForm() {
  form.value = {
    scriptId: undefined,
    scriptName: '',
    scriptType: 'k6',
    projectId: undefined,
    scriptContent: '',
    version: '1.0.0',
    status: '0',
    remark: ''
  }
}

onMounted(() => {
  getList()
  getProjectList()
  // 检查URL参数
  if (route.query.scriptId) {
    getScript(route.query.scriptId).then(response => {
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
    .header-actions {
      display: flex;
      gap: 10px;
    }
  }
}

.box-card {
  margin-bottom: 20px;
}

.ml-2 {
  margin-left: 8px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}
</style>
