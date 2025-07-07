/**
 * API配置文件
 * 
 * 注意：在生产环境中，API密钥应该通过环境变量或后端服务来提供，
 * 而不是直接存储在前端代码中
 */

// DeepSeek API配置
export const DEEPSEEK_CONFIG = {
  BASE_URL: process.env.VUE_APP_DEEPSEEK_BASE_URL || 'https://api.deepseek.com/v1',
  API_KEY: process.env.VUE_APP_DEEPSEEK_API_KEY || '',
  MODEL: process.env.VUE_APP_DEEPSEEK_MODEL || 'deepseek-reasoner'
}; 