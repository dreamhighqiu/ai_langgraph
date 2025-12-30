<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="所属项目" prop="project_id">
        <el-select v-model="queryParams.project_id" placeholder="请选择项目" clearable style="width: 200px">
          <el-option v-for="item in projectList" :key="item.project_id" :label="item.project_name" :value="item.project_id" />
        </el-select>
      </el-form-item>
      <el-form-item label="脚本名称" prop="script_name">
        <el-input v-model="queryParams.script_name" placeholder="请输入脚本名称" clearable @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="脚本类型" prop="script_type">
        <el-select v-model="queryParams.script_type" placeholder="请选择类型" clearable>
          <el-option label="K6性能测试" value="k6" />
          <el-option label="Playwright" value="playwright" />
          <el-option label="API测试" value="api" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['testing:script:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="MagicStick" @click="handleGenerate" v-hasPermi="['testing:script:generate']">AI生成</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['testing:script:remove']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="scriptList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="脚本ID" align="center" prop="script_id" width="80" />
      <el-table-column label="脚本名称" align="center" prop="script_name" :show-overflow-tooltip="true" />
      <el-table-column label="所属项目" align="center" prop="project_name" width="120" />
      <el-table-column label="脚本类型" align="center" prop="script_type" width="100">
        <template #default="scope">
          <el-tag :type="getScriptTypeTag(scope.row.script_type)">{{ getScriptTypeName(scope.row.script_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="版本" align="center" prop="version" width="80" />
      <el-table-column label="状态" align="center" prop="status" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">{{ scope.row.status === '0' ? '正常' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="create_time" width="160">
        <template #default="scope">
          <span>{{ parseTime(scope.row.create_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="280">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['testing:script:edit']">编辑</el-button>
          <el-button link type="success" icon="VideoPlay" @click="handleExecute(scope.row)" v-hasPermi="['testing:script:execute']">执行</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['testing:script:remove']">删除</el-button>
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

    <!-- 添加或修改脚本对话框 -->
    <el-dialog :title="title" v-model="open" width="800px" append-to-body>
      <el-form ref="scriptRef" :model="form" :rules="rules" label-width="100px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="脚本名称" prop="script_name">
              <el-input v-model="form.script_name" placeholder="请输入脚本名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属项目" prop="project_id">
              <el-select v-model="form.project_id" placeholder="请选择项目" style="width: 100%">
                <el-option v-for="item in projectList" :key="item.project_id" :label="item.project_name" :value="item.project_id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="脚本类型" prop="script_type">
              <el-select v-model="form.script_type" placeholder="请选择类型" style="width: 100%">
                <el-option label="K6性能测试" value="k6" />
                <el-option label="Playwright" value="playwright" />
                <el-option label="API测试" value="api" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio value="0">正常</el-radio>
                <el-radio value="1">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="脚本内容" prop="script_content">
          <el-input v-model="form.script_content" type="textarea" :rows="15" placeholder="请输入脚本内容" style="font-family: monospace;" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- AI生成脚本对话框 -->
    <el-dialog title="AI智能生成脚本" v-model="generateOpen" width="700px" append-to-body>
      <el-form ref="generateRef" :model="generateForm" :rules="generateRules" label-width="100px">
        <el-form-item label="脚本名称" prop="script_name">
          <el-input v-model="generateForm.script_name" placeholder="请输入脚本名称" />
        </el-form-item>
        <el-form-item label="所属项目" prop="project_id">
          <el-select v-model="generateForm.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option v-for="item in projectList" :key="item.project_id" :label="item.project_name" :value="item.project_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="脚本类型" prop="script_type">
          <el-select v-model="generateForm.script_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="K6性能测试" value="k6" />
            <el-option label="Playwright UI测试" value="playwright" />
            <el-option label="API测试" value="api" />
          </el-select>
        </el-form-item>
        <el-form-item label="生成提示" prop="prompt">
          <el-input 
            v-model="generateForm.prompt" 
            type="textarea" 
            :rows="6" 
            placeholder="请详细描述您要生成的测试脚本，例如：&#10;生成一个登录接口的性能测试脚本，接口地址为https://api.example.com/login，&#10;请求方法为POST，测试50个虚拟用户，持续30秒。"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" :loading="generateLoading" @click="submitGenerate">
            <el-icon v-if="!generateLoading"><MagicStick /></el-icon>
            {{ generateLoading ? '生成中...' : 'AI 生成' }}
          </el-button>
          <el-button @click="generateOpen = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 脚本详情对话框 -->
    <el-dialog title="脚本详情" v-model="viewOpen" width="800px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="脚本名称">{{ viewData.script_name }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ viewData.project_name }}</el-descriptions-item>
        <el-descriptions-item label="脚本类型">{{ getScriptTypeName(viewData.script_type) }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ viewData.version }}</el-descriptions-item>
        <el-descriptions-item label="创建者">{{ viewData.create_by }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(viewData.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="Agent ID" v-if="viewData.agent_id">{{ viewData.agent_id }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider content-position="left">脚本内容</el-divider>
      <el-input v-model="viewData.script_content" type="textarea" :rows="15" readonly style="font-family: monospace;" />
    </el-dialog>

    <!-- 执行配置对话框 -->
    <el-dialog title="执行脚本" v-model="executeOpen" width="500px" append-to-body>
      <el-form ref="executeRef" :model="executeForm" label-width="100px">
        <el-form-item label="脚本名称">
          <el-input v-model="executeForm.script_name" disabled />
        </el-form-item>
        <el-form-item label="执行配置">
          <el-input v-model="executeForm.configStr" type="textarea" :rows="4" placeholder='可选，JSON格式，如：{"vus": 10, "duration": "30s"}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" :loading="executeLoading" @click="confirmExecute">
            <el-icon v-if="!executeLoading"><VideoPlay /></el-icon>
            {{ executeLoading ? '执行中...' : '开始执行' }}
          </el-button>
          <el-button @click="executeOpen = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="TestingScript">
import { listScript, getScript, addScript, updateScript, delScript, generateScript, executeScript } from "@/api/testing/script";
import { listAllProject } from "@/api/testing/project";

const { proxy } = getCurrentInstance();
const router = useRouter();

const scriptList = ref([]);
const projectList = ref([]);
const open = ref(false);
const generateOpen = ref(false);
const viewOpen = ref(false);
const executeOpen = ref(false);
const loading = ref(true);
const generateLoading = ref(false);
const executeLoading = ref(false);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const viewData = ref({});
const executeForm = ref({});

const data = reactive({
  form: {},
  generateForm: {},
  queryParams: {
    page_num: 1,
    page_size: 10,
    project_id: undefined,
    script_name: undefined,
    script_type: undefined
  },
  rules: {
    script_name: [{ required: true, message: "脚本名称不能为空", trigger: "blur" }],
    project_id: [{ required: true, message: "所属项目不能为空", trigger: "change" }],
    script_type: [{ required: true, message: "脚本类型不能为空", trigger: "change" }]
  },
  generateRules: {
    script_name: [{ required: true, message: "脚本名称不能为空", trigger: "blur" }],
    project_id: [{ required: true, message: "所属项目不能为空", trigger: "change" }],
    script_type: [{ required: true, message: "脚本类型不能为空", trigger: "change" }],
    prompt: [{ required: true, message: "生成提示不能为空", trigger: "blur" }, { min: 10, message: "提示词至少10个字符", trigger: "blur" }]
  }
});

const { queryParams, form, generateForm, rules, generateRules } = toRefs(data);

function getScriptTypeName(type) {
  const typeMap = { 'k6': 'K6性能测试', 'playwright': 'Playwright', 'api': 'API测试' };
  return typeMap[type] || type;
}

function getScriptTypeTag(type) {
  const tagMap = { 'k6': 'warning', 'playwright': 'success', 'api': '' };
  return tagMap[type] || 'info';
}

function getList() {
  loading.value = true;
  listScript(queryParams.value).then(response => {
    scriptList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

function getProjectList() {
  listAllProject('0').then(response => {
    projectList.value = response.data;
  });
}

function cancel() {
  open.value = false;
  reset();
}

function reset() {
  form.value = {
    script_id: undefined,
    project_id: undefined,
    script_name: undefined,
    script_type: undefined,
    script_content: undefined,
    status: "0",
    remark: undefined
  };
  proxy.resetForm("scriptRef");
}

function handleQuery() {
  queryParams.value.page_num = 1;
  getList();
}

function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.script_id);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

function handleAdd() {
  reset();
  open.value = true;
  title.value = "新增脚本";
}

function handleGenerate() {
  generateForm.value = { script_name: '', project_id: undefined, script_type: 'k6', prompt: '' };
  generateOpen.value = true;
}

function handleView(row) {
  getScript(row.script_id).then(response => {
    viewData.value = response.data;
    viewOpen.value = true;
  });
}

function handleUpdate(row) {
  reset();
  getScript(row.script_id).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改脚本";
  });
}

function handleExecute(row) {
  executeForm.value = { script_id: row.script_id, script_name: row.script_name, configStr: '' };
  executeOpen.value = true;
}

function submitForm() {
  proxy.$refs["scriptRef"].validate(valid => {
    if (valid) {
      if (form.value.script_id != undefined) {
        updateScript(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addScript(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

function submitGenerate() {
  proxy.$refs["generateRef"].validate(valid => {
    if (valid) {
      generateLoading.value = true;
      generateScript(generateForm.value).then(response => {
        proxy.$modal.msgSuccess("脚本生成成功");
        generateOpen.value = false;
        generateLoading.value = false;
        getList();
      }).catch(() => {
        generateLoading.value = false;
      });
    }
  });
}

function confirmExecute() {
  executeLoading.value = true;
  let config = {};
  if (executeForm.value.configStr) {
    try {
      config = JSON.parse(executeForm.value.configStr);
    } catch (e) {
      proxy.$modal.msgError("配置格式错误，请输入有效的JSON");
      executeLoading.value = false;
      return;
    }
  }
  executeScript({ script_id: executeForm.value.script_id, config: config }).then(response => {
    proxy.$modal.msgSuccess("执行已启动");
    executeOpen.value = false;
    executeLoading.value = false;
    router.push({ path: '/testing/execution', query: { execution_id: response.data.execution_id } });
  }).catch(() => {
    executeLoading.value = false;
  });
}

function handleDelete(row) {
  const scriptIds = row.script_id || ids.value;
  proxy.$modal.confirm('是否确认删除脚本编号为"' + scriptIds + '"的数据项?').then(function() {
    return delScript(scriptIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

getProjectList();
getList();
</script>

