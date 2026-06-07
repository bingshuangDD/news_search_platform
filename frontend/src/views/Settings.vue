<template>
  <div class="settings-container">
    <van-nav-bar
      :title="$t('settings.title')"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <div class="settings-list">
      <van-cell-group inset :title="$t('settings.personalization')">
        <van-cell :title="$t('settings.themeCustomization')" is-link @click="showThemePopup = true" />
        <van-cell :title="$t('settings.languageSettings')" is-link @click="showLanguagePopup = true" />
      </van-cell-group>
      
      <van-cell-group inset :title="$t('settings.account')">
        <van-cell :title="$t('settings.privacySettings')" is-link />
        <van-cell :title="$t('settings.notificationSettings')" is-link />
        <van-cell :title="$t('settings.aboutUs')" is-link />
      </van-cell-group>
    </div>
    
    <!-- 主题选择弹出层 -->
    <van-popup
      v-model:show="showThemePopup"
      position="bottom"
      round
      :style="{ height: '40%' }"
    >
      <div class="popup-title">{{ $t('settings.selectTheme') }}</div>
      <div class="theme-list">
        <div 
          v-for="theme in themeList" 
          :key="theme.id" 
          class="theme-item"
          :class="{ active: currentTheme === theme.id }"
          @click="changeTheme(theme.id)"
        >
          <div class="theme-color" :style="{ backgroundColor: theme.primaryColor }"></div>
          <div class="theme-name">{{ theme.name }}</div>
        </div>
      </div>
    </van-popup>
    
    <!-- 语言选择弹出层 -->
    <van-popup
      v-model:show="showLanguagePopup"
      position="bottom"
      round
      :style="{ height: '40%' }"
    >
      <div class="popup-title">{{ $t('settings.selectLanguage') }}</div>
      <van-radio-group v-model="currentLanguage">
        <van-cell-group inset>
          <van-cell 
            v-for="lang in languageOptions" 
            :key="lang.value" 
            :title="lang.label" 
            clickable 
            @click="currentLanguage = lang.value"
            :class="{ 'language-active': currentLanguage === lang.value }"
          >
            <template #right-icon>
              <van-radio :name="lang.value" />
            </template>
          </van-cell>
        </van-cell-group>
      </van-radio-group>
      <div class="popup-footer">
        <van-button type="primary" block @click="changeLanguage">{{ $t('common.confirm') }}</van-button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useThemeStore } from '../store/theme';
import { useI18n } from 'vue-i18n';
import { useLanguageStore } from '../store/language';

const router = useRouter();
const themeStore = useThemeStore();
const languageStore = useLanguageStore();
const { t, locale } = useI18n();

// 返回上一页
const onClickLeft = () => {
  router.back();
};

// 主题相关
const showThemePopup = ref(false);
const themeList = computed(() => themeStore.getAllThemes);
const currentTheme = computed(() => themeStore.getCurrentTheme);

// 切换主题
const changeTheme = (themeId) => {
  themeStore.setTheme(themeId);
  showToast(t('settings.themeChanged'));
  showThemePopup.value = false;
};

// 语言相关
const showLanguagePopup = ref(false);
const currentLanguage = ref(languageStore.getCurrentLanguage);
const languageOptions = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' }
];

// 切换语言
const changeLanguage = () => {
  languageStore.setLanguage(currentLanguage.value);
  locale.value = currentLanguage.value;
  showLanguagePopup.value = false;
  showToast(t('settings.languageChanged'));
  // 强制刷新页面以应用语言更改
  window.location.reload();
};
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background-color: var(--background-color);
  color: var(--text-color);
  padding-top: 46px;
  padding-bottom: 20px;
}

.settings-list {
  margin-top: 20px;
}

.settings-list :deep(.van-cell-group) {
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 12px;
}

.settings-list :deep(.van-cell-group__title) {
  color: #64748B;
  font-size: 13px;
  padding: 8px 16px 4px;
}

.settings-list :deep(.van-cell) {
  padding: 14px 16px;
  transition: background-color 0.15s ease;
}

.settings-list :deep(.van-cell:active) {
  background-color: #F8FAFC;
}

/* ===== 弹出层 ===== */
.popup-title {
  text-align: center;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #0F172A;
  border-bottom: 1px solid #E2E8F0;
}

.theme-list {
  display: flex;
  flex-wrap: wrap;
  padding: 16px;
  justify-content: center;
}

.theme-item {
  width: 25%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.theme-item:active {
  transform: scale(0.95);
}

.theme-color {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-bottom: 8px;
  border: 2px solid transparent;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.theme-item.active .theme-color {
  border-color: #4F46E5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

.theme-name {
  font-size: 12px;
  color: #64748B;
}

.theme-item.active .theme-name {
  color: #4F46E5;
  font-weight: 600;
}

/* ===== 语言选项 ===== */
:deep(.language-active) {
  background-color: #EEF2FF;
}

.popup-footer {
  padding: 16px;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}
</style>