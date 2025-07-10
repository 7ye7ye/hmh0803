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
     * 代理主键
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 业务主键 (UUID), 考勤记录的唯一ID
     */
    private String logId;

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
    private String snapshotUrl;

    /**
     * 识别置信度得分 (0.0000-1.0000)
     */
    private BigDecimal confidenceScore;

    /**
     * 活体检测得分
     */
    private BigDecimal livenessScore;

    @Override
    public boolean equals(Object that) {
        if (this == that) {
            return true;
        }
        if (that == null) {
            return false;
        }
        if (getClass() != that.getClass()) {
            return false;
        }
        AttendanceLog other = (AttendanceLog) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getLogId() == null ? other.getLogId() == null : this.getLogId().equals(other.getLogId()))
            && (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
            && (this.getTimestamp() == null ? other.getTimestamp() == null : this.getTimestamp().equals(other.getTimestamp()))
            && (this.getSnapshotUrl() == null ? other.getSnapshotUrl() == null : this.getSnapshotUrl().equals(other.getSnapshotUrl()))
            && (this.getConfidenceScore() == null ? other.getConfidenceScore() == null : this.getConfidenceScore().equals(other.getConfidenceScore()))
            && (this.getLivenessScore() == null ? other.getLivenessScore() == null : this.getLivenessScore().equals(other.getLivenessScore()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getLogId() == null) ? 0 : getLogId().hashCode());
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getTimestamp() == null) ? 0 : getTimestamp().hashCode());
        result = prime * result + ((getSnapshotUrl() == null) ? 0 : getSnapshotUrl().hashCode());
        result = prime * result + ((getConfidenceScore() == null) ? 0 : getConfidenceScore().hashCode());
        result = prime * result + ((getLivenessScore() == null) ? 0 : getLivenessScore().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", id=").append(id);
        sb.append(", logId=").append(logId);
        sb.append(", userId=").append(userId);
        sb.append(", timestamp=").append(timestamp);
        sb.append(", snapshotUrl=").append(snapshotUrl);
        sb.append(", confidenceScore=").append(confidenceScore);
        sb.append(", livenessScore=").append(livenessScore);
        sb.append("]");
        return sb.toString();
    }
}