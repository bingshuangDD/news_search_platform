<template>
  <div class="register-page">
    <van-nav-bar
      :title="$t('register.title')"
      left-arrow
      @click-left="onClickLeft"
      fixed
    />

    <div class="register-container">
      <div class="register-brand">
        <div class="brand-icon">
          <van-icon name="newspaper-o" size="40" color="var(--text-inverse)" />
        </div>
        <h1 class="brand-name">{{ $t('register.title') }}</h1>
        <p class="brand-slogan">{{ $t('register.slogan') }}</p>
      </div>

      <van-form @submit="onSubmit" class="register-form">
        <van-cell-group inset>
          <van-field
            v-model="username"
            name="username"
            :label="$t('register.username')"
            :placeholder="$t('register.usernamePlaceholder')"
            :rules="[{ required: true, message: $t('register.usernameRequired') }]"
            left-icon="user-o"
          />
          <van-field
            v-model="password"
            type="password"
            name="password"
            :label="$t('register.password')"
            :placeholder="$t('register.passwordPlaceholder')"
            :rules="[{ required: true, message: $t('register.passwordRequired') }]"
            left-icon="lock"
          />
          <van-field
            v-model="confirmPassword"
            type="password"
            name="confirmPassword"
            :label="$t('register.confirmPassword')"
            :placeholder="$t('register.confirmPasswordPlaceholder')"
            :rules="[
              { required: true, message: $t('register.confirmPasswordRequired') },
              { validator: validatePassword, message: $t('register.passwordMismatch') }
            ]"
            left-icon="lock"
          />
        </van-cell-group>

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" size="large">
            {{ $t('register.submit') }}
          </van-button>
        </div>
      </van-form>

      <div class="login-link">
        <span>{{ $t('register.hasAccount') }}</span>
        <span class="link" @click="goToLogin">{{ $t('register.goLogin') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '../store/user'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')

const validatePassword = () => {
  return password.value === confirmPassword.value
}

const onSubmit = async () => {
  showToast({
    type: 'loading',
    message: t('register.registering'),
    forbidClick: true,
    duration: 0
  })

  try {
    const result = await userStore.register({
      username: username.value,
      password: password.value
    })

    if (result.success) {
      showToast({ type: 'success', message: result.message })
      router.replace('/home')
    } else {
      showToast({ type: 'fail', message: result.message })
    }
  } catch (error) {
    showToast({ type: 'fail', message: t('register.failed') })
  }
}

const onClickLeft = () => {
  router.back()
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background-color: var(--bg-base);
}

.register-container {
  padding-top: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ===== 品牌区 ===== */
.register-brand {
  margin: 40px 0 28px;
  text-align: center;
}

.brand-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
}

.brand-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px;
}

.brand-slogan {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* ===== 表单 ===== */
.register-form {
  width: 100%;
  padding: 0 16px;
}

.register-form :deep(.van-cell-group--inset) {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  background-color: var(--bg-surface);
}

.register-form :deep(.van-cell) {
  padding: 14px 16px;
  background-color: var(--bg-surface);
}

.register-form :deep(.van-field__left-icon) {
  margin-right: 8px;
  color: var(--text-tertiary);
}

.register-form :deep(.van-field__control) {
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  font-size: 15px;
  color: var(--text-primary);
}

.register-form :deep(.van-field__control::placeholder) {
  color: var(--text-tertiary);
}

.register-form :deep(.van-field__label) {
  color: var(--text-secondary);
  width: 70px;
}

.submit-btn {
  margin: 24px 0 16px;
}

.submit-btn :deep(.van-button) {
  border-radius: var(--radius-pill);
  background: var(--primary);
  border: none;
  box-shadow: var(--shadow-md);
  font-weight: 600;
  font-size: 16px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.submit-btn :deep(.van-button:active) {
  transform: scale(0.97);
  box-shadow: var(--shadow-lg);
}

.login-link {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.login-link .link {
  margin-left: 6px;
  color: var(--primary);
  font-weight: 600;
}

:deep(.van-nav-bar) {
  box-shadow: var(--shadow-sm);
}
</style>
