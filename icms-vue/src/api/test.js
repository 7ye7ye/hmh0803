import axios from 'axios';

// 创建axios实例
const request = axios.create({
    baseURL: process.env.VUE_APP_BASE_API,
    timeout: 10000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    }
});

// 相关的 api 接口
export const testApi = {
    //反转字符
    reverse() {
        console.log('调用测试接口，参数:');
        return request.get('/test/reverse');
    },
}