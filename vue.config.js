module.exports = {
  devServer: {
    port: 7000, // 端口号
    // 配置跨域
    proxy: {
      '/api':{
        target: 'http://127.0.0.1:8099',
        changeOrigin: true,
      }
    }
  },
}