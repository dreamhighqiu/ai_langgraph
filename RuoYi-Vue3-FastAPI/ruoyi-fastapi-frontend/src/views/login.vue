<template>
  <div class="login-page">
    <div class="login-shell">
      <div class="brand-panel">
        <div class="brand-top">
          <img class="brand-logo" :src="logo" alt="logo" />
          <div class="brand-name">{{ title }}</div>
        </div>
        <div class="brand-desc">企业级 AI 智能测试平台</div>
        <div class="brand-points">
          <div class="point">
            <span class="dot" />
            <span>测试用例 / 需求 / 缺陷一站式管理</span>
          </div>
          <div class="point">
            <span class="dot" />
            <span>自动化执行、报告与质量度量</span>
          </div>
          <div class="point">
            <span class="dot" />
            <span>AI 辅助生成与分析，提升交付效率</span>
          </div>
        </div>
      </div>

      <div class="form-panel">
        <el-form ref="loginRef" :model="loginForm" :rules="loginRules" class="login-form">
          <div class="form-brand">
            <img class="form-brand-logo" :src="logo" alt="logo" />
            <div class="form-brand-text">
              <div class="form-brand-title">{{ title }}</div>
              <div class="form-brand-sub">AI 智能测试平台</div>
            </div>
          </div>

          <div class="form-title">
            <div class="form-title-main">登录</div>
            <div class="form-title-sub">使用企业账号进入平台</div>
          </div>

          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              type="text"
              size="large"
              auto-complete="off"
              placeholder="账号"
              inputmode="text"
            >
              <template #prefix
                ><svg-icon icon-class="user" class="el-input__icon input-icon"
              /></template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              size="large"
              auto-complete="off"
              placeholder="密码"
              show-password
              @keyup.enter="handleLogin"
            >
              <template #prefix
                ><svg-icon icon-class="password" class="el-input__icon input-icon"
              /></template>
            </el-input>
          </el-form-item>

          <el-form-item prop="code" v-if="captchaEnabled">
            <el-input
              v-model="loginForm.code"
              size="large"
              auto-complete="off"
              placeholder="验证码"
              @keyup.enter="handleLogin"
            >
              <template #prefix
                ><svg-icon icon-class="validCode" class="el-input__icon input-icon"
              /></template>
              <template #append>
                <button class="captcha-append" type="button" @click="getCode" title="点击刷新验证码">
                  <img class="captcha-img" :src="codeUrl" alt="captcha" />
                  <span class="captcha-text">换一张</span>
                </button>
              </template>
            </el-input>
          </el-form-item>

          <div class="form-extra">
            <el-checkbox v-model="loginForm.rememberMe">记住密码</el-checkbox>
            <div v-if="register">
              <router-link class="link-type" :to="'/register'">立即注册</router-link>
            </div>
          </div>

          <el-form-item style="width: 100%">
            <el-button class="submit-btn" :loading="loading" size="large" type="primary" @click.prevent="handleLogin">
              <span v-if="!loading">登 录</span>
              <span v-else>登 录 中...</span>
            </el-button>
          </el-form-item>

          <div class="form-note">
            登录即表示你同意平台的安全策略与使用规范
          </div>
        </el-form>
      </div>
    </div>

    <div class="el-login-footer">
      <span>{{ footerContent }}</span>
    </div>
  </div>
</template>

<script setup>
import { getCodeImg } from "@/api/login";
import Cookies from "js-cookie";
import { encrypt, decrypt } from "@/utils/jsencrypt";
import useUserStore from '@/store/modules/user'
import defaultSettings from '@/settings'
import logo from '@/assets/logo/logo.svg'

const title = import.meta.env.VITE_APP_TITLE;
const footerContent = defaultSettings.footerContent
const userStore = useUserStore();
const route = useRoute();
const router = useRouter();
const { proxy } = getCurrentInstance();

const loginForm = ref({
  username: "",
  password: "",
  rememberMe: false,
  code: "",
  uuid: ""
});

const loginRules = {
  username: [{ required: true, trigger: "blur", message: "请输入您的账号" }],
  password: [{ required: true, trigger: "blur", message: "请输入您的密码" }],
  code: [{ required: true, trigger: "change", message: "请输入验证码" }]
};

const codeUrl = ref("");
const loading = ref(false);
// 验证码开关
const captchaEnabled = ref(true);
// 注册开关
const register = ref(false);
const redirect = ref(undefined);

