<template>
  <div class="my-container">
    <van-nav-bar :title="$t('my.title')" />
    <div class="user-info" @click="goToProfile" v-if="isLogin">
      <div class="avatar">
        <van-image
          round
          width="80"
          height="80"
          src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
        />
      </div>
      <div class="info">
        <div class="username">{{ isLogin ? userInfo.username : $t('my.notLoggedIn') }}</div>
        <div class="desc" v-if="isLogin">{{ userBio || $t('profile.bio') }}</div>
      </div>
      <van-icon name="arrow" class="arrow-icon" />
    </div>
    <div class="user-info" v-else>
      <div class="avatar">
        <van-image
          round
          width="80"
          height="80"
          src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
        />
      </div>
      <div class="info">
        <div class="username">{{ $t('my.notLoggedIn') }}</div>
        <div class="desc">
          <van-button type="primary" size="small" @click="goToLogin" style="margin-right: 10px">{{ $t('my.goToLogin') }}</van-button>
          <van-button type="default" size="small" @click="goToRegister">{{ $t('my.goToRegister') }}</van-button>
        </div>
      </div>
    </div>

    <div class="menu-list">
      <van-cell-group inset>
        <van-cell :title="$t('my.myFavorite')" is-link @click="goToFavorite" />
        <van-cell :title="$t('my.browsingHistory')" is-link @click="goToHistory" />
        <van-cell :title="$t('my.notifications')" is-link />
        <van-cell :title="$t('my.settings')" is-link @click="goToSettings" />
        <van-cell v-if="isLogin" :title="$t('my.logout')" @click="handleLogout" />
      </van-cell-group>
    </div>
    <tab-bar />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { useRouter } from 'vue-router';
import { computed, ref } from 'vue';
import { showDialog, showToast } from 'vant';
import TabBar from '../components/TabBar.vue';
import { useI18n } from 'vue-i18n';

const userStore = useUserStore();
const router = useRouter();
const { t } = useI18n();

// 从store获取用户信息和登录状态
const userInfo = computed(() => userStore.userInfo);
const isLogin = computed(() => userStore.getLoginStatus);
const userBio = computed(() => userStore.getUserBio || t('profile.bio'));

// 跳转到登录页
const goToLogin = () => {
  router.push('/login');
};

// 跳转到注册页
const goToRegister = () => {
  router.push('/register');
};

// 跳转到个人信息页
const goToProfile = () => {
  if (isLogin.value) {
    router.push('/profile');
  }
};

// 跳转到浏览历史页面
const goToHistory = () => {
  if (isLogin.value) {
    router.push('/history');
  } else {
    showToast(t('common.login'));
    router.push('/login');
  }
};

// 跳转到我的收藏页面
const goToFavorite = () => {
  if (isLogin.value) {
    router.push('/favorite');
  } else {
    showToast(t('common.login'));
    router.push('/login');
  }
};

// 跳转到设置页面
const goToSettings = () => {
  router.push('/settings');
};

// 退出登录
const handleLogout = () => {
  showDialog({
    title: t('common.confirm'),
    message: t('my.logout') + '?',
    showCancelButton: true,
  }).then((action) => {
    if (action === 'confirm') {
      userStore.logout();
      router.push('/login');
    }
  });
};

// 获取用户信息
onMounted(async () => {
  try {
    await userStore.getUserInfoDetail();
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
});
</script>

<style scoped>
.my-container {
  padding-top: 46px;
  padding-bottom: 50px;
  background-color: var(--background-color);
  color: var(--text-color);
  min-height: 100vh;
  box-sizing: border-box;
}

.van-nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 999;
}

/* ===== 用户信息卡片 ===== */
.user-info {
  display: flex;
  align-items: center;
  padding: 24px 16px;
  background: linear-gradient(135deg, #4F46E5, #7C3AED);
  color: #fff;
  border-radius: 20px;
  margin: 16px;
  position: relative;
  box-shadow: var(--shadow-modal);
}

.arrow-icon {
  position: absolute;
  right: 16px;
  color: rgba(255, 255, 255, 0.8);
}

.avatar {
  margin-right: 16px;
}

.avatar :deep(.van-image) {
  border: 3px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.info {
  flex: 1;
}

.username {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 4px;
  color: #fff;
}

.desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.desc :deep(.van-button) {
  font-size: 13px;
  border-radius: 999px;
}

.desc :deep(.van-button--primary) {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  color: #fff;
}

/* ===== 菜单列表 ===== */
.menu-list {
  margin: 0 16px;
}

.menu-list :deep(.van-cell-group) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-card);
  margin-bottom: 12px;
}

.menu-list :deep(.van-cell) {
  padding: 14px 16px;
  transition: background-color 0.15s ease;
}

.menu-list :deep(.van-cell:active) {
  background-color: #F8FAFC;
}

.menu-list :deep(.van-cell__right-icon) {
  color: #CBD5E1;
}

body.theme-dark .menu-list :deep(.van-cell:active) {
  background-color: #334155;
}
</style>