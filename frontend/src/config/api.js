/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}

export const aiChatConfig = {
  // 请求自己的后端，由后端代理转发到 AI 服务商
  apiEndpoint: 'http://127.0.0.1:8000/api/ai/chat',

  // API Key 由后端管理，前端不持有
  apiKey: '',

  // 使用的模型
  model: 'kimi-k2.6'
}
