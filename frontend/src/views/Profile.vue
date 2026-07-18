<template>
  <div class="profile-page">
    <van-nav-bar
      :title="$t('profile.title')"
      left-arrow
      @click-left="$router.back()"
      fixed
    />

    <div class="profile-container">
      <van-cell-group inset class="avatar-group">
        <van-cell :title="$t('profile.avatar')" center is-link>
          <template #right-icon>
            <div class="avatar-wrapper">
              <van-image
                round
                width="60"
                height="60"
                src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
              />
              <div class="avatar-badge">
                <van-icon name="photograph" size="10" color="var(--text-inverse)" />
              </div>
            </div>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset class="info-group">
        <van-cell :title="$t('profile.username')" :value="userInfo.username || 'admin'" />
        <van-cell :title="$t('profile.userId')" :value="`ID: ${userId || 'N/A'}`" />
        <van-cell
          :title="$t('profile.bio')"
          :value="userBio || $t('profile.bioEmpty')"
          is-link
          @click="openBioPopup"
        />
      </van-cell-group>

      <van-cell-group inset class="security-group">
        <van-cell :title="$t('profile.changePassword')" is-link @click="openPasswordPopup" />
      </van-cell-group>
    </div>

    <!-- 修改简介弹出层 -->
    <van-popup
      v-model:show="showBioPopup"
      position="bottom"
      round
      :style="{ height: '45%' }"
    >
      <div class="popup-header">
        <div class="popup-title">{{ $t('profile.editBio') }}</div>
      </div>

      <van-form @submit="saveBio" class="popup-form">
        <van-field
          v-model="bioForm.bio"
          rows="4"
          autosize
          type="textarea"
          maxlength="100"
          show-word-limit
          :placeholder="$t('profile.bioPlaceholder')"
          :rules="[{ required: true, message: $t('profile.bioRequired') }]"
        />

        <div class="popup-footer">
          <van-button type="primary" block round native-type="submit">{{ $t('common.save') }}</van-button>
        </div>
      </van-form>
    </van-popup>

    <!-- 修改密码弹出层 -->
    <van-popup
      v-model:show="showPasswordPopup"
      position="bottom"
      round
      :style="{ height: '55%' }"
    >
      <div class="popup-header">
        <div class="popup-title">{{ $t('profile.changePassword') }}</div>
      </div>

      <van-form @submit="savePassword" class="popup-form">
        <van-cell-group inset>
          <van-field
            v-model="passwordForm.oldPassword"
            type="password"
            :label="$t('profile.oldPassword')"
            :placeholder="$t('profile.oldPasswordPlaceholder')"
            :rules="[{ required: true, message: $t('profile.oldPasswordRequired') }]"
          />
          <van-field
            v-model="passwordForm.newPassword"
            type="password"
            :label="$t('profile.newPassword')"
            :placeholder="$t('profile.newPasswordPlaceholder')"
            :rules="[{ required: true, message: $t('profile.newPasswordRequired') }]"
          />
          <van-field
            v-model="passwordForm.confirmPassword"
            type="password"
            :label="$t('profile.confirmPassword')"
            :placeholder="$t('profile.confirmPasswordPlaceholder')"
            :rules="[
              { required: true, message: $t('profile.confirmPasswordRequired') },
              { validator: validateConfirmPassword, message: $t('profile.passwordMismatch') }
            ]"
          />
        </van-cell-group>

        <div class="popup-footer">
          <van-button type="primary" block round native-type="submit">{{ $t('common.save') }}</van-button>
        </div>
      </van-form>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../store/user'
import { showLoadingToast, showSuccessToast, showFailToast } from 'vant'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

onMounted(async () => {
  if (!userStore.getLoginStatus) {
    router.push('/login')
    return
  }

  const loading = showLoadingToast({ message: t('common.loading'), forbidClick: true, duration: 0 })
  try {
    const result = await userStore.getUserInfoDetail()
    loading.close()
    if (!result.success) {
      showFailToast(result.message || t('profile.loadFailed'))
    }
  } catch (error) {
    loading.close()
    showFailToast(t('profile.loadFailed'))
  }
})

const userInfo = computed(() => userStore.userInfo)
const userId = computed(() => userStore.token ? userStore.token.substring(0, 5) : '')
const userBio = computed(() => userStore.userInfo?.bio || '')

// 简介编辑
const showBioPopup = ref(false)
const bioForm = ref({ bio: '' })

const openBioPopup = () => {
  bioForm.value.bio = userBio.value
  showBioPopup.value = true
}

const saveBio = async () => {
  const loading = showLoadingToast({ message: t('common.loading'), forbidClick: true, duration: 0 })
  try {
    const result = await userStore.updateUserBio(bioForm.value.bio)
    loading.close()
    if (result?.success) {
      showSuccessToast(t('profile.bioUpdateSuccess'))
      showBioPopup.value = false
    } else {
      showFailToast(result?.message || t('profile.bioUpdateFailed'))
    }
  } catch (error) {
    loading.close()
    showFailToast(t('profile.bioUpdateFailed'))
  }
}

// 密码编辑
const showPasswordPopup = ref(false)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = () => {
  return passwordForm.value.newPassword === passwordForm.value.confirmPassword
}

const openPasswordPopup = () => {
  passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  showPasswordPopup.value = true
}

const savePassword = async () => {
  const loading = showLoadingToast({ message: t('common.loading'), forbidClick: true, duration: 0 })
  try {
    const result = await userStore.updatePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword
    )
    loading.close()
    if (result?.success) {
      showSuccessToast(t('profile.passwordUpdateSuccess'))
      showPasswordPopup.value = false
      passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
    } else {
      showFailToast(result?.message || t('profile.passwordUpdateFailed'))
    }
  } catch (error) {
    loading.close()
    showFailToast(t('profile.passwordUpdateFailed'))
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: var(--bg-base);
}

:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}

.profile-container {
  padding-top: 56px;
  padding-bottom: 20px;
}

.avatar-group,
.info-group,
.security-group {
  margin-top: 12px;
}

.avatar-group :deep(.van-cell-group),
.info-group :deep(.van-cell-group),
.security-group :deep(.van-cell-group) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.avatar-group :deep(.van-cell),
.info-group :deep(.van-cell),
.security-group :deep(.van-cell) {
  padding: 14px 16px;
}

.avatar-wrapper {
  position: relative;
}

.avatar-badge {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 20px;
  height: 20px;
  background-color: var(--primary);
  border-radius: 50%;
  border: 2px solid var(--bg-surface);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== 弹出层 ===== */
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

.popup-form {
  padding: 16px;
}

.popup-form :deep(.van-cell-group) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.popup-form :deep(.van-field) {
  padding: 14px 16px;
  background-color: var(--bg-surface);
}

.popup-form :deep(.van-field__label) {
  color: var(--text-secondary);
  width: 80px;
}

.popup-form :deep(.van-field__control) {
  color: var(--text-primary);
}

.popup-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background-color: var(--bg-surface);
  border-top: 1px solid var(--divider-color);
}

.popup-footer :deep(.van-button) {
  border-radius: var(--radius-pill);
}
</style>
