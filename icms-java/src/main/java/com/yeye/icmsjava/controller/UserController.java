package com.yeye.icmsjava.controller;

import com.yeye.icmsjava.model.User;
import com.yeye.icmsjava.model.request.UserLoginRequest;
import com.yeye.icmsjava.model.request.UserRegisterRequest;
import com.yeye.icmsjava.model.request.UserSigninRequest;
import com.yeye.icmsjava.service.UserService;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.annotation.Resource;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.apache.commons.lang3.StringUtils;

import com.yeye.icmsjava.model.User;
import com.yeye.icmsjava.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;

import static com.yeye.icmsjava.contant.UserConstant.USER_LOGIN_STATE;

@RestController
@RequestMapping("/user")
@Tag(name = "用户管理接口", description = "提供用户注册、登录、获取当前用户、退出登录等功能接口")
public class UserController {
    @Resource
    private UserService userService;

    @PostMapping("/register")
    @Operation(summary = "用户注册接口", description = "接收用户注册信息，完成用户注册操作，返回注册结果状态码")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "注册结果，1 表示成功，0 表示失败",
                    content = @Content(schema = @Schema(type = "integer", example = "1"))),
            @ApiResponse(responseCode = "400", description = "请求体为空或参数不合法",
                    content = @Content(schema = @Schema(type = "string", example = "请求体不能为空")))
    })
    public int userRegister(
            @RequestBody
            @Parameter(
                    name = "userRegisterRequest",
                    description = "注册信息（用户名、密码、确认密码）",
                    content = @Content(
                            schema = @Schema(
                                    implementation = UserRegisterRequest.class,
                                    example = "{\"username\":\"test_user\", \"password\":\"123456\", \"checkPassword\":\"123456\"}"
                            )
                    )
            )
            UserRegisterRequest userRegisterRequest) {
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
    @Operation(summary = "用户登录接口", description = "接收用户登录信息，验证通过后返回用户信息，登录失败返回对应提示")
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
    @Operation(summary = "获取当前用户接口", description = "从会话中获取当前登录用户的用户名并返回")
    public User getCurrentUser(HttpServletRequest request) {
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
        System.out.println(currentUser);
        return currentUser;
    }

    @PostMapping("/logout")
    @Operation(summary = "用户退出登录接口", description = "使当前用户会话失效，清除相关 Cookie，完成退出操作")
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

    @PostMapping("/signin")
    @Operation(summary = "用户签到接口", description = "接收用户签到信息，验证通过后返回用户信息，签到失败返回对应提示")
    public ResponseEntity<?> userSignin(@RequestBody UserSigninRequest userSigninRequest, HttpServletRequest request) {
        if (userSigninRequest == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("请求体不能为空");
        }

        String username = userSigninRequest.getUsername();
        String faceImage=userSigninRequest.getFaceImage();

        System.out.println(username+"发起签到请求");

        if (StringUtils.isAnyBlank(username)) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("用户名不能为空");
        }
        // 调用服务层进行登录验证
        User user = userService.userSignin(username, request,faceImage);

        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("签到失败");
        }
        System.out.println("已返回用户信息");
        // 签到成功，返回用户信息
        return ResponseEntity.ok(user);
    }
}
