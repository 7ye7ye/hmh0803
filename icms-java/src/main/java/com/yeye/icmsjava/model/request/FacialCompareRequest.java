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
}
