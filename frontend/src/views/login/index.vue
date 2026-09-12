<template>
  <div class="login-container">
    <div class="login-container-bg" :style="{ backgroundImage: 'url(' + campusBg + ')' }" aria-hidden="true" />
    <div class="bg-photo" :style="{ backgroundImage: 'url(' + campusBg + ')' }" aria-hidden="true" />
    <div class="bg-overlay" aria-hidden="true" />
    <div class="particles" aria-hidden="true">
      <span v-for="n in 7" :key="n" :class="'pt pt-' + n" />
    </div>

    <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" auto-complete="on" label-position="left">

      <div class="title-container anim-item anim-1">
        <span class="eyebrow">MEDIA DATA PLATFORM</span>
        <h3 class="title">传媒数据管理与分析系统</h3>
        <p class="subtitle">数据洞察，从一次登录开始</p>
      </div>

      <el-form-item prop="userName" class="anim-item anim-2">
        <span class="svg-container">
          <svg-icon icon-class="user" />
        </span>
        <el-input
          ref="userName"
          v-model="loginForm.userName"
          placeholder="用户名"
          name="userName"
          type="text"
          tabindex="1"
          auto-complete="on"
        />
      </el-form-item>

      <el-tooltip v-model="capsTooltip" content="Caps lock is On" placement="right" manual>
        <el-form-item prop="password" class="anim-item anim-3">
          <span class="svg-container">
            <svg-icon icon-class="password" />
          </span>
          <el-input
            :key="passwordType"
            ref="password"
            v-model="loginForm.password"
            :type="passwordType"
            placeholder="密码"
            name="password"
            tabindex="2"
            auto-complete="on"
            @keyup="checkCapslock"
            @blur="capsTooltip = false"
            @keyup.enter="handleLogin"
          />
          <span class="show-pwd" @click="showPwd">
            <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
          </span>
        </el-form-item>
      </el-tooltip>

      <el-checkbox v-model="loginForm.remember" class="remember-row anim-item anim-4">记住密码</el-checkbox>

      <el-button :loading="loading" type="primary" class="login-btn anim-item anim-5" @click.prevent="handleLogin">登 录</el-button>

      <p class="footer-note anim-item anim-6">Media Data Management &amp; Analysis System</p>

    </el-form>

  </div>
</template>

<script>
import { mapMutations } from 'vuex'
import loginApi from '@/api/login'
import campusBg from '@/assets/login/campus.jpg'

export default {
  name: 'Login',
  data () {
    const validateUsername = (rule, value, callback) => {
      if (value.length < 2) {
        callback(new Error('用户名不能少于2个字符'))
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      if (value.length < 5) {
        callback(new Error('密码不能少于5个字符'))
      } else {
        callback()
      }
    }
    return {
      campusBg,
      loginForm: {
        userName: '',
        password: '',
        remember: false
      },
      loginRules: {
        userName: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      passwordType: 'password',
      capsTooltip: false,
      loading: false,
      showDialog: false
    }
  },
  created () {
    // window.addEventListener('storage', this.afterQRScan)
  },
  mounted () {
    if (this.loginForm.userName === '') {
      this.$refs.userName.focus()
    } else if (this.loginForm.password === '') {
      this.$refs.password.focus()
    }
  },
  unmounted () {
    // window.removeEventListener('storage', this.afterQRScan)
  },
  methods: {
    checkCapslock ({ shiftKey, key } = {}) {
      if (key && key.length === 1) {
        // eslint-disable-next-line no-mixed-operators
        if (shiftKey && (key >= 'a' && key <= 'z') || !shiftKey && (key >= 'A' && key <= 'Z')) {
          this.capsTooltip = true
        } else {
          this.capsTooltip = false
        }
      }
      if (key === 'CapsLock' && this.capsTooltip === true) {
        this.capsTooltip = false
      }
    },
    showPwd () {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleLogin () {
      let _this = this
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          loginApi.login(this.loginForm).then(function (result) {
            if (result && result.code === 1) {
              _this.setUserName(_this.loginForm.userName)
              _this.$router.push({ path: '/' })
            } else {
              _this.loading = false
              _this.$message({
                message: result.message,
                type: 'error'
              })
            }
          }).catch(function (reason) {
            _this.loading = false
          })
        } else {
          return false
        }
      })
    },
    ...mapMutations('user', ['setUserName'])
  }
}
</script>

