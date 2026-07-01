<script setup lang="ts">
/**
 * 应用根组件：首次启动弹出隐私协议授权弹窗（微信小程序合规要求）。
 * 用户同意后写入 storage 标记，后续不再弹窗。
 */
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";

const PRIVACY_AGREED_KEY = "privacy_agreed";

function showPrivacyConsent() {
  uni.showModal({
    title: "隐私协议提示",
    content:
      "欢迎使用饭点小厨。为了提供食材推荐服务，我们需要获取你的微信登录信息并保存你的食材和偏好记录。继续使用即表示你同意《用户协议》和《隐私政策》。",
    confirmText: "同意并继续",
    cancelText: "查看协议",
    success: (res) => {
      if (res.confirm) {
        uni.setStorageSync(PRIVACY_AGREED_KEY, true);
      } else {
        // 用户选择查看协议，跳转隐私页后再决定
        uni.navigateTo({ url: "/pages/privacy/index" });
      }
    },
  });
}

onLaunch(() => {
  const agreed = uni.getStorageSync(PRIVACY_AGREED_KEY);
  if (!agreed) {
    showPrivacyConsent();
  }
  console.log("App Launch");
});
onShow(() => {
  console.log("App Show");
});
onHide(() => {
  console.log("App Hide");
});
</script>
<style></style>
