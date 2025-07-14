package com.yeye.icmsjava.service;

import com.yeye.icmsjava.model.User;
import com.baomidou.mybatisplus.extension.service.IService;
import jakarta.servlet.http.HttpServletRequest;

/**
* @author Administrator
* @description 针对表【user(用户表，包含认证用户的面部特征信息)】的数据库操作Service
* @createDate 2025-07-10 16:29:42
*/
public interface UserService extends IService<User> {
        /**
         * 用户注册
         *
         * @param  username 用户名
         * @param password 用户类
         * @param checkPassword 确认密码
         * @return 新用户id
         */
        int userRegister(String username, String password, String checkPassword,String faceEmbedding,String role);

        /**
         *
         * @param username
         * @param password
         * @return 脱敏后的用户信息
         */
        User userLogin(String username, String password, HttpServletRequest request,String faceEmbedding);

        /**
         * 用户脱敏
         *
         * @param originUser 未脱敏用户
         * @return 安全用户信息
         */
         User getSaftyUser(User originUser);

        /**
         *
         * @param username
         * @param faceImage
         * @return 脱敏后的用户信息
         */
        User userSignin(String username, HttpServletRequest request,String faceImage);
}
