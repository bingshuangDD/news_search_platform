<template>
  <div class="category">
    <van-nav-bar
      :title="$t('common.allCategories')"
      left-arrow
      @click-left="onClickLeft"
      fixed
    />

    <div class="category-container">
      <van-grid :column-num="3" :border="false">
        <van-grid-item
          v-for="category in displayCategories"
          :key="category.id"
          :text="getCategoryTranslation(category.name)"
          :icon="getCategoryIcon(category.name)"
          @click="goToCategoryNews(category.id)"
        />
      </van-grid>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { useNewsStore } from '../store/modules/news'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TabBar from '../components/TabBar.vue'
import { computed } from 'vue'

const newsStore = useNewsStore()
const router = useRouter()
const { t } = useI18n()

const displayCategories = computed(() => {
  return newsStore.categories.filter((category) => category.name !== '更多')
})

const onClickLeft = () => {
  router.back()
}

const goToCategoryNews = (categoryId) => {
  newsStore.changeCategory(categoryId)
  router.push({
    path: '/home',
    query: { categoryId: categoryId }
  })
}

const getCategoryTranslation = (categoryName) => {
  const categoryMap = {
    '头条': 'headline',
    '社会': 'society',
    '国内': 'domestic',
    '国际': 'international',
    '娱乐': 'entertainment',
    '体育': 'sports',
    '军事': 'military',
    '科技': 'technology',
    '财经': 'finance',
    '更多': 'more'
  }

  const key = categoryMap[categoryName]
  return key ? t(`home.categories.${key}`) : categoryName
}

const getCategoryIcon = (categoryName) => {
  const iconMap = {
    '头条': 'fire-o',
    '社会': 'friends-o',
    '国内': 'home-o',
    '国际': 'global-o',
    '娱乐': 'smile-o',
    '体育': 'chart-o',
    '军事': 'shield-o',
    '科技': 'desktop-o',
    '财经': 'balance-o'
  }
  return iconMap[categoryName] || 'newspaper-o'
}
</script>

<style scoped>
.category {
  padding-top: 46px;
  padding-bottom: 50px;
  background-color: var(--bg-base);
  min-height: 100vh;
}

:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}

.category-container {
  padding: 16px 12px;
}

:deep(.van-grid) {
  gap: 12px;
}

:deep(.van-grid-item) {
  margin-bottom: 4px;
}

:deep(.van-grid-item__content) {
  background-color: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 24px 12px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: transform 0.15s ease, background-color 0.15s ease;
}

:deep(.van-grid-item__content:active) {
  transform: scale(0.96);
  background-color: var(--bg-hover);
}

:deep(.van-grid-item__icon) {
  font-size: 32px;
  color: var(--primary);
}

:deep(.van-grid-item__text) {
  margin-top: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}
</style>
