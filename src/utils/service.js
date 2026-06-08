import axios from 'axios'
import router from '@/router'
axios.defaults.withCredentials = true
//axios.defaults.headers.post['Content-Type']="application/json"
// 创建一个axios实例
const service = axios.create({
  //baseURL: 'http://localhost:7000',  // 后端接口的基础路径
  baseURL: '/api',
  timeout: 20000 // 请求超时时间 30-30000ms
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    return config
  },
  error => {
    // 对请求错误做些什么
    console.log("request error:" + error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做一些处理，这里只返回响应数据中的data部分
    let res = response.data
    console.log(res)
    if(res === "需要登陆!"){
      localStorage.removeItem('userInfo');
      localStorage.removeItem('powerIdList');
      localStorage.removeItem('asideShowData');
      router.push('/login')
      return Promise.reject("登录过期，请先登录！")
    }
    // 兼容服务器端的字符串数据
    if (typeof res === "string") {
      res = res ? JSON.parse(res) : res
    }
    if(res.code === 0){
      return Promise.reject(res.msg)
    }
    /*
    if (res.code == "0") {
      console.log('response success!');
      return res.data
    }
    else if (res.code == "1") {
      console.log('response error!');
      return res.msg
    }
    else {
      return res;
    }
    */
    return res;
  },

  error => {
    // 对响应错误做些什么
    const data = error.response && error.response.data ? error.response.data : {}
    const message = data.msg || data.message || data.error || error.message || '请求失败'
    console.log('response err:' + message)
    error.message = message
    return Promise.reject(error)
  }
)

export default service
