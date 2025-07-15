package com.yeye.icmsjava.controller;

import com.yeye.icmsjava.model.AttendanceLog;
import com.yeye.icmsjava.model.request.AttendanceLogRequest;
import com.yeye.icmsjava.service.AttendanceLogService;
import com.yeye.icmsjava.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/attendance")
@Tag(name = "考勤管理接口", description = "提供查看考勤功能")
public class AttendanceLogController {
    @Resource
    private AttendanceLogService attendanceLogService;

    @GetMapping("/records")
    @Operation(summary = "返回考勤记录", description = "获取用户考勤记录")
    public List<AttendanceLogRequest> attendanceRecords() {
        return attendanceLogService.getAllRecords();
    }

}