watch(route, (newRoute) => {
    redirect.value = newRoute.query && newRoute.query.redirect;
}, { immediate: true });

function handleLogin() {
  proxy.$refs.loginRef.validate(valid => {
    if (valid) {
      loading.value = true;
      // 勾选了需要记住密码设置在 cookie 中设置记住用户名和密码
      if (loginForm.value.rememberMe) {
        Cookies.set("username", loginForm.value.username, { expires: 30 });
        Cookies.set("password", encrypt(loginForm.value.password), { expires: 30 });
        Cookies.set("rememberMe", loginForm.value.rememberMe, { expires: 30 });
      } else {
        // 否则移除
        Cookies.remove("username");
        Cookies.remove("password");
        Cookies.remove("rememberMe");
      }
      // 调用action的登录方法
      userStore.login(loginForm.value).then(() => {
        const query = route.query;
        const otherQueryParams = Object.keys(query).reduce((acc, cur) => {
          if (cur !== "redirect") {
            acc[cur] = query[cur];
          }
          return acc;
        }, {});
        router.push({ path: redirect.value || "/", query: otherQueryParams });
      }).catch(() => {
        loading.value = false;
        // 重新获取验证码
        if (captchaEnabled.value) {
          getCode();
        }
      });
    }
  });
}

function getCode() {
  getCodeImg().then(res => {
    captchaEnabled.value = res.captchaEnabled === undefined ? true : res.captchaEnabled;
    register.value = res.registerEnabled === undefined ? false : res.registerEnabled;
    if (captchaEnabled.value) {
      codeUrl.value = "data:image/gif;base64," + res.img;
      loginForm.value.uuid = res.uuid;
    }
  });
}

function getCookie() {
  const username = Cookies.get("username");
  const password = Cookies.get("password");
  const rememberMe = Cookies.get("rememberMe");
  loginForm.value = {
    username: username === undefined ? loginForm.value.username : username,
    password: password === undefined ? loginForm.value.password : decrypt(password),
    rememberMe: rememberMe === undefined ? false : Boolean(rememberMe)
  };
}

getCode();
getCookie();
</script>

<style lang="scss" scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px 60px;
  background:
    radial-gradient(1100px circle at 18% 16%, rgba(37, 99, 235, 0.30), transparent 60%),
    radial-gradient(980px circle at 82% 86%, rgba(20, 184, 166, 0.24), transparent 55%),
    radial-gradient(700px circle at 62% 18%, rgba(56, 189, 248, 0.18), transparent 52%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0)),
    #070b14;

  &::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
      radial-gradient(circle at 1px 1px, rgba(148, 163, 184, 0.12) 1px, transparent 1.6px),
      linear-gradient(rgba(148, 163, 184, 0.12) 1px, transparent 1px),
      linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px),
      repeating-linear-gradient(90deg, rgba(56, 189, 248, 0.08) 0 1px, transparent 1px 120px),
      repeating-linear-gradient(0deg, rgba(20, 184, 166, 0.06) 0 1px, transparent 1px 160px);
    background-size: 28px 28px, 72px 72px, 72px 72px, 100% 100%, 100% 100%;
    opacity: 0.34;
    pointer-events: none;
  }

  &::after {
    content: "";
    position: absolute;
    inset: -20%;
    pointer-events: none;
    opacity: 0.55;
    background-image:
      radial-gradient(650px circle at 16% 22%, rgba(37, 99, 235, 0.22), transparent 55%),
      radial-gradient(560px circle at 78% 72%, rgba(20, 184, 166, 0.20), transparent 55%),
      radial-gradient(520px circle at 72% 18%, rgba(56, 189, 248, 0.16), transparent 50%),
      conic-gradient(from 220deg at 50% 50%, rgba(37, 99, 235, 0.16), rgba(20, 184, 166, 0.14), rgba(56, 189, 248, 0.12), rgba(37, 99, 235, 0.16)),
      repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.05) 0 1px, transparent 1px 7px);
    filter: blur(28px);
    mix-blend-mode: screen;
    animation: loginAurora 14s ease-in-out infinite;
  }
}

