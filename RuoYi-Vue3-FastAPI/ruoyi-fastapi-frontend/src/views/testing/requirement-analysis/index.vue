<template>
  <div class="app-container">
    <!-- 页面标题 -->
    <el-card class="header-card mb-4">
      <div class="header-content">
        <div>
          <h2><el-icon><DocumentCopy /></el-icon> 需求分析管理</h2>
          <p class="subtitle">Requirement Analysis - AI智能分析需求文档，提取关键信息和测试点</p>
        </div>
      </div>
    </el-card>

    <!-- 搜索表单 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="项目" prop="projectId">
        <el-select v-model="queryParams.projectId" placeholder="选择项目" clearable style="width: 200px">
          <el-option
            v-for="item in projectList"
            :key="item.projectId"
            :label="item.projectName"
            :value="item.projectId"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="分析名称" prop="analysisName">
        <el-input
          v-model="queryParams.analysisName"
          placeholder="请输入分析名称"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="选择状态" clearable style="width: 120px">
          <el-option label="草稿" value="draft" />
          <el-option label="分析中" value="analyzing" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
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
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['testing:requirement:add']">AI 智能分析</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="primary" plain icon="MagicStick" @click="openAIChat" v-hasPermi="['testing:requirement:add']">AI 助手</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['testing:requirement:remove']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 表格 -->
    <el-table v-loading="loading" :data="analysisList" @selection-change="handleSelectionChange" border>
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="需求名称" align="left" min-width="200" :show-overflow-tooltip="true">
        <template #default="scope">
          <el-link type="primary" @click="handleDetail(scope.row)">{{ scope.row.requirement_name }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="项目" align="center" width="120">
        <template #default="scope">
          {{ getProjectName(scope.row.project_id) }}
        </template>
      </el-table-column>
      <el-table-column label="需求类型" align="center" prop="requirement_type" width="100" />
      <el-table-column label="优先级" align="center" width="90">
        <template #default="scope">
          <el-tag :type="getPriorityType(scope.row.priority)">{{ getPriorityLabel(scope.row.priority) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">{{ getStatusLabel(scope.row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建人" align="center" prop="createBy" width="100">
        <template #default="scope">{{ scope.row.create_by }}</template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" width="160">
        <template #default="scope">{{ scope.row.create_time }}</template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="250">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleDetail(scope.row)">详情</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['testing:requirement:edit']">编辑</el-button>
          <el-button 
            v-if="scope.row.report_url" 
            link 
            type="success" 
            icon="Download" 
            @click="handleDownload(scope.row)"
          >
            下载
          </el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['testing:requirement:remove']">删除</el-button>
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

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      title="需求分析详情"
      size="60%"
      :destroy-on-close="true"
    >
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="需求名称" :span="2">{{ currentDetail.requirement_name }}</el-descriptions-item>
          <el-descriptions-item label="需求标识">{{ currentDetail.requirement_identifier }}</el-descriptions-item>
          <el-descriptions-item label="需求类型">{{ currentDetail.requirement_type }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(currentDetail.priority)">{{ getPriorityLabel(currentDetail.priority) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentDetail.status)">{{ getStatusLabel(currentDetail.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="所属模块" :span="2">{{ currentDetail.module }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">需求描述</el-divider>
        <div class="section-content" v-html="formatMarkdown(currentDetail.description)"></div>

        <el-divider content-position="left">验收标准</el-divider>
        <div class="section-content" v-html="formatMarkdown(currentDetail.acceptance_criteria)"></div>

        <el-divider content-position="left">功能需求</el-divider>
        <div class="section-content" v-html="formatMarkdown(currentDetail.functional_requirements)"></div>

        <el-divider content-position="left">非功能需求</el-divider>
        <div class="section-content" v-html="formatMarkdown(currentDetail.non_functional_requirements)"></div>

        <el-divider content-position="left">业务规则</el-divider>
        <div class="section-content" v-html="formatMarkdown(currentDetail.business_rules)"></div>

        <el-divider content-position="left">依赖关系</el-divider>
        <div class="section-content" v-html="formatMarkdown(currentDetail.dependencies)"></div>
      </div>
    </el-drawer>

    <!-- 创建/编辑对话框 -->
    <RequirementCreateDialog
      ref="requirementDialogRef"
      v-model="dialogVisible"
      :edit-data="editData"
      :default-project-id="queryParams.projectId"
      @open-chat="handleOpenChat"
      @success="handleFormSuccess"
    />

    <!-- AI 对话抽屉 -->
    <AIChatDrawer
      v-model="aiChatVisible"
      assistant-id="requirement_analyzer_agent"
      assistant-name="AI 需求分析"
      :initial-prompt="aiInitialPrompt"
      :project-id="queryParams.projectId"
      @message-sent="handleAIMessageSent"
    />
  </div>
</template>

<script setup name="RequirementAnalysis">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy, MagicStick, ChatDotRound, Download } from '@element-plus/icons-vue'
import { listRequirementAnalysis, getRequirementAnalysis, addRequirementAnalysis, updateRequirementAnalysis, delRequirementAnalysis } from '@/api/testing/requirementAnalysis'
import { listAllProject } from '@/api/testing/project'
import AIChatDrawer from '@/views/testing/components/AIChatDrawer.vue'
import RequirementCreateDialog from '@/views/testing/components/RequirementCreateDialog.vue'

const { proxy } = getCurrentInstance()

const loading = ref(false)
const showSearch = ref(true)
const analysisList = ref([])
const projectList = ref([])
const total = ref(0)
const ids = ref([])
const multiple = ref(true)

const detailVisible = ref(false)
const dialogVisible = ref(false)
const aiChatVisible = ref(false)
const currentDetail = ref(null)
const currentId = ref(null)
const editData = ref(null)
const submitting = ref(false)
const aiInitialPrompt = ref('')

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  projectId: undefined,
  analysisName: undefined,
  status: undefined
})

const form = reactive({
  projectId: undefined,
  requirementName: '',
  requirementType: 'functional',
  priority: 'medium',
  module: '',
  description: '',
  acceptanceCriteria: ''
})

const rules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  requirementName: [{ required: true, message: '请输入需求名称', trigger: 'blur' }],
  requirementType: [{ required: true, message: '请选择需求类型', trigger: 'change' }]
}

const loadProjects = async () => {
  try {
    console.log('[RequirementAnalysis] 开始加载项目列表...')
    const res = await listAllProject('0')
    console.log('[RequirementAnalysis] 项目列表响应:', res)
    
    projectList.value = (res.data || []).map(item => ({
      projectId: item.project_id,
      projectName: item.project_name
    }))
    
    console.log('[RequirementAnalysis] 处理后的项目列表:', projectList.value)
    console.log('[RequirementAnalysis] 当前 queryParams.projectId:', queryParams.projectId)
    
    // 如果当前没有选择项目且项目列表不为空，自动选择第一个项目
    if (!queryParams.projectId && projectList.value.length > 0) {
      const firstProjectId = projectList.value[0].projectId
      console.log('[RequirementAnalysis] 准备自动选择项目，firstProjectId:', firstProjectId, 'type:', typeof firstProjectId)
      
      if (firstProjectId && firstProjectId > 0) {
        queryParams.projectId = firstProjectId
        console.log('[RequirementAnalysis] ✅ 已自动选择第一个项目:', firstProjectId)
      } else {
        console.warn('[RequirementAnalysis] ⚠️ 第一个项目ID无效:', firstProjectId)
      }
    } else {
      console.log('[RequirementAnalysis] 跳过自动选择项目。原因：', !queryParams.projectId ? '项目列表为空' : '已有选中项目')
    }
  } catch (error) {
    console.error('[RequirementAnalysis] ❌ 加载项目失败:', error)
    ElMessage.error('加载项目列表失败，请刷新页面重试')
  }
}

const getList = async () => {
  loading.value = true
  try {
    const res = await listRequirementAnalysis(queryParams)
    analysisList.value = res.data?.records || res.data?.rows || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error('加载列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  // 保存当前选中的项目ID
  const currentProjectId = queryParams.projectId
  console.log('[RequirementAnalysis] resetQuery: 保存项目ID', currentProjectId)
  
  proxy.resetForm('queryRef')
  
  // 恢复项目ID
  queryParams.projectId = currentProjectId
  console.log('[RequirementAnalysis] resetQuery: 恢复项目ID', queryParams.projectId)
  
  handleQuery()
}

const handleSelectionChange = (selection) => {
  ids.value = selection.map(item => item.requirement_id)
  multiple.value = !selection.length
}

const handleAdd = () => {
  currentId.value = null
  editData.value = null
  dialogVisible.value = true
}

const handleUpdate = async (row) => {
  currentId.value = row.requirement_id
  try {
    const res = await getRequirementAnalysis(row.requirement_id)
    editData.value = res.data
    dialogVisible.value = true
  } catch (error) {
    console.error('加载详情失败:', error)
  }
}

const handleFormSuccess = () => {
  getList()
}

const requirementDialogRef = ref(null)

const handleOpenChat = (data) => {
  console.log('[RequirementAnalysis] handleOpenChat 被调用，参数:', data)
  console.log('[RequirementAnalysis] 当前 queryParams.projectId:', queryParams.projectId)
  
  // 支持传递对象（包含 prompt 和 projectId）或字符串（仅 prompt）
  if (typeof data === 'object' && data.prompt) {
    aiInitialPrompt.value = data.prompt
    // 不再修改 queryParams.projectId，直接使用页面已选择的项目
    console.log('[RequirementAnalysis] 从对话框接收到 projectId:', data.projectId, '但使用页面的:', queryParams.projectId)
  } else {
    aiInitialPrompt.value = data
  }
  
  // 验证 projectId 是否有效
  if (!queryParams.projectId || queryParams.projectId === 0) {
    console.warn('[RequirementAnalysis] ⚠️ queryParams.projectId 无效，无法打开AI对话')
    ElMessage.warning('请先在搜索栏中选择项目！需求分析功能需要指定项目ID。')
    return
  }
  
  console.log('[RequirementAnalysis] ✅ 验证通过，打开AI对话，projectId:', queryParams.projectId)
  aiChatVisible.value = true
}

const handleUpdateOld = async (row) => {
  currentId.value = row.requirement_id
  try {
    const res = await getRequirementAnalysis(row.requirement_id)
    const data = res.data
    form.projectId = data.project_id
    form.requirementName = data.requirement_name
    form.requirementType = data.requirement_type || 'functional'
    form.priority = data.priority || 'medium'
    form.module = data.module || ''
    form.description = data.description || ''
    form.acceptanceCriteria = data.acceptance_criteria || ''
    dialogVisible.value = true
  } catch (error) {
    console.error('加载详情失败:', error)
  }
}

const handleDetail = async (row) => {
  try {
    const res = await getRequirementAnalysis(row.requirement_id)
    currentDetail.value = res.data
    detailVisible.value = true
  } catch (error) {
    console.error('加载详情失败:', error)
  }
}

const handleDelete = async (row) => {
  const requirementIds = row?.requirement_id ? [row.requirement_id] : ids.value
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${requirementIds.length} 条记录?`, '警告', { type: 'warning' })
    for (const id of requirementIds) {
      await delRequirementAnalysis(id)
    }
    proxy.$modal.msgSuccess('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const resetForm = () => {
  form.projectId = queryParams.projectId
  form.requirementName = ''
  form.requirementType = 'functional'
  form.priority = 'medium'
  form.module = ''
  form.description = ''
  form.acceptanceCriteria = ''
}

const submitForm = async () => {
  const valid = await proxy.$refs.formRef?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const submitData = {
      project_id: form.projectId,
      requirement_name: form.requirementName,
      requirement_type: form.requirementType,
      priority: form.priority,
      module: form.module,
      description: form.description,
      acceptance_criteria: form.acceptanceCriteria
    }
    
    if (currentId.value) {
      await updateRequirementAnalysis(currentId.value, submitData)
      proxy.$modal.msgSuccess('更新成功')
    } else {
      await addRequirementAnalysis(submitData)
      proxy.$modal.msgSuccess('创建成功')
    }
    dialogVisible.value = false
    getList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

const openAIAssistant = () => {
  console.log('[RequirementAnalysis] openAIAssistant 被调用')
  console.log('[RequirementAnalysis] 当前 queryParams.projectId:', queryParams.projectId, 'type:', typeof queryParams.projectId)
  
  // 验证是否已选择项目
  if (!queryParams.projectId || queryParams.projectId === 0) {
    console.warn('[RequirementAnalysis] ⚠️ 项目ID无效，无法打开AI助手')
    ElMessage.warning('请先在搜索栏中选择项目！需求分析功能需要指定项目ID。')
    return
  }
  
  console.log('[RequirementAnalysis] ✅ 项目ID验证通过，打开AI助手')
  aiInitialPrompt.value = ''
  aiChatVisible.value = true
}

const openAIChat = () => {
  console.log('[RequirementAnalysis] openAIChat 被调用')
  console.log('[RequirementAnalysis] 当前 queryParams.projectId:', queryParams.projectId, 'type:', typeof queryParams.projectId)
  console.log('[RequirementAnalysis] 项目列表长度:', projectList.value.length)
  
  // 验证是否已选择项目
  if (!queryParams.projectId || queryParams.projectId === 0) {
    console.warn('[RequirementAnalysis] ⚠️ 项目ID无效，无法打开AI对话')
    ElMessage.warning('请先在搜索栏中选择项目！需求分析功能需要指定项目ID。')
    return
  }
  
  console.log('[RequirementAnalysis] ✅ 项目ID验证通过，打开AI对话')
  aiInitialPrompt.value = ''
  aiChatVisible.value = true
}

const handleAIMessageSent = (data) => {
  if (data?.created) {
    getList()
  }
}

const getProjectName = (projectId) => {
  const project = projectList.value.find(p => p.projectId === projectId)
  return project?.projectName || '-'
}

const getStatusType = (status) => {
  const map = { draft: 'info', pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { draft: '草稿', pending: '待审核', approved: '已批准', rejected: '已拒绝' }
  return map[status] || status
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const map = { high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

const formatMarkdown = (text) => {
  if (!text) return '<span style="color: #999">暂无内容</span>'
  if (typeof text === 'object') return '<pre>' + JSON.stringify(text, null, 2) + '</pre>'
  return text.replace(/\n/g, '<br>')
}

// 下载报告
const handleDownload = async (row) => {
  // 使用analysis_id（数据库字段名）
  const analysisId = row.analysis_id || row.requirement_id
  if (!row.report_url && !analysisId) {
    ElMessage.warning('该需求分析还没有生成报告')
    return
  }
  
  try {
    // 使用后端代理下载接口，确保正确的编码
    const downloadUrl = `/testing/requirement/download/${analysisId}?format=markdown`
    // 创建隐藏的a标签下载
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `requirement_analysis_${analysisId}.md`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('开始下载报告')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 监听 queryParams.projectId 的变化，用于调试
watch(() => queryParams.projectId, (newVal, oldVal) => {
  console.log('[RequirementAnalysis] 🔄 queryParams.projectId 发生变化:', {
    旧值: oldVal,
    新值: newVal,
    调用栈: new Error().stack
  })
}, { immediate: true })

onMounted(async () => {
  console.log('[RequirementAnalysis] onMounted 开始执行')
  await loadProjects()
  console.log('[RequirementAnalysis] loadProjects 完成后，queryParams.projectId:', queryParams.projectId)
  await getList()
  console.log('[RequirementAnalysis] getList 完成后，queryParams.projectId:', queryParams.projectId)
})
</script>

<style scoped lang="scss">
.header-card {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  margin-bottom: 16px;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 24px;
    }

    .subtitle {
      margin: 8px 0 0 0;
      opacity: 0.9;
      font-size: 14px;
    }

    .header-actions .el-button {
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: white;
    }
  }
}

.detail-content {
  padding: 0 20px;

  .section-content {
    padding: 12px;
    background: #f9f9f9;
    border-radius: 4px;
    line-height: 1.8;
    min-height: 60px;
  }

  .score-item {
    text-align: center;
    padding: 16px;

    .score-label {
      margin-bottom: 12px;
      color: #606266;
      font-weight: 500;
    }
  }
}
</style>

