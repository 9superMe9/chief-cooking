import { defineStore } from "pinia";
import { ref } from "vue";
import { wechatLogin, type LoginResponse } from "../api/auth";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>("");
  const userInfo = ref<any>(null);

  function setToken(newToken: string) {
    token.value = newToken;
    uni.setStorageSync("token", newToken);
  }

  function setUserInfo(info: any) {
    userInfo.value = info;
    uni.setStorageSync("user", JSON.stringify(info));
  }

  function logout() {
    token.value = "";
    userInfo.value = null;
    uni.removeStorageSync("token");
    uni.removeStorageSync("user");
  }

  function init() {
    const savedToken = uni.getStorageSync("token");
    const savedUser = uni.getStorageSync("user");
    if (savedToken) {
      token.value = savedToken;
    }
    if (savedUser) {
      try {
        userInfo.value = JSON.parse(savedUser);
      } catch {
        userInfo.value = null;
      }
    }
  }

  async function login() {
    let code: string;
    // #ifdef H5
    // H5 无微信登录，生成随机 code 走后端 mock 登录（后端未配 AppID 时返回 test_openid_{code}）
    code = `h5_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    // #endif
    // #ifndef H5
    const loginRes = await new Promise<any>((resolve, reject) => {
      uni.login({
        provider: "weixin",
        success: resolve,
        fail: reject,
      });
    });
    code = loginRes.code;
    // #endif
    const response = await wechatLogin({ code });
    setToken(response.access_token);
    setUserInfo(response.user);
  }

  return {
    token,
    userInfo,
    setToken,
    setUserInfo,
    logout,
    init,
    login,
  };
});