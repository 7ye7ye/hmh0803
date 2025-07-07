# Vue 3 响应式系统学习指南

## 1. 响应式基础

### 1.1 ref 和 reactive
```javascript
import { ref, reactive } from 'vue'

// ref 用于基本类型
const count = ref(0)
const message = ref('Hello')

// reactive 用于对象
const user = reactive({
  name: 'John',
  age: 20
})

// 在模板中使用
// <div>{{ count }}</div>
// <div>{{ user.name }}</div>
```

### 1.2 响应式原理
- ref 和 reactive 都是 Vue 3 的响应式 API
- ref 用于基本类型（string、number、boolean 等）
- reactive 用于对象类型
- 在 JS 中访问 ref 值需要使用 .value
- 在模板中访问 ref 值不需要 .value

### 1.3 响应式更新
```javascript
// 更新 ref 值
count.value++

// 更新 reactive 对象
user.name = 'Jane'
user.age = 21
```

## 2. 计算属性和监听器

### 2.1 computed
```javascript
import { computed } from 'vue'

// 计算属性
const doubleCount = computed(() => count.value * 2)

// 带缓存的计算属性
const userInfo = computed({
  get: () => `${user.name} (${user.age})`,
  set: (newValue) => {
    const [name, age] = newValue.split(' (')
    user.name = name
    user.age = parseInt(age)
  }
})
```

### 2.2 watch 和 watchEffect
```javascript
import { watch, watchEffect } from 'vue'

// 监听特定值
watch(count, (newValue, oldValue) => {
  console.log('count changed:', newValue, oldValue)
})

// 监听多个值
watch([count, () => user.name], ([newCount, newName]) => {
  console.log('values changed:', newCount, newName)
})

// 自动追踪依赖
watchEffect(() => {
  console.log('count is:', count.value)
  console.log('user name is:', user.name)
})
```

## 3. 生命周期钩子

### 3.1 组合式 API 中的生命周期
```javascript
import { onMounted, onUpdated, onUnmounted } from 'vue'

// 组件挂载时
onMounted(() => {
  console.log('Component mounted')
})

// 组件更新时
onUpdated(() => {
  console.log('Component updated')
})

// 组件卸载时
onUnmounted(() => {
  console.log('Component unmounted')
})
```

## 4. 练习任务

### 练习 1：计数器组件
创建一个计数器组件，包含以下功能：
1. 显示当前计数
2. 增加和减少按钮
3. 显示计数的平方值
4. 当计数大于 10 时显示警告信息

```vue
<!-- Counter.vue -->
<template>
  <div class="counter">
    <h2>计数器: {{ count }}</h2>
    <p>平方值: {{ squareCount }}</p>
    <p v-if="count > 10" class="warning">计数超过 10！</p>
    <div class="buttons">
      <button @click="increment">+</button>
      <button @click="decrement">-</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const count = ref(0)
const squareCount = computed(() => count.value * count.value)

const increment = () => {
  count.value++
}

const decrement = () => {
  count.value--
}
</script>

<style scoped>
.counter {
  text-align: center;
  padding: 20px;
}

.warning {
  color: red;
  font-weight: bold;
}

.buttons {
  margin-top: 10px;
}

button {
  margin: 0 5px;
  padding: 5px 15px;
  font-size: 18px;
}
</style>
```

### 练习 2：用户信息表单
创建一个用户信息表单，包含以下功能：
1. 输入用户名和年龄
2. 实时显示用户信息
3. 表单验证（年龄必须大于 0）
4. 提交时显示完整信息

```vue
<!-- UserForm.vue -->
<template>
  <div class="user-form">
    <h2>用户信息</h2>
    <div class="form-group">
      <label>用户名：</label>
      <input v-model="user.name" />
    </div>
    <div class="form-group">
      <label>年龄：</label>
      <input type="number" v-model="user.age" />
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <button @click="submit" :disabled="!!error">提交</button>
    <div v-if="submitted" class="result">
      <h3>提交的信息：</h3>
      <p>用户名：{{ user.name }}</p>
      <p>年龄：{{ user.age }}</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'

const user = reactive({
  name: '',
  age: ''
})

const submitted = ref(false)
const error = computed(() => {
  if (user.age <= 0) {
    return '年龄必须大于 0'
  }
  return ''
})

const submit = () => {
  submitted.value = true
}
</script>

<style scoped>
.user-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.error {
  color: red;
  margin-bottom: 10px;
}

.result {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
```

### 练习 3：待办事项列表
创建一个待办事项列表，包含以下功能：
1. 添加新的待办事项
2. 标记待办事项为已完成
3. 删除待办事项
4. 显示完成和未完成的数量

