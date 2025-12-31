<template>
  <div class="restapi-config-panel">
    <el-form ref="configForm" :model="config" label-width="120px">
      <el-divider content-position="left">
        <el-icon><Link /></el-icon>
        API基础配置
      </el-divider>
      
      <el-form-item label="Base URL" prop="base_url">
        <el-input 
          v-model="config.base_url" 
          placeholder="https://api.example.com"
          style="width: 100%"
        >
          <template #prepend>
            <el-icon><Link /></el-icon>
          </template>
        </el-input>
        <span class="tip">所有API请求的基础URL</span>
      </el-form-item>

      <el-form-item label="请求超时">
        <el-input-number 
          v-model="config.timeout" 
          :min="1000" 
          :max="300000"
          :step="1000"
          controls-position="right"
        />
        <span class="tip">毫秒（推荐: 10000）</span>
      </el-form-item>

      <el-form-item label="重试次数">
        <el-input-number 
          v-model="config.retry" 
          :min="0" 
          :max="10"
          controls-position="right"
        />
        <span class="tip">失败后自动重试次数</span>
      </el-form-item>

      <el-divider content-position="left">
        <el-icon><Lock /></el-icon>
        认证配置
      </el-divider>

      <el-form-item label="认证类型" prop="auth_type">
        <el-radio-group v-model="config.auth_type">
          <el-radio label="none">无认证</el-radio>
          <el-radio label="bearer">Bearer Token</el-radio>
          <el-radio label="basic">Basic Auth</el-radio>
          <el-radio label="api_key">API Key</el-radio>
          <el-radio label="oauth2">OAuth 2.0</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- Bearer Token -->
      <template v-if="config.auth_type === 'bearer'">
        <el-form-item label="Token">
          <el-input 
            v-model="config.auth_config.token" 
            type="textarea"
            :rows="3"
            placeholder="输入Bearer Token"
            show-password
          />
        </el-form-item>
      </template>

      <!-- Basic Auth -->
      <template v-if="config.auth_type === 'basic'">
        <el-form-item label="用户名">
          <el-input v-model="config.auth_config.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input 
            v-model="config.auth_config.password" 
            type="password"
            show-password
          />
        </el-form-item>
      </template>

      <!-- API Key -->
      <template v-if="config.auth_type === 'api_key'">
        <el-form-item label="Key名称">
          <el-input 
            v-model="config.auth_config.key_name" 
            placeholder="例如: X-API-Key"
          />
        </el-form-item>
        <el-form-item label="Key值">
          <el-input 
            v-model="config.auth_config.key_value" 
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="传递方式">
          <el-radio-group v-model="config.auth_config.in">
            <el-radio label="header">Header</el-radio>
            <el-radio label="query">Query参数</el-radio>
          </el-radio-group>
        </el-form-item>
      </template>

      <!-- OAuth 2.0 -->
      <template v-if="config.auth_type === 'oauth2'">
        <el-form-item label="Token URL">
          <el-input v-model="config.auth_config.token_url" />
        </el-form-item>
        <el-form-item label="Client ID">
          <el-input v-model="config.auth_config.client_id" />
        </el-form-item>
        <el-form-item label="Client Secret">
          <el-input 
            v-model="config.auth_config.client_secret" 
            type="password"
            show-password
          />
        </el-form-item>
      </template>

      <el-divider content-position="left">
        <el-icon><Document /></el-icon>
        请求Headers
      </el-divider>

      <el-form-item label="默认Headers">
        <el-button type="text" icon="Plus" @click="showHeadersDialog = true">
          配置Headers
        </el-button>
        <el-tag 
          v-for="(value, key) in config.headers" 
          :key="key"
          closable
          @close="deleteHeader(key)"
          style="margin: 5px"
        >
          {{ key }}: {{ value }}
        </el-tag>
      </el-form-item>

      <el-divider content-position="left">
        <el-icon><CircleCheck /></el-icon>
        断言配置
      </el-divider>

      <el-form-item label="启用断言">
        <el-switch v-model="enableAssertions" />
        <span class="tip">自动验证响应结果</span>
      </el-form-item>

      <template v-if="enableAssertions">
        <el-card 
          v-for="(assertion, index) in config.assertions" 
          :key="index"
          class="assertion-card"
        >
          <template #header>
            <div class="card-header">
              <span>断言 {{ index + 1 }}</span>
              <el-button 
                type="danger" 
                text 
                icon="Delete" 
                @click="removeAssertion(index)"
              />
            </div>
          </template>
          <el-form-item label="断言类型">
            <el-select v-model="assertion.type" placeholder="选择断言类型">
              <el-option label="状态码" value="status_code" />
              <el-option label="响应时间" value="response_time" />
              <el-option label="JSON路径" value="json_path" />
              <el-option label="响应体包含" value="body_contains" />
              <el-option label="Header存在" value="header_exists" />
              <el-option label="响应大小" value="response_size" />
            </el-select>
          </el-form-item>

          <!-- 状态码断言 -->
          <template v-if="assertion.type === 'status_code'">
            <el-form-item label="期望状态码">
              <el-input-number v-model="assertion.expected" :min="100" :max="599" />
            </el-form-item>
          </template>

          <!-- 响应时间断言 -->
          <template v-if="assertion.type === 'response_time'">
            <el-form-item label="比较运算符">
              <el-select v-model="assertion.operator">
                <el-option label="小于 <" value="<" />
                <el-option label="小于等于 <=" value="<=" />
                <el-option label="大于 >" value=">" />
                <el-option label="大于等于 >=" value=">=" />
                <el-option label="等于 ==" value="==" />
              </el-select>
            </el-form-item>
            <el-form-item label="期望值(ms)">
              <el-input-number v-model="assertion.value" :min="0" />
            </el-form-item>
          </template>

          <!-- JSON路径断言 -->
          <template v-if="assertion.type === 'json_path'">
            <el-form-item label="JSON路径">
              <el-input 
                v-model="assertion.path" 
                placeholder="例如: $.data.user.name"
              />
            </el-form-item>
            <el-form-item label="期望值">
              <el-input v-model="assertion.expected" />
            </el-form-item>
          </template>

          <!-- 响应体包含断言 -->
          <template v-if="assertion.type === 'body_contains'">
            <el-form-item label="期望内容">
              <el-input v-model="assertion.text" placeholder="响应体应包含的文本" />
            </el-form-item>
          </template>

          <!-- Header存在断言 -->
          <template v-if="assertion.type === 'header_exists'">
            <el-form-item label="Header名称">
              <el-input v-model="assertion.header_name" />
            </el-form-item>
          </template>

          <!-- 响应大小断言 -->
          <template v-if="assertion.type === 'response_size'">
            <el-form-item label="比较运算符">
              <el-select v-model="assertion.operator">
                <el-option label="小于 <" value="<" />
                <el-option label="大于 >" value=">" />
              </el-select>
            </el-form-item>
            <el-form-item label="大小(bytes)">
              <el-input-number v-model="assertion.value" :min="0" />
            </el-form-item>
          </template>
        </el-card>

        <el-form-item>
          <el-button type="primary" plain icon="Plus" @click="addAssertion">
            添加断言
          </el-button>
        </el-form-item>
      </template>

      <el-divider content-position="left">
        <el-icon><Setting /></el-icon>
        高级选项
      </el-divider>

      <el-form-item label="使用RAG知识库">
        <el-switch v-model="config.use_rag" />
        <span class="tip">利用历史测试经验优化脚本</span>
      </el-form-item>

      <el-form-item label="并行执行">
        <el-switch v-model="config.parallel" />
        <span class="tip">并行执行多个API测试用例（提升速度）</span>
      </el-form-item>

      <el-form-item label="导入源">
        <el-select 
          v-model="importSource" 
          placeholder="支持从Swagger/Postman导入"
          @change="handleImportSource"
        >
          <el-option label="无" value="none" />
          <el-option label="Swagger/OpenAPI URL" value="swagger" />
          <el-option label="Postman Collection" value="postman" />
        </el-select>
      </el-form-item>

      <el-form-item label="环境变量">
        <el-button type="text" icon="Plus" @click="showEnvDialog = true">
          配置环境变量
        </el-button>
      </el-form-item>
    </el-form>

    <!-- Headers对话框 -->
    <el-dialog v-model="showHeadersDialog" title="配置默认Headers" width="600px">
      <el-form>
        <el-form-item 
          v-for="(value, key, index) in config.headers" 
          :key="index"
          :label="key"
        >
          <el-input v-model="config.headers[key]" style="width: 80%">
            <template #append>
              <el-button icon="Delete" @click="deleteHeader(key)" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-row :gutter="10">
            <el-col :span="10">
              <el-input v-model="newHeaderKey" placeholder="Header名称" />
            </el-col>
            <el-col :span="10">
              <el-input v-model="newHeaderValue" placeholder="Header值" />
            </el-col>
            <el-col :span="4">
              <el-button type="primary" icon="Plus" @click="addHeader" />
            </el-col>
          </el-row>
        </el-form-item>
        <el-divider />
        <div class="header-presets">
          <el-button 
            v-for="preset in headerPresets" 
            :key="preset.key"
            type="text" 
            size="small"
            @click="addPresetHeader(preset)"
          >
            + {{ preset.key }}
          </el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showHeadersDialog = false">关闭</el-button>
      </template>
    </el-dialog>

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
  base_url: '',
  auth_type: 'none',
  auth_config: {},
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000,
  retry: 3,
  use_rag: false,
  parallel: false,
  assertions: [
    { type: 'status_code', expected: 200 },
    { type: 'response_time', operator: '<', value: 1000 }
  ],
  env_vars: {},
  ...props.modelValue
})

