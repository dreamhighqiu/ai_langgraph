<template>
  <div class="app-container chat-container">
    <el-page-header @back="goBack">
      <template #content>
        <span class="text-large font-600 mr-3">RAG 问答 - {{ knowledgeName }}</span>
      </template>
    </el-page-header>

    <el-divider />

    <!-- 查询模式选择 -->
    <div class="mode-selector mb20">
      <span class="mode-label">查询模式：</span>
      <el-radio-group v-model="queryMode" size="small">
        <el-radio-button label="naive">
          <el-tooltip content="快速向量检索，速度最快" placement="top">
            <span>快速检索</span>
          </el-tooltip>
        </el-radio-button>
        <el-radio-button label="local">
          <el-tooltip content="局部知识图检索，关注相关实体" placement="top">
            <span>局部检索</span>
          </el-tooltip>
        </el-radio-button>
        <el-radio-button label="global">
          <el-tooltip content="全局知识图检索，综合分析" placement="top">
            <span>全局检索</span>
          </el-tooltip>
        </el-radio-button>
        <el-radio-button label="hybrid">
          <el-tooltip content="混合检索模式，平衡准确性和速度（推荐）" placement="top">
            <span>混合检索（推荐）</span>
          </el-tooltip>
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef">
      <div class="welcome-message" v-if="messages.length === 0">
        <el-icon :size="60" color="#409eff"><ChatLineRound /></el-icon>
        <h3>欢迎使用 RAG 智能问答</h3>
        <p>基于您上传的文档，我可以回答相关问题</p>
        <el-divider />
        <div class="tips">
          <h4>使用提示：</h4>
          <ul>
            <li>🔍 <strong>快速检索</strong>：适合精确查找特定信息</li>
            <li>🌐 <strong>局部检索</strong>：适合查询相关概念和关系</li>
            <li>🗺️ <strong>全局检索</strong>：适合理解整体架构</li>
            <li>⚡ <strong>混合检索</strong>：综合以上优势（推荐）</li>
          </ul>
        </div>
      </div>

      <div v-for="msg in messages" :key="msg.id" :class="['message-item', msg.role]">
        <div class="message-avatar">
          <el-avatar v-if="msg.role === 'user'" :size="40">
            <el-icon><User /></el-icon>
          </el-avatar>
          <el-avatar v-else :size="40" style="background-color: #409eff">
            <el-icon><ChatDotRound /></el-icon>
          </el-avatar>
        </div>
        <div class="message-content">
          <div class="message-header">
            <span class="message-role">{{ msg.role === 'user' ? '我' : 'AI 助手' }}</span>
            <span class="message-time">{{ msg.time }}</span>
          </div>
          <div class="message-text" v-html="formatMessage(msg.content)"></div>
          <div class="message-mode" v-if="msg.role === 'assistant' && msg.mode">
            <el-tag size="small" type="info">{{ getModeText(msg.mode) }}</el-tag>
          </div>
        </div>
      </div>

      <div v-if="loading" class="message-item assistant">
        <div class="message-avatar">
          <el-avatar :size="40" style="background-color: #409eff">
            <el-icon><ChatDotRound /></el-icon>
          </el-avatar>
        </div>
        <div class="message-content">
          <div class="message-header">
            <span class="message-role">AI 助手</span>
          </div>
          <div class="loading-indicator">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>思考中...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-area">
      <el-input
        v-model="inputText"
        :rows="3"
        type="textarea"
        placeholder="输入问题，按 Ctrl+Enter 或 点击发送按钮"
        @keydown.ctrl.enter="sendMessage"
        :disabled="loading"
      />
      <el-button 
        type="primary" 
        :loading="loading" 
        @click="sendMessage"
        :disabled="!inputText.trim()"
        size="large"
      >
        <el-icon v-if="!loading"><Promotion /></el-icon>
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup name="KnowledgeChat">
import { queryKnowledge } from "@/api/testing/knowledge";
import { marked } from 'marked';

const { proxy } = getCurrentInstance();
const router = useRouter();
const route = useRoute();

const knowledgeId = ref(null);
const knowledgeName = ref("");
const queryMode = ref("hybrid");
const inputText = ref("");
const messages = ref([]);
const loading = ref(false);
const messageListRef = ref(null);

// 配置 marked（v15+）
try {
  if (marked && typeof marked.setOptions === 'function') {
    marked.setOptions({
      breaks: true,
      gfm: true
    });
  }
} catch (error) {
  console.warn('marked 配置失败:', error);
}

