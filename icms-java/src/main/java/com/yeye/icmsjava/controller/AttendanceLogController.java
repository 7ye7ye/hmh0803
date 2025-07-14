package com.yeye.icmsjava.controller;

import com.yeye.icmsjava.model.AttendanceLog;
import com.yeye.icmsjava.model.request.AttendanceLogRequest;
import com.yeye.icmsjava.service.AttendanceLogService;
import com.yeye.icmsjava.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.PostMapping;

import java.util.List;

public class AttendanceLogController {
    @Resource
    private AttendanceLogService attendanceLogService;

    @PostMapping("/records")
    @Operation(summary = "返回考勤记录", description = "获取用户考勤记录")
    public List<AttendanceLogRequest> attendanceRecords() {
        return attendanceLogService.getAllRecords();
    }

}