const enableAssertions = ref(true)
const importSource = ref('none')
const showHeadersDialog = ref(false)
const showEnvDialog = ref(false)
const newHeaderKey = ref('')
const newHeaderValue = ref('')
const newEnvKey = ref('')
const newEnvValue = ref('')

// Header预设
const headerPresets = [
  { key: 'Accept', value: 'application/json' },
  { key: 'User-Agent', value: 'Automated-Testing/1.0' },
  { key: 'Accept-Language', value: 'zh-CN,zh;q=0.9' },
  { key: 'Cache-Control', value: 'no-cache' }
]

// 监听配置变化
watch(() => config, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

// 添加Header
const addHeader = () => {
  if (newHeaderKey.value && newHeaderValue.value) {
    config.headers[newHeaderKey.value] = newHeaderValue.value
    newHeaderKey.value = ''
    newHeaderValue.value = ''
  }
}

// 删除Header
const deleteHeader = (key) => {
  delete config.headers[key]
}

// 添加预设Header
const addPresetHeader = (preset) => {
  config.headers[preset.key] = preset.value
}

// 添加断言
const addAssertion = () => {
  config.assertions.push({
    type: 'status_code',
    expected: 200
  })
}

// 删除断言
const removeAssertion = (index) => {
  config.assertions.splice(index, 1)
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

// 处理导入源
const handleImportSource = (value) => {
  if (value === 'swagger') {
    // TODO: 显示Swagger导入对话框
  } else if (value === 'postman') {
    // TODO: 显示Postman导入对话框
  }
}

// 暴露方法
defineExpose({
  getConfig: () => config
})
</script>

<style scoped lang="scss">
.restapi-config-panel {
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

  .assertion-card {
    margin-bottom: 15px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    :deep(.el-card__body) {
      padding-top: 10px;
    }
  }

  .header-presets {
    .el-button {
      margin-right: 5px;
      margin-bottom: 5px;
    }
  }

  :deep(.el-input-number) {
    width: 200px;
  }

  .el-radio {
    margin-right: 20px;
    margin-bottom: 10px;
  }

  .el-tag {
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>

