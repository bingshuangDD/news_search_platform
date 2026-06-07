<template>
  <div class="ai-chat-container">
    <van-nav-bar title="AI问答" fixed />

    <!-- 模式切换标签 -->
    <div class="chat-mode-tabs">
      <van-tabs v-model:active="chatMode" type="card">
        <van-tab name="rag" title="📰 新闻问答" />
        <van-tab name="free" title="💬 自由聊天" />
      </van-tabs>
    </div>

    <div class="chat-content">
      <div class="messages-container" ref="messagesContainer">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-content">
            <div v-if="message.role === 'assistant' && message.content === ''" class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div v-else v-html="formatMessage(message.content)"></div>
          </div>
        </div>
      </div>
      
      <div class="input-container">
        <van-field
          v-model="userInput"
          rows="1"
          autosize
          type="textarea"
          placeholder="请输入问题..."
          class="chat-input"
          @keypress.enter.prevent="sendMessage"
        />
        <van-button 
          type="primary" 
          class="send-button" 
          :disabled="isLoading || !userInput.trim()" 
          @click="sendMessage"
        >
          发送
        </van-button>
      </div>
    </div>
    
    <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue';
import TabBar from '../components/TabBar.vue';
import { showToast } from 'vant';
import * as marked from 'marked';
import DOMPurify from 'dompurify';
import { aiChatConfig } from '../config/api';

// 聊天消息
const messages = ref([
  { role: 'assistant', content: '你好！我是新闻问答助手，可以基于本站新闻内容回答你的问题。试试问"最近有什么科技新闻"吧！' }
]);
const userInput = ref('');
const messagesContainer = ref(null);
const isLoading = ref(false);
const chatMode = ref('rag');  // 'rag' | 'free'

// 切换模式时重置对话
const onModeChange = (name) => {
  messages.value = [
    { role: 'assistant', content: name === 'rag'
      ? '你好！我是新闻问答助手，可以基于本站新闻内容回答你的问题。试试问"最近有什么科技新闻"吧！'
      : '你好！我是AI助手，有什么可以帮助你的吗？'
    }
  ];
};

// 从配置文件获取API设置
const apiEndpoint = ref(aiChatConfig.apiEndpoint);
const apiKey = ref(aiChatConfig.apiKey);
const model = ref(aiChatConfig.model);

// 格式化消息内容（支持Markdown）
const formatMessage = (content) => {
  if (!content) return '';
  // 使用marked解析Markdown，并用DOMPurify清理HTML
  return DOMPurify.sanitize(marked.parse(content));
};

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  
  // 添加用户消息
  const userMessage = userInput.value.trim();
  messages.value.push({ role: 'user', content: userMessage });
  userInput.value = '';
  
  // 添加AI消息占位
  messages.value.push({ role: 'assistant', content: '' });
  
  // 滚动到底部
  await nextTick();
  scrollToBottom();
  
  // 发送请求
  isLoading.value = true;
  try {
    const body = chatMode.value === 'rag'
      ? JSON.stringify({ question: userMessage, top_k: 3 })
      : (() => {
          const allMessages = messages.value.slice(0, -1).map(msg => ({ role: msg.role, content: msg.content }));
          return JSON.stringify({ model: model.value, messages: allMessages, stream: true });
        })();

    const endpoint = chatMode.value === 'rag'
      ? (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000') + '/api/ai/ask'
      : apiEndpoint.value;

    await fetchAIResponse(endpoint, body);
  } catch (error) {
    console.error('Error fetching AI response:', error);
    // 更新最后一条消息为错误信息
    messages.value[messages.value.length - 1].content = `发生错误: ${error.message || '请检查网络连接和API设置'}`;
  } finally {
    isLoading.value = false;
    await nextTick();
    scrollToBottom();
  }
};

// 获取AI响应（使用SSE）
const fetchAIResponse = async (endpoint, body) => {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error?.message || `HTTP error! status: ${response.status}`);
    }
    
    // 处理SSE流
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let aiResponse = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') continue;
        
        try {
          const json = JSON.parse(data);
          // 适配阿里云DashScope的返回格式
          const content = json.choices?.[0]?.delta?.content || 
                         json.output?.text || 
                         json.choices?.[0]?.message?.content || '';
          if (content) {
            aiResponse += content;
            // 更新最后一条消息
            messages.value[messages.value.length - 1].content = aiResponse;
            await nextTick();
            scrollToBottom();
          }
        } catch (e) {
          console.error('Error parsing SSE data:', e);
        }
      }
    }
  }
  
  // 如果没有收到任何内容
  if (!aiResponse) {
    messages.value[messages.value.length - 1].content = '抱歉，我无法生成回复。请检查API设置或稍后再试。';
  }
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
};

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 监听消息变化，自动滚动
watch(messages, () => {
  nextTick(scrollToBottom);
}, { deep: true });

