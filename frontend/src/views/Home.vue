<template>
  <div class="home">
    <van-nav-bar :title="$t('home.title')" fixed />

    <div class="category-tabs" :class="{ 'is-sticky': isSticky }">
      <van-tabs
        v-model:active="activeTab"
        sticky
        swipeable
        animated
        @click-tab="onClickTab"
        @scroll="onTabsScroll"
      >
        <van-tab
          v-for="category in tabCategories"
          :key="category.id"
          :title="getCategoryTranslation(category.name)"
          :name="category.id"
        >
          <van-pull-refresh v-model="newsStore.refreshing" @refresh="onRefresh">
            <news-list-skeleton v-if="showSkeleton" />
            <van-list
              v-else
              v-model:loading="listLoading"
              :finished="newsStore.finished"
              :finished-text="$t('home.noMore')"
              :immediate-check="false"
              @load="onLoad"
            >
              <van-swipe-cell
                v-for="item in newsStore.newsList"
                :key="item.id"
                :ref="(el) => setSwipeCellRef(el, item.id)"
                @open="openSwipeId = item.id"
                @close="openSwipeId = null"
              >
                <template #default>
                  <div @click.capture="onItemClick(item, $event)">
                    <news-item :news="item" />
                  </div>
                </template>
                <template #right>
                  <div class="swipe-actions" role="group" :aria-label="$t('home.swipeActions')">
                    <div
                      class="swipe-btn favorite"
                      :class="{ 'is-favorite': isFavorite(item.id) }"
                      role="button"
                      tabindex="0"
                      :aria-label="isFavorite(item.id) ? $t('home.cancelFavorite') : $t('home.favorite')"
                      @click="handleFavorite(item)"
                    >
                      <van-icon :name="isFavorite(item.id) ? 'star' : 'star-o'" aria-hidden="true" />
                      <span>{{ isFavorite(item.id) ? $t('home.cancelFavorite') : $t('home.favorite') }}</span>
                    </div>
                    <div
                      class="swipe-btn share"
                      role="button"
                      tabindex="0"
                      :aria-label="$t('home.share')"
                      @click="handleShare(item)"
                    >
                      <van-icon name="share-o" aria-hidden="true" />
                      <span>{{ $t('home.share') }}</span>
                    </div>
                  </div>
                </template>
              </van-swipe-cell>
            </van-list>
          </van-pull-refresh>
        </van-tab>
      </van-tabs>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useNewsStore } from '../store/modules/news'
import { useFavoriteStore } from '../store/modules/favorite'
import { useUserStore } from '../store/user'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import NewsItem from '../components/NewsItem.vue'
import NewsListSkeleton from '../components/NewsListSkeleton.vue'
import TabBar from '../components/TabBar.vue'

const newsStore = useNewsStore()
const favoriteStore = useFavoriteStore()
const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const activeTab = ref(1)
const isSticky = ref(false)
const openSwipeId = ref(null)
const swipeCellRefs = new Map()

const MORE_CATEGORY_ID = 10

// 显示的分类（不含"更多"）
const displayCategories = computed(() => {
  return newsStore.categories.filter(category => category.name !== '更多')
})

// Tabs 展示的分类，末尾追加"更多"
const tabCategories = computed(() => {
  return [
    ...displayCategories.value,
    { id: MORE_CATEGORY_ID, name: '更多' }
  ]
})

// 是否显示骨架屏
const showSkeleton = computed(() => newsStore.loading && newsStore.newsList.length === 0)

// 骨架屏期间不显示 van-list 自己的加载指示器
const listLoading = computed(() => newsStore.loading && !showSkeleton.value)

// 收藏 id 集合，减少模板重复计算
const favoriteIds = computed(() => new Set(favoriteStore.favorites.map(item => item.id)))

// 获取分类名称的翻译
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

// 跳转到分类页面
const goToCategory = () => {
  router.push('/category')
}

// 处理 tab 点击
const onClickTab = ({ name }) => {
  if (name === MORE_CATEGORY_ID) {
    goToCategory()
    return
  }
  newsStore.changeCategory(name)
}

// 下拉刷新
const onRefresh = () => {
  newsStore.getNewsList(true)
}

// 上拉加载更多
const onLoad = () => {
  newsStore.getNewsList()
}

// 收藏 / 取消收藏
const isFavorite = (id) => favoriteIds.value.has(id)

const handleFavorite = async (news) => {
  closeSwipeCell(news.id)

  if (!userStore.getLoginStatus) {
    showToast(t('newsDetail.loginToFavorite'))
    router.push('/login')
    return
  }

  const result = await favoriteStore.toggleFavorite(news)
  if (result === true) {
    showToast(t('newsDetail.addedToFavorite'))
  } else if (result === false) {
    showToast(t('newsDetail.removedFromFavorite'))
  } else {
    showToast(t('newsDetail.favoriteFailed'))
  }
}

