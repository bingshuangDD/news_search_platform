<template>
  <div class="app">
    <router-view v-slot="{ Component, route }">
      <transition :name="route.meta.transition || 'page-fade'" mode="out-in">
        <template v-if="route.meta.keepAlive">
          <keep-alive>
            <component :is="Component" :key="route.path" />
          </keep-alive>
        </template>
        <template v-else>
          <component :is="Component" :key="route.path" />
        </template>
      </transition>
    </router-view>
  </div>
</template>

<script setup>
// App.vue 作为根组件
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 16px;
  background-color: var(--bg-base);
  color: var(--text-primary);
  height: 100%;
  width: 100%;
}

.app {
  max-width: 750px;
  margin: 0 auto;
  height: 100%;
}

/* 移动端适配 */
@media screen and (max-width: 750px) {
  html {
    font-size: calc(100vw / 750 * 16);
  }
}
</style>
