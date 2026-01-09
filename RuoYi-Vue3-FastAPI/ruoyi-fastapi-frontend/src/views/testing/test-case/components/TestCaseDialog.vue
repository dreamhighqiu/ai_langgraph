<template>
  <el-dialog
    v-model="visible"
    :title="caseId ? '编辑测试用例' : '新建测试用例'"
    width="900px"
    :close-on-click-modal="false"
    destroy-on-close
    @open="handleOpen"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-tabs v-model="activeTab">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="用例名称" prop="caseName">
                <el-input v-model="form.caseName" placeholder="请输入用例名称" maxlength="200" show-word-limit />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="模板类型" prop="template">
                <el-radio-group v-model="form.template">
                  <el-radio value="test_case">普通用例</el-radio>
                  <el-radio value="test_case_bdd">BDD用例</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="用例类型" prop="caseType">
                <el-select v-model="form.caseType" placeholder="选择用例类型" style="width: 100%">
                  <el-option label="功能测试" value="functional" />
                  <el-option label="回归测试" value="regression" />
                  <el-option label="冒烟测试" value="smoke" />
                  <el-option label="性能测试" value="performance" />
                  <el-option label="安全测试" value="security" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="优先级" prop="priority">
                <el-select v-model="form.priority" placeholder="选择优先级" style="width: 100%">
                  <el-option label="紧急" value="critical" />
                  <el-option label="高" value="high" />
                  <el-option label="中" value="medium" />
                  <el-option label="低" value="low" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="描述" prop="description">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入用例描述" />
          </el-form-item>

          <el-form-item label="前置条件" prop="preconditions">
            <el-input v-model="form.preconditions" type="textarea" :rows="2" placeholder="请输入前置条件" />
          </el-form-item>

          <el-form-item label="标签" prop="tags">
            <el-select
              v-model="form.tags"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入标签并回车"
              style="width: 100%"
            >
              <el-option v-for="tag in tagOptions" :key="tag" :label="tag" :value="tag" />
            </el-select>
          </el-form-item>
        </el-tab-pane>

        <!-- 普通用例步骤 -->
        <el-tab-pane label="测试步骤" name="steps" v-if="form.template === 'test_case'">
          <div class="steps-container">
            <div v-for="(step, index) in form.testCaseSteps" :key="index" class="step-item">
              <div class="step-header">
                <span class="step-number">步骤 {{ index + 1 }}</span>
                <el-button type="danger" size="small" :icon="Delete" circle @click="removeStep(index)" />
              </div>
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-input
                    v-model="step.action"
                    type="textarea"
                    :rows="2"
                    placeholder="操作步骤描述"
                  />
                </el-col>
                <el-col :span="12">
                  <el-input
                    v-model="step.expected"
                    type="textarea"
                    :rows="2"
                    placeholder="预期结果"
                  />
                </el-col>
              </el-row>
            </div>
            <el-button type="primary" plain :icon="Plus" @click="addStep">添加步骤</el-button>
          </div>
        </el-tab-pane>

        <!-- BDD 用例 -->
        <el-tab-pane label="BDD 场景" name="bdd" v-if="form.template === 'test_case_bdd'">
          <el-form-item label="Feature" prop="feature">
            <el-input v-model="form.feature" type="textarea" :rows="2" placeholder="功能描述" />
          </el-form-item>

          <el-form-item label="Scenario" prop="scenario">
            <el-input v-model="form.scenario" type="textarea" :rows="2" placeholder="场景描述" />
          </el-form-item>

          <el-form-item label="Background" prop="background">
            <el-input v-model="form.background" type="textarea" :rows="2" placeholder="背景描述（可选）" />
          </el-form-item>

          <el-divider content-position="left">Given（前提条件）</el-divider>
          <div class="bdd-steps">
            <div v-for="(step, index) in form.givenSteps" :key="'given-' + index" class="bdd-step-item">
              <el-input v-model="form.givenSteps[index]" placeholder="Given..." />
              <el-button type="danger" :icon="Delete" circle size="small" @click="form.givenSteps.splice(index, 1)" />
            </div>
            <el-button type="primary" plain size="small" :icon="Plus" @click="form.givenSteps.push('')">添加 Given</el-button>
          </div>

          <el-divider content-position="left">When（操作）</el-divider>
          <div class="bdd-steps">
            <div v-for="(step, index) in form.whenSteps" :key="'when-' + index" class="bdd-step-item">
              <el-input v-model="form.whenSteps[index]" placeholder="When..." />
              <el-button type="danger" :icon="Delete" circle size="small" @click="form.whenSteps.splice(index, 1)" />
            </div>
            <el-button type="primary" plain size="small" :icon="Plus" @click="form.whenSteps.push('')">添加 When</el-button>
          </div>

          <el-divider content-position="left">Then（预期结果）</el-divider>
          <div class="bdd-steps">
            <div v-for="(step, index) in form.thenSteps" :key="'then-' + index" class="bdd-step-item">
              <el-input v-model="form.thenSteps[index]" placeholder="Then..." />
              <el-button type="danger" :icon="Delete" circle size="small" @click="form.thenSteps.splice(index, 1)" />
            </div>
            <el-button type="primary" plain size="small" :icon="Plus" @click="form.thenSteps.push('')">添加 Then</el-button>
          </div>
        </el-tab-pane>

        <!-- 测试数据 -->
        <el-tab-pane label="测试数据" name="data">
          <el-form-item label="测试数据" prop="testData">
            <el-input v-model="form.testData" type="textarea" :rows="6" placeholder="请输入测试数据（JSON或文本格式）" />
          </el-form-item>

          <el-form-item label="预期结果" prop="expectedResults">
            <el-input v-model="form.expectedResults" type="textarea" :rows="4" placeholder="请输入预期结果" />
          </el-form-item>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getTestCase, addTestCase, updateTestCase } from '@/api/testing/testCase'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  caseId: {
    type: Number,
    default: null
  },
  projectId: {
    type: Number,
    required: true
  },
  folderId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const formRef = ref(null)
