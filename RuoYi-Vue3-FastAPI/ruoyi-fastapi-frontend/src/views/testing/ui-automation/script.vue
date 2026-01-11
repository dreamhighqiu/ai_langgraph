<template>
  <div class="app-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><Document /></el-icon> Playwright UI测试脚本</h2>
          <p class="subtitle">Playwright UI Test Scripts</p>
        </div>
        <el-button type="primary" @click="handleAdd" v-hasPermi="['testing:script:add']">
          <el-icon><Plus /></el-icon> AI生成脚本
        </el-button>
      </div>
    </el-card>

    <el-card>
      <el-form :model="queryParams" ref="queryFormRef" :inline="true">
        <el-form-item label="项目" prop="project_id">
          <el-select v-model="queryParams.project_id" placeholder="选择项目" clearable style="width: 200px">
            <el-option
              v-for="project in projectList"
              :key="project.projectId"
              :label="project.projectName"
              :value="project.projectId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="脚本名称" prop="script_name">
          <el-input
            v-model="queryParams.script_name"
            placeholder="请输入脚本名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="浏览器" prop="browser">
          <el-select v-model="queryParams.browser" placeholder="选择浏览器" clearable style="width: 150px">
            <el-option label="Chromium" value="chromium" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="WebKit" value="webkit" />
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

      <el-table v-loading="loading" :data="scriptList" :row-class-name="tableRowClassName">
        <el-table-column label="ID" prop="scriptId" width="80" align="center" />
        <el-table-column label="脚本名称" prop="scriptName" show-overflow-tooltip min-width="180">
          <template #default="scope">
            <span class="script-name">
              <el-icon><DocumentCopy /></el-icon>
              {{ scope.row.scriptName }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="项目" prop="projectName" width="150" show-overflow-tooltip />
        <el-table-column label="语言" prop="language" width="120" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.language === 'typescript'" type="primary" size="small">TypeScript</el-tag>
            <el-tag v-else type="success" size="small">JavaScript</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="浏览器" prop="browser" width="120" align="center">
          <template #default="scope">
            <el-tag type="info" size="small">{{ scope.row.browser }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Agent" prop="agentId" width="100" show-overflow-tooltip />
        <el-table-column label="状态" prop="status" width="80" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.status === '0'" type="success" size="small">正常</el-tag>
            <el-tag v-else type="danger" size="small">停用</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="createTime" width="160" align="center" />
        <el-table-column label="操作" align="center" width="260" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)" size="small">
              查看
            </el-button>
            <el-button
              link
              type="success"
              icon="VideoPlay"
              @click="handleExecute(scope.row)"
              v-hasPermi="['testing:script:execute']"
              size="small"
            >
              执行
            </el-button>
            <el-button
              link
              type="danger"
              icon="Delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['testing:script:remove']"
              size="small"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total > 0"
        :total="total"
        v-model:page="queryParams.page_num"
        v-model:limit="queryParams.page_size"
        @pagination="getList"
      />
    </el-card>

    <!-- 查看脚本详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="`脚本详情 - ${currentScript?.scriptName}`"
      width="70%"
      top="5vh"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="脚本ID">{{ currentScript?.scriptId }}</el-descriptions-item>
        <el-descriptions-item label="脚本名称">{{ currentScript?.scriptName }}</el-descriptions-item>
        <el-descriptions-item label="项目">{{ currentScript?.projectName }}</el-descriptions-item>
        <el-descriptions-item label="语言">{{ currentScript?.language }}</el-descriptions-item>
        <el-descriptions-item label="浏览器">{{ currentScript?.browser }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ currentScript?.version }}</el-descriptions-item>
        <el-descriptions-item label="Agent ID">{{ currentScript?.agentId || '-' }}</el-descriptions-item>
        <el-descriptions-item label="使用RAG">
          <el-tag v-if="currentScript?.useRag === '1'" type="success" size="small">是</el-tag>
          <el-tag v-else type="info" size="small">否</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ currentScript?.createTime }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentScript?.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">脚本内容</el-divider>
      <div class="script-content">
        <pre><code>{{ currentScript?.scriptContent || '无脚本内容' }}</code></pre>
      </div>

      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleExecute(currentScript)">
          <el-icon><VideoPlay /></el-icon> 执行脚本
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="UIAutomationScript">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { listUIScripts, getUIScript, deleteUIScript } from '@/api/testing/uiAutomation'
import { listProject } from '@/api/testing/project'

const router = useRouter()
const route = useRoute()

const queryFormRef = ref(null)
const loading = ref(false)
const total = ref(0)
const scriptList = ref([])
const projectList = ref([])
const viewDialogVisible = ref(false)
const currentScript = ref(null)

const queryParams = reactive({
  page_num: 1,
  page_size: 10,
  project_id: null,
  script_name: null,
  browser: null,
  status: null
})

// 加载项目列表
async function loadProjects() {
  try {
    const response = await listProject({ projectType: 'ui', status: '0', pageNum: 1, pageSize: 100 })
    projectList.value = response.data?.rows || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 获取脚本列表
async function getList() {
  loading.value = true
  try {
    const response = await listUIScripts(queryParams)
    scriptList.value = response.data?.rows || []
    total.value = response.data?.total || 0
  } catch (error) {
    console.error('获取脚本列表失败:', error)
    ElMessage.error('获取脚本列表失败')
  } finally {
    loading.value = false
  }
}

// 表格行样式
function tableRowClassName({ row }) {
  const highlightId = route.query.highlightId
  if (highlightId && row.scriptId === Number(highlightId)) {
    return 'highlight-row'
  }
  return ''
}

function handleQuery() {
  queryParams.page_num = 1
  getList()
}

function resetQuery() {
  queryFormRef.value?.resetFields()
  handleQuery()
}

// AI生成脚本
function handleAdd() {
  router.push({ path: '/testing/ui-automation/generate' })
}

// 查看脚本详情
async function handleView(row) {
  try {
    const response = await getUIScript(row.scriptId)
    currentScript.value = response.data
    viewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取脚本详情失败')
  }
}

// 执行脚本
function handleExecute(row) {
  router.push({
    path: '/testing/ui-automation/execution',
    query: { scriptId: row.scriptId }
  })
}

// 删除脚本
function handleDelete(row) {
  ElMessageBox.confirm(
    `确认删除脚本"${row.scriptName}"吗？此操作不可恢复。`,
    '警告',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteUIScript(row.scriptId)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadProjects()
  getList()
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
    }
    .subtitle {
      color: #909399;
      margin: 0;
    }
  }
}

.script-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.script-content {
  max-height: 500px;
  overflow-y: auto;
  background: #282c34;
  border-radius: 4px;
  border: 1px solid #dcdfe6;

  pre {
    margin: 0;
    padding: 16px;

    code {
      font-family: 'Consolas', 'Monaco', monospace;
      font-size: 13px;
      line-height: 1.6;
      color: #abb2bf;
      white-space: pre;
      word-wrap: normal;
    }
  }
}

:deep(.highlight-row) {
  background-color: #ecf5ff !important;
  animation: highlight-fade 2s ease-in-out;
}

@keyframes highlight-fade {
  0%, 100% {
    background-color: transparent;
  }
  50% {
    background-color: #ecf5ff;
  }
}
</style>

