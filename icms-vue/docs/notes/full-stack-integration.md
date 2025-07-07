# 前后端集成练习指南

## 1. 项目结构

### 1.1 前端项目 (Vue 3)
```
esds-vue/
├── src/
│   ├── api/          # API 请求封装
│   ├── components/   # 组件
│   ├── views/        # 页面
│   ├── store/        # Pinia 状态管理
│   └── router/       # 路由配置
```

### 1.2 后端项目 (Spring Boot)
```
esds/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/example/esds/
│       │       ├── controller/  # 控制器
│       │       ├── service/     # 服务层
│       │       ├── model/       # 数据模型
│       │       └── repository/  # 数据访问层
│       └── resources/
│           └── application.properties  # 配置文件
```

## 2. 练习任务：用户管理系统

### 2.1 后端实现

#### 2.1.1 用户实体类
```java
// User.java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private Integer age;
    private String email;
    
    // getters and setters
}
```

#### 2.1.2 用户控制器
```java
// UserController.java
@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "http://localhost:5173") // Vue 开发服务器地址
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public List<User> getAllUsers() {
        return userService.findAll();
    }
    
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        return userService.findById(id);
    }
    
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }
    
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User user) {
        return userService.update(id, user);
    }
    
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

### 2.2 前端实现

#### 2.2.1 API 封装
```javascript
// src/api/user.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 5000
})

export const userApi = {
  // 获取所有用户
  getUsers() {
    return api.get('/users')
  },
  
  // 获取单个用户
  getUser(id) {
    return api.get(`/users/${id}`)
  },
  
  // 创建用户
  createUser(user) {
    return api.post('/users', user)
  },
  
  // 更新用户
  updateUser(id, user) {
    return api.put(`/users/${id}`, user)
  },
  
  // 删除用户
  deleteUser(id) {
    return api.delete(`/users/${id}`)
  }
}
```

#### 2.2.2 Pinia Store
```javascript
// src/store/user.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userApi } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 获取所有用户
  async function fetchUsers() {
    loading.value = true
    error.value = null
    try {
      const response = await userApi.getUsers()
      users.value = response.data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // 创建用户
  async function createUser(user) {
    loading.value = true
    error.value = null
    try {
      const response = await userApi.createUser(user)
      users.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新用户
  async function updateUser(id, userData) {
    loading.value = true
    error.value = null
    try {
      const response = await userApi.updateUser(id, userData)
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除用户
  async function deleteUser(id) {
    loading.value = true
    error.value = null
    try {
      await userApi.deleteUser(id)
      users.value = users.value.filter(u => u.id !== id)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    users,
    loading,
    error,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser
  }
})
```

#### 2.2.3 用户列表组件
```vue
<!-- src/views/UserList.vue -->
<template>
  <div class="user-list">
    <h2>用户列表</h2>
    
    <!-- 加载状态 -->
    <div v-if="userStore.loading" class="loading">
      加载中...
    </div>
    
    <!-- 错误提示 -->
    <div v-if="userStore.error" class="error">
      {{ userStore.error }}
    </div>
    
    <!-- 用户表单 -->
    <div class="add-user">
      <input v-model="newUser.name" placeholder="用户名" />
      <input type="number" v-model="newUser.age" placeholder="年龄" />
      <input v-model="newUser.email" placeholder="邮箱" />
      <button @click="handleAddUser" :disabled="userStore.loading">
        添加用户
      </button>
    </div>
    
    <!-- 用户列表 -->
    <ul v-if="!userStore.loading && !userStore.error">
      <li v-for="user in userStore.users" :key="user.id">
        <router-link :to="{ name: 'userDetail', params: { id: user.id }}">
          {{ user.name }} ({{ user.age }}) - {{ user.email }}
        </router-link>
        <button @click="handleDeleteUser(user.id)" :disabled="userStore.loading">
          删除
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const newUser = ref({ name: '', age: '', email: '' })

// 组件挂载时获取用户列表
onMounted(async () => {
  await userStore.fetchUsers()
})

// 添加用户
const handleAddUser = async () => {
  try {
    await userStore.createUser(newUser.value)
    newUser.value = { name: '', age: '', email: '' }
  } catch (error) {
    console.error('添加用户失败:', error)
  }
}

// 删除用户
const handleDeleteUser = async (id) => {
  try {
    await userStore.deleteUser(id)
  } catch (error) {
    console.error('删除用户失败:', error)
  }
}
</script>

<style scoped>
.user-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: red;
  padding: 10px;
  margin-bottom: 20px;
  border: 1px solid red;
  border-radius: 4px;
}

.add-user {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.add-user input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

a {
  color: #333;
  text-decoration: none;
}

a:hover {
  color: #4CAF50;
}
</style>
```

## 3. 开发步骤

1. 后端开发
   - 在 IDEA 中创建 Spring Boot 项目
   - 实现用户实体类和数据库表
   - 实现用户服务层和控制器
   - 配置跨域和数据库连接

2. 前端开发
   - 创建 API 请求封装
   - 实现 Pinia store 管理用户状态
   - 实现用户列表和详情页面
   - 添加加载状态和错误处理

3. 集成测试
   - 启动后端服务（默认端口 8080）
   - 启动前端开发服务器（默认端口 5173）
   - 测试用户 CRUD 操作
   - 检查错误处理和加载状态

## 4. 注意事项

1. 跨域配置
   - 后端需要配置 CORS
   - 前端需要正确设置 API 基础 URL

2. 错误处理
   - 前端需要处理网络错误
   - 后端需要返回合适的错误信息

3. 数据验证
   - 前端进行基本的数据验证
   - 后端进行更严格的数据验证

4. 状态管理
   - 使用 Pinia 管理全局状态
   - 合理使用 loading 和 error 状态

## 5. 进阶练习

1. 添加用户认证
   - 实现登录/注册功能
   - 添加 JWT 认证
   - 保护需要认证的 API

2. 添加数据筛选和分页
   - 实现用户搜索功能
   - 添加分页功能
   - 优化数据加载性能

3. 添加数据可视化
   - 使用图表展示用户数据
   - 添加数据统计功能
   - 实现数据导出功能 