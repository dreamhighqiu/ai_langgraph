<template>
  <div class="playwright-config-panel">
    <el-form ref="configForm" :model="config" label-width="120px">
      <el-divider content-position="left">
        <el-icon><Monitor /></el-icon>
        浏览器配置
      </el-divider>
      
      <el-form-item label="浏览器类型" prop="browser">
        <el-radio-group v-model="config.browser">
          <el-radio label="chromium">
            <el-icon><ChromeFilled /></el-icon>
            Chromium
          </el-radio>
          <el-radio label="firefox">
            <el-icon><FireFilled /></el-icon>
            Firefox
          </el-radio>
          <el-radio label="webkit">
            <el-icon><Apple /></el-icon>
            WebKit (Safari)
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="运行模式" prop="headless">
        <el-switch 
          v-model="config.headless"
          active-text="无头模式（后台运行）"
          inactive-text="有头模式（显示浏览器）"
        />
        <span class="tip">无头模式更快，有头模式便于调试</span>
      </el-form-item>

      <el-form-item label="视口尺寸">
        <el-row :gutter="10">
          <el-col :span="10">
            <el-input-number 
              v-model="config.viewport.width" 
              :min="320" 
              :max="3840"
              controls-position="right"
            >
              <template #prepend>宽</template>
            </el-input-number>
          </el-col>
          <el-col :span="2" style="text-align: center">×</el-col>
          <el-col :span="10">
            <el-input-number 
              v-model="config.viewport.height" 
              :min="240" 
              :max="2160"
              controls-position="right"
            >
              <template #prepend>高</template>
            </el-input-number>
          </el-col>
        </el-row>
        <div class="preset-viewports">
          <el-button 
            v-for="preset in viewportPresets" 
            :key="preset.name"
            type="text" 
            size="small"
            @click="setViewport(preset)"
          >
            {{ preset.name }}
          </el-button>
        </div>
      </el-form-item>

      <el-divider content-position="left">
        <el-icon><Camera /></el-icon>
        截图与录屏
      </el-divider>

      <el-form-item label="失败时截图">
        <el-switch v-model="config.screenshot" />
        <span class="tip">测试失败时自动截图</span>
      </el-form-item>

      <el-form-item label="录制视频">
        <el-switch v-model="config.video" />
        <span class="tip">完整录制测试过程（会增加执行时间）</span>
      </el-form-item>

      <el-form-item v-if="config.video" label="视频质量">
        <el-radio-group v-model="config.video_quality">
          <el-radio label="low">低（快速）</el-radio>
          <el-radio label="medium">中（推荐）</el-radio>
          <el-radio label="high">高（详细）</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-divider content-position="left">
        <el-icon><Clock /></el-icon>
        执行选项
      </el-divider>

      <el-form-item label="操作超时">
        <el-input-number 
          v-model="config.timeout" 
          :min="1000" 
          :max="300000"
          :step="1000"
          controls-position="right"
        />
        <span class="tip">毫秒（推荐: 30000）</span>
      </el-form-item>

      <el-form-item label="减慢执行速度">
        <el-slider 
          v-model="config.slow_mo" 
          :min="0" 
          :max="5000" 
          :step="100"
          show-input
          :marks="slowMoMarks"
        />
        <span class="tip">每个操作延迟毫秒数，便于观察（调试时使用）</span>
      </el-form-item>

      <el-divider content-position="left">
        <el-icon><DocumentAdd /></el-icon>
        测试数据与页面对象
      </el-divider>

      <el-form-item label="页面对象模式">
        <el-switch v-model="config.use_page_objects" />
        <span class="tip">使用页面对象模式组织测试代码（推荐）</span>
      </el-form-item>

      <el-form-item label="测试数据源">
        <el-select 
          v-model="config.data_source" 
          placeholder="选择测试数据来源"
          style="width: 300px"
        >
          <el-option label="无（硬编码）" value="none" />
          <el-option label="CSV文件" value="csv" />
          <el-option label="JSON文件" value="json" />
          <el-option label="数据库" value="database" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="config.data_source !== 'none'" label="数据文件路径">
        <el-input 
          v-model="config.data_file" 
          placeholder="例如: ./test-data/users.csv"
        />
      </el-form-item>

      <el-divider content-position="left">
        <el-icon><Setting /></el-icon>
        高级选项
      </el-divider>

      <el-form-item label="使用RAG知识库">
        <el-switch v-model="config.use_rag" />
        <span class="tip">利用历史测试经验优化脚本</span>
      </el-form-item>

      <el-form-item label="并发执行">
        <el-switch v-model="config.parallel" />
        <el-input-number 
          v-if="config.parallel"
          v-model="config.workers" 
          :min="1" 
          :max="10"
          style="margin-left: 10px"
        />
        <span class="tip" v-if="config.parallel">并发Worker数量</span>
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
      </el-template>
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
  browser: 'chromium',
  headless: true,
  viewport: { width: 1280, height: 720 },
  screenshot: true,
  video: false,
  video_quality: 'medium',
  timeout: 30000,
  slow_mo: 0,
  use_page_objects: true,
  data_source: 'none',
  data_file: '',
  use_rag: false,
  parallel: false,
  workers: 1,
  env_vars: {},
  ...props.modelValue
})

// 视口预设
const viewportPresets = [
  { name: '桌面 FHD', width: 1920, height: 1080 },
  { name: '桌面 HD', width: 1280, height: 720 },
  { name: '平板', width: 768, height: 1024 },
  { name: 'iPhone 14', width: 390, height: 844 },
  { name: 'Android', width: 360, height: 640 }
]

// 慢速执行标记
const slowMoMarks = {
  0: '正常',
  1000: '1秒',
  2000: '2秒',
  3000: '3秒',
  5000: '5秒'
}

const showEnvDialog = ref(false)
const newEnvKey = ref('')
const newEnvValue = ref('')

// 监听配置变化
watch(() => config, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

// 设置视口
const setViewport = (preset) => {
  config.viewport.width = preset.width
  config.viewport.height = preset.height
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
.playwright-config-panel {
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

  .preset-viewports {
    margin-top: 10px;
    .el-button {
      margin-right: 5px;
    }
  }

  :deep(.el-input-number) {
    width: 150px;
  }

  .el-radio {
    margin-right: 20px;
  }
}
</style>

