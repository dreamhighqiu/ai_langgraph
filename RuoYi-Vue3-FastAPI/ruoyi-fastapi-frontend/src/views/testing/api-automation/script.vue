<template>
  <div class="app-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2><el-icon><Document /></el-icon> REST API测试脚本</h2>
          <p class="subtitle">REST API Test Scripts</p>
        </div>
        <el-button type="primary" @click="handleAdd" v-hasPermi="['testing:script:add']">
          <el-icon><Plus /></el-icon> 新建脚本
        </el-button>
      </div>
    </el-card>

    <el-card>
      <el-form :model="queryParams" ref="queryForm" :inline="true">
        <el-form-item label="脚本名称" prop="scriptName">
          <el-input v-model="queryParams.scriptName" placeholder="请输入脚本名称" clearable />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
            <el-option label="草稿" value="0" />
            <el-option label="已发布" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="scriptList">
        <el-table-column label="脚本名称" prop="scriptName" show-overflow-tooltip />
        <el-table-column label="关联需求" prop="requirementName" show-overflow-tooltip />
        <el-table-column label="HTTP方法" prop="httpMethod" width="120" />
        <el-table-column label="状态" prop="status" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.status === '0'" type="info">草稿</el-tag>
            <el-tag v-else type="success">已发布</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="createTime" width="160" />
        <el-table-column label="操作" align="center" width="300" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看</el-button>
            <el-button link type="primary" icon="VideoPlay" @click="handleExecute(scope.row)" v-hasPermi="['testing:script:execute']">执行</el-button>
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['testing:script:edit']">修改</el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['testing:script:remove']">删除</el-button>
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

<script setup name="APIAutomationScript">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const total = ref(0)
const scriptList = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  scriptName: undefined,
  scriptType: 'api',
  status: undefined
})

function getList() {
  scriptList.value = []
  total.value = 0
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryParams.scriptName = undefined
  queryParams.status = undefined
  handleQuery()
}

function handleAdd() {
  ElMessage.info('新建API测试脚本')
}

function handleView(row) {
  ElMessage.info('查看脚本')
}

function handleExecute(row) {
  ElMessage.info('执行API测试')
}

function handleUpdate(row) {
  ElMessage.info('修改脚本')
}

function handleDelete(row) {
  ElMessage.info('删除脚本')
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

