<template>
  <view class="container">
    <view class="nav-bar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="nav-title">我的收藏</text>
      <text class="nav-placeholder"></text>
    </view>

    <view class="content">
      <view class="recipe-list" v-if="favorites.length > 0">
        <view
          v-for="recipe in favorites"
          :key="recipe.id"
          class="recipe-card"
          @click="goToDetail(recipe.id)"
        >
          <image v-if="recipe.image_url" class="recipe-image" :src="recipe.image_url" mode="aspectFill" />
          <view v-else class="recipe-image recipe-image-placeholder">
            <text class="placeholder-emoji">🍽️</text>
          </view>
          <view class="recipe-info">
            <text class="recipe-name">{{ recipe.name }}</text>
            <text class="recipe-description">{{ recipe.description }}</text>
            <view class="recipe-tags">
              <text class="tag">{{ recipe.taste }}</text>
              <text class="tag">{{ recipe.cooking_time }}</text>
            </view>
          </view>
          <text class="remove-btn" @click.stop="removeFavorite(recipe.id)">×</text>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="empty-icon">❤️</text>
        <text class="empty-title">暂无收藏</text>
        <text class="empty-hint">快去收藏喜欢的菜谱吧</text>
        <view class="empty-btn" @click="goHome">去逛逛</view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getFavorites, removeFavorite as apiRemoveFavorite, type RecipeResponse } from "../../api/recipes";

const favorites = ref<RecipeResponse[]>([]);

function goBack() {
  uni.navigateBack();
}

function goHome() {
  uni.reLaunch({ url: "/pages/index/index" });
}

async function fetchFavorites() {
  try {
    const res = await getFavorites();
    favorites.value = res;
  } catch (error) {
    console.error("获取收藏失败:", error);
  }
}

async function removeFavorite(recipeId: string) {
  uni.showModal({
    title: "提示",
    content: "确定要取消收藏吗？",
    success: async (res) => {
      if (res.confirm) {
        try {
          await apiRemoveFavorite(recipeId);
          favorites.value = favorites.value.filter(r => r.id !== recipeId);
          uni.showToast({ title: "已取消收藏", icon: "none" });
        } catch {
          uni.showToast({ title: "操作失败", icon: "none" });
        }
      }
    }
  });
}

function goToDetail(recipeId: string) {
  uni.navigateTo({ url: `/pages/detail/index?id=${recipeId}` });
}

onMounted(() => {
  fetchFavorites();
});
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

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 50rpx 30rpx 20rpx;
}

.back-btn {
  font-size: 40rpx;
  color: #1F3D2E;
  padding: 10rpx;
  font-weight: 300;
}

.nav-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 2rpx;
}

.nav-placeholder {
  width: 60rpx;
}

.content {
  padding: 20rpx 30rpx 40rpx;
}

.recipe-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.recipe-card {
  display: flex;
  background: #FFFFFF;
  border-radius: 20rpx;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.recipe-image {
  width: 200rpx;
  height: 200rpx;
  flex-shrink: 0;
  border-radius: 14rpx;
}

.recipe-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #F4EFE6 0%, #E8DDC8 100%);
}

.placeholder-emoji {
  font-size: 72rpx;
}

.recipe-info {
  flex: 1;
  padding: 22rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.recipe-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.recipe-description {
  font-size: 24rpx;
  color: #5A5042;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 8rpx 0;
}

.recipe-tags {
  display: flex;
  gap: 10rpx;
}

.tag {
  background: #F4EFE6;
  padding: 6rpx 16rpx;
  border-radius: 6rpx;
  font-size: 20rpx;
  color: #5A5042;
  letter-spacing: 0.5rpx;
}

.remove-btn {
  position: absolute;
  top: 14rpx;
  right: 14rpx;
  width: 44rpx;
  height: 44rpx;
  background: rgba(31, 61, 46, 0.65);
  color: #FAF7F2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 300;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 30rpx;
}

.empty-title {
  font-size: 32rpx;
  color: #1F3D2E;
  font-weight: 600;
  margin-bottom: 14rpx;
  letter-spacing: 1rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: #8A8275;
  margin-bottom: 40rpx;
  letter-spacing: 1rpx;
}

.empty-btn {
  background: #1F3D2E;
  color: #FAF7F2;
  padding: 22rpx 70rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  letter-spacing: 2rpx;
  position: relative;
  overflow: hidden;
}

.empty-btn::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6rpx;
  background: #C8763A;
}
</style>