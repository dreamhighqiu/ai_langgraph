<template>
  <div class="app-container test-case-container">
    <!-- 左侧文件夹树 -->
    <div class="folder-tree-panel">
      <div class="panel-header">
        <el-select v-model="currentProjectId" placeholder="选择项目" size="small" @change="handleProjectChange">
          <el-option
            v-for="item in projectList"
            :key="item.project_id"
            :label="item.project_name"
            :value="item.project_id"
          />
        </el-select>
      </div>
      <div class="panel-content">
        <el-tree
          ref="folderTreeRef"
          :data="folderTree"
          node-key="folder_id"
          :props="{ label: 'folder_name', children: 'children' }"
          highlight-current
          default-expand-all
          @node-click="handleFolderClick"
        >
          <template #default="{ node, data }">
            <span class="folder-node">
              <el-icon><Folder /></el-icon>
              <span class="folder-name">{{ node.label }}</span>
              <span class="folder-count" v-if="data.case_count">({{ data.case_count }})</span>
            </span>
          </template>
        </el-tree>
        <el-empty v-if="!folderTree.length" description="暂无文件夹" :image-size="60" />
      </div>
      <div class="panel-footer">
        <el-button type="primary" size="small" :icon="Plus" @click="handleAddFolder">新建文件夹</el-button>
      </div>
    </div>

    <!-- 右侧测试用例列表 -->
    <div class="test-case-panel">
      <!-- 页面标题 -->
      <el-card class="header-card">
        <div class="header-content">
          <div>
            <h2><el-icon><Document /></el-icon> 测试用例管理</h2>
            <p class="subtitle">Test Case Management - 管理和组织测试用例，支持AI智能生成</p>
          </div>
          <div class="header-actions">
            <el-dropdown @command="handleAICommand" v-hasPermi="['testing:testcase:add']">
              <el-button type="success">
                <el-icon><MagicStick /></el-icon>
                AI 生成用例
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="generate">
                    <el-icon><MagicStick /></el-icon>
                    AI 生成
                  </el-dropdown-item>
                  <el-dropdown-item command="document">
                    <el-icon><Upload /></el-icon>
                    从文档生成
                  </el-dropdown-item>
                  <el-dropdown-item command="chat" divided>
                    <el-icon><ChatDotRound /></el-icon>
                    AI 对话助手
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-card>

      <!-- 搜索表单 -->
      <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" class="search-form">
        <el-form-item label="用例名称" prop="caseName">
          <el-input v-model="queryParams.caseName" placeholder="请输入用例名称" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="queryParams.priority" placeholder="选择优先级" clearable style="width: 120px">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="queryParams.status" placeholder="选择状态" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="待评审" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已废弃" value="deprecated" />
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
          <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['testing:testcase:add']">新增</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['testing:testcase:remove']">删除</el-button>
        </el-col>
        <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
      </el-row>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="testCaseList" @selection-change="handleSelectionChange" border>
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column label="用例名称" align="left" min-width="200" :show-overflow-tooltip="true">
          <template #default="scope">
            <el-link type="primary" @click="handleDetail(scope.row)">{{ scope.row.case_name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="用例类型" align="center" width="100">
          <template #default="scope">
            <el-tag type="info" size="small">{{ getCaseTypeLabel(scope.row.case_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" align="center" width="80">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)" size="small">{{ getPriorityLabel(scope.row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" align="center" width="90">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">{{ getStatusLabel(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建人" align="center" prop="create_by" width="100" />
        <el-table-column label="创建时间" align="center" prop="create_time" width="160" />
        <el-table-column label="操作" align="center" width="200">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleDetail(scope.row)">详情</el-button>
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['testing:testcase:edit']">编辑</el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['testing:testcase:remove']">删除</el-button>
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
    </div>

    <!-- 文件夹编辑对话框 -->
    <el-dialog v-model="folderDialogVisible" :title="currentFolderId ? '编辑文件夹' : '新建文件夹'" width="500px">
      <el-form ref="folderFormRef" :model="folderForm" :rules="folderRules" label-width="100px">
        <el-form-item label="文件夹名称" prop="folderName">
          <el-input v-model="folderForm.folderName" placeholder="请输入文件夹名称" />
        </el-form-item>
        <el-form-item label="父文件夹" prop="parentId">
          <el-tree-select
            v-model="folderForm.parentId"
            :data="folderTree"
            :props="{ label: 'folder_name', value: 'folder_id', children: 'children' }"
            placeholder="选择父文件夹（可选）"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="folderForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="folderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFolderForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 测试用例详情/编辑抽屉 -->
    <el-drawer
      v-model="detailVisible"
      :title="isEditing ? (currentCaseId ? '编辑测试用例' : '新建测试用例') : '测试用例详情'"
      size="55%"
      :destroy-on-close="true"
    >
      <div v-if="!isEditing && currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例名称" :span="2">{{ currentDetail.case_name }}</el-descriptions-item>
          <el-descriptions-item label="用例类型">{{ getCaseTypeLabel(currentDetail.case_type) }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(currentDetail.priority)">{{ getPriorityLabel(currentDetail.priority) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentDetail.status)">{{ getStatusLabel(currentDetail.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="自动化状态">{{ currentDetail.is_automated ? '已自动化' : '未自动化' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">前置条件</el-divider>
        <div class="section-content">{{ currentDetail.preconditions || '无' }}</div>

        <el-divider content-position="left">测试步骤</el-divider>
        <el-table :data="parseSteps(currentDetail.test_case_steps)" border size="small">
          <el-table-column label="步骤" type="index" width="60" align="center" />
          <el-table-column label="操作" prop="action" min-width="200" />
          <el-table-column label="预期结果" prop="expected" min-width="200" />
        </el-table>

        <el-divider content-position="left">预期结果</el-divider>
        <div class="section-content">{{ currentDetail.expected_result || '无' }}</div>

        <div class="detail-footer">
          <el-button type="primary" @click="startEdit(currentDetail)">编辑</el-button>
          <el-button @click="detailVisible = false">关闭</el-button>
        </div>
      </div>

      <!-- 编辑表单 -->
      <div v-else class="edit-form">
        <el-form ref="caseFormRef" :model="caseForm" :rules="caseRules" label-width="100px">
          <el-form-item label="用例名称" prop="caseName">
            <el-input v-model="caseForm.caseName" placeholder="请输入用例名称" />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="用例类型" prop="caseType">
                <el-select v-model="caseForm.caseType" placeholder="选择类型" style="width: 100%">
                  <el-option label="功能测试" value="functional" />
                  <el-option label="性能测试" value="performance" />
                  <el-option label="安全测试" value="security" />
                  <el-option label="接口测试" value="api" />
                  <el-option label="UI测试" value="ui" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="优先级" prop="priority">
                <el-select v-model="caseForm.priority" placeholder="选择优先级" style="width: 100%">
                  <el-option label="高" value="high" />
                  <el-option label="中" value="medium" />
                  <el-option label="低" value="low" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="前置条件">
            <el-input v-model="caseForm.preconditions" type="textarea" :rows="2" placeholder="请输入前置条件" />
          </el-form-item>
          <el-form-item label="测试步骤">
            <div class="steps-editor">
              <div v-for="(step, index) in caseForm.steps" :key="index" class="step-item">
                <div class="step-header">
                  <span>步骤 {{ index + 1 }}</span>
                  <el-button type="danger" :icon="Delete" circle size="small" @click="removeStep(index)" />
                </div>
                <el-input v-model="step.action" placeholder="操作步骤" class="step-input" />
                <el-input v-model="step.expected" placeholder="预期结果" class="step-input" />
              </div>
              <el-button type="primary" plain :icon="Plus" @click="addStep">添加步骤</el-button>
            </div>
          </el-form-item>
          <el-form-item label="预期结果">
            <el-input v-model="caseForm.expectedResult" type="textarea" :rows="2" placeholder="请输入整体预期结果" />
          </el-form-item>
        </el-form>
        <div class="edit-footer">
          <el-button type="primary" @click="submitCaseForm" :loading="submitting">保存</el-button>
          <el-button @click="cancelEdit">取消</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- AI 对话抽屉 -->
    <AIChatDrawer
      v-model="aiChatVisible"
      assistant-id="testcase_generator_agent"
      assistant-name="AI 用例生成"
      :project-id="currentProjectId"
      :folder-id="currentFolderId"
      :initial-prompt="aiInitialPrompt"
      @message-sent="handleAIMessageSent"
    />

    <!-- AI 生成测试用例对话框 -->
    <AIGenerateDialog
      v-model="aiGenerateDialogVisible"
      :project-id="currentProjectId"
      :folder-id="currentFolderId"
      @open-chat="handleOpenAIChat"
      @success="handleAIGenerateSuccess"
    />

    <!-- AI 从文档生成测试用例对话框 -->
    <AIDocGenerateDialog
      v-model="aiDocDialogVisible"
      :project-id="currentProjectId"
      :folder-id="currentFolderId"
      @open-chat="handleOpenAIChat"
      @success="handleAIGenerateSuccess"
    />
  </div>
</template>

<script setup name="TestCase">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Folder, Plus, Delete, MagicStick, ArrowDown, Upload, ChatDotRound } from '@element-plus/icons-vue'
import { listTestCase, getTestCase, addTestCase, updateTestCase, delTestCase } from '@/api/testing/testCase'
import { getFolderTree, addFolder, updateFolder } from '@/api/testing/folder'
import { listAllProject } from '@/api/testing/project'
import AIChatDrawer from '@/views/testing/components/AIChatDrawer.vue'
import AIGenerateDialog from '@/views/testing/components/AIGenerateDialog.vue'
import AIDocGenerateDialog from '@/views/testing/components/AIDocGenerateDialog.vue'

const { proxy } = getCurrentInstance()

// 状态
const loading = ref(false)
const showSearch = ref(true)
const testCaseList = ref([])
const projectList = ref([])
const folderTree = ref([])
const total = ref(0)
const ids = ref([])
const multiple = ref(true)

const currentProjectId = ref(null)
const currentFolderId = ref(null)
const currentCaseId = ref(null)
const currentDetail = ref(null)

const detailVisible = ref(false)
const folderDialogVisible = ref(false)
const aiChatVisible = ref(false)
const aiGenerateDialogVisible = ref(false)
const aiDocDialogVisible = ref(false)
const aiInitialPrompt = ref('')
const isEditing = ref(false)
const submitting = ref(false)

const folderTreeRef = ref(null)

// 查询参数
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  projectId: null,
  folderId: null,
  caseName: '',
  priority: '',
  status: ''
})

// 文件夹表单
const folderForm = reactive({
  folderName: '',
  parentId: null,
  description: ''
})

const folderRules = {
  folderName: [{ required: true, message: '请输入文件夹名称', trigger: 'blur' }]
}

// 测试用例表单
const caseForm = reactive({
  caseName: '',
  caseType: 'functional',
  priority: 'medium',
  preconditions: '',
  steps: [{ action: '', expected: '' }],
  expectedResult: ''
})

const caseRules = {
  caseName: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  caseType: [{ required: true, message: '请选择用例类型', trigger: 'change' }]
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await listAllProject('0')
    projectList.value = res.data || []
    if (projectList.value.length > 0) {
      // 确保 project_id 是数字类型
      const firstProjectId = Number(projectList.value[0].project_id)
      if (!isNaN(firstProjectId) && firstProjectId > 0) {
        currentProjectId.value = firstProjectId
        await loadFolderTree()
        await getList()
      } else {
        console.error('无效的项目ID:', projectList.value[0].project_id)
        proxy.$modal.msgWarning('项目数据异常，请刷新页面重试')
      }
    } else {
      console.warn('项目列表为空')
    }
  } catch (error) {
    console.error('加载项目失败:', error)
    // 如果是用户未登录错误，给出友好提示
    if (error?.message?.includes('用户信息为空') || error?.message?.includes('登录')) {
      proxy.$modal.msgWarning('请先登录后再访问此页面')
    } else {
      proxy.$modal.msgError('加载项目失败: ' + (error?.message || '未知错误'))
    }
  }
}

// 加载文件夹树
const loadFolderTree = async () => {
  if (!currentProjectId.value) {
    console.warn('项目ID为空，跳过加载文件夹树')
    return
  }
  try {
    // 确保 projectId 是数字类型
    const projectId = Number(currentProjectId.value)
    if (isNaN(projectId) || projectId <= 0) {
      console.error('无效的项目ID:', currentProjectId.value)
      return
    }
    const res = await getFolderTree(projectId)
    folderTree.value = res.data || []
  } catch (error) {
    console.error('加载文件夹失败:', error)
    // 忽略用户信息错误（在 loadProjects 中已处理）
    if (!error?.message?.includes('用户信息为空') && !error?.message?.includes('项目ID不能为空')) {
      proxy.$modal.msgError('加载文件夹失败: ' + (error?.message || '未知错误'))
    }
  }
}

// 加载测试用例列表
const getList = async () => {
  if (!currentProjectId.value) {
    console.warn('项目ID为空，跳过加载测试用例列表')
    return
  }
  loading.value = true
  try {
    // 确保 projectId 是数字类型
    const projectId = Number(currentProjectId.value)
    if (isNaN(projectId) || projectId <= 0) {
      console.error('无效的项目ID:', currentProjectId.value)
      loading.value = false
      return
    }
    queryParams.projectId = projectId
    queryParams.folderId = currentFolderId.value ? Number(currentFolderId.value) : null
    const res = await listTestCase(queryParams)
    testCaseList.value = res.data?.records || res.data?.rows || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error('加载列表失败:', error)
    // 忽略用户信息错误（在 loadProjects 中已处理）
    if (!error?.message?.includes('用户信息为空')) {
      proxy.$modal.msgError('加载测试用例失败: ' + (error?.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

// 项目切换
const handleProjectChange = async () => {
  currentFolderId.value = null
  await loadFolderTree()
  await getList()
}

// 文件夹点击
const handleFolderClick = (data) => {
  currentFolderId.value = data.folder_id
  queryParams.pageNum = 1
  getList()
}

// 搜索
const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  proxy.resetForm('queryRef')
  handleQuery()
}

// 选择变化
const handleSelectionChange = (selection) => {
  ids.value = selection.map(item => item.case_id)
  multiple.value = !selection.length
}

// 新增文件夹
const handleAddFolder = () => {
  folderForm.folderName = ''
  folderForm.parentId = currentFolderId.value
  folderForm.description = ''
  folderDialogVisible.value = true
}

// 提交文件夹
const submitFolderForm = async () => {
  const valid = await proxy.$refs.folderFormRef?.validate()
  if (!valid) return

  try {
    await addFolder({
      project_id: currentProjectId.value,
      parent_id: folderForm.parentId,
      folder_name: folderForm.folderName,
      description: folderForm.description
    })
    proxy.$modal.msgSuccess('创建成功')
    folderDialogVisible.value = false
    await loadFolderTree()
  } catch (error) {
    console.error('创建文件夹失败:', error)
  }
}

// 新增测试用例
const handleAdd = () => {
  currentCaseId.value = null
  currentDetail.value = null
  resetCaseForm()
  isEditing.value = true
  detailVisible.value = true
}

// 编辑
const handleUpdate = async (row) => {
  try {
    const res = await getTestCase(row.case_id)
    currentDetail.value = res.data
    startEdit(res.data)
  } catch (error) {
    console.error('加载详情失败:', error)
  }
}

// 详情
const handleDetail = async (row) => {
  try {
    const res = await getTestCase(row.case_id)
    currentDetail.value = res.data
    currentCaseId.value = row.case_id
    isEditing.value = false
    detailVisible.value = true
  } catch (error) {
    console.error('加载详情失败:', error)
  }
}

// 开始编辑
const startEdit = (data) => {
  currentCaseId.value = data.case_id
  caseForm.caseName = data.case_name
  caseForm.caseType = data.case_type || 'functional'
  caseForm.priority = data.priority || 'medium'
  caseForm.preconditions = data.preconditions || ''
  caseForm.expectedResult = data.expected_result || ''
  caseForm.steps = parseSteps(data.test_case_steps)
  if (!caseForm.steps.length) {
    caseForm.steps = [{ action: '', expected: '' }]
  }
  isEditing.value = true
}

const cancelEdit = () => {
  if (currentDetail.value) {
    isEditing.value = false
  } else {
    detailVisible.value = false
  }
}

const resetCaseForm = () => {
  caseForm.caseName = ''
  caseForm.caseType = 'functional'
  caseForm.priority = 'medium'
  caseForm.preconditions = ''
  caseForm.expectedResult = ''
  caseForm.steps = [{ action: '', expected: '' }]
}

// 步骤操作
const addStep = () => {
  caseForm.steps.push({ action: '', expected: '' })
}

const removeStep = (index) => {
  if (caseForm.steps.length > 1) {
    caseForm.steps.splice(index, 1)
  }
}

// 解析步骤
const parseSteps = (steps) => {
  if (!steps) return []
  if (Array.isArray(steps)) return steps
  try {
    return JSON.parse(steps)
  } catch {
    return []
  }
}

// 提交测试用例
const submitCaseForm = async () => {
  const valid = await proxy.$refs.caseFormRef?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const submitData = {
      project_id: currentProjectId.value,
      folder_id: currentFolderId.value,
      case_name: caseForm.caseName,
      case_type: caseForm.caseType,
      priority: caseForm.priority,
      preconditions: caseForm.preconditions,
      expected_result: caseForm.expectedResult,
      test_case_steps: caseForm.steps.filter(s => s.action || s.expected)
    }

    if (currentCaseId.value) {
      await updateTestCase(currentCaseId.value, submitData)
      proxy.$modal.msgSuccess('更新成功')
    } else {
      await addTestCase(submitData)
      proxy.$modal.msgSuccess('创建成功')
    }
    detailVisible.value = false
    getList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  const caseIds = row?.case_id ? [row.case_id] : ids.value
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${caseIds.length} 条测试用例?`, '警告', { type: 'warning' })
    for (const id of caseIds) {
      await delTestCase(id)
    }
    proxy.$modal.msgSuccess('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// AI 命令处理
const handleAICommand = (command) => {
  switch (command) {
    case 'generate':
      openAIGenerateDialog()
      break
    case 'document':
      openAIDocDialog()
      break
    case 'chat':
      openAIChat()
      break
  }
}

// AI 对话
const openAIChat = () => {
  aiInitialPrompt.value = ''
  aiChatVisible.value = true
}

// 打开AI生成对话框
const openAIGenerateDialog = () => {
  aiGenerateDialogVisible.value = true
}

// 打开AI从文档生成对话框
const openAIDocDialog = () => {
  aiDocDialogVisible.value = true
}

// 处理打开AI聊天（从对话框）
const handleOpenAIChat = (prompt) => {
  aiInitialPrompt.value = prompt
  aiChatVisible.value = true
}

// AI生成成功回调
const handleAIGenerateSuccess = () => {
  getList()
}

const handleAIMessageSent = (data) => {
  if (data?.created) {
    getList()
  }
}

// 工具函数
const getCaseTypeLabel = (type) => {
  const map = { functional: '功能测试', performance: '性能测试', security: '安全测试', api: '接口测试', ui: 'UI测试' }
  return map[type] || type
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const map = { high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

const getStatusType = (status) => {
  const map = { draft: 'info', pending: 'warning', approved: 'success', deprecated: 'danger' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { draft: '草稿', pending: '待评审', approved: '已通过', deprecated: '已废弃' }
  return map[status] || status
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.test-case-container {
  display: flex;
  gap: 16px;
  height: calc(100vh - 100px);
}

.folder-tree-panel {
  width: 280px;
  min-width: 280px;
  background: white;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  .panel-header {
    padding: 12px;
    border-bottom: 1px solid #ebeef5;
  }

  .panel-content {
    flex: 1;
    overflow: auto;
    padding: 12px;

    .folder-node {
      display: flex;
      align-items: center;
      gap: 6px;

      .folder-name {
        flex: 1;
      }

      .folder-count {
        color: #909399;
        font-size: 12px;
      }
    }
  }

  .panel-footer {
    padding: 12px;
    border-top: 1px solid #ebeef5;
    text-align: center;
  }
}

.test-case-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .header-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        font-size: 22px;
      }

      .subtitle {
        margin: 6px 0 0 0;
        opacity: 0.9;
        font-size: 13px;
      }

      .header-actions .el-button {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
      }
    }
  }

  .search-form {
    margin-bottom: 12px;
  }
}

.detail-content {
  padding: 0 20px;

  .section-content {
    padding: 12px;
    background: #f9f9f9;
    border-radius: 4px;
    min-height: 40px;
    line-height: 1.8;
  }

  .detail-footer {
    margin-top: 24px;
    text-align: center;
  }
}

.edit-form {
  padding: 0 20px;

  .steps-editor {
    .step-item {
      background: #f5f7fa;
      padding: 12px;
      border-radius: 4px;
      margin-bottom: 12px;

      .step-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-weight: 500;
      }

      .step-input {
        margin-bottom: 8px;
      }
    }
  }

  .edit-footer {
    margin-top: 24px;
    text-align: center;
  }
}
</style>