<style lang="scss">
/* 全局层：覆盖 element-plus 内部样式（不能 scoped） */

$panel: #101d33;
$cursor: #eaf2ff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

.login-container {
  .el-input {
    display: inline-block;
    height: 50px;
    width: 85%;

    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $cursor;
      height: 50px;
      caret-color: #22d3ee;
      font-size: 14px;

      &::placeholder {
        color: rgba(148, 178, 214, 0.55);
      }

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $panel inset !important;
        -webkit-text-fill-color: $cursor !important;
        transition: background-color 9999s ease-in-out 0s;
      }
    }
  }

  // Element Plus 2.x 的 input 外层 wrapper：透明底 + 细边框，聚焦时由外层 form-item 发光
  .el-input__wrapper {
    background-color: transparent;
    box-shadow: none !important;
  }

  .el-form-item {
    border: 1px solid rgba(148, 178, 214, 0.28);
    background: rgba(10, 20, 38, 0.42);
    border-radius: 12px;
    margin-bottom: 18px;
    transition: border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;

    &:focus-within {
      border-color: rgba(34, 211, 238, 0.75);
      background: rgba(10, 20, 38, 0.6);
      box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.14);
    }
  }

  .el-form-item__error {
    padding-top: 4px;
  }

  .el-checkbox {
    color: rgba(226, 238, 250, 0.92);

    .el-checkbox__label {
      color: rgba(226, 238, 250, 0.92);
      font-size: 13px;
    }

    .el-checkbox__inner {
      background: rgba(10, 20, 38, 0.4);
      border-color: rgba(148, 178, 214, 0.5);
    }
  }

  .el-checkbox__input.is-checked + .el-checkbox__label {
    color: #67e8f9;
  }

  .el-button--primary.login-btn {
    position: relative;
    overflow: hidden;
    width: 100%;
    height: 46px;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 6px;
    color: #04121f;
    background: linear-gradient(135deg, #67e8f9 0%, #38bdf8 55%, #4f8cff 100%);
    box-shadow: 0 8px 22px -8px rgba(56, 189, 248, 0.6);
    transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
    margin-bottom: 18px;

    // 流光扫过
    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 55%;
      height: 100%;
      background: linear-gradient(105deg, transparent 0%, rgba(255, 255, 255, 0.55) 50%, transparent 100%);
      transform: translateX(-160%) skewX(-18deg);
      animation: btn-shimmer 3.6s ease-in-out infinite;
      pointer-events: none;
    }

    &:hover {
      transform: translateY(-1px);
      filter: brightness(1.06);
      box-shadow: 0 12px 28px -8px rgba(56, 189, 248, 0.7);
    }

    &:active {
      transform: translateY(0);
      filter: brightness(0.97);
    }
  }

  @keyframes btn-shimmer {
    0%, 55% { transform: translateX(-160%) skewX(-18deg); }
    85%, 100% { transform: translateX(320%) skewX(-18deg); }
  }
}
</style>

<style lang="scss" scoped>
$dark_gray: #a8c3de;
$light_gray: #eaf2ff;

