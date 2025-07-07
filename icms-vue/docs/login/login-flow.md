# 登录功能说明文档

## 1. 登录流程

### 1.1 前端发送请求
```javascript
// 发送的数据格式
{
    username: "用户名",
    password: "密码"
}
```

### 1.2 后端返回数据
```javascript
// 返回的数据格式
{
    id: 3,                // 用户ID
    username: "用户名",
    password: null,       // 密码字段（后端会置空）
    userLevel: 0,        // 用户级别：0-普通用户，1-管理员
    isDeleted: null
}
```

### 1.3 处理流程
1. 用户点击登录按钮
2. 前端收集表单数据（用户名和密码）
3. 调用 `userApi.login()` 发送请求
4. 后端验证成功后返回用户信息
5. 前端根据返回的用户信息：
   - 将用户名保存到 Pinia store 中
   - 根据 userLevel 决定跳转路径：
     - userLevel = 0：跳转到普通用户页面 `/home`
     - userLevel = 1：跳转到管理员页面 `/admin`

## 2. 状态管理说明

### 2.1 Pinia Store
```javascript
// useLoginUserStore.js
const loginUser = ref({
    username: '未登录'
});

// 保存登录状态
function setLoginUser(username) {
    loginUser.value = {
        username: username || '未登录'
    };
}
```

### 2.2 登录状态维护
- 使用 Cookie 保持会话（withCredentials: true）
- 用户信息存储在 Pinia store 中
- 可以通过 `fetchLoginUser()` 随时获取最新用户状态

## 3. 路由权限控制

### 3.1 路由配置
```javascript
{
    path: '/home',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }  // 需要登录才能访问
},
{
    path: '/admin',
    name: 'admin',
    component: AdminView,
    meta: { requiresAuth: true, requiresAdmin: true }  // 需要管理员权限
}
```

### 3.2 路由守卫
- 检查访问页面是否需要登录（meta.requiresAuth）
- 检查访问页面是否需要管理员权限（meta.requiresAdmin）
- 未登录用户重定向到登录页面
- 登录后返回原来要访问的页面
- 普通用户访问管理员页面会被重定向到首页

## 4. 注意事项

1. 登录接口直接返回用户对象，不需要检查 code 字段
2. 密码在传输时是明文，建议后续添加加密
3. 所有请求都需要设置 withCredentials: true 以保持会话
4. 用户级别（userLevel）决定了用户的权限和可访问的页面
5. 路由跳转前会进行权限检查

## 5. 可优化项

1. 添加密码加密
2. 添加登录失败次数限制
3. 添加记住密码功能
4. 添加自动登录功能
5. 添加登录验证码
6. 完善错误提示信息
7. 添加路由切换动画
8. 优化权限控制逻辑 