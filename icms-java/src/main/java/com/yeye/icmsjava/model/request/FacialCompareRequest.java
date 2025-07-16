package com.yeye.icmsjava.model.request;

import lombok.Data; // 自动生成 getter, setter, toString, equals, hashCode
import lombok.NoArgsConstructor; // 自动生成无参构造函数
import lombok.AllArgsConstructor; // 自动生成全参构造函数

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FacialCompareRequest {
    private String status;
    private Boolean verified; // 对应 JSON 中的 "verified" 字段
    private Double distance; // 对应 JSON 中的 "distance" 字段
    private Double threshold; // 对应 JSON 中的 "threshold" 字段
    private String message;

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Boolean getVerified() {
        return verified;
    }

    public void setVerified(Boolean verified) {
        this.verified = verified;
    }

    public Double getDistance() {
        return distance;
    }

    public void setDistance(Double distance) {
        this.distance = distance;
    }

    public Double getThreshold() {
        return threshold;
    }

    public void setThreshold(Double threshold) {
        this.threshold = threshold;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
