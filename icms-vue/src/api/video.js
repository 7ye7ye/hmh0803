import axios from 'axios';

console.log('21当前环境变量 VIDEO_API:', process.env.VUE_APP_VIDEO_API);

// 创建axios实例
const request = axios.create({
    baseURL: process.env.VUE_APP_VIDEO_API,
    timeout: 20000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    }
});

// 视频相关的 api 接口
export const videoApi = {
    // 上报陌生人登录告警
    reportStrangerAlert(data) {
        console.log('调用陌生人告警接口，参数:', data);
        return request.post('/alert/stranger', data);
    }
}
