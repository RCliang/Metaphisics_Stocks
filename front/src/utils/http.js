import axios from 'axios'
import { ElMessage } from 'element-plus'


const http = {}
const baseUrl = "http://localhost:8000"

const instance = axios.create({
    timeout: 5000,
    // baseURL
    baseURL: baseUrl
})

// 添加请求拦截器
instance.interceptors.request.use(
    function (config) {
        // 请求头添加token
        // if (store.state.UserToken) {
        //     config.headers.Authorization = store.state.UserToken
        // }
        return config
    },
    function (error) {
        return Promise.reject(error)
    }
)

instance.interceptors.response.use(
    response => {
        return response
    },
    err => {
        if (err && err.response) {
            switch (err.response.status) {
                case 400:
                    err.message = '请求出错'
                    break
                case 401:
                    ElMessage.warning({
                        message: '授权失败，请重新登录'
                    })
                    store.commit('LOGIN_OUT')
                    setTimeout(() => {
                        window.location.reload()
                    }, 1000)

                    return
                case 403:
                    err.message = '拒绝访问'
                    break
                case 404:
                    err.message = '请求错误,未找到该资源'
                    break
                case 500:
                    err.message = '服务器端出错'
                    break
            }
        } else {
            err.message = '连接服务器失败'
        }
        ElMessage.error({
            message: err.message
        })
        return Promise.reject(err.response)
    }
)

// http.get = function (url, options) {
//     return new Promise((resolve, reject) => {
//         instance
//             .get(url, options)
//             .then(response => {
//                 if (response.code === 200) {
//                     resolve(response.data)
//                 } else {
//                     ElMessage.error({
//                         message: response.message
//                     })
//                     reject(response.message)
//                 }
//             })
//             .catch(e => {
//                 console.log(e)
//             })
//     })
// }

// http.post = function (url, data, options) {
//     return new Promise((resolve, reject) => {
//         instance
//             .post(url, data, options)
//             .then(response => {
//                 if (response.code === 200) {
//                     resolve(response.data)
//                 } else {
//                     ElMessage.error({
//                         message: response.message
//                     })
//                     reject(response.message)
//                 }
//             })
//             .catch(e => {
//                 console.log(e)
//             })
//     })
// }

export default instance