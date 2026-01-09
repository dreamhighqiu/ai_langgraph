<template>
  <div class="app-container">
    <!-- 页面标题 -->
    <el-card class="header-card mb-4">
      <div class="header-content">
        <div>
          <h2><el-icon><Warning /></el-icon> 缺陷分析管理</h2>
          <p class="subtitle">Defect Analysis - AI智能分析缺陷，提供根因分析和修复建议</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="openAIChat" v-hasPermi="['testing:defect:add']">
            <el-icon><MagicStick /></el-icon>
            AI 智能分析
          </el-button>
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
      <el-form-item label="严重程度" prop="severity">
        <el-select v-model="queryParams.severity" placeholder="选择严重程度" clearable style="width: 120px">
          <el-option label="致命" value="critical" />
          <el-option label="严重" value="high" />
          <el-option label="一般" value="medium" />
          <el-option label="轻微" value="low" />
        </el-select>
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
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['testing:defect:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['testing:defect:remove']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 表格 -->
    <el-table v-loading="loading" :data="analysisList" @selection-change="handleSelectionChange" border>
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="分析名称" align="left" min-width="200" :show-overflow-tooltip="true">
        <template #default="scope">
          <el-link type="primary" @click="handleDetail(scope.row)">{{ scope.row.analysis_name }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="缺陷标题" align="left" min-width="180" :show-overflow-tooltip="true">
        <template #default="scope">{{ scope.row.defect_title }}</template>
      </el-table-column>
      <el-table-column label="严重程度" align="center" width="100">
        <template #default="scope">
          <el-tag :type="getSeverityType(scope.row.severity)">{{ getSeverityLabel(scope.row.severity) }}</el-tag>
        </template>
      </el-table-column>
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
      <el-table-column label="缺陷类型" align="center" prop="defect_type" width="100" />
      <el-table-column label="创建人" align="center" width="100">
        <template #default="scope">{{ scope.row.create_by }}</template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" width="160">
        <template #default="scope">{{ scope.row.create_time }}</template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleDetail(scope.row)">详情</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['testing:defect:edit']">编辑</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['testing:defect:remove']">删除</el-button>
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
      title="缺陷分析详情"
      size="60%"
      :destroy-on-close="true"
    >
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="分析名称" :span="2">{{ currentDetail.analysis_name }}</el-descriptions-item>
          <el-descriptions-item label="缺陷标题" :span="2">{{ currentDetail.defect_title }}</el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="getSeverityType(currentDetail.severity)">{{ getSeverityLabel(currentDetail.severity) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(currentDetail.priority)">{{ getPriorityLabel(currentDetail.priority) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="缺陷类型">{{ currentDetail.defect_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentDetail.status)">{{ getStatusLabel(currentDetail.status) }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">缺陷描述</el-divider>
        <div class="section-content">{{ currentDetail.defect_description || '暂无描述' }}</div>

        <el-divider content-position="left">分析概述</el-divider>
        <div class="section-content" v-html="formatContent(currentDetail.executive_summary)"></div>

        <el-divider content-position="left">根因分析</el-divider>
        <div class="section-content" v-html="formatContent(currentDetail.root_cause_analysis)"></div>

        <el-divider content-position="left">影响分析</el-divider>
        <div class="section-content" v-html="formatContent(currentDetail.impact_analysis)"></div>

        <el-divider content-position="left">复现步骤</el-divider>
        <div class="section-content">
          <ol v-if="currentDetail.reproduction_steps?.length">
            <li v-for="(step, i) in currentDetail.reproduction_steps" :key="i">{{ step }}</li>
          </ol>
          <span v-else class="no-content">暂无内容</span>
        </div>

        <el-divider content-position="left">修复建议</el-divider>
        <div class="section-content">
          <ul v-if="currentDetail.fix_suggestions?.length">
            <li v-for="(item, i) in currentDetail.fix_suggestions" :key="i">{{ item }}</li>
          </ul>
          <span v-else class="no-content">暂无内容</span>
        </div>

        <el-divider content-position="left">预防措施</el-divider>
        <div class="section-content">
          <ul v-if="currentDetail.prevention_measures?.length">
            <li v-for="(item, i) in currentDetail.prevention_measures" :key="i">{{ item }}</li>
          </ul>
          <span v-else class="no-content">暂无内容</span>
        </div>
      </div>
    </el-drawer>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentId ? '编辑缺陷分析' : '新建缺陷分析'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目" prop="projectId">
              <el-select v-model="form.projectId" placeholder="选择项目" style="width: 100%">
                <el-option
                  v-for="item in projectList"
                  :key="item.projectId"
                  :label="item.projectName"
                  :value="item.projectId"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分析名称" prop="analysisName">
              <el-input v-model="form.analysisName" placeholder="请输入分析名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="缺陷标题" prop="defectTitle">
          <el-input v-model="form.defectTitle" placeholder="请输入缺陷标题" />
        </el-form-item>
        <el-form-item label="缺陷描述" prop="defectDescription">
          <el-input v-model="form.defectDescription" type="textarea" :rows="4" placeholder="请输入缺陷描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="严重程度" prop="severity">
              <el-select v-model="form.severity" placeholder="选择严重程度" style="width: 100%">
                <el-option label="致命" value="critical" />
                <el-option label="严重" value="high" />
                <el-option label="一般" value="medium" />
                <el-option label="轻微" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="选择优先级" style="width: 100%">
                <el-option label="紧急" value="urgent" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="缺陷类型" prop="defectType">
              <el-select v-model="form.defectType" placeholder="选择类型" style="width: 100%">
                <el-option label="功能缺陷" value="functional" />
                <el-option label="性能问题" value="performance" />
                <el-option label="安全漏洞" value="security" />
                <el-option label="UI问题" value="ui" />
                <el-option label="兼容性" value="compatibility" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- AI 对话抽屉 -->
    <AIChatDrawer
      v-model="aiChatVisible"
      assistant-id="defect_analyzer_agent"
      assistant-name="AI 缺陷分析"
      :initial-prompt="aiInitialPrompt"
      :project-id="queryParams.projectId"
      @message-sent="handleAIMessageSent"
    />
  </div>
</template>

<script setup name="DefectAnalysis">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, MagicStick } from '@element-plus/icons-vue'
import { listDefectAnalysis, getDefectAnalysis, addDefectAnalysis, updateDefectAnalysis, delDefectAnalysis } from '@/api/testing/defectAnalysis'
import { listAllProject } from '@/api/testing/project'
import AIChatDrawer from '@/views/testing/components/AIChatDrawer.vue'

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
const submitting = ref(false)
const aiInitialPrompt = ref('')

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  projectId: undefined,
  analysisName: undefined,
  severity: undefined,
  status: undefined
})

const form = reactive({
  projectId: undefined,
  analysisName: '',
  defectTitle: '',
  defectDescription: '',
  severity: 'medium',
  priority: 'medium',
  defectType: 'functional'
})

const rules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  analysisName: [{ required: true, message: '请输入分析名称', trigger: 'blur' }],
  defectTitle: [{ required: true, message: '请输入缺陷标题', trigger: 'blur' }]
}

const loadProjects = async () => {
  try {
    const res = await listAllProject('0')
    projectList.value = (res.data || []).map(item => ({
      projectId: item.project_id,
      projectName: item.project_name
    }))
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

const getList = async () => {
  loading.value = true
  try {
    const res = await listDefectAnalysis(queryParams)
    analysisList.value = res.data?.rows || res.data?.records || []
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
  proxy.resetForm('queryRef')
  handleQuery()
}

const handleSelectionChange = (selection) => {
  ids.value = selection.map(item => item.analysis_id)
  multiple.value = !selection.length
}

const handleAdd = () => {
  currentId.value = null
  resetForm()
  dialogVisible.value = true
}

const handleUpdate = async (row) => {
  currentId.value = row.analysis_id
  try {
    const res = await getDefectAnalysis(row.analysis_id)
    const data = res.data
    form.projectId = data.project_id
    form.analysisName = data.analysis_name
    form.defectTitle = data.defect_title
    form.defectDescription = data.defect_description
    form.severity = data.severity
    form.priority = data.priority
    form.defectType = data.defect_type
    dialogVisible.value = true
  } catch (error) {
    console.error('加载详情失败:', error)
  }
}

const handleDetail = async (row) => {
  try {
    const res = await getDefectAnalysis(row.analysis_id)
    currentDetail.value = res.data
    detailVisible.value = true
  } catch (error) {
    console.error('加载详情失败:', error)
  }
}

const handleDelete = async (row) => {
  const analysisIds = row?.analysis_id ? [row.analysis_id] : ids.value
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${analysisIds.length} 条记录?`, '警告', { type: 'warning' })
    for (const id of analysisIds) {
      await delDefectAnalysis(id)
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
  form.analysisName = ''
  form.defectTitle = ''
  form.defectDescription = ''
  form.severity = 'medium'
  form.priority = 'medium'
  form.defectType = 'functional'
}

const submitForm = async () => {
  const valid = await proxy.$refs.formRef?.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (currentId.value) {
      await updateDefectAnalysis(currentId.value, form)
      proxy.$modal.msgSuccess('更新成功')
    } else {
      await addDefectAnalysis(form)
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

const openAIChat = () => {
  aiInitialPrompt.value = ''
  aiChatVisible.value = true
}

const handleAIMessageSent = (data) => {
  if (data?.created) {
    getList()
  }
}

const getSeverityType = (severity) => {
  const map = { critical: 'danger', high: 'warning', medium: '', low: 'info' }
  return map[severity] || 'info'
}

const getSeverityLabel = (severity) => {
  const map = { critical: '致命', high: '严重', medium: '一般', low: '轻微' }
  return map[severity] || severity
}

const getPriorityType = (priority) => {
  const map = { urgent: 'danger', high: 'warning', medium: '', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const map = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

const getStatusType = (status) => {
  const map = { draft: 'info', analyzing: 'warning', completed: 'success', failed: 'danger' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { draft: '草稿', analyzing: '分析中', completed: '已完成', failed: '失败' }
  return map[status] || status
}

const formatContent = (content) => {
  if (!content) return '<span class="no-content">暂无内容</span>'
  if (typeof content === 'object') {
    return '<pre>' + JSON.stringify(content, null, 2) + '</pre>'
  }
  return content.replace(/\n/g, '<br>')
}

onMounted(async () => {
  await loadProjects()
  await getList()
})
</script>

<style scoped lang="scss">
.header-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
    min-height: 40px;

    ol, ul {
      margin: 0;
      padding-left: 20px;
    }

    pre {
      margin: 0;
      white-space: pre-wrap;
      font-size: 13px;
    }

    .no-content {
      color: #999;
    }
  }
}
</style>

