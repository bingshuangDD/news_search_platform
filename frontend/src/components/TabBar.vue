<template>
  <van-tabbar route active-color="var(--primary)" inactive-color="var(--text-tertiary)">
    <van-tabbar-item to="/home" icon="home-o">{{ $t('nav.home') }}</van-tabbar-item>
    <van-tabbar-item to="/aichat" icon="chat-o">{{ $t('nav.aiChat') }}</van-tabbar-item>
    <van-tabbar-item to="/my" icon="user-o">{{ $t('nav.my') }}</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
// TabBar 完全由 Vant 的 route 模式驱动，无需手动管理 active 状态
</script>

<style scoped>
:deep(.van-tabbar) {
  background-color: var(--bg-surface);
  box-shadow: 0 -1px 0 var(--border-color);
  border-top: none;
}

:deep(.van-tabbar-item__icon) {
  font-size: 22px;
}

:deep(.van-tabbar-item__text) {
  font-size: 11px;
}
</style>
