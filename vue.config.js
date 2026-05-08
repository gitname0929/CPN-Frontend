module.exports = {
  devServer: {
    port: 7000, // 端口号
    // 配置跨域
    proxy: {
      '/api':{
        target: 'http://100.127.132.2:8080', //100.127.132.2 localhost
        changeOrigin: true,
        pathRewrite: {
          // 路径重写，
          "^/api": "" // 替换target中的请求地址
        }
      }
    }
  },
}