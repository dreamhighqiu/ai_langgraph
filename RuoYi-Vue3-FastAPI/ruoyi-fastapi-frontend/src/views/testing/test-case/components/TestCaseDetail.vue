<template>
  <el-drawer
    v-model="visible"
    title="测试用例详情"
    size="50%"
    :destroy-on-close="true"
    @open="loadDetail"
  >
    <div v-loading="loading" class="detail-container">
      <template v-if="testCase">
        <!-- 头部信息 -->
        <div class="detail-header">
          <div class="case-title">
            <el-tag type="info" size="small">{{ testCase.caseIdentifier }}</el-tag>
            <h3>{{ testCase.caseName }}</h3>
          </div>
          <div class="case-meta">
            <el-tag :type="getPriorityType(testCase.priority)">{{ getPriorityLabel(testCase.priority) }}</el-tag>
            <el-tag :type="getStatusType(testCase.status)">{{ getStatusLabel(testCase.status) }}</el-tag>
            <el-tag>{{ testCase.template === 'test_case_bdd' ? 'BDD' : '普通' }}</el-tag>
          </div>
        </div>

        <el-divider />

        <!-- 基本信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例类型">{{ getCaseTypeLabel(testCase.caseType) }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ testCase.createBy }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ testCase.createTime }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ testCase.updateTime }}</el-descriptions-item>
        </el-descriptions>

        <!-- 描述 -->
        <div class="section" v-if="testCase.description">
          <h4>描述</h4>
          <p>{{ testCase.description }}</p>
        </div>

        <!-- 前置条件 -->
        <div class="section" v-if="testCase.preconditions">
          <h4>前置条件</h4>
          <p>{{ testCase.preconditions }}</p>
        </div>

        <!-- 普通用例步骤 -->
        <div class="section" v-if="testCase.template === 'test_case' && testCase.testCaseSteps?.length">
          <h4>测试步骤</h4>
          <el-table :data="testCase.testCaseSteps" border>
            <el-table-column label="步骤" prop="step_number" width="60" align="center" />
            <el-table-column label="操作描述" prop="action" />
            <el-table-column label="预期结果" prop="expected" />
          </el-table>
        </div>

        <!-- BDD 用例 -->
        <template v-if="testCase.template === 'test_case_bdd'">
          <div class="section" v-if="testCase.feature">
            <h4>Feature</h4>
            <pre class="bdd-content">{{ testCase.feature }}</pre>
          </div>
          <div class="section" v-if="testCase.scenario">
            <h4>Scenario</h4>
            <pre class="bdd-content">{{ testCase.scenario }}</pre>
          </div>
          <div class="section" v-if="testCase.background">
            <h4>Background</h4>
            <pre class="bdd-content">{{ testCase.background }}</pre>
          </div>
          <div class="section" v-if="testCase.givenSteps?.length">
            <h4>Given</h4>
            <ul class="bdd-list">
              <li v-for="(step, i) in testCase.givenSteps" :key="i">{{ step }}</li>
            </ul>
          </div>
          <div class="section" v-if="testCase.whenSteps?.length">
            <h4>When</h4>
            <ul class="bdd-list">
              <li v-for="(step, i) in testCase.whenSteps" :key="i">{{ step }}</li>
            </ul>
          </div>
          <div class="section" v-if="testCase.thenSteps?.length">
            <h4>Then</h4>
            <ul class="bdd-list">
              <li v-for="(step, i) in testCase.thenSteps" :key="i">{{ step }}</li>
            </ul>
          </div>
        </template>

        <!-- 测试数据 -->
        <div class="section" v-if="testCase.testData">
          <h4>测试数据</h4>
          <pre class="data-content">{{ testCase.testData }}</pre>
        </div>

        <!-- 预期结果 -->
        <div class="section" v-if="testCase.expectedResults">
          <h4>预期结果</h4>
          <p>{{ testCase.expectedResults }}</p>
        </div>

        <!-- 标签 -->
        <div class="section" v-if="testCase.tags?.length">
          <h4>标签</h4>
          <div class="tags">
            <el-tag v-for="tag in testCase.tags" :key="tag" size="small">{{ tag }}</el-tag>
          </div>
        </div>
      </template>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getTestCase } from '@/api/testing/testCase'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  caseId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const testCase = ref(null)

const loadDetail = async () => {
  if (!props.caseId) return

  loading.value = true
  try {
    const res = await getTestCase(props.caseId)
    const data = res.data
    testCase.value = {
      caseId: data.case_id,
      caseIdentifier: data.case_identifier,
      caseName: data.case_name,
      caseType: data.case_type,
      template: data.template,
      priority: data.priority,
      status: data.status,
      description: data.description,
      preconditions: data.preconditions,
      testData: data.test_data,
      expectedResults: data.expected_results,
      testCaseSteps: data.test_case_steps,
      feature: data.feature,
      scenario: data.scenario,
      background: data.background,
      givenSteps: data.given_steps,
      whenSteps: data.when_steps,
      thenSteps: data.then_steps,
      tags: data.tags,
      createBy: data.create_by,
      createTime: data.create_time,
      updateTime: data.update_time
    }
  } catch (error) {
    console.error('加载详情失败:', error)
  } finally {
    loading.value = false
  }
}

const getPriorityType = (priority) => {
  const map = { critical: 'danger', high: 'warning', medium: '', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const map = { critical: '紧急', high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

const getStatusType = (status) => {
  const map = { draft: 'info', active: 'success', deprecated: 'danger' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { draft: '草稿', active: '激活', deprecated: '废弃' }
  return map[status] || status
}

const getCaseTypeLabel = (type) => {
  const map = {
    functional: '功能测试',
    regression: '回归测试',
    smoke: '冒烟测试',
    performance: '性能测试',
    security: '安全测试'
  }
  return map[type] || type
}
</script>

<style scoped lang="scss">
.detail-container {
  padding: 0 20px;

  .detail-header {
    .case-title {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      h3 {
        margin: 0;
        font-size: 18px;
      }
    }

    .case-meta {
      display: flex;
      gap: 8px;
    }
  }

  .section {
    margin: 20px 0;

    h4 {
      margin: 0 0 12px;
      color: #303133;
      font-size: 14px;
      font-weight: 600;
    }

    p {
      margin: 0;
      color: #606266;
      line-height: 1.6;
    }
  }

  .bdd-content {
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    margin: 0;
    white-space: pre-wrap;
    font-family: inherit;
    line-height: 1.6;
  }

  .bdd-list {
    margin: 0;
    padding-left: 20px;

    li {
      margin: 6px 0;
      color: #606266;
    }
  }

  .data-content {
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    margin: 0;
    white-space: pre-wrap;
    font-family: monospace;
    font-size: 13px;
    max-height: 200px;
    overflow: auto;
  }

  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>

