package com.yeye.icmsjava.model;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Data;

/**
 * 考勤日志表
 * @TableName attendance_log
 */
@TableName(value ="attendance_log")
@Data
public class AttendanceLog {
    /**
     * 自增主键
     */
    @TableId(type = IdType.AUTO)
    private String id;

    /**
     * 签到的用户ID
     */
    private Integer userId;

    /**
     * 签到发生时间
     */
    private LocalDateTime timestamp;

    /**
     * 签到瞬间的现场快照路径 (URL)
     */
    private String faceImage;

    /**
     * 识别置信度得分 (0.0000-1.0000)
     */
    private BigDecimal confidenceScore;

    /**
     * 活体检测得分
     */
    private BigDecimal livenessScore;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public BigDecimal getConfidenceScore() {
        return confidenceScore;
    }

    public void setConfidenceScore(BigDecimal confidenceScore) {
        this.confidenceScore = confidenceScore;
    }

    public BigDecimal getLivenessScore() {
        return livenessScore;
    }

    public void setLivenessScore(BigDecimal livenessScore) {
        this.livenessScore = livenessScore;
    }

    public String getFaceImage() {
        return faceImage;
    }

    public void setFaceImage(String faceImage) {
        this.faceImage = faceImage;
    }
}
