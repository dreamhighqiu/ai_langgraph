<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span><el-icon><Monitor /></el-icon> UI自动化测试</span>
          <el-button type="primary" @click="handleGenerate">
            <el-icon><Plus /></el-icon> AI生成脚本
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
        <!-- Tab 1: 脚本管理 -->
        <el-tab-pane label="脚本管理" name="scripts">
          <template #label>
            <span><el-icon><Document /></el-icon> 脚本管理</span>
          </template>
          <script-list />
        </el-tab-pane>

        <!-- Tab 2: 脚本生成 -->
        <el-tab-pane label="脚本生成" name="generate">
          <template #label>
            <span><el-icon><MagicStick /></el-icon> 脚本生成</span>
          </template>
          <generate-page />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup name="UIAutomation">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ScriptList from './script.vue'
import GeneratePage from './generate.vue'

const router = useRouter()
const route = useRoute()

const activeTab = ref('scripts')

function handleTabChange(tabName) {
  // Tab切换时的处理
}

function handleGenerate() {
  activeTab.value = 'generate'
}

onMounted(() => {
  // 根据路由参数设置默认Tab
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}
</style>
