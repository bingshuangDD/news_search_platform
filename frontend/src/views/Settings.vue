<template>
  <div class="settings-container">
    <van-nav-bar
      :title="$t('settings.title')"
      left-arrow
      @click-left="onClickLeft"
      fixed
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
      :style="{ height: '45%' }"
    >
      <div class="popup-header">
        <div class="popup-title">{{ $t('settings.selectTheme') }}</div>
      </div>

      <div class="theme-grid">
        <div
          v-for="theme in themeList"
          :key="theme.id"
          class="theme-card"
          :class="{ active: currentTheme === theme.id }"
          @click="changeTheme(theme.id)"
        >
          <div class="theme-preview" :style="previewStyle(theme)">
            <div class="preview-bar"></div>
            <div class="preview-content">
              <div class="preview-line"></div>
              <div class="preview-line short"></div>
            </div>
          </div>
          <div class="theme-name">{{ $t(`theme.${theme.id}`) }}</div>
          <van-icon v-if="currentTheme === theme.id" name="success" class="check-icon" />
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
      <div class="popup-header">
        <div class="popup-title">{{ $t('settings.selectLanguage') }}</div>
      </div>

      <van-radio-group v-model="currentLanguage">
        <van-cell-group inset>
          <van-cell
            v-for="lang in languageOptions"
            :key="lang.value"
            :title="lang.label"
            clickable
            :class="{ 'language-active': currentLanguage === lang.value }"
            @click="currentLanguage = lang.value"
          >
            <template #right-icon>
              <van-radio :name="lang.value" />
            </template>
          </van-cell>
        </van-cell-group>
      </van-radio-group>

      <div class="popup-footer">
        <van-button type="primary" block round @click="changeLanguage">{{ $t('common.confirm') }}</van-button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useThemeStore } from '../store/theme'
import { useI18n } from 'vue-i18n'
import { useLanguageStore } from '../store/language'

const router = useRouter()
const themeStore = useThemeStore()
const languageStore = useLanguageStore()
const { t, locale } = useI18n()

const onClickLeft = () => {
  router.back()
}

const showThemePopup = ref(false)
const themeList = computed(() => themeStore.getAllThemes)
const currentTheme = computed(() => themeStore.getCurrentTheme)

const previewStyle = (theme) => {
  const isDark = theme.id === 'dark'
  return {
    backgroundColor: isDark ? 'var(--bg-surface)' : 'var(--bg-base)',
    borderColor: theme.id === currentTheme.value ? theme.primaryColor : 'transparent'
  }
}

const changeTheme = (themeId) => {
  themeStore.setTheme(themeId)
  showToast(t('settings.themeChanged'))
  showThemePopup.value = false
}

const showLanguagePopup = ref(false)
const currentLanguage = ref(languageStore.getCurrentLanguage)
const languageOptions = [
  { label: t('settings.languages.zhCN'), value: 'zh-CN' },
  { label: t('settings.languages.enUS'), value: 'en-US' }
]

const changeLanguage = () => {
  languageStore.setLanguage(currentLanguage.value)
  locale.value = currentLanguage.value
  showLanguagePopup.value = false
  showToast(t('settings.languageChanged'))
  window.location.reload()
}
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  padding-top: 46px;
  padding-bottom: 20px;
}

:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}

.settings-list {
  margin-top: 16px;
}

.settings-list :deep(.van-cell-group) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 12px;
  box-shadow: var(--shadow-sm);
}

.settings-list :deep(.van-cell-group__title) {
  color: var(--text-tertiary);
  font-size: 13px;
  padding: 12px 16px 6px;
}

.settings-list :deep(.van-cell) {
  padding: 14px 16px;
  transition: background-color 0.15s ease;
}

.settings-list :deep(.van-cell:active) {
  background-color: var(--bg-hover);
}

.settings-list :deep(.van-cell__title) {
  color: var(--text-primary);
  font-size: 15px;
}

.settings-list :deep(.van-cell__right-icon) {
  color: var(--text-tertiary);
}

/* ===== 弹出层头部 ===== */
.popup-header {
  text-align: center;
  padding: 16px;
  border-bottom: 1px solid var(--divider-color);
}

.popup-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* ===== 主题卡片 ===== */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 16px;
}

.theme-card {
  position: relative;
  padding: 12px;
  background-color: var(--bg-surface);
  border: 1.5px solid var(--border-color);
  border-radius: var(--radius-lg);
  transition: border-color 0.2s ease, transform 0.15s ease;
}

.theme-card:active {
  transform: scale(0.98);
}

.theme-card.active {
  border-color: var(--primary);
}

.theme-preview {
  height: 80px;
  border-radius: var(--radius-md);
  border: 2px solid transparent;
  padding: 10px;
  overflow: hidden;
}

.preview-bar {
  height: 10px;
  background-color: var(--preview-line);
  border-radius: var(--radius-sm);
  margin-bottom: 10px;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preview-line {
  height: 8px;
  background-color: var(--preview-line-light);
  border-radius: var(--radius-sm);
}

.preview-line.short {
  width: 60%;
}

.theme-name {
  margin-top: 10px;
  font-size: 14px;
  color: var(--text-primary);
  text-align: center;
}

.check-icon {
  position: absolute;
  top: 8px;
  right: 8px;
  color: var(--primary);
  font-size: 16px;
}

/* ===== 语言选项 ===== */
:deep(.language-active) {
  background-color: var(--primary-light);
}

.popup-footer {
  padding: 16px;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: var(--bg-surface);
  border-top: 1px solid var(--divider-color);
}

.popup-footer :deep(.van-button) {
  border-radius: var(--radius-pill);
}
</style>
