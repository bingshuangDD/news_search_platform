<template>
  <div class="ai-chat-container">
    <van-nav-bar :title="$t('aiChat.title')" fixed />

    <!-- 模式切换 -->
    <div class="chat-mode-bar">
      <div class="mode-pills">
        <button
          class="mode-pill"
          :class="{ active: chatMode === 'rag' }"
          @click="chatMode = 'rag'"
        >
          <van-icon name="newspaper-o" class="pill-icon" />
          <span>{{ $t('aiChat.ragMode') }}</span>
        </button>
        <button
          class="mode-pill"
          :class="{ active: chatMode === 'free' }"
          @click="chatMode = 'free'"
        >
          <van-icon name="chat-o" class="pill-icon" />
          <span>{{ $t('aiChat.freeMode') }}</span>
        </button>
      </div>
    </div>

    <div class="chat-content">
      <div class="messages-container" ref="messagesContainer">
        <div
          v-for="message in messages"
          :key="message.id"
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
          :placeholder="$t('aiChat.placeholder')"
          class="chat-input"
          maxlength="500"
          show-word-limit
          @keypress.enter.prevent="sendMessage"
        />
        <van-button
          type="primary"
          class="send-button"
          :disabled="isLoading || !userInput.trim()"
          @click="sendMessage"
        >
          <van-icon name="send" size="18" />
        </van-button>
      </div>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import TabBar from '../components/TabBar.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { aiChatConfig } from '../config/api'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

let messageId = 0
const generateId = () => ++messageId

const messages = ref([
  {
    id: generateId(),
    role: 'assistant',
    content: t('aiChat.ragWelcome')
  }
])
const userInput = ref('')
const messagesContainer = ref(null)
const isLoading = ref(false)
const chatMode = ref('rag')

const onModeChange = (name) => {
  messages.value = [
    {
      id: generateId(),
      role: 'assistant',
      content: name === 'rag' ? t('aiChat.ragWelcome') : t('aiChat.freeWelcome')
    }
  ]
}

const formatMessage = (content) => {
  if (!content) return ''
  try {
    return DOMPurify.sanitize(marked.parse(content))
  } catch {
    return DOMPurify.sanitize(content)
  }
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const userMessage = userInput.value.trim()
  messages.value.push({
    id: generateId(),
    role: 'user',
    content: userMessage
  })
  userInput.value = ''

  messages.value.push({
    id: generateId(),
    role: 'assistant',
    content: ''
  })

  await nextTick()
  scrollToBottom()

  isLoading.value = true
  try {
    const body =
      chatMode.value === 'rag'
        ? JSON.stringify({ question: userMessage, top_k: 3 })
        : JSON.stringify({
            model: aiChatConfig.model,
            messages: messages.value.slice(0, -1).map((msg) => ({
              role: msg.role,
              content: msg.content
            })),
            stream: true
          })

    const endpoint =
      chatMode.value === 'rag' ? aiChatConfig.ragEndpoint : aiChatConfig.apiEndpoint

    await fetchAIResponse(endpoint, body)
  } catch (error) {
    const errorMessage = error.message || t('aiChat.networkError')
    messages.value[messages.value.length - 1].content = t('aiChat.error', { message: errorMessage })
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const fetchAIResponse = async (endpoint, body) => {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: body
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.error?.message || `HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let aiResponse = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue

          try {
            const json = JSON.parse(data)
            const content =
              json.choices?.[0]?.delta?.content ||
              json.output?.text ||
              json.choices?.[0]?.message?.content ||
              ''
            if (content) {
              aiResponse += content
              messages.value[messages.value.length - 1].content = aiResponse
              await nextTick()
              scrollToBottom()
            }
          } catch {
            // 忽略无法解析的 SSE 数据
          }
        }
      }
    }

    if (!aiResponse) {
      messages.value[messages.value.length - 1].content = t('aiChat.emptyResponse')
    }
  } catch (error) {
    throw error
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(
  messages,
  () => {
    nextTick(scrollToBottom)
  },
  { deep: true }
)

watch(chatMode, (newMode) => {
  onModeChange(newMode)
})

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-top: 46px;
  padding-bottom: 50px;
  box-sizing: border-box;
  background-color: var(--bg-base);
}

:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}

/* ===== 模式切换 ===== */
.chat-mode-bar {
  background-color: var(--bg-surface);
  padding: 10px 16px;
  box-shadow: var(--shadow-sm);
}

.mode-pills {
  display: flex;
  gap: 10px;
}

.mode-pill {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  padding: 0 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-pill);
  background-color: var(--bg-surface);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.mode-pill.active {
  background-color: var(--primary-light);
  border-color: var(--primary-light);
  color: var(--primary);
}

.pill-icon {
  font-size: 14px;
}

/* ===== 聊天内容 ===== */
.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.message {
  margin-bottom: 12px;
  max-width: 82%;
  animation: fadeSlideUp 0.2s ease both;
}

.user-message {
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-content {
  padding: 10px 14px;
  word-break: break-word;
  font-size: 15px;
  line-height: 1.55;
}

.user-message .message-content {
  background-color: var(--primary);
  color: var(--text-inverse);
  border-radius: var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg);
}

.ai-message .message-content {
  background-color: var(--bg-surface);
  color: var(--text-primary);
  border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

/* ===== Markdown 内容样式 ===== */
.message-content :deep(p) {
  margin: 0 0 8px;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(pre) {
  background-color: var(--bg-hover);
  padding: 10px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
}

.message-content :deep(code) {
  background-color: var(--bg-hover);
  padding: 2px 5px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.user-message .message-content :deep(pre),
.user-message .message-content :deep(code) {
  background-color: rgba(255, 255, 255, 0.15);
}

.message-content :deep(a) {
  color: var(--primary);
  text-decoration: underline;
}

.message-content :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-md);
}

/* ===== 输入区 ===== */
.input-container {
  display: flex;
  align-items: flex-end;
  padding: 10px 12px;
  background-color: var(--bg-surface);
  gap: 8px;
  box-shadow: 0 -1px 0 var(--border-color);
}

.input-container :deep(.van-field) {
  flex: 1;
  background: var(--bg-hover);
  border-radius: var(--radius-pill);
  padding: 8px 16px;
}

.input-container :deep(.van-field__control) {
  background: transparent;
  color: var(--text-primary);
}

.input-container :deep(.van-field__word-limit) {
  color: var(--text-tertiary);
}

.chat-input {
  flex: 1;
}

.send-button {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-pill);
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s ease;
}

.send-button:active:not(:disabled) {
  transform: scale(0.92);
}

/* ===== 打字指示器 ===== */
.typing-indicator {
  display: flex;
  padding: 6px 4px;
  gap: 4px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: var(--text-tertiary);
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
</style>
