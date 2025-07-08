package com.yeye.icmsjava.service;

import com.yeye.icmsjava.model.User;
import com.baomidou.mybatisplus.extension.service.IService;
import jakarta.servlet.http.HttpServletRequest;

/**
* @author Administrator
* @description 针对表【user】的数据库操作Service
* @createDate 2025-07-08 15:10:41
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
    int userRegister(String username, String password, String checkPassword);

    /**
     *
     * @param username
     * @param password
     * @return 脱敏后的用户信息
     */
    User userLogin(String username, String password, HttpServletRequest request);

    /**
     * 用户脱敏
     *
     * @param originUser 未脱敏用户
     * @return 安全用户信息
     */
    public User getSaftyUser(User originUser);
}

