package com.yeye.icmsjava.model.request;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AttendanceLogRequest {
    /**
     * 签到用户名
     */
    private String username;
    /**
     * 签到发生时间
     */
    private LocalDateTime timestamp;
}
