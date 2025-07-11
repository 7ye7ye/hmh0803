import axios from 'axios';

console.log('当前环境变量 BASE_API:', process.env.VUE_APP_BASE_API);
console.log('当前环境变量 AI_API:', process.env.VUE_APP_AI_API);
// 创建axios实例
const request = axios.create({
    baseURL: process.env.VUE_APP_AI_API,
    timeout: 10000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    }
});

// 用户相关的 api 接口
export const aiApi = {
    // 人脸识别
    start_facial_recognition(){
        return request.get('ai/facial/get_latest_vector');
    }

}