# Pinia Store 使用指南

## 1. Store 的基本概念

### 1.1 什么是 Store？
- Store 是 Pinia 中的状态管理单元
- 用于集中管理应用的状态（state）
- 类似于 Vuex，但更轻量级且支持 TypeScript

### 1.2 Store 的优势
1. 状态集中管理
2. 支持 TypeScript
3. 支持 Vue 3 组合式 API
4. 支持代码分割
5. 支持开发者工具

## 2. Store 的创建和使用

### 2.1 创建 Store
```javascript
// stores/counter.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 选项式 API 风格
export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    name: 'Counter'
  }),
  getters: {
    doubleCount: (state) => state.count * 2
  },
  actions: {
    increment() {
      this.count++
    }
  }
})

// 组合式 API 风格（推荐）
export const useCounterStore = defineStore('counter', () => {
  // 状态
  const count = ref(0)
  const name = ref('Counter')

  // getter
  const doubleCount = computed(() => count.value * 2)

  // action
  function increment() {
    count.value++
  }

  return {
    count,
    name,
    doubleCount,
    increment
  }
})
```

### 2.2 在组件中使用 Store
```javascript
<script setup>
import { useCounterStore } from '@/stores/counter'

const store = useCounterStore()

// 访问状态
console.log(store.count)

// 调用 action
store.increment()

// 访问 getter
console.log(store.doubleCount)
</script>
```

## 3. Store 的核心概念

### 3.1 State（状态）
```javascript
// 定义状态
const count = ref(0)
const user = ref({
  name: 'John',
  age: 20
})

// 返回状态
return {
  count,
  user
}
```

### 3.2 Getters（计算属性）
```javascript
// 定义 getter
const doubleCount = computed(() => count.value * 2)
const userInfo = computed(() => `${user.value.name} (${user.value.age})`)

// 返回 getter
return {
  doubleCount,
  userInfo
}
```

### 3.3 Actions（方法）
```javascript
// 定义 action
function increment() {
  count.value++
}

async function fetchUser() {
  const response = await api.getUser()
  user.value = response.data
}

// 返回 action
return {
  increment,
  fetchUser
}
```

## 4. Store 的高级特性

### 4.1 Store 持久化
```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  
  return {
    user
  }
}, {
  persist: true // 启用持久化
})
```

### 4.2 Store 订阅
```javascript
// 监听 store 的变化
store.$subscribe((mutation, state) => {
  console.log('Store changed:', mutation)
})
```

### 4.3 Store 重置
```javascript
// 重置 store 到初始状态
store.$reset()
```

## 5. 最佳实践

### 5.1 Store 的命名和组织
```javascript
// 按功能模块组织 store
stores/
  ├── user.js      // 用户相关状态
  ├── menu.js      // 菜单相关状态
  └── settings.js  // 设置相关状态
```

### 5.2 状态设计原则
1. 单一职责原则
   - 每个 store 只管理一个领域的状态
   - 避免在一个 store 中混合不同领域的状态

2. 状态最小化
   - 只存储必要的状态
   - 避免存储可以从其他状态计算出的数据

3. 状态扁平化
   - 避免过深的状态嵌套
   - 使用 getter 处理复杂的数据转换

### 5.3 代码示例
```javascript
// stores/menu.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMenuStore = defineStore('menu', () => {
  // 状态
  const currentMenu = ref('home')
  const menuItems = ref([
    { key: 'home', label: '首页' },
  ])

  // getter
  const currentMenuItem = computed(() => 
    menuItems.value.find(item => item.key === currentMenu.value)
  )

  // action
  function setCurrentMenu(menu) {
    currentMenu.value = menu
  }

  return {
    currentMenu,
    menuItems,
    currentMenuItem,
    setCurrentMenu
  }
}, {
  persist: true
})
```

## 6. 常见问题和解决方案

### 6.1 状态更新问题
问题：状态更新后视图没有更新
解决：
```javascript
// 确保使用 ref 或 reactive
const count = ref(0)  // 正确
let count = 0        // 错误
```

### 6.2 异步操作
```javascript
async function fetchData() {
  try {
    const response = await api.getData()
    data.value = response.data
  } catch (error) {
    console.error('Error:', error)
  }
}
```

### 6.3 状态持久化问题
问题：刷新页面后状态丢失
解决：
```javascript
defineStore('store', {
  // ... store 配置
}, {
  persist: {
    key: 'store-key',  // 存储的键名
    storage: localStorage  // 存储方式
  }
})
```

## 7. 调试技巧

### 7.1 使用 Vue DevTools
- 安装 Vue DevTools 插件
- 在开发者工具中查看 store 状态
- 可以追踪状态变化

### 7.2 日志记录
```javascript
function updateState(newValue) {
  console.log('Before update:', state.value)
  state.value = newValue
  console.log('After update:', state.value)
}
```

## 8. 总结

Pinia Store 提供了：
1. 清晰的状态管理方案
2. 良好的 TypeScript 支持
3. 灵活的组合式 API
4. 简单的持久化方案
5. 强大的开发者工具支持

使用 Store 时要注意：
1. 遵循单一职责原则
2. 保持状态扁平化
3. 合理使用 getter
4. 正确处理异步操作
5. 适当使用持久化 