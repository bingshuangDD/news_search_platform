<template>
  <div class="app-empty">
    <van-empty :image="image" :description="description">
      <template v-if="actionText" #default>
        <van-button
          type="primary"
          size="small"
          round
          class="action-btn"
          @click="$emit('action')"
        >
          {{ actionText }}
        </van-button>
      </template>
    </van-empty>
  </div>
</template>

<script setup>
defineProps({
  description: {
    type: String,
    default: ''
  },
  actionText: {
    type: String,
    default: ''
  },
  image: {
    type: String,
    default: 'default'
  }
})

defineEmits(['action'])
</script>

<style scoped>
.app-empty {
  padding: 48px 24px;
}

.app-empty :deep(.van-empty__description) {
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 12px;
}

.action-btn {
  margin-top: 16px;
  padding: 0 24px;
  height: 36px;
}
</style>
