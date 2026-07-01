<template>
  <view class="container">
    <scroll-view scroll-y class="scroll-content">
      <view class="agreement-content">
        <text class="agreement-title">用户协议</text>
        <text class="agreement-version">版本号：V1.0</text>
        <text class="agreement-date">更新日期：2024年1月1日</text>

        <text class="section-title">一、服务条款</text>
        <text class="section-content">欢迎使用饭点小厨（以下简称"本服务"）。本服务由饭点小厨开发团队（以下简称"我们"）提供。您在使用本服务前，应仔细阅读并理解本协议的全部内容。</text>

        <text class="section-title">二、用户账户</text>
        <text class="section-content">您需要通过微信登录来使用本服务。您应确保您的账户信息真实、准确、完整。您对您账户下的所有活动负全部责任。</text>

        <text class="section-title">三、服务内容</text>
        <text class="section-content">本服务提供以下功能：</text>
        <text class="list-item">1. 食材识别：通过拍照或手动输入识别食材</text>
        <text class="list-item">2. 菜谱推荐：根据您的食材和偏好推荐合适的菜谱</text>
        <text class="list-item">3. 菜谱收藏：收藏您喜欢的菜谱</text>
        <text class="list-item">4. 历史记录：查看您的浏览历史</text>

        <text class="section-title">四、用户行为规范</text>
        <text class="section-content">您在使用本服务时，应遵守以下规定：</text>
        <text class="list-item">1. 不得上传违法、违规或侵犯他人权益的内容</text>
        <text class="list-item">2. 不得滥用本服务，包括但不限于恶意刷量、攻击服务器等</text>
        <text class="list-item">3. 不得未经授权访问他人账户</text>

        <text class="section-title">五、免责声明</text>
        <text class="section-content">本服务提供的菜谱和建议仅供参考，我们不对其准确性、适用性或安全性做出任何保证。用户在使用菜谱时应自行判断并承担相应风险。</text>

        <text class="section-title">六、协议变更</text>
        <text class="section-content">我们有权随时修改本协议。修改后的协议将在本页面发布，您继续使用本服务即视为同意修改后的协议。</text>

        <text class="section-title">七、联系方式</text>
        <text class="section-content">如果您对本协议有任何疑问或建议，请通过以下方式联系我们：</text>
        <text class="contact-info">邮箱：support@chief-cooking.com</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
</script>

<style lang="scss" scoped>
/* 现代食器主题：与首页统一 */
.container {
  min-height: 100vh;
  background: #FAF7F2;
  background-image:
    radial-gradient(circle at 15% 10%, rgba(31, 61, 46, 0.04) 0%, transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(200, 118, 58, 0.05) 0%, transparent 45%);
}

.scroll-content {
  height: 100vh;
}

.agreement-content {
  padding: 50rpx 30rpx 60rpx;
}

.agreement-title {
  font-size: 42rpx;
  font-weight: 600;
  color: #1F3D2E;
  text-align: center;
  display: block;
  margin-bottom: 18rpx;
  letter-spacing: 2rpx;
}

.agreement-version, .agreement-date {
  font-size: 22rpx;
  color: #8A8275;
  text-align: center;
  display: block;
  margin-bottom: 8rpx;
  letter-spacing: 1rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F3D2E;
  margin-top: 40rpx;
  margin-bottom: 18rpx;
  display: block;
  letter-spacing: 1rpx;
  padding-left: 18rpx;
  position: relative;
}

.section-title::before {
  content: "";
  position: absolute;
  left: 0;
  top: 8rpx;
  bottom: 8rpx;
  width: 6rpx;
  background: #C8763A;
  border-radius: 3rpx;
}

.section-content {
  font-size: 28rpx;
  color: #5A5042;
  line-height: 1.8;
  display: block;
  margin-bottom: 18rpx;
  letter-spacing: 0.5rpx;
}

.list-item {
  font-size: 28rpx;
  color: #5A5042;
  line-height: 1.8;
  display: block;
  margin-bottom: 10rpx;
  padding-left: 24rpx;
  letter-spacing: 0.5rpx;
}

.contact-info {
  font-size: 28rpx;
  color: #C8763A;
  display: block;
  letter-spacing: 1rpx;
  margin-top: 8rpx;
}
</style>