.login-container {
  min-height: 100%;
  width: 100%;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #8ea6bf;
  background-size: cover;
  background-position: center 62%;

  .login-container-bg {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center 62%;
    filter: brightness(1.12) saturate(1.05);
  }

  .bg-photo {
    position: absolute;
    inset: -5%;
    background-size: cover;
    background-position: center 62%;
    filter: brightness(1.12) saturate(1.05);
    animation: ken-burns 38s ease-in-out infinite alternate;
    will-change: transform;
  }

  @keyframes ken-burns {
    0% { transform: scale(1.02) translate3d(-1.2%, 0.6%, 0); }
    50% { transform: scale(1.09) translate3d(1.4%, -1%, 0); }
    100% { transform: scale(1.04) translate3d(0.6%, 1.2%, 0); }
  }

  .bg-overlay {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(120% 90% at 50% 42%, transparent 48%, rgba(4, 10, 20, 0.24) 100%),
      linear-gradient(155deg, rgba(6, 13, 26, 0.26) 0%, rgba(9, 20, 38, 0.10) 45%, rgba(5, 15, 28, 0.32) 100%);
  }

  .particles {
    position: absolute;
    inset: 0;
    pointer-events: none;

    .pt {
      position: absolute;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(180, 235, 255, 0.9), rgba(120, 200, 255, 0) 70%);
      opacity: 0;
      animation: pt-float 14s ease-in-out infinite;
    }

    .pt-1 { left: 8%;  bottom: -4%; width: 7px;  height: 7px;  animation-delay: 0s; }
    .pt-2 { left: 22%; bottom: -4%; width: 4px;  height: 4px;  animation-delay: 3.2s; animation-duration: 17s; }
    .pt-3 { left: 41%; bottom: -4%; width: 9px;  height: 9px;  animation-delay: 1.4s; animation-duration: 20s; }
    .pt-4 { left: 63%; bottom: -4%; width: 5px;  height: 5px;  animation-delay: 5.6s; }
    .pt-5 { left: 78%; bottom: -4%; width: 8px;  height: 8px;  animation-delay: 2.3s; animation-duration: 18s; }
    .pt-6 { left: 90%; bottom: -4%; width: 4px;  height: 4px;  animation-delay: 7.8s; }
    .pt-7 { left: 52%; bottom: -4%; width: 3px;  height: 3px;  animation-delay: 9.5s; animation-duration: 22s; }
  }

  @keyframes pt-float {
    0%   { transform: translate3d(0, 0, 0); opacity: 0; }
    12%  { opacity: 0.75; }
    55%  { opacity: 0.35; }
    100% { transform: translate3d(26px, -92vh, 0); opacity: 0; }
  }

  .login-form {
    position: relative;
    z-index: 1;
    width: 420px;
    max-width: calc(100% - 40px);
    padding: 44px 44px 26px 44px;
    overflow: hidden;
    border-radius: 20px;
    background: rgba(8, 16, 30, 0.52);
    border: 1px solid rgba(170, 205, 235, 0.24);
    box-shadow: 0 24px 70px -18px rgba(2, 8, 20, 0.9), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(22px) saturate(140%);
    -webkit-backdrop-filter: blur(22px) saturate(140%);
  }

  // 逐行滑入
  .anim-item {
    animation: slide-in 0.7s cubic-bezier(0.22, 0.85, 0.35, 1) both;
  }

  .anim-1 { animation-delay: 0.05s; }
  .anim-2 { animation-delay: 0.18s; }
  .anim-3 { animation-delay: 0.31s; }
  .anim-4 { animation-delay: 0.44s; }
  .anim-5 { animation-delay: 0.57s; }
  .anim-6 { animation-delay: 0.7s; }

  @keyframes slide-in {
    from {
      opacity: 0;
      transform: translateX(-30px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .bg-photo,
    .particles .pt,
    .anim-item,
    .login-container .login-btn::after {
      animation: none !important;
    }
  }

  .svg-container {
    padding: 8px 5px 8px 16px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
    transition: color 0.25s ease;
  }

  .el-form-item:focus-within .svg-container {
    color: #67e8f9;
  }

  .title-container {
    position: relative;
    text-align: center;
    margin-bottom: 34px;

    .eyebrow {
      display: block;
      font-size: 11px;
      letter-spacing: 5px;
      color: #67e8f9;
      opacity: 0.9;
      margin-bottom: 12px;
      font-weight: 600;
      text-shadow: 0 1px 8px rgba(4, 12, 24, 0.6);
    }

    .title {
      font-size: 23px;
      color: $light_gray;
      margin: 0;
      text-align: center;
      font-weight: 700;
      letter-spacing: 1px;
      text-shadow: 0 2px 14px rgba(4, 12, 24, 0.65);
    }

    .subtitle {
      margin: 12px 0 0;
      font-size: 12.5px;
      color: rgba(196, 220, 243, 0.8);
      letter-spacing: 2px;
      text-shadow: 0 1px 8px rgba(4, 12, 24, 0.6);
    }
  }

  .remember-row {
    display: flex;
    margin: 2px 0 20px 4px;
  }

  .show-pwd {
    position: absolute;
    right: 12px;
    top: 12px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
    user-select: none;
    transition: color 0.2s ease;

    &:hover {
      color: #67e8f9;
    }
  }

  .footer-note {
    margin: 6px 0 4px;
    text-align: center;
    font-size: 11px;
    letter-spacing: 1.5px;
    color: rgba(170, 200, 230, 0.55);
  }
}
</style>
