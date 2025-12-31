<template>
  <div class="app-container">
    <el-row :gutter="20">
      <!-- 头部标题 -->
      <el-col :span="24">
        <el-card class="box-card header-card">
          <div class="header-content">
            <div>
              <h2><el-icon><Odometer /></el-icon> 性能测试需求管理</h2>
              <p class="subtitle">K6 Performance Testing Requirements</p>
            </div>
            <el-button type="primary" @click="handleAdd" v-hasPermi="['performance:requirement:add']">
              <el-icon><Plus /></el-icon> 新建需求
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 查询区域 -->
      <el-col :span="24">
        <el-card class="box-card">
          <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
            <el-form-item label="需求名称" prop="requirementName">
              <el-input
                v-model="queryParams.requirementName"
                placeholder="请输入需求名称"
                clearable
                style="width: 200px"
                @keyup.enter="handleQuery"
              />
            </el-form-item>
            <el-form-item label="项目" prop="projectId">
              <el-select v-model="queryParams.projectId" placeholder="请选择项目" clearable style="width: 200px">
                <el-option
                  v-for="project in projectList"
                  :key="project.projectId"
                  :label="project.projectName"
                  :value="project.projectId"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="queryParams.priority" placeholder="请选择优先级" clearable style="width: 120px">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态" prop="status">
              <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 120px">
                <el-option label="待处理" value="0" />
                <el-option label="进行中" value="1" />
                <el-option label="已完成" value="2" />
                <el-option label="已关闭" value="3" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
              <el-button icon="Refresh" @click="resetQuery">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 列表区域 -->
      <el-col :span="24">
        <el-card class="box-card">
          <el-table v-loading="loading" :data="requirementList" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column label="ID" prop="requirementId" width="80" align="center" />
            <el-table-column label="需求名称" prop="requirementName" min-width="200" show-overflow-tooltip />
            <el-table-column label="项目" prop="projectName" width="150" show-overflow-tooltip />
            <el-table-column label="优先级" prop="priority" width="100" align="center">
              <template #default="scope">
                <el-tag v-if="scope.row.priority === 'high'" type="danger">高</el-tag>
                <el-tag v-else-if="scope.row.priority === 'medium'" type="warning">中</el-tag>
                <el-tag v-else type="info">低</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" prop="status" width="100" align="center">
              <template #default="scope">
                <el-tag v-if="scope.row.status === '0'" type="info">待处理</el-tag>
                <el-tag v-else-if="scope.row.status === '1'" type="primary">进行中</el-tag>
                <el-tag v-else-if="scope.row.status === '2'" type="success">已完成</el-tag>
                <el-tag v-else type="danger">已关闭</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" prop="createTime" width="160" align="center">
              <template #default="scope">
                <span>{{ parseTime(scope.row.createTime) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="320" fixed="right">
              <template #default="scope">
                <el-button link type="primary" icon="View" @click="handleView(scope.row)">详情</el-button>
                <el-button link type="success" icon="MagicStick" @click="handleGenerate(scope.row)" v-hasPermi="['performance:requirement:generate']">AI生成</el-button>
                <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['performance:requirement:edit']">修改</el-button>
                <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['performance:requirement:remove']">删除</el-button>
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
      </el-col>
    </el-row>

    <!-- 新增/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="800px" append-to-body destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="需求名称" prop="requirementName">
              <el-input v-model="form.requirementName" placeholder="请输入需求名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属项目" prop="projectId">
              <el-select v-model="form.projectId" placeholder="请选择项目" style="width: 100%">
                <el-option
                  v-for="project in projectList"
                  :key="project.projectId"
                  :label="project.projectName"
                  :value="project.projectId"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="请选择优先级" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="需求描述" prop="description">
              <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请详细描述性能测试需求，包括测试目标、接口信息、并发要求等" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="验收标准" prop="acceptanceCriteria">
              <el-input v-model="form.acceptanceCriteria" type="textarea" :rows="3" placeholder="请输入验收标准，例如：响应时间P95<500ms，错误率<1%，TPS>1000" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="标签">
              <el-tag
                v-for="(tag, index) in form.tags"
                :key="index"
                closable
                @close="handleTagClose(index)"
                class="mr-2"
              >{{ tag }}</el-tag>
              <el-input
                v-if="tagInputVisible"
                ref="tagInputRef"
                v-model="tagInputValue"
                size="small"
                style="width: 100px"
                @keyup.enter="handleTagConfirm"
                @blur="handleTagConfirm"
              />
              <el-button v-else size="small" @click="showTagInput">+ 添加标签</el-button>
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

    <!-- 详情对话框 -->
    <el-dialog title="需求详情" v-model="detailVisible" width="700px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="需求名称" :span="2">{{ currentRequirement.requirementName }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ currentRequirement.projectName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag v-if="currentRequirement.priority === 'high'" type="danger">高</el-tag>
          <el-tag v-else-if="currentRequirement.priority === 'medium'" type="warning">中</el-tag>
          <el-tag v-else type="info">低</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag v-if="currentRequirement.status === '0'" type="info">待处理</el-tag>
          <el-tag v-else-if="currentRequirement.status === '1'" type="primary">进行中</el-tag>
          <el-tag v-else-if="currentRequirement.status === '2'" type="success">已完成</el-tag>
          <el-tag v-else type="danger">已关闭</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(currentRequirement.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="需求描述" :span="2">{{ currentRequirement.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="验收标准" :span="2">{{ currentRequirement.acceptanceCriteria || '无' }}</el-descriptions-item>
        <el-descriptions-item label="标签" :span="2">
          <el-tag v-for="(tag, index) in currentRequirement.tags" :key="index" class="mr-2">{{ tag }}</el-tag>
          <span v-if="!currentRequirement.tags || currentRequirement.tags.length === 0">无</span>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentRequirement.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- AI生成脚本对话框 -->
    <el-dialog title="AI生成K6性能测试脚本" v-model="generateVisible" width="800px" append-to-body destroy-on-close>
      <el-card class="requirement-info mb-4">
        <template #header>
          <span>需求信息</span>
        </template>
        <el-descriptions :column="1" size="small">
          <el-descriptions-item label="需求名称">{{ currentRequirement.requirementName }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ currentRequirement.description || '无' }}</el-descriptions-item>
          <el-descriptions-item label="验收标准">{{ currentRequirement.acceptanceCriteria || '无' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-form :model="generateConfig" label-width="120px">
        <el-divider content-position="left">K6配置参数</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="虚拟用户数">
              <el-input-number v-model="generateConfig.vus" :min="1" :max="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="测试时长">
              <el-input v-model="generateConfig.duration" placeholder="如：30s, 1m, 5m" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="压力阶段">
              <div v-for="(stage, index) in generateConfig.stages" :key="index" class="stage-item">
                <el-input-number v-model="stage.target" :min="0" placeholder="目标用户数" style="width: 120px" />
                <span class="mx-2">用户，持续</span>
                <el-input v-model="stage.duration" placeholder="时长" style="width: 100px" />
                <el-button v-if="index > 0" type="danger" link @click="removeStage(index)">删除</el-button>
              </div>
              <el-button type="primary" link @click="addStage">+ 添加阶段</el-button>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="性能阈值">
              <el-input v-model="generateConfig.thresholdsText" type="textarea" :rows="3" placeholder='{"http_req_duration": ["p(95)<500"], "http_req_failed": ["rate<0.01"]}' />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="使用RAG增强">
              <el-switch v-model="generateConfig.useRag" />
              <span class="ml-2 text-gray">开启后将从知识库查询相似案例</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="generateVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmGenerate" :loading="generating">
            <el-icon v-if="!generating"><MagicStick /></el-icon>
            {{ generating ? '正在生成...' : '开始生成' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="PerformanceRequirement">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  listRequirement, 
  getRequirement, 
  addRequirement, 
  updateRequirement, 
  delRequirement,
  generateScriptFromRequirement 
} from '@/api/testing/requirement'
import { listProject } from '@/api/testing/project'

const { proxy } = getCurrentInstance()
const router = useRouter()

// 数据定义
const loading = ref(false)
const total = ref(0)
const requirementList = ref([])
const projectList = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const generateVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const generating = ref(false)
const selectedIds = ref([])
const currentRequirement = ref({})

// 标签输入
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const tagInputRef = ref(null)

// 查询参数
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  requirementName: undefined,
  requirementType: 'performance',
  projectId: undefined,
  priority: undefined,
  status: undefined
})

// 表单数据
const form = ref({
  requirementId: undefined,
  requirementName: '',
  requirementType: 'performance',
  projectId: undefined,
  description: '',
  acceptanceCriteria: '',
  priority: 'medium',
  status: '0',
  tags: [],
  remark: ''
})

// 表单验证规则
const rules = {
  requirementName: [{ required: true, message: '需求名称不能为空', trigger: 'blur' }],
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  description: [{ required: true, message: '需求描述不能为空', trigger: 'blur' }]
}

// AI生成配置
const generateConfig = reactive({
  vus: 10,
  duration: '30s',
  stages: [
    { duration: '10s', target: 10 },
    { duration: '30s', target: 50 },
    { duration: '10s', target: 0 }
  ],
  thresholdsText: '{"http_req_duration": ["p(95)<500"], "http_req_failed": ["rate<0.01"]}',
  useRag: true
})

/** 查询需求列表 */
function getList() {
  loading.value = true
  const query = {
    requirement_name: queryParams.requirementName,
    requirement_type: queryParams.requirementType,
    project_id: queryParams.projectId,
    priority: queryParams.priority,
    status: queryParams.status,
    page_num: queryParams.pageNum,
    page_size: queryParams.pageSize
  }
  const projectNameMap = Object.fromEntries(projectList.value.map(p => [p.projectId, p.projectName]))
  listRequirement(query).then(response => {
    const rows = response.rows || response.data?.rows || []
    const totalNum = response.total ?? response.data?.total ?? 0
    requirementList.value = rows.map(item => ({
      requirementId: item.requirement_id,
      projectId: item.project_id,
      projectName: projectNameMap[item.project_id] || '',
      requirementName: item.requirement_name,
      requirementType: item.requirement_type,
      description: item.description,
      acceptanceCriteria: item.acceptance_criteria,
      priority: item.priority,
      status: item.status,
      tags: item.tags || [],
      remark: item.remark,
      createTime: item.create_time,
      createBy: item.create_by,
      updateTime: item.update_time,
      updateBy: item.update_by
    }))
    total.value = totalNum
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

/** 查询项目列表 */
function getProjectList() {
  const query = {
    project_type: 'performance',
    // 允许正常/停用项目都可选择，避免选项为空
    status: undefined,
    page_num: 1,
    page_size: 100
  }
  listProject(query).then(response => {
    const rows = response.rows || response.data?.rows || []
    projectList.value = rows.map(item => ({
      projectId: item.project_id,
      projectName: item.project_name
    }))
  })
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  queryParams.requirementName = undefined
  queryParams.projectId = undefined
  queryParams.priority = undefined
  queryParams.status = undefined
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.requirementId)
}

/** 新增按钮操作 */
function handleAdd() {
  resetForm()
  dialogTitle.value = '新建性能测试需求'
  dialogVisible.value = true
}

/** 查看详情 */
function handleView(row) {
  getRequirement(row.requirementId).then(response => {
    const data = response.data || response
    currentRequirement.value = {
      requirementId: data.requirement_id || data.requirementId,
      projectId: data.project_id || data.projectId,
      projectName: row.projectName || '',
      requirementName: data.requirement_name || data.requirementName,
      requirementType: data.requirement_type || data.requirementType,
      description: data.description,
      acceptanceCriteria: data.acceptance_criteria || data.acceptanceCriteria,
      priority: data.priority,
      status: data.status,
      tags: data.tags || [],
      remark: data.remark,
      createTime: data.create_time || data.createTime,
      updateTime: data.update_time || data.updateTime
    }
    detailVisible.value = true
  })
}

/** 修改按钮操作 */
function handleUpdate(row) {
  resetForm()
  getRequirement(row.requirementId).then(response => {
    const data = response.data || response
    form.value = {
      requirementId: data.requirement_id || data.requirementId,
      requirementName: data.requirement_name || data.requirementName,
      requirementType: 'performance',
      projectId: data.project_id || data.projectId,
      description: data.description,
      acceptanceCriteria: data.acceptance_criteria || data.acceptanceCriteria,
      priority: data.priority,
      status: data.status,
      tags: data.tags || [],
      remark: data.remark
    }
    dialogTitle.value = '修改性能测试需求'
    dialogVisible.value = true
  })
}

/** AI生成脚本 */
function handleGenerate(row) {
  currentRequirement.value = row
  generateConfig.vus = 10
  generateConfig.duration = '30s'
  generateConfig.stages = [
    { duration: '10s', target: 10 },
    { duration: '30s', target: 50 },
    { duration: '10s', target: 0 }
  ]
  generateConfig.thresholdsText = '{"http_req_duration": ["p(95)<500"], "http_req_failed": ["rate<0.01"]}'
  generateConfig.useRag = true
  generateVisible.value = true
}

/** 确认生成脚本 */
function confirmGenerate() {
  // 解析阈值配置
  let thresholds = {}
  if (generateConfig.thresholdsText) {
    try {
      thresholds = JSON.parse(generateConfig.thresholdsText)
    } catch (e) {
      ElMessage.error('阈值配置格式错误，请输入有效的JSON')
      return
    }
  }

  generating.value = true
  generateScriptFromRequirement(currentRequirement.value.requirementId, {
    useRag: generateConfig.useRag,
    config: {
      vus: generateConfig.vus,
      duration: generateConfig.duration,
      stages: generateConfig.stages,
      thresholds: thresholds
    }
  }).then(response => {
    ElMessage.success('K6脚本生成成功！')
    generateVisible.value = false
    // 跳转到脚本管理页面
    router.push({ path: '/performance/script', query: { scriptId: response.data?.script_id } })
  }).catch(error => {
    console.error('生成失败:', error)
  }).finally(() => {
    generating.value = false
  })
}

/** 删除按钮操作 */
function handleDelete(row) {
  const ids = row.requirementId || selectedIds.value.join(',')
  ElMessageBox.confirm('是否确认删除选中的性能测试需求?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return delRequirement(ids)
  }).then(() => {
    getList()
    ElMessage.success('删除成功')
  }).catch(() => {})
}

/** 提交表单 */
function submitForm() {
  proxy.$refs.formRef.validate(valid => {
    if (valid) {
      submitLoading.value = true
      const submitData = { ...form.value }
      
      const api = submitData.requirementId ? updateRequirement : addRequirement
      api(submitData).then(() => {
        ElMessage.success(submitData.requirementId ? '修改成功' : '新增成功')
        dialogVisible.value = false
        getList()
      }).finally(() => {
        submitLoading.value = false
      })
    }
  })
}

/** 重置表单 */
function resetForm() {
  form.value = {
    requirementId: undefined,
    requirementName: '',
    requirementType: 'performance',
    projectId: undefined,
    description: '',
    acceptanceCriteria: '',
    priority: 'medium',
    status: '0',
    tags: [],
    remark: ''
  }
}

// 标签操作
function handleTagClose(index) {
  form.value.tags.splice(index, 1)
}

function showTagInput() {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

function handleTagConfirm() {
  if (tagInputValue.value) {
    if (!form.value.tags) {
      form.value.tags = []
    }
    form.value.tags.push(tagInputValue.value)
  }
  tagInputVisible.value = false
  tagInputValue.value = ''
}

// 压力阶段操作
function addStage() {
  generateConfig.stages.push({ duration: '10s', target: 0 })
}

function removeStage(index) {
  generateConfig.stages.splice(index, 1)
}

// 初始化
onMounted(() => {
  getList()
  getProjectList()
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
  }
}

.box-card {
  margin-bottom: 20px;
}

.requirement-info {
  margin-bottom: 20px;
}

.stage-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.mx-2 {
  margin: 0 8px;
}

.mr-2 {
  margin-right: 8px;
}

.ml-2 {
  margin-left: 8px;
}

.mb-4 {
  margin-bottom: 16px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}
</style>