@keyframes loginAurora {
  0% {
    transform: translate3d(-2%, -2%, 0) rotate(0deg);
  }
  50% {
    transform: translate3d(2%, 2%, 0) rotate(10deg);
  }
  100% {
    transform: translate3d(-2%, -2%, 0) rotate(0deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-page::after {
    animation: none;
  }
}

.login-shell {
  position: relative;
  width: 1060px;
  max-width: 100%;
  display: grid;
  grid-template-columns: 1fr 440px;
  gap: 0;
  align-items: stretch;
  border-radius: 22px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(2, 6, 23, 0.40);
  backdrop-filter: blur(16px);
  box-shadow: 0 22px 60px rgba(2, 6, 23, 0.60);
}

.brand-panel {
  position: relative;
  overflow: hidden;
  padding: 44px 42px;
  background:
    radial-gradient(900px circle at 20% 20%, rgba(37, 99, 235, 0.55), transparent 55%),
    radial-gradient(700px circle at 85% 80%, rgba(20, 184, 166, 0.45), transparent 55%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.35));
  border-right: 1px solid rgba(255, 255, 255, 0.10);
  color: #fff;

  &::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
      radial-gradient(600px circle at 20% 30%, rgba(255, 255, 255, 0.14), transparent 55%),
      radial-gradient(500px circle at 80% 70%, rgba(255, 255, 255, 0.10), transparent 55%);
    pointer-events: none;
  }
}

.brand-top {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  width: 44px;
  height: 44px;
  display: block;
  filter: drop-shadow(0 6px 14px rgba(2, 6, 23, 0.35));
}

.brand-name {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 0.4px;
}

.brand-desc {
  position: relative;
  margin-top: 18px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.88);
}

.brand-points {
  position: relative;
  margin-top: 22px;
  display: grid;
  gap: 12px;
  color: rgba(255, 255, 255, 0.92);

  .point {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 12px 14px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.14);
    backdrop-filter: blur(14px);
    font-size: 13px;
    line-height: 1.5;
  }

  .dot {
    margin-top: 6px;
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.88);
    box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.12);
  }
}

.form-panel {
  background: rgba(255, 255, 255, 0.94);
  padding: 34px 34px 18px;
  display: flex;
  align-items: center;
}

.login-form {
  width: 100%;
}

.form-brand {
  display: none;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.form-brand-logo {
  width: 32px;
  height: 32px;
}

.form-brand-title {
  font-weight: 800;
  color: #0f172a;
  letter-spacing: 0.2px;
  line-height: 1.1;
}

.form-brand-sub {
  margin-top: 2px;
  font-size: 12px;
  color: #64748b;
}

.form-title {
  margin-bottom: 18px;
  text-align: left;

  .form-title-main {
    font-size: 20px;
    font-weight: 800;
    color: #0f172a;
  }
  .form-title-sub {
    margin-top: 6px;
    font-size: 12px;
    color: #64748b;
  }
}

.input-icon {
  height: 39px;
  width: 14px;
  margin-left: 0px;
}

.captcha-append {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 0 10px;
  height: 38px;
  border: 0;
  background: transparent;
  cursor: pointer;

  &:focus-visible {
    outline: 2px solid rgba(37, 99, 235, 0.45);
    outline-offset: 2px;
    border-radius: 10px;
  }
}

.captcha-img {
  height: 28px;
  width: auto;
  border-radius: 8px;
}

.captcha-text {
  font-size: 12px;
  color: #64748b;
}

.form-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 6px 0 16px;
}

.submit-btn {
  width: 100%;
}

.form-note {
  margin-top: 2px;
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
}

.el-login-footer {
  height: 40px;
  line-height: 40px;
  position: fixed;
  bottom: 0;
  width: 100%;
  text-align: center;
  color: rgba(255, 255, 255, 0.85);
  font-family: Arial;
  font-size: 12px;
  letter-spacing: 0.5px;
}

:deep(.el-form-item) {
  margin-bottom: 14px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 0 12px;
  border: 1px solid #e2e8f0;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: rgba(37, 99, 235, 0.65);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.14);
}

:deep(.el-input-group__append) {
  background: transparent;
  border-left: 1px solid rgba(226, 232, 240, 0.9);
}

:deep(.el-checkbox__label) {
  color: #334155;
}

:deep(.el-button--primary) {
  border: 0;
  background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 45%, #14b8a6 100%);
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.18);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #1d4ed8 0%, #0284c7 45%, #0d9488 100%);
}

@media screen and (max-width: 980px) {
  .login-shell {
    grid-template-columns: 1fr;
    width: 520px;
  }
  .brand-panel {
    display: none;
  }
  .form-panel {
    padding: 26px 22px 14px;
  }
  .form-brand {
    display: flex;
  }
}

@media screen and (max-width: 520px) {
  .login-shell {
    border-radius: 18px;
  }
}
</style>
