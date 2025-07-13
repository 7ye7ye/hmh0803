package com.yeye.icmsjava.controller;

import com.yeye.icmsjava.model.User;
import com.yeye.icmsjava.model.request.UserLoginRequest;
import com.yeye.icmsjava.model.request.UserRegisterRequest;
import com.yeye.icmsjava.service.UserService;
import jakarta.annotation.Resource;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.apache.commons.lang3.StringUtils;

import java.util.HashMap;

import static com.yeye.icmsjava.contant.UserConstant.USER_LOGIN_STATE;

@RestController
@RequestMapping("/user")
public class UserController {
    @Resource
    private UserService userService;

    @PostMapping("/register")
    public int userRegister(@RequestBody UserRegisterRequest userRegisterRequest) {
        if(userRegisterRequest==null){
            return 0;
        }
        String username=userRegisterRequest.getUsername();
        String password=userRegisterRequest.getPassword();
        String checkPassword=userRegisterRequest.getCheckPassword();
        String faceEmbedding=userRegisterRequest.getFaceEmbedding();

        if(StringUtils.isAnyBlank(username,password,checkPassword,faceEmbedding)){
            return 0;
        }
        return userService.userRegister(username,password,checkPassword,faceEmbedding);
    }

    @PostMapping("/login")
    public ResponseEntity<?> userLogin(@RequestBody UserLoginRequest userLoginRequest, HttpServletRequest request) {
        if (userLoginRequest == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("请求体不能为空");
        }

        String username = userLoginRequest.getUsername();
        String password = userLoginRequest.getPassword();
        String faceEmbedding=userLoginRequest.getFaceEmbedding();

        System.out.println(username);
        System.out.println(password);

        if (StringUtils.isAnyBlank(username, password)) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("用户名和密码不能为空");
        }
        // 调用服务层进行登录验证
        User user = userService.userLogin(username, password, request,faceEmbedding);

        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("登录失败");
        }
        System.out.println("已返回用户信息");
        // 登录成功，返回用户信息
        return ResponseEntity.ok(user);
    }

    //USER_LOGIN_STATE还有问题
    @GetMapping("/current")
    public String getCurrentUser(HttpServletRequest request) {
        Object userObj=null;
        try {
            userObj = request.getSession().getAttribute(USER_LOGIN_STATE);
            System.out.println("Retrieved user info: " + userObj);
            System.out.println("Session ID (get): " + request.getSession().getId());

        } catch (Exception e) {
            e.printStackTrace();
        }
        User currentUser = (User) userObj;
        if(currentUser==null){
            return null;
        }
        return currentUser.getUsername();
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout(HttpServletRequest request, HttpServletResponse response) {
        try {
            // 获取当前会话
            HttpSession session = request.getSession(false);
            if (session != null) {
                // 使会话失效
                session.invalidate();
            }

            // 清除相关的 cookie
            Cookie[] cookies = request.getCookies();
            if (cookies != null) {
                for (Cookie cookie : cookies) {
                    if ("JSESSIONID".equals(cookie.getName())) {
                        cookie.setValue("");
                        cookie.setPath("/");
                        cookie.setMaxAge(0);
                        response.addCookie(cookie);
                    }
                }
            }

            return ResponseEntity.ok().body(new HashMap<String, Object>() {{
                put("code", 0);
                put("message", "退出成功");
            }});
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new HashMap<String, Object>() {{
                        put("code", 500);
                        put("message", "退出失败");
                    }});
        }
    }
}
