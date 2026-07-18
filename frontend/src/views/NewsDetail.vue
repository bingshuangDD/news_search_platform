<template>
  <div class="news-detail">
    <van-nav-bar
      :title="$t('nav.newsDetail')"
      left-arrow
      @click-left="onClickLeft"
      fixed
    />

    <!-- 骨架屏加载态 -->
    <div v-if="loading" class="detail-skeleton">
      <div class="skeleton-title skeleton"></div>
      <div class="skeleton-info skeleton"></div>
      <div class="skeleton-cover skeleton"></div>
      <div class="skeleton-paragraph skeleton"></div>
      <div class="skeleton-paragraph skeleton"></div>
      <div class="skeleton-paragraph skeleton"></div>
    </div>

    <div v-else-if="newsStore.newsDetail.id" class="detail-content">
      <div class="title-container">
        <h1
          class="title"
          @touchstart="onTitleTouchStart"
          @touchend="onTitleTouchEnd"
          @touchmove="onTitleTouchMove"
          @touchcancel="onTitleTouchEnd"
        >{{ newsStore.newsDetail.title }}</h1>
        <div class="actions">
          <van-button
            class="action-btn share-btn"
            icon="share-o"
            :aria-label="$t('home.share')"
            @click="shareNews"
          />
          <van-button
            class="action-btn favorite-btn"
            :icon="isFavorite ? 'star' : 'star-o'"
            :class="{ 'is-favorite': isFavorite }"
            :aria-label="isFavorite ? $t('home.cancelFavorite') : $t('home.favorite')"
            @click="toggleFavorite"
          />
        </div>
      </div>

      <div class="info">
        <span v-if="newsStore.newsDetail.author">{{ newsStore.newsDetail.author }}</span>
        <span v-if="newsStore.newsDetail.publishTime">{{ newsStore.newsDetail.publishTime }}</span>
        <span v-if="newsStore.newsDetail.views">{{ formatViews(newsStore.newsDetail.views) }}</span>
      </div>

      <div v-if="newsStore.newsDetail.image" class="cover">
        <van-image
          :src="newsStore.newsDetail.image"
          :alt="newsStore.newsDetail.title"
          width="100%"
          fit="cover"
          radius="16"
          lazy-load
        >
          <template #loading>
            <div class="cover-placeholder">
              <van-icon name="photo-o" size="32" color="var(--text-tertiary)" />
            </div>
          </template>
          <template #error>
            <div class="cover-placeholder">
              <van-icon name="photo-fail-o" size="32" color="var(--text-tertiary)" />
            </div>
          </template>
        </van-image>
      </div>

      <div class="content">
        <p v-for="(paragraph, index) in contentParagraphs" :key="index">{{ paragraph }}</p>
      </div>

      <div v-if="newsStore.newsDetail.relatedNews?.length" class="related-news">
        <h3>{{ $t('newsDetail.related') }}</h3>
        <div class="related-list">
          <div
            class="related-item clickable"
            v-for="item in newsStore.newsDetail.relatedNews"
            :key="item.id"
            @click="goToRelatedNews(item.id)"
          >
            <div class="related-image">
              <van-image
                :src="item.image"
                :alt="item.title"
                width="140"
                height="90"
                fit="cover"
                radius="12"
                lazy-load
              >
                <template #loading>
                  <div class="related-image-placeholder"><van-icon name="photo-o" size="20" color="var(--text-tertiary)" /></div>
                </template>
                <template #error>
                  <div class="related-image-placeholder"><van-icon name="photo-fail-o" size="20" color="var(--text-tertiary)" /></div>
                </template>
              </van-image>
            </div>
            <div class="related-title ellipsis-2">{{ item.title }}</div>
          </div>
        </div>
      </div>
    </div>

    <van-empty v-else :description="$t('newsDetail.loadFailed')">
      <van-button type="primary" size="small" round @click="reload">{{ $t('common.retry') }}</van-button>
    </van-empty>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNewsStore } from '../store/modules/news'
import { useHistoryStore } from '../store/modules/history'
import { useFavoriteStore } from '../store/modules/favorite'
import { useUserStore } from '../store/user'
import { showToast } from 'vant'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const router = useRouter()
const newsStore = useNewsStore()
const historyStore = useHistoryStore()
const favoriteStore = useFavoriteStore()
const userStore = useUserStore()
const { t } = useI18n()

const loading = ref(true)

const newsId = computed(() => Number(route.params.id))

const contentParagraphs = computed(() => {
  if (!newsStore.newsDetail.content) return []
  return newsStore.newsDetail.content.split('\n\n').filter(p => p.trim())
})

const isFavorite = computed(() => {
  return favoriteStore.isFavorite(newsId.value)
})

const onClickLeft = () => {
  router.back()
}

const goToRelatedNews = (id) => {
  router.push(`/news/detail/${id}`)
}

const reload = () => {
  loadDetail()
}

