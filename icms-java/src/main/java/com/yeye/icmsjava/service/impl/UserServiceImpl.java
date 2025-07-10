package com.yeye.icmsjava.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.yeye.icmsjava.model.User;
import com.yeye.icmsjava.service.UserService;
import com.yeye.icmsjava.mapper.UserMapper;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.util.DigestUtils;

/**
* @author Administrator
* @description 针对表【user(用户表，包含认证用户的面部特征信息)】的数据库操作Service实现
* @createDate 2025-07-10 16:29:42
*/
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User>
    implements UserService{
        @Resource
        private UserMapper userMapper;//注入userMapper
        /**
         * 盐值：混淆密码
         */
        private static final String SALT="caoyue";
        /**
         * 用户登录态键：通过键可以找到唯一的一条数据
         */
        private static final String USER_LOGIN_STATE="user_login_state";

        @Override
        public int userRegister(String username, String password, String checkPassword,String faceEmbedding) {
            //一，校验
            //1.非空
            if(StringUtils.isAnyBlank(username,password,checkPassword,faceEmbedding)){
                //todo:修改为自定义异常
                return -1;
            }
            //2.用户名不小于2和密码不小于4
            if(username.length()<2||password.length()<4||checkPassword.length()<4){
                return -1;
            }
            //4.用户名不能包含特殊字符
            String regex = "^[\\u4e00-\\u9fa5a-zA-Z0-9]+$"; // 只允许中文、英文字母、数字
            if (!username.matches(regex)) {
                return -1;
            }

            //两次输入密码相同
            if(!password.equals(checkPassword)){
                return -1;
            }
            //3.用户名不能重复：查询数据库(放最后节约型性能)
            QueryWrapper<User> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("username", username);
            long count = userMapper.selectCount(queryWrapper);
            if(count>0){
                return -1;
            }

            //二.加密
            String newPassword= DigestUtils.md5DigestAsHex((SALT+password).getBytes());

            //插入数据
            User user=new User();
            user.setUsername(username);
            user.setPassword(newPassword);
            user.setFaceEmbedding(faceEmbedding);
            boolean saveResult=this.save(user);//service的方法，userMapper.insert(user)返回Int类型
            if(!saveResult){
                return -1;
            }

            return user.getUserId();

        }

        @Override
        public User userLogin(String username, String password, HttpServletRequest request,String faceEmbedding) {
            //一，校验用户名和密码是否合法
            //一，校验
            //1.非空
            if(StringUtils.isAnyBlank(username,password)){
                System.out.println("1");
                return null;
            }
            //2.用户名不小于2和密码不小于4
            if(username.length()<2||password.length()<4){
                System.out.println("2");
                return null;
            }
            //4.用户名不能包含特殊字符
            // 校验用户名，只允许中文、英文字母、数字
            //可以防止sql注入
            String regex = "^[\\u4e00-\\u9fa5a-zA-Z0-9]+$"; // 只允许中文、英文字母、数字
            if (!username.matches(regex)) {
                System.out.println("3");
                return null;
            }

//     二，加密,因为数据库里存的也是加密后的密码
        String newPassword=DigestUtils.md5DigestAsHex((SALT+password).getBytes());

            //三，查询用户是否存在
            QueryWrapper<User> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("username", username);
            queryWrapper.eq("password", password);
            //如何验证人脸？
            queryWrapper.eq("faceEmbedding", faceEmbedding);
            User user=userMapper.selectOne(queryWrapper);
            System.out.println(user);
            //用户不存在
            if(user==null){
                System.out.println("4");
                return null;
            }

            //四，用户脱敏:只返回需要显示的数据，防止数据库的数据暴露给前端
            User saftyUser=getSaftyUser(user);
            //五，记录用户的登录态
            request.getSession().setAttribute(USER_LOGIN_STATE,user);
            System.out.println("Backend recorded login user data: " + saftyUser);

            System.out.println("Session ID (save): " + request.getSession().getId());

            return saftyUser;
        }

        /**
         * 用户脱敏
         *
         * @param originUser
         * @return
         */
        public User getSaftyUser(User originUser){
            if(originUser==null){
                return null;
            }
            User saftyUser=new User();
            saftyUser.setUserId(originUser.getUserId());
            saftyUser.setUsername(originUser.getUsername());
            saftyUser.setRole(originUser.getRole());
            return saftyUser;
        }

}




