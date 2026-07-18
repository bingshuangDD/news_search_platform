<template>
  <div class="news-card clickable" @click="goToDetail">
    <div v-if="image" class="news-image">
      <van-image
        :src="image"
        :alt="title"
        width="120"
        height="80"
        fit="cover"
        radius="12"
        lazy-load
      >
        <template #loading>
          <div class="image-placeholder">
            <van-icon name="photo-o" size="20" color="var(--text-tertiary)" />
          </div>
        </template>
        <template #error>
          <div class="image-placeholder">
            <van-icon name="photo-fail-o" size="20" color="var(--text-tertiary)" />
          </div>
        </template>
      </van-image>
    </div>

    <div class="news-content">
      <div class="news-title ellipsis-2">{{ title }}</div>
      <div class="news-meta">
        <slot name="meta">
          <span v-if="author">{{ author }}</span>
          <span v-if="time">{{ time }}</span>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  id: {
    type: [Number, String],
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  image: {
    type: String,
    default: ''
  },
  author: {
    type: String,
    default: ''
  },
  time: {
    type: String,
    default: ''
  }
})

const router = useRouter()

const goToDetail = () => {
  if (!props.id) return
  router.push(`/news/detail/${props.id}`)
}
</script>

<style scoped>
.news-card {
  display: flex;
  padding: 12px 14px;
  background-color: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: background-color 0.15s ease;
}

.news-card:active {
  background-color: var(--bg-hover);
}

.news-image {
  width: 120px;
  height: 80px;
  flex-shrink: 0;
  margin-right: 12px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background-color: var(--bg-hover);
}

.image-placeholder {
  width: 120px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-hover);
}

.news-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 80px;
}

.news-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.45;
}

.news-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.news-meta span:not(:last-child)::after {
  content: '·';
  margin-left: 4px;
  color: var(--text-disabled);
}
</style>
