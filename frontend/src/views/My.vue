<template>
  <div class="my-container">
    <van-nav-bar :title="$t('my.title')" fixed />

    <!-- 用户信息卡片 -->
    <div class="user-card" @click="goToProfile">
      <div class="avatar-wrapper">
        <van-image
          round
          width="64"
          height="64"
          src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
          class="avatar"
        />
        <div class="avatar-badge">
          <van-icon name="photograph" size="12" color="var(--text-inverse)" />
        </div>
      </div>

      <div class="user-meta">
        <div class="username">{{ isLogin ? userInfo.username : $t('my.notLoggedIn') }}</div>
        <div v-if="isLogin" class="bio">{{ userBio || $t('profile.bio') }}</div>
        <div v-else class="auth-actions">
          <van-button
            type="primary"
            size="small"
            round
            class="login-btn"
            @click.stop="goToLogin"
          >{{ $t('my.goToLogin') }}</van-button>
          <van-button
            type="default"
            size="small"
            round
            class="register-btn"
            @click.stop="goToRegister"
          >{{ $t('my.goToRegister') }}</van-button>
        </div>
      </div>

      <van-icon v-if="isLogin" name="arrow" class="arrow-icon" />
    </div>

    <!-- 菜单列表 -->
    <div class="menu-list">
      <van-cell-group inset>
        <van-cell :title="$t('my.myFavorite')" is-link @click="goToFavorite" />
        <van-cell :title="$t('my.browsingHistory')" is-link @click="goToHistory" />
        <van-cell :title="$t('my.notifications')" is-link />
        <van-cell :title="$t('my.settings')" is-link @click="goToSettings" />
      </van-cell-group>

      <van-cell-group v-if="isLogin" inset class="logout-group">
        <van-cell :title="$t('my.logout')" is-link center @click="handleLogout">
          <template #right-icon>
            <van-icon name="close" class="logout-icon" />
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useUserStore } from '../store/user'
import { useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import TabBar from '../components/TabBar.vue'
import { useI18n } from 'vue-i18n'

const userStore = useUserStore()
const router = useRouter()
const { t } = useI18n()

const userInfo = computed(() => userStore.userInfo)
const isLogin = computed(() => userStore.getLoginStatus)
const userBio = computed(() => userStore.getUserBio || t('profile.bioEmpty'))

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

const goToProfile = () => {
  if (isLogin.value) {
    router.push('/profile')
  }
}

const goToHistory = () => {
  if (isLogin.value) {
    router.push('/history')
  } else {
    showToast(t('common.login'))
    router.push('/login')
  }
}

const goToFavorite = () => {
  if (isLogin.value) {
    router.push('/favorite')
  } else {
    showToast(t('common.login'))
    router.push('/login')
  }
}

const goToSettings = () => {
  router.push('/settings')
}

const handleLogout = () => {
  showDialog({
    title: t('common.confirm'),
    message: t('my.logout') + '?',
    showCancelButton: true
  }).then((action) => {
    if (action === 'confirm') {
      userStore.logout()
      router.push('/login')
    }
  })
}

onMounted(async () => {
  if (!isLogin.value) return
  try {
    await userStore.getUserInfoDetail()
  } catch (error) {
    // 静默失败，不影响界面展示
  }
})
</script>

<style scoped>
.my-container {
  padding-top: 46px;
  padding-bottom: 50px;
  background-color: var(--bg-base);
  color: var(--text-primary);
  min-height: 100vh;
  box-sizing: border-box;
}

:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}

/* ===== 用户信息卡片 ===== */
.user-card {
  display: flex;
  align-items: center;
  padding: 20px 16px;
  margin: 12px 16px 16px;
  background: linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-hover) 100%);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  position: relative;
  transition: background-color 0.15s ease;
}

.user-card:active {
  background: var(--bg-hover);
}

.avatar-wrapper {
  position: relative;
  margin-right: 16px;
  flex-shrink: 0;
}

.avatar {
  border: 2px solid var(--border-color);
}

.avatar-badge {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 22px;
  height: 22px;
  background-color: var(--primary);
  border-radius: 50%;
  border: 2px solid var(--bg-surface);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-meta {
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.bio {
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.auth-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.login-btn {
  height: 28px;
  padding: 0 14px;
  font-size: 13px;
}

.register-btn {
  height: 28px;
  padding: 0 14px;
  font-size: 13px;
  border-color: var(--border-color);
  color: var(--text-secondary);
}

.arrow-icon {
  color: var(--text-tertiary);
  font-size: 16px;
}

/* ===== 菜单列表 ===== */
.menu-list {
  margin: 0 16px;
}

.menu-list :deep(.van-cell-group) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 12px;
  box-shadow: var(--shadow-sm);
}

.menu-list :deep(.van-cell) {
  padding: 14px 16px;
  transition: background-color 0.15s ease;
}

.menu-list :deep(.van-cell:active) {
  background-color: var(--bg-hover);
}

.menu-list :deep(.van-cell__title) {
  color: var(--text-primary);
  font-size: 15px;
}

.menu-list :deep(.van-cell__right-icon) {
  color: var(--text-tertiary);
}

.logout-group :deep(.van-cell__title) {
  color: var(--color-danger);
}

.logout-icon {
  color: var(--color-danger);
  font-size: 16px;
}
</style>
