package com.yeye.icmsjava.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.yeye.icmsjava.mapper.AttendanceLogMapper;
import com.yeye.icmsjava.mapper.UserMapper;
import com.yeye.icmsjava.model.AttendanceLog;
import com.yeye.icmsjava.model.User;
import com.yeye.icmsjava.model.request.AttendanceLogRequest;
import com.yeye.icmsjava.service.AttendanceLogService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class AttendanceLogServiceImpl extends ServiceImpl<AttendanceLogMapper, AttendanceLog> implements AttendanceLogService {

    @Resource
    private UserMapper userMapper;

    @Override
    public List<AttendanceLogRequest> getAllRecords() {
        // 使用MyBatis-Plus提供的list()方法获取所有记录
        List<AttendanceLog> attendanceLogs = this.list();
        List<AttendanceLogRequest> attendanceLogRequests = new ArrayList<>();

        // 根据用户id获取用户名
        for (AttendanceLog attendanceLog : attendanceLogs) {
            AttendanceLogRequest attendanceLogRequest = new AttendanceLogRequest();
            // 设置签到时间
            attendanceLogRequest.setTimestamp(attendanceLog.getTimestamp());
            
            // 使用userMapper直接查询用户信息
            User user = userMapper.selectById(attendanceLog.getUserId());
            if (user != null) {
                attendanceLogRequest.setUsername(user.getUsername());
            }
            
            attendanceLogRequests.add(attendanceLogRequest);
        }
        return attendanceLogRequests;
    }
}




