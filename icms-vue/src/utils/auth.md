# 登录验证功能使用指南

本项目提供了一套登录验证和提示框功能，可以在需要用户登录的功能点上轻松添加验证。

## 功能介绍

1. **路由级别验证**：通过路由元信息 `meta.requiresAuth` 进行全局验证
2. **功能级别验证**：在任何需要登录的功能点上添加验证
3. **优雅的登录提示**：提供友好的登录提示框，引导用户登录
4. **重定向功能**：登录后自动回到原来访问的页面

## 使用方法

### 1. 路由级别验证

在 `router/index.js` 中配置需要登录的路由：

```js
const routes = [
  {
    path: '/protected-page',
    name: 'protectedPage',
    component: ProtectedPageComponent,
    meta: { requiresAuth: true } // 标记需要登录
  }
]
```

这样，当用户访问需要登录的路由时，系统会自动验证登录状态并提示登录。

### 2. 功能级别验证

在任何功能点（如按钮点击、链接跳转等）上添加登录验证：

```js
import { requireAuth } from '@/utils/auth'

// 在方法中使用
const handleProtectedFunction = async () => {
  // 验证用户是否已登录
  const isAuthorized = await requireAuth({
    title: '功能名称',
    message: '当前功能需要登录，请先登录',
    redirectUrl: '/optional-redirect-path'
  });
  
  // 如果已登录，执行后续操作
  if (isAuthorized) {
    // 执行需要登录的操作
    console.log('用户已登录，执行受保护的功能');
  }
};
```

### 3. API 参考

#### `requireAuth(options)`

验证用户是否已登录，如未登录则显示提示框。

**参数**：
- `options` (Object): 配置选项
  - `title` (String): 提示框标题，默认为 "登录提示"
  - `message` (String): 提示信息，默认为 "当前功能需要登录才能使用"
  - `redirectUrl` (String): 登录后重定向的URL，默认为当前路径

**返回值**：
- `Promise<boolean>`: 表示用户是否已登录

#### `showLoginPrompt(options)`

仅显示登录提示框，不进行验证。

**参数**：
与 `requireAuth` 相同

**返回值**：
- `Promise<boolean>`: 始终为 false，表示用户点击了关闭

#### `checkIsLoggedIn()`

仅检查用户是否已登录，不显示提示框。

**返回值**：
- `Promise<boolean>`: 表示用户是否已登录

## 示例

### 在按钮点击时验证

```vue
<template>
  <button @click="handleClick">需要登录的功能</button>
</template>

<script setup>
import { requireAuth } from '@/utils/auth'

const handleClick = async () => {
  const isAuthorized = await requireAuth({
    message: '此功能需要登录才能使用，请先登录'
  });
  
  if (isAuthorized) {
    // 执行需要登录的操作
  }
}
</script>
```

### 在路由跳转前验证

```js
const navigateToProtectedPage = async () => {
  const isAuthorized = await requireAuth();
  
  if (isAuthorized) {
    router.push('/protected-page');
  }
};
``` 