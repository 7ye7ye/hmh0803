const path = require('path')

// 路径解析函数
const resolve = dir => {
  return path.join(__dirname, dir)
}

// 生产环境基础路径（影响静态资源加载）
const BASE_URL = process.env.NODE_ENV === 'production' 
  ? './'  // 生产环境使用相对路径，避免部署时路径错误
  : '/'   // 开发环境使用根路径

module.exports = {
  // 基础路径（与BASE_URL保持一致，优先使用publicPath）
  publicPath: BASE_URL,
  
  // transpileDependencies: 默认情况下 babel-loader 会忽略所有 node_modules 中的文件。
  // 如果你想要通过 Babel 显式转译一个依赖，可以在这个选项中列出来
  transpileDependencies: [],
  
  // ESLint 检查：开发环境启用，生产环境禁用（加速打包）
  lintOnSave: process.env.NODE_ENV !== 'production',
  
  // 配置路径别名
  chainWebpack: config => {
    config.resolve.alias
      .set('@', resolve('src'))        // 源码根目录
      .set('_c', resolve('src/components'))  // 组件目录
      .set('_assets', resolve('src/assets'))  // 静态资源目录
    
    // 生产环境优化：移除console和debugger
    if (process.env.NODE_ENV === 'production') {
      config.optimization.minimizer('terser').tap(options => {
        options[0].terserOptions.compress.drop_console = true
        options[0].terserOptions.compress.drop_debugger = true
        return options
      })
    }
  },
  
  // 生产环境不生成 sourceMap（减小包体积，保护源码）
  productionSourceMap: false,
  
  // 开发服务器配置
  devServer: {
    port: 8085,         // 端口号
    open: true,         // 自动打开浏览器
    client: {
      overlay: true,
    },
  },
  
  // CSS 配置
  css: {
    // 提取CSS到单独文件（生产环境推荐，避免样式阻塞）
    extract: process.env.NODE_ENV === 'production',
    
    // CSS loader 配置
    loaderOptions: {
      // 全局注入变量（可选）
      // sass: {
      //   prependData: `@import "@/assets/style/variable.scss";`
      // }
    }
  },
  
  // 优化配置
  configureWebpack: config => {
    // 生产环境配置
    if (process.env.NODE_ENV === 'production') {
      // 分割代码（优化加载速度）
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            name: 'vendors',
            test: /[\\/]node_modules[\\/]/,
            priority: 10,
            chunks: 'initial'
          }
        }
      }
      
      // 如需禁用CSS压缩（测试样式丢失是否由压缩导致），取消下面注释
      // config.optimization.minimizer = config.optimization.minimizer.filter(
      //   minimizer => minimizer.constructor.name !== 'CssMinimizerPlugin'
      // )
    }
  }
}