// 分享
const handleShare = async (news) => {
  closeSwipeCell(news.id)

  const url = `${window.location.origin}/news/detail/${news.id}`
  const copyToClipboard = async () => {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(url)
      showToast(t('home.shareSuccess'))
    } else {
      showToast(t('home.shareFailed'))
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
    await copyToClipboard().catch(() => showToast(t('home.shareFailed')))
  }
}

const setSwipeCellRef = (el, id) => {
  if (el) {
    swipeCellRefs.set(id, el)
  }
}

const closeSwipeCell = (id) => {
  const cell = swipeCellRefs.get(id)
  if (cell && typeof cell.close === 'function') {
    cell.close()
  }
}

// 点击已滑开的列表项时，先关闭滑块并阻止跳转
const onItemClick = (item, event) => {
  if (openSwipeId.value === item.id) {
    closeSwipeCell(item.id)
    event.stopPropagation()
    event.preventDefault()
  }
}

// 分类栏吸顶状态
const onTabsScroll = ({ isFixed }) => {
  isSticky.value = isFixed
}

// 激活 tab 自动滚动到可视区中间
const scrollActiveTabIntoView = () => {
  nextTick(() => {
    const activeEl = document.querySelector('.category-tabs .van-tab--active')
    if (!activeEl) return
    activeEl.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
  })
}

// 监听路由参数，同步激活 tab
watch(
  () => route.query.categoryId,
  (newCategoryId) => {
    if (!newCategoryId) {
      activeTab.value = newsStore.currentCategory
      return
    }
    const categoryId = Number(newCategoryId)
    if (categoryId === MORE_CATEGORY_ID) return

    const index = displayCategories.value.findIndex(cat => cat.id === categoryId)
    if (index !== -1) {
      activeTab.value = categoryId
      newsStore.changeCategory(categoryId)
    }
  },
  { immediate: true }
)

// 监听激活 tab：滑动切换时加载对应分类，并滚动 tab 到可视区中间
watch(activeTab, (newTab) => {
  if (newTab !== MORE_CATEGORY_ID && newsStore.currentCategory !== newTab) {
    newsStore.changeCategory(newTab)
  }
  scrollActiveTabIntoView()
})

// 监听分类列表变化，设置默认激活项
watch(
  displayCategories,
  (categories) => {
    if (!categories.length) return
    if (route.query.categoryId) return
    const currentId = newsStore.currentCategory
    const exists = categories.some(cat => cat.id === currentId)
    activeTab.value = exists ? currentId : categories[0].id
  },
  { immediate: true }
)

// 切换分类或清空列表时，清理滑块引用，避免内存泄漏和误操作
watch(
  () => newsStore.newsList.length,
  () => {
    openSwipeId.value = null
    swipeCellRefs.clear()
  }
)

onMounted(() => {
  newsStore.getCategories().then(() => {
    if (!newsStore.newsList.length) {
      newsStore.getNewsList()
    }
  })
})
</script>

<style scoped>
.home {
  padding-top: 46px;
  padding-bottom: 50px;
  background-color: var(--bg-base);
  min-height: 100vh;
}

/* 导航栏 */
:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}

/* 分类标签栏 */
.category-tabs {
  position: relative;
}

:deep(.van-tabs__wrap) {
  background-color: var(--bg-surface);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease;
}

.category-tabs.is-sticky :deep(.van-tabs__wrap) {
  box-shadow: var(--shadow-md);
}

:deep(.van-tabs__nav) {
  padding: 6px 8px;
}

:deep(.van-tab) {
  padding: 0 14px;
  margin: 0 3px;
  font-size: 14px;
  color: var(--text-secondary);
  border-radius: var(--radius-pill);
  transition: background-color 0.2s ease, color 0.2s ease;
}

:deep(.van-tab--active) {
  font-weight: 600;
  color: var(--primary);
  background-color: var(--primary-light);
}

/* 隐藏默认底部指示线 */
:deep(.van-tabs__line) {
  display: none;
}

/* 列表内容区背景 */
:deep(.van-tab__pane) {
  min-height: calc(100vh - 140px);
}

:deep(.van-pull-refresh) {
  background-color: var(--bg-base);
}

/* 最后一个 tab（更多）使用不同图标暗示 */
:deep(.van-tab:last-child .van-tab__text) {
  display: flex;
  align-items: center;
  gap: 2px;
}

:deep(.van-tab:last-child .van-tab__text::after) {
  content: '›';
  font-size: 16px;
  transform: rotate(90deg);
  opacity: 0.6;
}

/* 列表项滑动手势 */
.swipe-actions {
  display: flex;
  height: 100%;
}

.swipe-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 68px;
  height: 100%;
  gap: 4px;
  font-size: 12px;
  color: var(--text-inverse);
  background-color: var(--primary);
}

.swipe-btn.favorite {
  background-color: var(--color-warning);
}

.swipe-btn.favorite.is-favorite {
  background-color: var(--text-tertiary);
}

.swipe-btn.share {
  background-color: var(--primary);
}

.swipe-btn .van-icon {
  font-size: 18px;
}
</style>
