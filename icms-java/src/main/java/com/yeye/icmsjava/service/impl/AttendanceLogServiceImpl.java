package com.yeye.icmsjava.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.yeye.icmsjava.model.AttendanceLog;
import com.yeye.icmsjava.service.AttendanceLogService;
import com.yeye.icmsjava.mapper.AttendanceLogMapper;
import org.springframework.stereotype.Service;

/**
* @author Administrator
* @description 针对表【attendance_log(考勤日志表)】的数据库操作Service实现
* @createDate 2025-07-10 16:29:42
*/
@Service
public class AttendanceLogServiceImpl extends ServiceImpl<AttendanceLogMapper, AttendanceLog>
    implements AttendanceLogService{

}




