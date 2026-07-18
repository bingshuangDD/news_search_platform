<template>
  <div class="news-item clickable" @click="goToDetail">
    <div class="news-content">
      <h3 class="news-title ellipsis-2">{{ news.title }}</h3>
      <p v-if="news.description" class="news-desc ellipsis-2">{{ news.description }}</p>
      <div class="news-info">
        <span v-if="news.author" class="news-author">{{ news.author }}</span>
        <span v-if="news.publishTime" class="news-time">{{ news.publishTime }}</span>
        <span v-if="news.views" class="news-views">{{ formatViews(news.views) }}</span>
      </div>
    </div>
    <div class="news-image">
      <van-image
        :src="news.image"
        :alt="news.title"
        width="120"
        height="80"
        fit="cover"
        radius="12"
        lazy-load
      >
        <template #loading>
          <div class="image-placeholder">
            <van-icon name="photo-o" size="24" color="var(--text-tertiary)" />
          </div>
        </template>
        <template #error>
          <div class="image-placeholder">
            <van-icon name="photo-fail-o" size="24" color="var(--text-tertiary)" />
          </div>
        </template>
      </van-image>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  news: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const { t } = useI18n()

const goToDetail = () => {
  if (!props.news?.id) return
  router.push(`/news/detail/${props.news.id}`)
}

const formatViews = (views) => {
  const num = Number(views)
  if (Number.isNaN(num)) return views
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}${t('newsItem.tenThousand')}`
  }
  return `${num} ${t('newsItem.views')}`
}
</script>

<style scoped>
.news-item {
  display: flex;
  padding: 14px 16px;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--divider-color);
  transition: background-color 0.15s ease;
}

.news-item:active {
  background-color: var(--bg-hover);
}

.news-content {
  flex: 1;
  margin-right: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 80px;
}

.news-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.45;
  margin: 0;
}

.news-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.45;
  margin: 6px 0 0;
}

.news-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.news-info span:not(:last-child)::after {
  content: '·';
  margin-left: 4px;
  color: var(--text-disabled);
}

.news-image {
  width: 120px;
  height: 80px;
  flex-shrink: 0;
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

</style>
