<template>
  <div class="app-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><DataAnalysis /></el-icon> UI自动化测试报告</h2>
          <p class="subtitle">Playwright/Allure Test Reports</p>
        </div>
      </div>
    </el-card>

    <el-card>
      <el-form :model="queryParams" ref="queryForm" :inline="true">
        <el-form-item label="报告名称" prop="reportName">
          <el-input v-model="queryParams.reportName" placeholder="请输入报告名称" clearable />
        </el-form-item>
        <el-form-item label="生成时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="reportList">
        <el-table-column label="报告名称" prop="reportName" show-overflow-tooltip />
        <el-table-column label="关联脚本" prop="scriptName" show-overflow-tooltip />
        <el-table-column label="浏览器" prop="browser" width="100" />
        <el-table-column label="测试结果" prop="result" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.result === 'passed'" type="success">通过</el-tag>
            <el-tag v-else type="danger">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="生成时间" prop="createTime" width="160" />
        <el-table-column label="操作" align="center" width="250" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看详情</el-button>
            <el-button link type="success" icon="Download" @click="handleDownload(scope.row)">下载报告</el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)">删除</el-button>
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
  </div>
</template>

<script setup name="UIAutomationReport">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const total = ref(0)
const reportList = ref([])
const dateRange = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  reportName: undefined,
  reportType: 'ui'
})

function getList() {
  reportList.value = []
  total.value = 0
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryParams.reportName = undefined
  dateRange.value = []
  handleQuery()
}

function handleView(row) {
  ElMessage.info('查看报告详情')
}

function handleDownload(row) {
  ElMessage.info('下载报告')
}

function handleDelete(row) {
  ElMessage.info('删除报告')
}

onMounted(() => {
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
</style>

