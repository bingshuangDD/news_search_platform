<template>
  <div class="register-page">
    <van-nav-bar
      title="用户注册"
      left-arrow
      @click-left="onClickLeft"
      fixed
    />
    
    <div class="register-container">
      <div class="register-logo">
        <van-image
          width="80"
          height="80"
          src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
          round
        />
        <h2>新闻资讯</h2>
      </div>
      
      <van-form @submit="onSubmit" class="register-form">
        <van-cell-group inset>
          <van-field
            v-model="username"
            name="username"
            label="用户名"
            placeholder="请输入用户名"
            :rules="[{ required: true, message: '请填写用户名' }]"
          />
          <van-field
            v-model="password"
            type="password"
            name="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请填写密码' }]"
          />
          <van-field
            v-model="confirmPassword"
            type="password"
            name="confirmPassword"
            label="确认密码"
            placeholder="请再次输入密码"
            :rules="[
              { required: true, message: '请确认密码' },
              { validator: validatePassword, message: '两次密码不一致' }
            ]"
          />
        </van-cell-group>
        
        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" size="large">
            注册
          </van-button>
        </div>
        
        <div class="login-link">
          已有账号？<span @click="goToLogin">去登录</span>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useUserStore } from '../store/user';

const router = useRouter();
const userStore = useUserStore();

const username = ref('');
const password = ref('');
const confirmPassword = ref('');

// 验证两次密码是否一致
const validatePassword = () => {
  return password.value === confirmPassword.value;
};

const onSubmit = async () => {
  // 显示加载提示
  showToast({
    type: 'loading',
    message: '注册中...',
    forbidClick: true,
    duration: 0
  });
  
  try {
    // 调用API注册
    const result = await userStore.register({
      username: username.value,
      password: password.value
    });
    
    if (result.success) {
      showToast({
        type: 'success',
        message: result.message
      });
      
      router.push('/');
    } else {
      showToast({
        type: 'fail',
        message: result.message
      });
    }
  } catch (error) {
    showToast({
      type: 'fail',
      message: '注册失败，请稍后再试'
    });
  }
};

const onClickLeft = () => {
  router.back();
};

const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background-color: #F8FAFC;
}

.register-container {
  padding-top: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.register-logo {
  margin: 40px 0;
  text-align: center;
}

.register-logo :deep(.van-image) {
  animation: logoBreathe 3s ease-in-out infinite;
}

@keyframes logoBreathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.register-logo h2 {
  margin-top: 16px;
  color: #0F172A;
  font-size: 22px;
  font-weight: 700;
}

.register-form {
  width: 100%;
  padding: 0 16px;
}

/* ===== 表单卡片 ===== */
.register-form :deep(.van-cell-group--inset) {
  border-radius: 20px;
  box-shadow: var(--shadow-modal);
  margin: 0;
  overflow: hidden;
}

.register-form :deep(.van-cell) {
  padding: 14px 16px;
}

.register-form :deep(.van-field__control) {
  background: #F1F5F9;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 15px;
}

.register-form :deep(.van-field__control::placeholder) {
  color: #94A3B8;
}

.submit-btn {
  margin: 24px 16px;
}

.submit-btn :deep(.van-button) {
  border-radius: 999px;
  background: linear-gradient(135deg, #4F46E5, #7C3AED);
  border: none;
  box-shadow: var(--shadow-float);
  font-weight: 600;
  font-size: 16px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.submit-btn :deep(.van-button:active) {
  transform: scale(0.97);
  box-shadow: var(--shadow-modal);
}

.login-link {
  text-align: center;
  margin-top: 16px;
  color: #94A3B8;
  font-size: 14px;
}

.login-link span {
  color: #4F46E5;
  font-weight: 600;
}
</style>