const formatViews = (views) => {
  const num = Number(views)
  if (Number.isNaN(num)) return views
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}${t('newsItem.tenThousand')}`
  }
  return `${num} ${t('newsItem.views')}`
}

const toggleFavorite = async () => {
  if (!userStore.getLoginStatus) {
    showToast({
      message: t('newsDetail.loginToFavorite'),
      position: 'bottom'
    })
    router.push('/login')
    return
  }

  const status = await favoriteStore.toggleFavorite(newsStore.newsDetail)

  if (status === true) {
    showToast({ message: t('newsDetail.addedToFavorite'), position: 'bottom' })
  } else if (status === false) {
    showToast({ message: t('newsDetail.removedFromFavorite'), position: 'bottom' })
  } else {
    showToast({ message: t('newsDetail.favoriteFailed'), position: 'bottom' })
  }
}

// 分享
const shareNews = async () => {
  const news = newsStore.newsDetail
  const url = `${window.location.origin}/news/detail/${news.id}`
  const copyToClipboard = async () => {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(url)
      showToast({ message: t('home.shareSuccess'), position: 'bottom' })
    } else {
      showToast({ message: t('home.shareFailed'), position: 'bottom' })
    }
  }

  try {
    if (navigator.share) {
      await navigator.share({
        title: news.title,
        text: news.description || news.title,
        url
      })
      return
    }
    await copyToClipboard()
  } catch (err) {
    if (err.name === 'AbortError') return
    await copyToClipboard().catch(() => showToast({ message: t('home.shareFailed'), position: 'bottom' }))
  }
}

// 标题长按复制
let longPressTimer = null

const copyTitle = async () => {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(newsStore.newsDetail.title)
      showToast({ message: t('newsDetail.copySuccess'), position: 'bottom' })
    } else {
      showToast({ message: t('newsDetail.copyFailed'), position: 'bottom' })
    }
  } catch {
    showToast({ message: t('newsDetail.copyFailed'), position: 'bottom' })
  }
}

const onTitleTouchStart = () => {
  longPressTimer = setTimeout(() => {
    copyTitle()
  }, 500)
}

const onTitleTouchEnd = () => {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}

const onTitleTouchMove = () => {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}

const loadDetail = async () => {
  loading.value = true
  await newsStore.getNewsDetail(newsId.value)
  loading.value = false

  if (!newsStore.newsDetail.id) return

  if (userStore.getLoginStatus) {
    try {
      await historyStore.addHistoryApi(newsStore.newsDetail.id)
    } catch {
      // 历史记录失败不影响阅读
    }
  }

  favoriteStore.loadFavorites()

  if (userStore.getLoginStatus) {
    const result = await favoriteStore.checkFavoriteStatusApi(newsStore.newsDetail.id)
    if (result.success && !result.isLocal) {
      if (result.isFavorite && !favoriteStore.isFavorite(newsStore.newsDetail.id)) {
        favoriteStore.addFavorite(newsStore.newsDetail)
      } else if (!result.isFavorite && favoriteStore.isFavorite(newsStore.newsDetail.id)) {
        favoriteStore.removeFavorite(newsStore.newsDetail.id)
      }
    }
  }
}

onMounted(loadDetail)

onBeforeUnmount(() => {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
})
</script>

<style scoped>
.news-detail {
  padding-top: 46px;
  background-color: var(--bg-base);
  min-height: 100vh;
}

:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}

/* 骨架屏 */
.detail-skeleton {
  padding: 16px;
}

.skeleton-title {
  height: 28px;
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
}

.skeleton-info {
  height: 16px;
  width: 60%;
  border-radius: var(--radius-sm);
  margin-bottom: 16px;
}

.skeleton-cover {
  height: 200px;
  border-radius: var(--radius-lg);
  margin-bottom: 16px;
}

.skeleton-paragraph {
  height: 14px;
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
}

.skeleton-paragraph:last-child {
  width: 70%;
}

/* 内容区 */
.detail-content {
  padding: 16px;
  background-color: var(--bg-surface);
  min-height: calc(100vh - 46px);
}

.title-container {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 12px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.45;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  padding: 0;
  border-radius: var(--radius-pill);
  background-color: var(--bg-hover);
  border: none;
  color: var(--text-tertiary);
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s ease, background-color 0.15s ease;
}

.action-btn:active {
  transform: scale(0.92);
}

.share-btn {
  color: var(--primary);
  background-color: var(--primary-light);
}

.favorite-btn.is-favorite {
  color: var(--color-warning);
  background-color: var(--color-warning-light);
}

.info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

.info span:not(:last-child)::after {
  content: '·';
  margin-left: 4px;
  color: var(--text-disabled);
}

.cover {
  margin-bottom: 20px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background-color: var(--bg-hover);
}

.cover :deep(.van-image__img) {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-hover);
}

.content {
  font-size: 17px;
  line-height: 1.9;
  color: var(--text-primary);
}

.content p {
  margin-bottom: 20px;
  text-align: left;
  text-indent: 2em;
  letter-spacing: 0.01em;
}

.content p:first-child {
  margin-top: 0;
}

.content p:last-child {
  margin-bottom: 0;
}

/* 相关推荐 */
.related-news {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid var(--divider-color);
}

.related-news h3 {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 14px;
}

.related-list {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  -webkit-overflow-scrolling: touch;
}

.related-list::-webkit-scrollbar {
  display: none;
}

.related-item {
  display: flex;
  flex-direction: column;
  width: 140px;
  flex-shrink: 0;
  background-color: var(--bg-surface);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.related-item:active {
  background-color: var(--bg-hover);
}

.related-image {
  width: 140px;
  height: 90px;
  background-color: var(--bg-hover);
}

.related-image-placeholder {
  width: 140px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.related-title {
  font-size: 13px;
  line-height: 1.45;
  padding: 10px;
  color: var(--text-secondary);
  min-height: 56px;
}

/* 空状态 */
:deep(.van-empty) {
  padding-top: 80px;
}

:deep(.van-empty__description) {
  color: var(--text-tertiary);
  margin-bottom: 16px;
}
</style>
