<template>
    <div id="basicLayout">
        <a-layout>
            <a-layout-header class="header">
                <GlobalHeader />
            </a-layout-header>
            <a-layout-content class="content">
                <router-view />
            </a-layout-content>
        </a-layout>
    </div>
</template>

<script setup>
import GlobalHeader from '@/components/GlobalHeader.vue';

</script>

<style scoped>
#basicLayout {
}

#basicLayout .header {
    width: 100%;
    background: white;
    position: fixed;
    top: 0;
    left: 0; /* 确保 Header 水平填充 */
    z-index: 10; /* 确保 Header 在最上层 */
    height: 60px; /* 增加 header 高度 */
    padding: 0 20px; /* 调整内边距 */
    box-shadow: 0 2px 8px #f0f1f2; /* 添加阴影 */
    display: flex; /* 使用 Flexbox 对齐 */
    align-items: center;
}

#basicLayout .content {
    /* 移除 position: fixed */
    background: #f0f2f5; /* 设置背景色与页面一致 */
    padding: 20px;
    margin-top: 60px; /* 添加上边距，等于 Header 的高度 */
    min-height: calc(100vh - 60px); /* 确保内容区域至少占满剩余高度 */
}
</style>


