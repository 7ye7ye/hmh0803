package com.yeye.icmsjava.model;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

/**
 * 用户表，包含认证用户的面部特征信息
 * @TableName user
 */
@TableName(value ="user")
@Data
public class User {
    /**
     * 用户唯一ID (自增)
     */
    @TableId(type = IdType.AUTO)
    private Integer userId;

    /**
     * 用户名/学号/工号 (唯一)
     */
    private String username;

    /**
     * 加密后的密码
     */
    private String password;

    /**
     * 用户角色
     */
    private Object role;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;

    /**
     * 最后更新时间
     */
    private LocalDateTime updatedAt;

    /**
     * 面部特征向量 （存储为JSON数组字符串）
     */
    private String faceEmbedding;

    /**
     * 用于注册的源照片存储路径
     */
    private String sourceImageUrl;

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
        User other = (User) that;
        return (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
            && (this.getUsername() == null ? other.getUsername() == null : this.getUsername().equals(other.getUsername()))
            && (this.getPassword() == null ? other.getPassword() == null : this.getPassword().equals(other.getPassword()))
            && (this.getRole() == null ? other.getRole() == null : this.getRole().equals(other.getRole()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()))
            && (this.getUpdatedAt() == null ? other.getUpdatedAt() == null : this.getUpdatedAt().equals(other.getUpdatedAt()))
            && (this.getFaceEmbedding() == null ? other.getFaceEmbedding() == null : this.getFaceEmbedding().equals(other.getFaceEmbedding()))
            && (this.getSourceImageUrl() == null ? other.getSourceImageUrl() == null : this.getSourceImageUrl().equals(other.getSourceImageUrl()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getUsername() == null) ? 0 : getUsername().hashCode());
        result = prime * result + ((getPassword() == null) ? 0 : getPassword().hashCode());
        result = prime * result + ((getRole() == null) ? 0 : getRole().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
        result = prime * result + ((getUpdatedAt() == null) ? 0 : getUpdatedAt().hashCode());
        result = prime * result + ((getFaceEmbedding() == null) ? 0 : getFaceEmbedding().hashCode());
        result = prime * result + ((getSourceImageUrl() == null) ? 0 : getSourceImageUrl().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", userId=").append(userId);
        sb.append(", username=").append(username);
        sb.append(", password=").append(password);
        sb.append(", role=").append(role);
        sb.append(", createdAt=").append(createdAt);
        sb.append(", updatedAt=").append(updatedAt);
        sb.append(", faceEmbedding=").append(faceEmbedding);
        sb.append(", sourceImageUrl=").append(sourceImageUrl);
        sb.append("]");
        return sb.toString();
    }
}