<template>
  <div class="k6-config-panel">
    <el-form ref="configForm" :model="config" label-width="120px">
      <el-divider content-position="left">
        <el-icon><Odometer /></el-icon>
        虚拟用户配置
      </el-divider>
      
      <el-form-item label="虚拟用户数" prop="vus">
        <el-input-number 
          v-model="config.vus" 
          :min="1" 
          :max="10000"
          placeholder="同时运行的虚拟用户数量"
        />
        <span class="tip">推荐: 10-100（小型）, 100-1000（中型）, 1000+（大型）</span>
      </el-form-item>

      <el-form-item label="测试时长" prop="duration">
        <el-input 
          v-model="config.duration" 
          placeholder="例如: 30s, 5m, 1h"
          style="width: 200px"
        />
        <span class="tip">格式: 数字+单位（s秒/m分/h时）</span>
      </el-form-item>

      <el-divider content-position="left">
        <el-icon><TrendCharts /></el-icon>
        压力阶段配置（可选）
      </el-divider>

      <el-form-item label="启用压力阶段">
        <el-switch v-model="enableStages" @change="toggleStages" />
        <span class="tip">阶梯式增加/减少负载</span>
      </el-form-item>

      <template v-if="enableStages">
        <el-form-item 
          v-for="(stage, index) in config.stages" 
          :key="index"
          :label="`阶段 ${index + 1}`"
        >
          <el-row :gutter="10">
            <el-col :span="8">
              <el-input 
                v-model="stage.duration" 
                placeholder="时长(如30s)"
              >
                <template #prepend>时长</template>
              </el-input>
            </el-col>
            <el-col :span="8">
              <el-input-number 
                v-model="stage.target" 
                :min="0" 
                :max="10000"
                placeholder="目标VUS"
              >
                <template #prepend>VUS</template>
              </el-input-number>
            </el-col>
            <el-col :span="8">
              <el-button 
                type="danger" 
                icon="Delete" 
                @click="removeStage(index)"
                :disabled="config.stages.length === 1"
              />
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" plain icon="Plus" @click="addStage">
            添加阶段
          </el-button>
        </el-form-item>
      </template>

      <el-divider content-position="left">
        <el-icon><CircleCheck /></el-icon>
        性能阈值配置
      </el-divider>

      <el-form-item label="响应时间阈值">
        <el-select 
          v-model="config.thresholds.http_req_duration" 
          multiple 
          placeholder="选择或输入阈值"
          allow-create
          filterable
          default-first-option
          style="width: 100%"
        >
          <el-option label="p(95) < 500ms" value="p(95)<500" />
          <el-option label="p(99) < 1000ms" value="p(99)<1000" />
          <el-option label="p(90) < 300ms" value="p(90)<300" />
          <el-option label="平均 < 200ms" value="avg<200" />
        </el-select>
        <span class="tip">p(95)表示95%的请求响应时间</span>
      </el-form-item>

      <el-form-item label="错误率阈值">
        <el-select 
          v-model="config.thresholds.http_req_failed" 
          multiple 
          placeholder="选择或输入阈值"
          allow-create
          filterable
          default-first-option
          style="width: 100%"
        >
          <el-option label="错误率 < 1%" value="rate<0.01" />
          <el-option label="错误率 < 5%" value="rate<0.05" />
          <el-option label="错误率 < 0.1%" value="rate<0.001" />
        </el-select>
        <span class="tip">HTTP请求失败率阈值</span>
      </el-form-item>

      <el-divider content-position="left">
        <el-icon><Setting /></el-icon>
        高级选项
      </el-divider>

      <el-form-item label="使用RAG知识库">
        <el-switch v-model="config.use_rag" />
        <span class="tip">利用历史测试经验优化脚本</span>
      </el-form-item>

      <el-form-item label="环境变量">
        <el-button type="text" icon="Plus" @click="showEnvDialog = true">
          配置环境变量
        </el-button>
      </el-form-item>
    </el-form>

    <!-- 环境变量对话框 -->
    <el-dialog v-model="showEnvDialog" title="环境变量配置" width="600px">
      <el-form>
        <el-form-item 
          v-for="(value, key, index) in config.env_vars" 
          :key="index"
          :label="key"
        >
          <el-input v-model="config.env_vars[key]" style="width: 80%">
            <template #append>
              <el-button icon="Delete" @click="deleteEnv(key)" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-row :gutter="10">
            <el-col :span="10">
              <el-input v-model="newEnvKey" placeholder="变量名" />
            </el-col>
            <el-col :span="10">
              <el-input v-model="newEnvValue" placeholder="变量值" />
            </el-col>
            <el-col :span="4">
              <el-button type="primary" icon="Plus" @click="addEnv" />
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEnvDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

// 配置数据
const config = reactive({
  vus: 10,
  duration: '30s',
  use_rag: false,
  stages: [
    { duration: '10s', target: 10 },
    { duration: '30s', target: 100 },
    { duration: '10s', target: 0 }
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01']
  },
  env_vars: {},
  ...props.modelValue
})

const enableStages = ref(true)
const showEnvDialog = ref(false)
const newEnvKey = ref('')
const newEnvValue = ref('')

// 监听配置变化
watch(() => config, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

// 切换压力阶段
const toggleStages = (val) => {
  if (!val) {
    config.stages = []
  } else {
    config.stages = [
      { duration: '10s', target: 10 },
      { duration: '30s', target: 100 },
      { duration: '10s', target: 0 }
    ]
  }
}

// 添加压力阶段
const addStage = () => {
  config.stages.push({
    duration: '30s',
    target: config.vus
  })
}

// 删除压力阶段
const removeStage = (index) => {
  config.stages.splice(index, 1)
}

// 添加环境变量
const addEnv = () => {
  if (newEnvKey.value && newEnvValue.value) {
    config.env_vars[newEnvKey.value] = newEnvValue.value
    newEnvKey.value = ''
    newEnvValue.value = ''
  }
}

// 删除环境变量
const deleteEnv = (key) => {
  delete config.env_vars[key]
}

// 暴露方法
defineExpose({
  getConfig: () => config
})
</script>

<style scoped lang="scss">
.k6-config-panel {
  padding: 20px;
  
  .tip {
    margin-left: 10px;
    font-size: 12px;
    color: #909399;
  }

  .el-divider {
    margin: 30px 0 20px 0;
    
    .el-icon {
      margin-right: 5px;
    }
  }

  :deep(.el-input-number) {
    width: 200px;
  }
}
</style>

