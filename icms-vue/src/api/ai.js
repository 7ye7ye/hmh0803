import axios from 'axios';

console.log('当前环境变量 BASE_API:', process.env.VUE_APP_BASE_API);
console.log('当前环境变量 AI_API:', process.env.VUE_APP_AI_API);

// 创建axios实例
const request = axios.create({
    baseURL: process.env.VUE_APP_AI_API || 'http://localhost:8000',
    timeout: 10000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    }
});

// AI相关的API接口
export const aiApi = {
    // 获取实时人脸向量
    start_facial_recognition(data) {
        if (data && data.image) {
            return request.post('ai/facial/recognize', { image: data.image });
        }
        return request.get('ai/facial/get_latest_vector');
    },

    // 获取视频流
    getVideoFeed() {
        return `${request.defaults.baseURL}/ai/facial/video_feed_cors`;
    }
}