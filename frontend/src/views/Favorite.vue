<template>
  <div class="favorite-container">
    <van-nav-bar
      :title="$t('favorite.title')"
      left-arrow
      @click-left="onClickLeft"
      fixed
    >
      <template #right>
        <span
          class="nav-clear"
          :class="{ disabled: !favoriteStore.getFavorites.length }"
          @click="onClickClear"
        >{{ $t('favorite.clear') }}</span>
      </template>
    </van-nav-bar>

    <div v-if="favoriteStore.getFavorites.length" class="favorite-list">
      <van-swipe-cell
        v-for="item in favoriteStore.getFavorites"
        :key="item.id"
        class="favorite-swipe-cell"
      >
        <news-card
          :id="item.id"
          :title="item.title"
          :image="item.image"
          :author="item.author"
        >
          <template #meta>
            <span v-if="item.author">{{ item.author }}</span>
            <span v-if="item.publishTime">{{ item.publishTime }}</span>
            <span v-if="item.favoriteTime">{{ $t('favorite.favoriteAt') }} {{ item.favoriteTime }}</span>
          </template>
        </news-card>

        <template #right>
          <van-button
            square
            :text="$t('favorite.delete')"
            type="danger"
            class="delete-button"
            @click="confirmDelete(item.id)"
          />
        </template>
      </van-swipe-cell>
    </div>

    <app-empty
      v-else
      :description="$t('favorite.empty')"
      :action-text="$t('favorite.goHome')"
      @action="goHome"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFavoriteStore } from '../store/modules/favorite'
import { showDialog, showToast } from 'vant'
import NewsCard from '../components/NewsCard.vue'
import AppEmpty from '../components/AppEmpty.vue'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const favoriteStore = useFavoriteStore()
const { t } = useI18n()

const onClickLeft = () => {
  router.back()
}

const goHome = () => {
  router.push('/home')
}

const removeFavorite = async (id) => {
  const result = await favoriteStore.removeFavoriteApi(id)
  if (result.success) {
    favoriteStore.removeFavorite(id)
  }
}

const confirmDelete = (id) => {
  showDialog({
    title: t('common.confirm'),
    message: t('favorite.confirmDelete'),
    showCancelButton: true
  }).then((action) => {
    if (action === 'confirm') {
      removeFavorite(id)
    }
  })
}

const onClickClear = () => {
  if (!favoriteStore.getFavorites.length) return

  showDialog({
    title: t('common.confirm'),
    message: t('favorite.confirmClear'),
    showCancelButton: true
  }).then(async (action) => {
    if (action === 'confirm') {
      const result = await favoriteStore.clearFavoritesApi()
      if (!result || !result.success) {
        showToast(t('favorite.clearFailed'))
      }
    }
  })
}

onMounted(async () => {
  try {
    const result = await favoriteStore.getFavoriteListApi()
    if (!result || !result.success) {
      favoriteStore.loadFavorites()
    }
  } catch (error) {
    favoriteStore.loadFavorites()
  }
})
</script>

<style scoped>
.favorite-container {
  padding-top: 46px;
  padding-bottom: 20px;
  background-color: var(--bg-base);
  min-height: 100vh;
}

:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}

.nav-clear {
  font-size: 14px;
  color: var(--color-danger);
  padding: 8px;
}

.nav-clear.disabled {
  color: var(--text-disabled);
  pointer-events: none;
}

.favorite-list {
  padding: 12px 16px;
}

.favorite-swipe-cell {
  margin-bottom: 10px;
}

.delete-button {
  height: 100%;
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
}
</style>
