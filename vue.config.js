module.exports = {
  devServer: {
    host: '0.0.0.0',
    port: 7001, // 端口号
    public: '192.168.31.36:7001',
    disableHostCheck: true,
    // 配置跨域
    proxy: {
      '/api':{
        target: 'http://127.0.0.1:8099',
        changeOrigin: true,
      }
    }
  },
}
