<template>
  <div class="news-list-skeleton">
    <div
      v-for="i in count"
      :key="i"
      class="skeleton-item"
    >
      <div class="skeleton-content">
        <div class="skeleton-title skeleton"></div>
        <div class="skeleton-desc skeleton"></div>
        <div class="skeleton-info skeleton"></div>
      </div>
      <div class="skeleton-image skeleton"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  count: {
    type: Number,
    default: 6
  }
})
</script>

<style scoped>
.news-list-skeleton {
  padding: 8px 0;
}

.skeleton-item {
  display: flex;
  padding: 14px 16px;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--divider-color);
}

.skeleton-content {
  flex: 1;
  margin-right: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 80px;
}

.skeleton-title {
  height: 18px;
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
}

.skeleton-desc {
  height: 14px;
  width: 80%;
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
}

.skeleton-info {
  height: 12px;
  width: 50%;
  border-radius: var(--radius-sm);
}

.skeleton-image {
  width: 120px;
  height: 80px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
}
</style>
