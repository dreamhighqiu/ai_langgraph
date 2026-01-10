<template>
  <div class="app-container dashboard">
    <el-card shadow="never" class="welcome-card" v-loading="loading">
      <div class="welcome">
        <div class="welcome-left">
          <div class="welcome-title">质量看板</div>
          <div class="welcome-subtitle">
            <span class="muted">欢迎回来，</span>{{ displayName }}
            <span class="muted">｜近</span>{{ days }}<span class="muted">天质量概览</span>
          </div>
        </div>
        <div class="welcome-right">
          <el-select v-model="days" size="small" style="width: 120px" @change="load">
            <el-option v-for="opt in dayOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-button size="small" type="primary" @click="load" :loading="loading">刷新</el-button>
        </div>
      </div>

      <el-row :gutter="12" class="kpi-row">
        <el-col :xs="12" :sm="8" :lg="4">
          <div class="kpi-card" @click="go('/testing/project')">
            <div class="kpi-label">项目</div>
            <div class="kpi-value">{{ kpi.projects }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :lg="4">
          <div class="kpi-card" @click="go('/testing/script')">
            <div class="kpi-label">脚本</div>
            <div class="kpi-value">{{ kpi.scripts }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :lg="4">
          <div class="kpi-card" @click="go('/testing/test-case')">
            <div class="kpi-label">用例</div>
            <div class="kpi-value">{{ kpi.test_cases }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :lg="4">
          <div class="kpi-card" @click="go('/testing/requirement')">
            <div class="kpi-label">需求</div>
            <div class="kpi-value">{{ kpi.requirements }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :lg="4">
          <div class="kpi-card danger" @click="go('/testing/bug-report')">
            <div class="kpi-label">未关闭缺陷</div>
            <div class="kpi-value">{{ kpi.bugs_open }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :lg="4">
          <div class="kpi-card">
            <div class="kpi-label">执行成功率</div>
            <div class="kpi-value">
              {{ kpi.executions.success_rate }}<span class="kpi-unit">%</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <div class="kpi-footer">
        <div class="kpi-footer-item">
          <span class="muted">近{{ days }}天执行</span>
          <span class="strong">{{ kpi.executions.total }}</span>
        </div>
        <div class="kpi-footer-item">
          <span class="muted">成功</span>
          <span class="strong success">{{ kpi.executions.success }}</span>
        </div>
        <div class="kpi-footer-item">
          <span class="muted">失败</span>
          <span class="strong danger">{{ kpi.executions.failed }}</span>
        </div>
        <div class="kpi-footer-item">
          <span class="muted">运行中</span>
          <span class="strong warn">{{ kpi.executions.running }}</span>
        </div>
      </div>
    </el-card>

    <el-row :gutter="12" class="mt-3">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>执行趋势</span>
              <span class="muted">近{{ days }}天</span>
            </div>
          </template>
          <div ref="trendRef" class="chart" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>缺陷状态</span>
              <span class="muted">全量统计</span>
            </div>
          </template>
          <div ref="bugRef" class="chart" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" class="mt-3">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>最近执行</span>
              <el-button link type="primary" @click="go('/testing/execution')">进入执行监控</el-button>
            </div>
          </template>
          <el-table :data="recentExecutions" size="small" style="width: 100%">
            <el-table-column label="时间" min-width="160">
              <template #default="{ row }">
                <span>{{ formatTime(row.create_time) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="project_name" label="项目" min-width="140" show-overflow-tooltip />
            <el-table-column prop="script_name" label="脚本" min-width="180" show-overflow-tooltip />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.execution_status)" effect="light">
                  {{ statusText(row.execution_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="耗时" width="90" align="right">
              <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
            </el-table-column>
          </el-table>
          <div v-if="!recentExecutions.length && !loading" class="empty-hint">暂无执行记录</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>快捷入口</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button @click="go('/testing/project')" plain>项目管理</el-button>
            <el-button @click="go('/testing/test-case')" plain>用例管理</el-button>
            <el-button @click="go('/testing/script')" plain>脚本中心</el-button>
            <el-button @click="go('/testing/execution')" type="primary">执行监控</el-button>
            <el-button @click="go('/testing/report')" plain>测试报告</el-button>
            <el-button @click="go('/testing/bug-report')" plain>缺陷管理</el-button>
          </div>
          <div class="health">
            <div class="health-title">稳定性</div>
            <el-progress :percentage="kpi.executions.success_rate || 0" :stroke-width="10" :show-text="false" />
            <div class="health-metrics">
              <div class="health-metric">
                <div class="muted">成功</div>
                <div class="strong success">{{ kpi.executions.success }}</div>
              </div>
              <div class="health-metric">
                <div class="muted">失败</div>
                <div class="strong danger">{{ kpi.executions.failed }}</div>
              </div>
              <div class="health-metric">
                <div class="muted">运行中</div>
                <div class="strong warn">{{ kpi.executions.running }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup name="DashBoard">
import * as echarts from 'echarts'
import { getDashboardSummary } from '@/api/testing/dashboard'
import useUserStore from '@/store/modules/user'

const router = useRouter()
const { proxy } = getCurrentInstance()
const userStore = useUserStore()

const loading = ref(false)
const days = ref(7)
const dayOptions = [
  { label: '近7天', value: 7 },
  { label: '近14天', value: 14 },
  { label: '近30天', value: 30 }
]

const kpi = reactive({
  projects: 0,
  scripts: 0,
  test_cases: 0,
  requirements: 0,
  bugs_open: 0,
  executions: {
    total: 0,
    success: 0,
    failed: 0,
    running: 0,
    success_rate: 0
  }
})

const executionTrend = ref([])
const bugStatus = ref({})
const recentExecutions = ref([])

const trendRef = ref(null)
const bugRef = ref(null)
let trendChart
let bugChart

const displayName = computed(() => userStore.nickName || userStore.name || '用户')

function go(path) {
  router.push(path)
}

function formatTime(val) {
  if (!val) return '-'
  return proxy?.parseTime ? proxy.parseTime(val, '{y}-{m}-{d} {h}:{i}') : String(val)
}

function formatDuration(seconds) {
  if (seconds === undefined || seconds === null || seconds === '') return '-'
  const s = Number(seconds)
  if (Number.isNaN(s)) return '-'
  if (s < 60) return `${Math.round(s)}s`
  const m = Math.floor(s / 60)
  const r = Math.round(s % 60)
  return `${m}m ${r}s`
}

function statusText(status) {
  const map = {
    pending: '待执行',
    running: '运行中',
    success: '成功',
    failed: '失败',
    cancelled: '已取消'
  }
  return map[status] || status || '-'
}

function statusTagType(status) {
  if (status === 'success') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'running') return 'warning'
  if (status === 'pending') return 'info'
  return 'info'
}

async function load() {
  loading.value = true
  try {
    const res = await getDashboardSummary(days.value)
    const data = res?.data || {}

    const nextKpi = data.kpi || {}
    kpi.projects = Number(nextKpi.projects || 0)
    kpi.scripts = Number(nextKpi.scripts || 0)
    kpi.test_cases = Number(nextKpi.test_cases || 0)
    kpi.requirements = Number(nextKpi.requirements || 0)
    kpi.bugs_open = Number(nextKpi.bugs_open || 0)

    const exec = nextKpi.executions || {}
    kpi.executions.total = Number(exec.total || 0)
    kpi.executions.success = Number(exec.success || 0)
    kpi.executions.failed = Number(exec.failed || 0)
    kpi.executions.running = Number(exec.running || 0)
    kpi.executions.success_rate = Number(exec.success_rate || 0)

    executionTrend.value = Array.isArray(data.execution_trend) ? data.execution_trend : []
    bugStatus.value = data.bug_status || {}
    recentExecutions.value = Array.isArray(data.recent_executions) ? data.recent_executions : []

    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  if (trendRef.value) {
    if (!trendChart) trendChart = echarts.init(trendRef.value)
    const x = executionTrend.value.map((i) => i.date)
    const success = executionTrend.value.map((i) => Number(i.success || 0))
    const failed = executionTrend.value.map((i) => Number(i.failed || 0))
    const total = executionTrend.value.map((i) => Number(i.total || 0))
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 20, top: 30, bottom: 30 },
      legend: { data: ['成功', '失败', '总执行'] },
      xAxis: { type: 'category', data: x, axisTick: { show: false } },
      yAxis: { type: 'value' },
      series: [
        { name: '成功', type: 'bar', stack: 'run', data: success, barMaxWidth: 18, itemStyle: { color: '#16a34a' } },
        { name: '失败', type: 'bar', stack: 'run', data: failed, barMaxWidth: 18, itemStyle: { color: '#ef4444' } },
        { name: '总执行', type: 'line', data: total, smooth: true, itemStyle: { color: '#3b82f6' } }
      ]
    })
  }

  if (bugRef.value) {
    if (!bugChart) bugChart = echarts.init(bugRef.value)
    const entries = Object.entries(bugStatus.value || {})
      .map(([name, value]) => ({ name, value: Number(value || 0) }))
      .filter((i) => i.value > 0)

    bugChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          label: { show: entries.length > 0, formatter: '{b}: {c}' },
          emphasis: { label: { show: true, fontWeight: 'bold' } },
          data: entries.length ? entries : [{ name: '暂无数据', value: 0 }]
        }
      ]
    })
  }

  window.addEventListener('resize', handleResize, { passive: true })
}

function handleResize() {
  trendChart?.resize?.()
  bugChart?.resize?.()
}

onMounted(() => {
  load()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose?.()
  bugChart?.dispose?.()
})
</script>

<style scoped lang="scss">
.dashboard {
  .welcome-card {
    border-radius: 10px;
  }

  .welcome {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
  }

  .welcome-title {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: 0.2px;
  }

  .welcome-subtitle {
    margin-top: 6px;
    font-size: 13px;
    color: #334155;
  }

  .muted {
    color: #64748b;
  }

  .strong {
    font-weight: 700;
    color: #0f172a;
  }

  .success {
    color: #16a34a;
  }

  .danger {
    color: #ef4444;
  }

  .warn {
    color: #f59e0b;
  }

  .kpi-row {
    margin-top: 6px;
  }

  .kpi-card {
    cursor: pointer;
    user-select: none;
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
    transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;

    &:hover {
      transform: translateY(-1px);
      border-color: #c7d2fe;
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
    }

    &.danger {
      border-color: #fecaca;
    }
  }

  .kpi-label {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 6px;
  }

  .kpi-value {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
  }

  .kpi-unit {
    font-size: 12px;
    margin-left: 2px;
    color: #64748b;
    font-weight: 600;
  }

  .kpi-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px dashed #e2e8f0;
  }

  .kpi-footer-item {
    display: flex;
    gap: 8px;
    align-items: baseline;
    font-size: 12px;
  }

  .chart-card {
    border-radius: 10px;
  }

  .chart {
    height: 320px;
    width: 100%;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    font-weight: 600;
  }

  .quick-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .health {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px dashed #e2e8f0;
  }

  .health-title {
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 10px;
  }

  .health-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 10px;
  }

  .health-metric {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px;
    background: #fff;
  }

  .empty-hint {
    padding: 12px 0 6px;
    color: #94a3b8;
    font-size: 12px;
    text-align: center;
  }
}
</style>