```vue
<!-- TodoList.vue -->
<template>
  <div class="todo-list">
    <h2>待办事项</h2>
    <div class="add-todo">
      <input v-model="newTodo" @keyup.enter="addTodo" placeholder="添加新待办" />
      <button @click="addTodo">添加</button>
    </div>
    <div class="stats">
      <p>未完成: {{ incompleteCount }}</p>
      <p>已完成: {{ completeCount }}</p>
    </div>
    <ul class="todos">
      <li v-for="todo in todos" :key="todo.id" :class="{ completed: todo.completed }">
        <input type="checkbox" v-model="todo.completed" />
        <span>{{ todo.text }}</span>
        <button @click="removeTodo(todo.id)">删除</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const newTodo = ref('')
const todos = ref([])

const addTodo = () => {
  if (newTodo.value.trim()) {
    todos.value.push({
      id: Date.now(),
      text: newTodo.value,
      completed: false
    })
    newTodo.value = ''
  }
}

const removeTodo = (id) => {
  todos.value = todos.value.filter(todo => todo.id !== id)
}

const completeCount = computed(() => 
  todos.value.filter(todo => todo.completed).length
)

const incompleteCount = computed(() => 
  todos.value.filter(todo => !todo.completed).length
)
</script>

<style scoped>
.todo-list {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.add-todo {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.stats {
  margin-bottom: 20px;
}

.todos {
  list-style: none;
  padding: 0;
}

.todos li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.completed span {
  text-decoration: line-through;
  color: #999;
}
</style>
```

## 5. 进阶练习：结合 Pinia 和 Vue Router

### 练习 4：用户管理系统
创建一个简单的用户管理系统，包含以下功能：
1. 用户列表页面
2. 用户详情页面
3. 使用 Pinia 管理用户状态
4. 使用 Vue Router 进行路由管理

```javascript
// stores/user.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const users = ref([
    { id: 1, name: 'John', age: 20 },
    { id: 2, name: 'Jane', age: 25 }
  ])

  const addUser = (user) => {
    users.value.push(user)
  }

  const updateUser = (id, userData) => {
    const index = users.value.findIndex(u => u.id === id)
    if (index !== -1) {
      users.value[index] = { ...users.value[index], ...userData }
    }
  }

  const deleteUser = (id) => {
    users.value = users.value.filter(u => u.id !== id)
  }

  return {
    users,
    addUser,
    updateUser,
    deleteUser
  }
})
```

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import UserList from '@/views/UserList.vue'
import UserDetail from '@/views/UserDetail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/users',
      name: 'userList',
      component: UserList
    },
    {
      path: '/users/:id',
      name: 'userDetail',
      component: UserDetail
    }
  ]
})

export default router
```

```vue
<!-- views/UserList.vue -->
<template>
  <div class="user-list">
    <h2>用户列表</h2>
    <div class="add-user">
      <input v-model="newUser.name" placeholder="用户名" />
      <input type="number" v-model="newUser.age" placeholder="年龄" />
      <button @click="addUser">添加用户</button>
    </div>
    <ul>
      <li v-for="user in userStore.users" :key="user.id">
        <router-link :to="{ name: 'userDetail', params: { id: user.id }}">
          {{ user.name }} ({{ user.age }})
        </router-link>
        <button @click="deleteUser(user.id)">删除</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const newUser = ref({ name: '', age: '' })

const addUser = () => {
  if (newUser.value.name && newUser.value.age) {
    userStore.addUser({
      id: Date.now(),
      ...newUser.value
    })
    newUser.value = { name: '', age: '' }
  }
}

const deleteUser = (id) => {
  userStore.deleteUser(id)
}
</script>

<style scoped>
.user-list {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.add-user {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
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
</style>
```

```vue
<!-- views/UserDetail.vue -->
<template>
  <div class="user-detail">
    <h2>用户详情</h2>
    <div v-if="user">
      <div class="form-group">
        <label>用户名：</label>
        <input v-model="editedUser.name" />
      </div>
      <div class="form-group">
        <label>年龄：</label>
        <input type="number" v-model="editedUser.age" />
      </div>
      <button @click="saveUser">保存</button>
    </div>
    <p v-else>用户不存在</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const user = computed(() => 
  userStore.users.find(u => u.id === parseInt(route.params.id))
)

const editedUser = ref({ name: '', age: '' })

// 当用户数据加载时，初始化编辑表单
if (user.value) {
  editedUser.value = { ...user.value }
}

const saveUser = () => {
  if (user.value) {
    userStore.updateUser(user.value.id, editedUser.value)
    router.push('/users')
  }
}
</script>

<style scoped>
.user-detail {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}
</style>
```

## 6. 总结

Vue 3 的响应式系统提供了：
1. 简单直观的 API（ref、reactive）
2. 强大的计算属性（computed）
3. 灵活的数据监听（watch、watchEffect）
4. 完整的生命周期钩子

使用这些特性时要注意：
1. 正确使用 ref 和 reactive
2. 合理使用计算属性优化性能
3. 适当使用监听器处理副作用
4. 注意响应式数据的解包和访问方式 