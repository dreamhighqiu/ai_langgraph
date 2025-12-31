<template>
  <div class="performance-testing-workspace">
    <el-page-header @back="$router.back()" content="性能测试工作台">
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
          <el-tag type="success">性能测试</el-tag>
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
            :test-type="'performance'"
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
            :test-type="'performance'"
            :script-type="'k6'"
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
            :test-type="'performance'"
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
            :test-type="'performance'"
            :report-type="'k6'"
            :project-id="currentProject.projectId"
            :highlight-report-id="highlightReportId"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 项目选择对话框 -->
    <el-dialog title="选择性能测试项目" v-model="showProjectSelector" width="600px">
      <el-table
        :data="performanceProjects"
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

<script setup name="PerformanceTesting">
import { listProject } from '@/api/testing/project'
import { getRequirementStatistics } from '@/api/testing/requirement'
import RequirementList from '../components/RequirementList.vue'
import ScriptList from '../script/index.vue'  // 复用现有的脚本列表组件
import ExecutionList from '../execution/index.vue'  // 复用现有的执行列表组件
import ReportList from '../report/index.vue'  // 复用现有的报告列表组件

const { proxy } = getCurrentInstance()

const activeTab = ref('requirements')
const currentProject = ref(null)
const performanceProjects = ref([])
const showProjectSelector = ref(false)

// 高亮ID（用于跨tab跳转后高亮显示）
const highlightScriptId = ref(null)
const highlightExecutionId = ref(null)
const highlightReportId = ref(null)

// 统计数据
const statistics = ref({
  totalRequirements: 0,
  totalScripts: 0,
  totalExecutions: 0,
  totalReports: 0
})

/** 获取性能测试项目列表 */
function getPerformanceProjects() {
  listProject({
    projectType: 'performance',
    status: '0',
    pageNum: 1,
    pageSize: 100
  }).then(response => {
    performanceProjects.value = response.data.rows
    // 如果有项目，默认选择第一个
    if (performanceProjects.value.length > 0 && !currentProject.value) {
      currentProject.value = performanceProjects.value[0]
      loadStatistics()
    }
  })
}

/** 选择项目 */
function selectProject(project) {
  currentProject.value = project
  showProjectSelector.value = false
  loadStatistics()
  // 刷新当前tab的数据
  handleTabChange(activeTab.value)
}

/** 加载统计数据 */
function loadStatistics() {
  if (!currentProject.value) return

  // 加载需求统计
  getRequirementStatistics(currentProject.value.projectId).then(response => {
    statistics.value.totalRequirements = response.data.total || 0
  })

  // TODO: 加载其他统计数据（脚本、执行、报告）
  // 这些可以通过各自的API获取
}

/** Tab切换处理 */
function handleTabChange(tabName) {
  // 清除高亮
  highlightScriptId.value = null
  highlightExecutionId.value = null
  highlightReportId.value = null
}

/** 处理生成脚本事件（从需求tab跳转到脚本tab） */
function handleGenerateScript(scriptData) {
  activeTab.value = 'scripts'
  // 高亮刚生成的脚本
  if (scriptData && scriptData.script_id) {
    highlightScriptId.value = scriptData.script_id
    proxy.$modal.msgSuccess(`脚本已生成，ID: ${scriptData.script_id}`)
  }
}

/** 处理执行脚本事件（从脚本tab跳转到执行tab） */
function handleExecuteScript(executionData) {
  activeTab.value = 'executions'
  // 高亮刚创建的执行记录
  if (executionData && executionData.execution_id) {
    highlightExecutionId.value = executionData.execution_id
    proxy.$modal.msgSuccess(`脚本开始执行，ID: ${executionData.execution_id}`)
  }
}

/** 处理查看报告事件（从执行tab跳转到报告tab） */
function handleViewReport(reportData) {
  activeTab.value = 'reports'
  // 高亮对应的报告
  if (reportData && reportData.report_id) {
    highlightReportId.value = reportData.report_id
  }
}

/** 需求创建成功回调 */
function handleRequirementCreated(requirement) {
  loadStatistics()
}

// 初始化
onMounted(() => {
  getPerformanceProjects()
})
</script>

<style scoped lang="scss">
.performance-testing-workspace {
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

