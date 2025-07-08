import axios from 'axios';

console.log('当前环境变量 BASE_API:', process.env.VUE_APP_BASE_API);

// 创建axios实例
const request = axios.create({
    baseURL: process.env.VUE_APP_BASE_API,
    timeout: 10000,
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
    }
}