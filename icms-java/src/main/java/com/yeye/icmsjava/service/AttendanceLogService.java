package com.yeye.icmsjava.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.yeye.icmsjava.model.AttendanceLog;
import com.yeye.icmsjava.model.request.AttendanceLogRequest;

import java.util.List;

public interface AttendanceLogService extends IService<AttendanceLog> {
    /**
     * 获取所有考勤记录
     * @return 考勤记录列表
     */
    List<AttendanceLogRequest> getAllRecords();
}
