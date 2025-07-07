// 用户类型定义
export interface UserType {
    id?: number;
    username: string;
    userAccount?: string;
    avatarUrl?: string;
    gender?: number;
    phone?: string;
    email?: string;
    userStatus?: number;
    userRole?: number;
    createTime?: string;
    // ... 其他可能的字段
}

// 通用响应类型
export interface BaseResponse<T> {
    code: number;
    data: T;
    message: string;
    description: string;
} 