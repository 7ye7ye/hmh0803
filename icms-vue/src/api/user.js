import axios from 'axios';

console.log('当前环境变量 BASE_API:', process.env.VUE_APP_BASE_API);

// 创建axios实例
const request = axios.create({
    baseURL: process.env.VUE_APP_BASE_API,
    timeout: 20000,//签到功能有时处理较慢，增大超时时间至20s
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    }
});

// 用户相关的 api 接口
export const userApi = {
    // 用户登录
    login(data) {
        console.log('调用登录接口，参数:', data);
        console.log('完整请求URL:', request.defaults.baseURL + '/user/login');
        return request.post('user/login', data);
    },
    
    // 用户注册
    register(data) {
        console.log('调用注册接口，参数:', data);
        return request.post('user/register', data);
    },
    
    // 获取当前用户信息
    getCurrentUser() {
        return request.get('user/current');
    },

    // 退出登录
    logout() {
        console.log('调用退出登录接口');
        return request.post('user/logout', null, {
            withCredentials: true
        });
    },

    // 用户签到
    signin(data) {
        return request.post('user/signin', data);
    },

    // 更新用户信息
     updateUser(data) {
        return request.put('user/update', data);
    },

    // 更新用户人脸信息
    updateFaceInfo(data) {
        return request.put('user/face', data);
    },

    // 重置密码
    resetPassword(data) {
        return request.post('user/reset-password', data);
    },

    

}