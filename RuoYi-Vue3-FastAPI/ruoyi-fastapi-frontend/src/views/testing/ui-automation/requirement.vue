<template>
  <div class="app-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><Monitor /></el-icon> UI自动化测试需求</h2>
          <p class="subtitle">Playwright UI Automation Requirements</p>
        </div>
        <el-button type="primary" @click="handleAdd" v-hasPermi="['testing:requirement:add']">
          <el-icon><Plus /></el-icon> 新建需求
        </el-button>
      </div>
    </el-card>

    <el-card>
      <el-form :model="queryParams" ref="queryForm" :inline="true">
        <el-form-item label="需求名称" prop="requirementName">
          <el-input v-model="queryParams.requirementName" placeholder="请输入需求名称" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="queryParams.priority" placeholder="请选择优先级" clearable>
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
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

      <el-table v-loading="loading" :data="requirementList">
        <el-table-column type="selection" width="55" />
        <el-table-column label="需求名称" prop="requirementName" show-overflow-tooltip />
        <el-table-column label="项目" prop="projectName" show-overflow-tooltip />
        <el-table-column label="优先级" prop="priority" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.priority === 'high'" type="danger">高</el-tag>
            <el-tag v-else-if="scope.row.priority === 'medium'" type="warning">中</el-tag>
            <el-tag v-else type="info">低</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.status === '0'" type="info">待处理</el-tag>
            <el-tag v-else-if="scope.row.status === '1'" type="primary">进行中</el-tag>
            <el-tag v-else-if="scope.row.status === '2'" type="success">已完成</el-tag>
            <el-tag v-else type="danger">已关闭</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="createTime" width="160" />
        <el-table-column label="操作" align="center" width="300" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)">详情</el-button>
            <el-button link type="primary" icon="MagicStick" @click="handleGenerate(scope.row)" v-hasPermi="['testing:requirement:generate']">AI生成</el-button>
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['testing:requirement:edit']">修改</el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['testing:requirement:remove']">删除</el-button>
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

<script setup name="UIAutomationRequirement">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const total = ref(0)
const requirementList = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  requirementName: undefined,
  requirementType: 'ui',
  priority: undefined,
  status: undefined
})

function getList() {
  // TODO: 调用实际API
  requirementList.value = []
  total.value = 0
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryParams.requirementName = undefined
  queryParams.priority = undefined
  queryParams.status = undefined
  handleQuery()
}

function handleAdd() {
  ElMessage.info('新建UI测试需求')
}

function handleView(row) {
  ElMessage.info('查看需求详情')
}

function handleGenerate(row) {
  ElMessage.info('AI生成Playwright脚本')
}

function handleUpdate(row) {
  ElMessage.info('修改需求')
}

function handleDelete(row) {
  ElMessage.info('删除需求')
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