const activeTab = ref('basic')
const submitting = ref(false)
const tagOptions = ref(['冒烟测试', '回归测试', '核心功能', '边界测试', 'API测试', 'UI测试'])

const form = reactive({
  caseName: '',
  template: 'test_case',
  caseType: 'functional',
  priority: 'medium',
  description: '',
  preconditions: '',
  testData: '',
  expectedResults: '',
  testCaseSteps: [{ step_number: 1, action: '', expected: '' }],
  feature: '',
  scenario: '',
  background: '',
  givenSteps: [''],
  whenSteps: [''],
  thenSteps: [''],
  tags: []
})

const rules = {
  caseName: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { max: 200, message: '长度不能超过200个字符', trigger: 'blur' }
  ],
  caseType: [{ required: true, message: '请选择用例类型', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

// 加载测试用例
const loadTestCase = async () => {
  if (!props.caseId) return

  try {
    const res = await getTestCase(props.caseId)
    const data = res.data
    
    form.caseName = data.case_name
    form.template = data.template || 'test_case'
    form.caseType = data.case_type
    form.priority = data.priority
    form.description = data.description
    form.preconditions = data.preconditions
    form.testData = data.test_data
    form.expectedResults = data.expected_results
    form.testCaseSteps = data.test_case_steps || [{ step_number: 1, action: '', expected: '' }]
    form.feature = data.feature
    form.scenario = data.scenario
    form.background = data.background
    form.givenSteps = data.given_steps?.length ? data.given_steps : ['']
    form.whenSteps = data.when_steps?.length ? data.when_steps : ['']
    form.thenSteps = data.then_steps?.length ? data.then_steps : ['']
    form.tags = data.tags || []
  } catch (error) {
    console.error('加载测试用例失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  form.caseName = ''
  form.template = 'test_case'
  form.caseType = 'functional'
  form.priority = 'medium'
  form.description = ''
  form.preconditions = ''
  form.testData = ''
  form.expectedResults = ''
  form.testCaseSteps = [{ step_number: 1, action: '', expected: '' }]
  form.feature = ''
  form.scenario = ''
  form.background = ''
  form.givenSteps = ['']
  form.whenSteps = ['']
  form.thenSteps = ['']
  form.tags = []
  activeTab.value = 'basic'
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 添加步骤
const addStep = () => {
  form.testCaseSteps.push({
    step_number: form.testCaseSteps.length + 1,
    action: '',
    expected: ''
  })
}

// 移除步骤
const removeStep = (index) => {
  form.testCaseSteps.splice(index, 1)
  // 重新编号
  form.testCaseSteps.forEach((step, i) => {
    step.step_number = i + 1
  })
}

// 提交
const handleSubmit = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const data = {
      projectId: props.projectId,
      folderId: props.folderId,
      caseName: form.caseName,
      template: form.template,
      caseType: form.caseType,
      priority: form.priority,
      description: form.description,
      preconditions: form.preconditions,
      testData: form.testData,
      expectedResults: form.expectedResults,
      testCaseSteps: form.testCaseSteps.filter(s => s.action || s.expected),
      feature: form.feature,
      scenario: form.scenario,
      background: form.background,
      givenSteps: form.givenSteps.filter(s => s),
      whenSteps: form.whenSteps.filter(s => s),
      thenSteps: form.thenSteps.filter(s => s),
      tags: form.tags
    }

    if (props.caseId) {
      await updateTestCase(props.caseId, data)
      ElMessage.success('更新成功')
    } else {
      await addTestCase(data)
      ElMessage.success('创建成功')
    }

    visible.value = false
    emit('success')
  } catch (error) {
    ElMessage.error(error?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleOpen = () => {
  if (props.caseId) {
    loadTestCase()
  }
}

const handleClose = () => {
  resetForm()
}
</script>

<style scoped lang="scss">
.steps-container {
  .step-item {
    margin-bottom: 16px;
    padding: 12px;
    background: #f9f9f9;
    border-radius: 4px;

    .step-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;

      .step-number {
        font-weight: 600;
        color: #409eff;
      }
    }
  }
}

.bdd-steps {
  .bdd-step-item {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;

    .el-input {
      flex: 1;
    }
  }
}
</style>

