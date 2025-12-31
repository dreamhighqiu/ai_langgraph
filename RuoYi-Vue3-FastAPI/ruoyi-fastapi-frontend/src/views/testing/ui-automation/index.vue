<template>
  <div class="ui-automation-workspace">
    <el-page-header @back="$router.back()" content="UI自动化测试工作台">
      <template #extra>
        <el-button type="primary" @click="showProjectSelector = true">
          <el-icon><Operation /></el-icon>
          切换项目
        </el-button>
      </template>
    </el-page-header>

    <!-- 项目信息卡片 -->
    <el-card class="mt-4" v-if="currentProject">
      <template #header>
        <div class="card-header">
          <span>当前项目：{{ currentProject.projectName }}</span>
          <el-tag type="primary">UI自动化</el-tag>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="项目描述">{{ currentProject.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="项目状态">
          <el-tag v-if="currentProject.status === '0'" type="success">正常</el-tag>
          <el-tag v-else type="danger">停用</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(currentProject.createTime) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="mt-4">
      <el-col :span="6">
        <el-card>
          <el-statistic title="需求总数" :value="statistics.totalRequirements" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="脚本总数" :value="statistics.totalScripts" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="执行次数" :value="statistics.totalExecutions" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="报告数量" :value="statistics.totalReports" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 主工作区 - Tab面板 -->
    <el-card class="mt-4 workspace-card">
      <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
        <!-- Tab 1: 需求管理 -->
        <el-tab-pane label="需求管理" name="requirements">
          <template #label>
            <span><el-icon><List /></el-icon> 需求管理</span>
          </template>
          <requirement-list
            v-if="currentProject"
            :test-type="'ui'"
            :project-id="currentProject.projectId"
            @generate-script="handleGenerateScript"
            @requirement-created="handleRequirementCreated"
          />
        </el-tab-pane>

        <!-- Tab 2: 脚本生成 -->
        <el-tab-pane label="脚本生成" name="scripts">
          <template #label>
            <span><el-icon><Document /></el-icon> 脚本生成</span>
          </template>
          <script-list
            v-if="currentProject"
            :test-type="'ui'"
            :script-type="'playwright'"
            :project-id="currentProject.projectId"
            :highlight-script-id="highlightScriptId"
            @execute="handleExecuteScript"
          />
        </el-tab-pane>

        <!-- Tab 3: 脚本执行 -->
        <el-tab-pane label="脚本执行" name="executions">
          <template #label>
            <span><el-icon><VideoPlay /></el-icon> 脚本执行</span>
          </template>
          <execution-list
            v-if="currentProject"
            :test-type="'ui'"
            :project-id="currentProject.projectId"
            :highlight-execution-id="highlightExecutionId"
            @view-report="handleViewReport"
          />
        </el-tab-pane>

        <!-- Tab 4: 报告输出 -->
        <el-tab-pane label="报告输出" name="reports">
          <template #label>
            <span><el-icon><DataAnalysis /></el-icon> 报告输出</span>
          </template>
          <report-list
            v-if="currentProject"
            :test-type="'ui'"
            :report-type="'playwright'"
            :project-id="currentProject.projectId"
            :highlight-report-id="highlightReportId"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 项目选择对话框 -->
    <el-dialog title="选择UI自动化项目" v-model="showProjectSelector" width="600px">
      <el-table
        :data="uiProjects"
        @row-click="selectProject"
        highlight-current-row
        style="width: 100%"
      >
        <el-table-column property="projectName" label="项目名称" />
        <el-table-column property="description" label="项目描述" show-overflow-tooltip />
        <el-table-column property="status" label="状态" width="80">
          <template #default="scope">
            <el-tag v-if="scope.row.status === '0'" type="success" size="small">正常</el-tag>
            <el-tag v-else type="danger" size="small">停用</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showProjectSelector = false">取消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="UIAutomation">
import { listProject } from '@/api/testing/project'
import { getRequirementStatistics } from '@/api/testing/requirement'
import RequirementList from '../components/RequirementList.vue'
import ScriptList from '../script/index.vue'
import ExecutionList from '../execution/index.vue'
import ReportList from '../report/index.vue'

const { proxy } = getCurrentInstance()

const activeTab = ref('requirements')
const currentProject = ref(null)
const uiProjects = ref([])
const showProjectSelector = ref(false)

const highlightScriptId = ref(null)
const highlightExecutionId = ref(null)
const highlightReportId = ref(null)

const statistics = ref({
  totalRequirements: 0,
  totalScripts: 0,
  totalExecutions: 0,
  totalReports: 0
})

function getUIProjects() {
  listProject({
    projectType: 'ui',
    status: '0',
    pageNum: 1,
    pageSize: 100
  }).then(response => {
    uiProjects.value = response.data.rows
    if (uiProjects.value.length > 0 && !currentProject.value) {
      currentProject.value = uiProjects.value[0]
      loadStatistics()
    }
  })
}

function selectProject(project) {
  currentProject.value = project
  showProjectSelector.value = false
  loadStatistics()
  handleTabChange(activeTab.value)
}

function loadStatistics() {
  if (!currentProject.value) return
  getRequirementStatistics(currentProject.value.projectId).then(response => {
    statistics.value.totalRequirements = response.data.total || 0
  })
}

function handleTabChange(tabName) {
  highlightScriptId.value = null
  highlightExecutionId.value = null
  highlightReportId.value = null
}

function handleGenerateScript(scriptData) {
  activeTab.value = 'scripts'
  if (scriptData && scriptData.script_id) {
    highlightScriptId.value = scriptData.script_id
    proxy.$modal.msgSuccess(`Playwright脚本已生成，ID: ${scriptData.script_id}`)
  }
}

function handleExecuteScript(executionData) {
  activeTab.value = 'executions'
  if (executionData && executionData.execution_id) {
    highlightExecutionId.value = executionData.execution_id
    proxy.$modal.msgSuccess(`UI测试开始执行，ID: ${executionData.execution_id}`)
  }
}

function handleViewReport(reportData) {
  activeTab.value = 'reports'
  if (reportData && reportData.report_id) {
    highlightReportId.value = reportData.report_id
  }
}

function handleRequirementCreated(requirement) {
  loadStatistics()
}

onMounted(() => {
  getUIProjects()
})
</script>

<style scoped lang="scss">
.ui-automation-workspace {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .workspace-card {
    min-height: 600px;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    
    .el-icon {
      margin-right: 5px;
    }
  }
}

.mt-4 {
  margin-top: 16px;
}
</style>