// 监听模式切换
watch(chatMode, (newMode) => {
  onModeChange(newMode);
});

// 组件挂载时滚动到底部
onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-top: 46px;
  padding-bottom: 50px;
  box-sizing: border-box;
  background-color: var(--background-color);
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px 10px;
}

.message {
  margin-bottom: 10px;
  max-width: 80%;
  animation: fadeSlideUp 0.3s ease both;
}

.user-message {
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-content {
  padding: 12px 14px;
  word-break: break-word;
  font-size: 15px;
  line-height: 1.55;
}

.user-message .message-content {
  background: linear-gradient(135deg, #4F46E5, #7C3AED);
  color: white;
  border-radius: 16px 16px 4px 16px;
}

.ai-message .message-content {
  background-color: #FFFFFF;
  color: #1E293B;
  border-radius: 16px 16px 16px 4px;
  box-shadow: var(--shadow-card);
}

/* ===== 输入区 ===== */
.input-container {
  display: flex;
  align-items: flex-end;
  padding: 10px 12px;
  background-color: #fff;
  gap: 8px;
  box-shadow: 0 -1px 3px rgba(15, 23, 42, 0.04);
}

.input-container :deep(.van-field) {
  flex: 1;
  background: #F1F5F9;
  border-radius: 24px;
  padding: 8px 16px;
}

.input-container :deep(.van-field__control) {
  background: transparent;
}

.chat-input {
  flex: 1;
}

.send-button {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  flex-shrink: 0;
  box-shadow: var(--shadow-float);
  transition: transform 0.15s ease;
}

.send-button:active:not(:disabled) {
  transform: scale(0.92);
}

.send-button :deep(.van-button__text) {
  font-size: 14px;
}

/* ===== Markdown 内容样式 ===== */
.message-content pre {
  background-color: rgba(0, 0, 0, 0.06);
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-content code {
  background-color: rgba(0, 0, 0, 0.06);
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 13px;
}

.user-message .message-content pre,
.user-message .message-content code {
  background-color: rgba(255, 255, 255, 0.15);
}

.message-content img {
  max-width: 100%;
}

/* ===== 打字指示器 ===== */
.typing-indicator {
  display: flex;
  padding: 6px;
  gap: 4px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #94A3B8;
  border-radius: 50%;
  display: inline-block;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}

/* ===== 模式切换标签 ===== */
.chat-mode-tabs {
  background: #fff;
  padding: 4px 0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

.chat-mode-tabs :deep(.van-tabs__nav--card) {
  margin: 0 12px;
  background: #F1F5F9;
  border-radius: 12px;
  border: none;
}

.chat-mode-tabs :deep(.van-tabs__nav--card .van-tab) {
  border: none;
  background: transparent;
  color: #64748B;
  border-radius: 10px;
  font-size: 13px;
  transition: all 0.2s ease;
}

.chat-mode-tabs :deep(.van-tabs__nav--card .van-tab--active) {
  background: #FFFFFF;
  color: #4F46E5;
  font-weight: 600;
  box-shadow: var(--shadow-card);
}

/* ===== 深色模式适配 ===== */
body.theme-dark .message-content pre,
body.theme-dark .message-content code {
  background-color: rgba(255, 255, 255, 0.08);
}

body.theme-dark .ai-message .message-content {
  background-color: #1E293B;
  color: #F8FAFC;
}

body.theme-dark .input-container {
  background-color: #1E293B;
}

body.theme-dark .input-container :deep(.van-field) {
  background: #334155;
}

body.theme-dark .chat-mode-tabs {
  background: #1E293B;
}

body.theme-dark .chat-mode-tabs :deep(.van-tabs__nav--card) {
  background: #334155;
}

body.theme-dark .chat-mode-tabs :deep(.van-tabs__nav--card .van-tab--active) {
  background: #475569;
  color: #818CF8;
}
</style>