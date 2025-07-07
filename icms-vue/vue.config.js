const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发代理配置，将API请求转发到后端
  devServer: {
    port: 8080, // 固定端口为8080
    proxy: {
      '/api': {
        target: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8090',
        changeOrigin: true
      }
    }
  }
})
