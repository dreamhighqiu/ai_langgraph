<template>
  <div class="requirement-container">
    <!-- 查询表单 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="需求名称" prop="requirementName">
        <el-input
          v-model="queryParams.requirementName"
          placeholder="请输入需求名称"
          clearable
          @keyup.enter="handleQuery"
        />
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

    <!-- 操作工具栏 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['testing:requirement:add']"
        >新增需求</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['testing:requirement:remove']"
        >删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 需求列表 -->
    <el-table v-loading="loading" :data="requirementList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="需求ID" align="center" prop="requirementId" width="80" />
      <el-table-column label="需求名称" align="center" prop="requirementName" :show-overflow-tooltip="true" />
      <el-table-column label="优先级" align="center" prop="priority" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.priority === 'high'" type="danger">高</el-tag>
          <el-tag v-else-if="scope.row.priority === 'medium'" type="warning">中</el-tag>
          <el-tag v-else type="info">低</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" prop="status" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.status === '0'" type="info">待处理</el-tag>
          <el-tag v-else-if="scope.row.status === '1'" type="primary">进行中</el-tag>
          <el-tag v-else-if="scope.row.status === '2'" type="success">已完成</el-tag>
          <el-tag v-else type="danger">已关闭</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="标签" align="center" prop="tags" width="200">
        <template #default="scope">
          <el-tag
            v-for="(tag, index) in scope.row.tags"
            :key="index"
            size="small"
            class="mr-1"
          >{{ tag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="280">
        <template #default="scope">
          <el-button
            link
            type="primary"
            icon="View"
            @click="handleDetail(scope.row)"
          >详情</el-button>
          <el-button
            link
            type="success"
            icon="MagicStick"
            @click="handleGenerateScript(scope.row)"
            v-hasPermi="['testing:requirement:generate']"
          >AI生成</el-button>
          <el-button
            link
            type="primary"
            icon="Edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['testing:requirement:edit']"
          >修改</el-button>
          <el-button
            link
            type="danger"
            icon="Delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['testing:requirement:remove']"
          >删除</el-button>
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

    <!-- 添加或修改需求对话框 -->
    <el-dialog :title="title" v-model="open" width="800px" append-to-body>
      <el-form ref="requirementRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="需求名称" prop="requirementName">
          <el-input v-model="form.requirementName" placeholder="请输入需求名称" />
        </el-form-item>
        <el-form-item label="需求描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入需求描述" />
        </el-form-item>
        <el-form-item label="验收标准" prop="acceptanceCriteria">
          <el-input
            v-model="acceptanceCriteriaText"
            type="textarea"
            :rows="3"
            placeholder='请输入验收标准（JSON格式），例如：{"response_time": "p95<500ms"}'
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio label="low">低</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="high">高</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标签" prop="tags">
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
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancel">取 消</el-button>
          <el-button type="primary" @click="submitForm">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- AI生成脚本对话框 -->
    <el-dialog title="AI生成测试脚本" v-model="generateDialogVisible" width="600px" append-to-body>
      <el-form :model="generateForm" label-width="120px">
        <el-form-item label="需求名称">
          <el-input :value="currentRequirement.requirementName" disabled />
        </el-form-item>
        <el-form-item label="是否使用RAG" prop="useRag">
          <el-switch v-model="generateForm.useRag" />
          <span class="ml-2 text-gray-500">开启后将从知识库查询相似案例增强生成质量</span>
        </el-form-item>
        <el-form-item label="配置参数" prop="config">
          <el-input
            v-model="generateConfigText"
            type="textarea"
            :rows="6"
            placeholder="请输入配置参数（JSON格式），例如：&#10;{&#10;  &quot;vus&quot;: 100,&#10;  &quot;duration&quot;: &quot;60s&quot;&#10;}"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="generateDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmGenerate" :loading="generating">
            <el-icon v-if="!generating"><MagicStick /></el-icon>
            {{ generating ? '生成中...' : '开始生成' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="RequirementList">
import { listRequirement, getRequirement, delRequirement, addRequirement, updateRequirement, generateScriptFromRequirement } from '@/api/testing/requirement'
import { listProject } from '@/api/testing/project'

const { proxy } = getCurrentInstance()

// 定义 props
const props = defineProps({
  testType: {
    type: String,
    required: true,
    validator: (value) => ['performance', 'ui', 'api'].includes(value)
  },
  projectId: {
    type: Number,
    default: null
  }
})

// 定义 emit
const emit = defineEmits(['generate-script', 'requirement-created'])

const requirementList = ref([])
const open = ref(false)
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref('')

// 查询参数
const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  requirementName: null,
  requirementType: props.testType,
  projectId: props.projectId,
  priority: null,
  status: null
})

// 表单数据
const form = ref({})
const acceptanceCriteriaText = ref('')

// 标签相关
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const tagInputRef = ref(null)

// AI生成相关
const generateDialogVisible = ref(false)
const generating = ref(false)
const currentRequirement = ref({})
const generateForm = ref({
  useRag: true,
  config: {}
})
const generateConfigText = ref('')

// 表单校验
const rules = {
  requirementName: [
    { required: true, message: '需求名称不能为空', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '需求描述不能为空', trigger: 'blur' }
  ]
}

/** 查询需求列表 */
function getList() {
  loading.value = true
  listRequirement(queryParams.value).then(response => {
    const rows = response?.rows || response?.data?.rows || []
    total.value = response?.total ?? response?.data?.total ?? 0
    requirementList.value = (rows || []).map(item => ({
      requirementId: item.requirement_id,
      projectId: item.project_id,
      requirementName: item.requirement_name,
      requirementType: item.requirement_type,
      description: item.description,
      acceptanceCriteria: item.acceptance_criteria,
      priority: item.priority,
      status: item.status,
      tags: item.tags || [],
      attachments: item.attachments,
      createBy: item.create_by,
      createTime: item.create_time,
      updateBy: item.update_by,
      updateTime: item.update_time,
      remark: item.remark
    }))
    loading.value = false
  })
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm('queryRef')
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.requirementId)
  single.value = selection.length !== 1
  multiple.value = !selection.length
}

/** 新增按钮操作 */
function handleAdd() {
  reset()
  open.value = true
  title.value = '添加需求'
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset()
  const requirementId = row.requirementId || ids.value[0]
  getRequirement(requirementId).then(response => {
    const raw = response?.data || response
    form.value = {
      requirementId: raw.requirement_id,
      projectId: raw.project_id,
      requirementName: raw.requirement_name,
      requirementType: raw.requirement_type,
      description: raw.description,
      acceptanceCriteria: raw.acceptance_criteria,
      priority: raw.priority,
      status: raw.status,
      tags: raw.tags || [],
      attachments: raw.attachments,
      remark: raw.remark
    }
    acceptanceCriteriaText.value = JSON.stringify(form.value.acceptanceCriteria || {}, null, 2)
    open.value = true
    title.value = '修改需求'
  })
}

/** 详情按钮操作 */
function handleDetail(row) {
  const requirementId = row.requirementId
  proxy.$router.push({
    path: '/testing/requirement/detail',
    query: { id: requirementId }
  })
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs['requirementRef'].validate(valid => {
    if (valid) {
      // 解析验收标准
      if (acceptanceCriteriaText.value) {
        try {
          form.value.acceptanceCriteria = JSON.parse(acceptanceCriteriaText.value)
        } catch (e) {
          proxy.$modal.msgError('验收标准格式错误，请输入有效的JSON')
          return
        }
      }

      // 设置需求类型和项目ID
      form.value.requirementType = props.testType
      if (props.projectId) {
        form.value.projectId = props.projectId
      }

      if (form.value.requirementId != null) {
        updateRequirement(form.value).then(response => {
          proxy.$modal.msgSuccess('修改成功')
          open.value = false
          getList()
          emit('requirement-created', form.value)
        })
      } else {
        addRequirement(form.value).then(response => {
          proxy.$modal.msgSuccess('新增成功')
          open.value = false
          getList()
          emit('requirement-created', response?.data || response)
        })
      }
    }
  })
}

/** 删除按钮操作 */
function handleDelete(row) {
  const requirementIds = row.requirementId || ids.value.join(',')
  proxy.$modal.confirm('是否确认删除需求编号为"' + requirementIds + '"的数据项？').then(function () {
    return delRequirement(requirementIds)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess('删除成功')
  }).catch(() => {})
}

/** AI生成脚本按钮操作 */
function handleGenerateScript(row) {
  currentRequirement.value = row
  generateForm.value = {
    useRag: true,
    config: {}
  }
  // 根据测试类型设置默认配置
  if (props.testType === 'performance') {
    generateForm.value.config = {
      vus: 10,
      duration: '30s'
    }
  } else if (props.testType === 'ui') {
    generateForm.value.config = {
      browser: 'chromium',
      headless: true
    }
  } else if (props.testType === 'api') {
    generateForm.value.config = {
      timeout: 10000
    }
  }
  generateConfigText.value = JSON.stringify(generateForm.value.config, null, 2)
  generateDialogVisible.value = true
}

/** 确认生成脚本 */
function confirmGenerate() {
  // 解析配置
  if (generateConfigText.value) {
    try {
      generateForm.value.config = JSON.parse(generateConfigText.value)
    } catch (e) {
      proxy.$modal.msgError('配置参数格式错误，请输入有效的JSON')
      return
    }
  }

  generating.value = true
  generateScriptFromRequirement(currentRequirement.value.requirementId, generateForm.value)
    .then(response => {
      proxy.$modal.msgSuccess('脚本生成成功')
      generateDialogVisible.value = false
      // 触发事件，通知父组件切换到脚本tab
      emit('generate-script', response.data)
    })
    .catch(error => {
      console.error('生成脚本失败:', error)
    })
    .finally(() => {
      generating.value = false
    })
}

// 标签操作
function handleTagClose(index) {
  form.value.tags.splice(index, 1)
}

function showTagInput() {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value.focus()
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

/** 表单重置 */
function reset() {
  form.value = {
    requirementId: null,
    projectId: props.projectId,
    requirementName: null,
    requirementType: props.testType,
    description: null,
    acceptanceCriteria: null,
    priority: 'medium',
    status: '0',
    tags: [],
    remark: null
  }
  acceptanceCriteriaText.value = ''
  proxy.resetForm('requirementRef')
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
}

// 初始化
onMounted(() => {
  getList()
})

// 监听projectId变化
watch(() => props.projectId, (newVal) => {
  queryParams.value.projectId = newVal
  getList()
})
</script>

<style scoped>
.mr-1 {
  margin-right: 4px;
}
.mr-2 {
  margin-right: 8px;
}
.ml-2 {
  margin-left: 8px;
}
.text-gray-500 {
  color: #6b7280;
  font-size: 12px;
}
</style>