/** 发送消息 */
async function sendMessage() {
  if (!inputText.value.trim() || loading.value) return;

  const query = inputText.value.trim();
  
  // 添加用户消息
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: query,
    time: formatTime(new Date())
  };
  messages.value.push(userMessage);
  
  inputText.value = "";
  loading.value = true;

  // 滚动到底部
  scrollToBottom();

  try {
    // 调用 API
    const response = await queryKnowledge(knowledgeId.value, {
      query: query,
      mode: queryMode.value
    });

    // 添加助手回复
    const assistantMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: response.data.answer || "抱歉，我无法回答这个问题。",
      time: formatTime(new Date()),
      mode: queryMode.value
    };
    messages.value.push(assistantMessage);
  } catch (error) {
    // 添加错误消息
    const errorMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: `抱歉，查询失败：${error.message || '未知错误'}`,
      time: formatTime(new Date())
    };
    messages.value.push(errorMessage);
  } finally {
    loading.value = false;
    // 滚动到底部
    scrollToBottom();
  }
}

/** 格式化消息（Markdown 渲染） */
function formatMessage(text) {
  try {
    if (!marked) {
      return text;
    }
    // marked v15+ 使用 marked.parse() 或 marked()
    if (typeof marked.parse === 'function') {
      return marked.parse(text);
    } else if (typeof marked === 'function') {
      return marked(text);
    } else {
      return text;
    }
  } catch (error) {
    console.error('Markdown 解析错误:', error);
    return text;
  }
}

/** 格式化时间 */
function formatTime(date) {
  const h = date.getHours().toString().padStart(2, '0');
  const m = date.getMinutes().toString().padStart(2, '0');
  const s = date.getSeconds().toString().padStart(2, '0');
  return `${h}:${m}:${s}`;
}

/** 获取模式文本 */
function getModeText(mode) {
  const modeMap = {
    'naive': '快速检索',
    'local': '局部检索',
    'global': '全局检索',
    'hybrid': '混合检索'
  };
  return modeMap[mode] || mode;
}

/** 滚动到底部 */
function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
    }
  });
}

/** 返回 */
function goBack() {
  router.back();
}

/** 清空对话 */
function clearChat() {
  proxy.$modal.confirm('是否确认清空所有对话？').then(() => {
    messages.value = [];
    proxy.$modal.msgSuccess("对话已清空");
  }).catch(() => {});
}

onMounted(() => {
  // 从路由参数中获取 knowledgeId（路径参数）
  knowledgeId.value = route.params.knowledgeId || route.query.knowledgeId;
  knowledgeName.value = route.query.knowledgeName || "未知";
  
  if (!knowledgeId.value) {
    proxy.$modal.msgError("缺少知识库ID参数");
    router.back();
  }
});
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  max-height: 900px;
}

.text-large {
  font-size: 18px;
}

.font-600 {
  font-weight: 600;
}

.mr-3 {
  margin-right: 12px;
}

.mb20 {
  margin-bottom: 20px;
}

.mode-selector {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.mode-label {
  font-weight: 600;
  margin-right: 12px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  min-height: 400px;
  max-height: 600px;
}

.welcome-message {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.welcome-message h3 {
  margin: 20px 0 10px;
  font-size: 24px;
  color: #333;
}

.welcome-message p {
  margin: 0 0 20px;
  font-size: 16px;
}

.tips {
  text-align: left;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tips h4 {
  margin: 0 0 15px;
  font-size: 16px;
  color: #333;
}

.tips ul {
  margin: 0;
  padding-left: 20px;
}

.tips li {
  margin-bottom: 10px;
  line-height: 1.6;
}

.message-item {
  display: flex;
  margin-bottom: 24px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 12px;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-item.user .message-content {
  background: #409eff;
  color: white;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
}

.message-role {
  font-weight: 600;
}

.message-item.user .message-role,
.message-item.user .message-time {
  color: rgba(255, 255, 255, 0.9);
}

.message-time {
  color: #999;
}

.message-text {
  word-break: break-word;
  line-height: 1.6;
}

.message-text :deep(p) {
  margin: 8px 0;
}

.message-text :deep(pre) {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}

.message-text :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  padding-left: 20px;
}

.message-text :deep(li) {
  margin: 4px 0;
}

.message-mode {
  margin-top: 8px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 20px 0 0;
}

.input-area .el-textarea {
  flex: 1;
}

.input-area :deep(.el-textarea__inner) {
  resize: none;
  border-radius: 8px;
}

.input-area .el-button {
  height: auto;
  padding: 12px 24px;
  border-radius: 8px;
}

/* 滚动条样式 */
.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}
</style>

