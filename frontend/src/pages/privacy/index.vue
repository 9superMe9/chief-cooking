<template>
  <view class="container">
    <scroll-view scroll-y class="scroll-content">
      <view class="privacy-content">
        <text class="privacy-title">隐私政策</text>
        <text class="privacy-version">版本号：V1.0</text>
        <text class="privacy-date">更新日期：2024年1月1日</text>

        <text class="section-title">一、我们收集的信息</text>
        <text class="section-content">我们尊重您的隐私，仅收集必要的信息以提供服务：</text>
        <text class="list-item">1. 用户信息：通过微信登录获取您的昵称和头像</text>
        <text class="list-item">2. 食材信息：您上传的食材图片和手动输入的食材名称</text>
        <text class="list-item">3. 偏好信息：您选择的口味偏好、用餐人群等</text>
        <text class="list-item">4. 使用记录：您的浏览历史、收藏记录等</text>

        <text class="section-title">二、信息的使用</text>
        <text class="section-content">我们收集的信息主要用于：</text>
        <text class="list-item">1. 提供个性化的菜谱推荐服务</text>
        <text class="list-item">2. 优化服务体验和功能</text>
        <text class="list-item">3. 保障服务安全</text>

        <text class="section-title">三、信息的保护</text>
        <text class="section-content">我们采取多种安全措施保护您的信息：</text>
        <text class="list-item">1. 使用加密技术传输和存储敏感信息</text>
        <text class="list-item">2. 限制访问权限，仅授权人员可访问</text>
        <text class="list-item">3. 定期进行安全审计和更新</text>

        <text class="section-title">四、信息的共享</text>
        <text class="section-content">我们不会向第三方出售您的个人信息。在以下情况下，我们可能会共享您的信息：</text>
        <text class="list-item">1. 获得您的明确同意</text>
        <text class="list-item">2. 遵守法律法规的要求</text>
        <text class="list-item">3. 保护我们的合法权益</text>

        <text class="section-title">五、您的权利</text>
        <text class="section-content">您有权：</text>
        <text class="list-item">1. 查看和修改您的个人信息</text>
        <text class="list-item">2. 删除您的收藏和历史记录</text>
        <text class="list-item">3. 注销您的账户</text>

        <text class="section-title">六、儿童隐私</text>
        <text class="section-content">本服务不面向13岁以下儿童。如果我们发现13岁以下儿童使用本服务，我们将立即删除相关信息。</text>

        <text class="section-title">七、政策变更</text>
        <text class="section-content">我们有权随时修改本政策。修改后的政策将在本页面发布，您继续使用本服务即视为同意修改后的政策。</text>

        <text class="section-title">八、联系方式</text>
        <text class="section-content">如果您对本政策有任何疑问或建议，请通过以下方式联系我们：</text>
        <text class="contact-info">邮箱：privacy@chief-cooking.com</text>
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

.privacy-content {
  padding: 50rpx 30rpx 60rpx;
}

.privacy-title {
  font-size: 42rpx;
  font-weight: 600;
  color: #1F3D2E;
  text-align: center;
  display: block;
  margin-bottom: 18rpx;
  letter-spacing: 2rpx;
}

.privacy-version, .privacy-date {
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