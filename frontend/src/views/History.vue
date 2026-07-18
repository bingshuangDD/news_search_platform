<template>
  <div class="history-container">
    <van-nav-bar
      :title="$t('history.title')"
      left-arrow
      @click-left="onClickLeft"
      fixed
    >
      <template #right>
        <span
          class="nav-clear"
          :class="{ disabled: !historyStore.getHistory.length }"
          @click="onClickClear"
        >{{ $t('history.clear') }}</span>
      </template>
    </van-nav-bar>

    <div v-if="historyStore.getHistory.length" class="history-list">
      <van-swipe-cell
        v-for="item in historyStore.getHistory"
        :key="item.id"
        class="history-swipe-cell"
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
            <span v-if="item.viewTime">{{ $t('history.viewAt') }} {{ item.viewTime }}</span>
          </template>
        </news-card>

        <template #right>
          <van-button
            square
            :text="$t('history.delete')"
            type="danger"
            class="delete-button"
            @click="confirmDelete(item.id)"
          />
        </template>
      </van-swipe-cell>
    </div>

    <app-empty
      v-else
      :description="$t('history.empty')"
      :action-text="$t('history.goHome')"
      @action="goHome"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useHistoryStore } from '../store/modules/history'
import { showDialog, showToast } from 'vant'
import NewsCard from '../components/NewsCard.vue'
import AppEmpty from '../components/AppEmpty.vue'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const historyStore = useHistoryStore()
const { t } = useI18n()

const onClickLeft = () => {
  router.back()
}

const goHome = () => {
  router.push('/home')
}

const removeHistory = async (id) => {
  const result = await historyStore.removeHistoryApi(id)
  if (!result.success && !result.isLocal) {
    showToast(result.message || t('history.deleteFailed'))
  }
}

const confirmDelete = (id) => {
  showDialog({
    title: t('common.confirm'),
    message: t('history.confirmDelete'),
    showCancelButton: true
  }).then((action) => {
    if (action === 'confirm') {
      removeHistory(id)
    }
  })
}

const onClickClear = () => {
  if (!historyStore.getHistory.length) return

  showDialog({
    title: t('common.confirm'),
    message: t('history.confirmClear'),
    showCancelButton: true
  }).then(async (action) => {
    if (action === 'confirm') {
      const result = await historyStore.clearHistoryApi()
      if (!result.success && !result.isLocal) {
        showToast(result.message || t('history.clearFailed'))
      }
    }
  })
}

onMounted(async () => {
  try {
    const result = await historyStore.getHistoryListApi()
    if (!result || !result.success) {
      historyStore.loadHistory()
    }
  } catch (error) {
    historyStore.loadHistory()
  }
})
</script>

<style scoped>
.history-container {
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

.history-list {
  padding: 12px 16px;
}

.history-swipe-cell {
  margin-bottom: 10px;
}

.delete-button {
  height: 100%;
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
}
</style>
