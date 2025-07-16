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
export const attendanceApi = {
    // 考勤相关的API
    // 获取考勤记录
    getAttendanceRecords() {
        return request.get('attendance/records', {});
    },

    // 导出考勤记录
    exportAttendance(params) {
        return request.get('attendance/export', { 
            params,
            responseType: 'blob'
        });
    },

    // 更新考勤规则
    updateAttendanceRule(data) {
        return request.put('attendance/rule', data);
    },
}