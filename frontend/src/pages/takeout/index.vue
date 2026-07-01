<template>
  <view class="container">
    <view class="nav-bar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="nav-title">外食建议</text>
      <text class="nav-placeholder"></text>
    </view>

    <view class="content">
      <view class="header-card">
        <text class="header-icon">🍽️</text>
        <text class="header-title">今天不想做饭？</text>
        <text class="header-subtitle">为你推荐几个菜系方向，复制关键词去外卖App搜索</text>
      </view>

      <view class="pref-tip" v-if="userTaste">
        <text class="pref-tip-text">根据你偏好的「{{ userTaste }}」口味，已为你优先排序</text>
      </view>

      <view class="cuisine-list">
        <view v-for="cuisine in sortedCuisines" :key="cuisine.id" class="cuisine-card">
          <view class="cuisine-header">
            <text class="cuisine-emoji">{{ cuisine.emoji }}</text>
            <view class="cuisine-title-area">
              <text class="cuisine-name">{{ cuisine.name }}</text>
              <text class="cuisine-desc">{{ cuisine.description }}</text>
            </view>
            <text v-if="isPreferred(cuisine)" class="preferred-tag">偏好</text>
          </view>

          <view class="keyword-section">
            <text class="keyword-label">推荐搜索：</text>
            <view class="keyword-list">
              <text
                v-for="kw in cuisine.keywords"
                :key="kw"
                class="keyword-tag"
                @click="copyKeyword(kw)"
              >{{ kw }}</text>
            </view>
          </view>

          <view class="copy-btn" @click="copyAllKeywords(cuisine)">
            <text class="copy-btn-text">复制全部关键词</text>
          </view>
        </view>
      </view>

      <view class="tips-card">
        <text class="tips-icon">💡</text>
        <view class="tips-content">
          <text class="tips-title">点餐小贴士</text>
          <text class="tips-text">点击单个关键词可快速复制；也可复制全部关键词，打开外卖App粘贴搜索，挑评分高、距离近的商家。</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRecipeStore } from "../../stores/recipe";

interface CuisineDirection {
  id: string;
  name: string;
  emoji: string;
  description: string;
  keywords: string[];
  tasteTags: string[];
}

const recipeStore = useRecipeStore();

const userTaste = computed(() => recipeStore.preferences?.taste || "");

const cuisineDirections: CuisineDirection[] = [
  {
    id: "1",
    name: "川菜",
    emoji: "🌶️",
    description: "麻辣鲜香，下饭神器",
    keywords: ["水煮鱼", "麻婆豆腐", "回锅肉", "宫保鸡丁"],
    tasteTags: ["麻辣", "重口味", "辣"],
  },
  {
    id: "2",
    name: "粤菜",
    emoji: "🥬",
    description: "清淡鲜美，原汁原味",
    keywords: ["白切鸡", "清蒸鱼", "老火靓汤", "虾饺"],
    tasteTags: ["清淡", "清淡"],
  },
  {
    id: "3",
    name: "湘菜",
    emoji: "🔥",
    description: "香辣开胃，米饭杀手",
    keywords: ["剁椒鱼头", "小炒肉", "辣椒炒肉", "外婆菜"],
    tasteTags: ["辣", "重口味"],
  },
  {
    id: "4",
    name: "日料",
    emoji: "🍣",
    description: "精致清淡，食材本味",
    keywords: ["寿司", "刺身", "拉面", "天妇罗"],
    tasteTags: ["清淡"],
  },
  {
    id: "5",
    name: "韩餐",
    emoji: "🍲",
    description: "暖锅烤肉，氛围感满满",
    keywords: ["部队锅", "韩式烤肉", "石锅拌饭", "泡菜汤"],
    tasteTags: ["重口味"],
  },
  {
    id: "6",
    name: "西餐",
    emoji: "🍝",
    description: "浪漫优雅，仪式感强",
    keywords: ["牛排", "意面", "披萨", "凯撒沙拉"],
    tasteTags: ["清淡"],
  },
  {
    id: "7",
    name: "快餐简餐",
    emoji: "🍔",
    description: "快速便捷，省时省力",
    keywords: ["汉堡", "炸鸡", "盖饭", "三明治"],
    tasteTags: [],
  },
  {
    id: "8",
    name: "面食小吃",
    emoji: "🍜",
    description: "暖胃管饱，性价比高",
    keywords: ["牛肉面", "馄饨", "饺子", "过桥米线"],
    tasteTags: [],
  },
];

function isPreferred(cuisine: CuisineDirection): boolean {
  if (!userTaste.value) return false;
  return cuisine.tasteTags.includes(userTaste.value);
}

const sortedCuisines = computed(() => {
  if (!userTaste.value) return cuisineDirections;
  return [...cuisineDirections].sort((a, b) => {
    const aMatch = isPreferred(a) ? 0 : 1;
    const bMatch = isPreferred(b) ? 0 : 1;
    return aMatch - bMatch;
  });
});

function copyKeyword(keyword: string) {
  uni.setClipboardData({
    data: keyword,
    success: () => {
      uni.showToast({ title: `已复制：${keyword}`, icon: "none" });
    },
  });
}

function copyAllKeywords(cuisine: CuisineDirection) {
  const text = cuisine.keywords.join(" ");
  uni.setClipboardData({
    data: text,
    success: () => {
      uni.showToast({ title: "关键词已复制，去外卖App搜索吧", icon: "none" });
    },
  });
}

function goBack() {
  uni.navigateBack();
}
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

.header-card {
  background: #1F3D2E;
  border-radius: 24rpx;
  padding: 44rpx 36rpx;
  text-align: center;
  margin-bottom: 22rpx;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.12);
}

.header-card::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 200rpx;
  height: 100%;
  background: linear-gradient(135deg, transparent 40%, rgba(200, 118, 58, 0.25) 100%);
}

.header-icon {
  font-size: 72rpx;
  display: block;
  margin-bottom: 14rpx;
  position: relative;
  z-index: 1;
}

.header-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #FAF7F2;
  display: block;
  margin-bottom: 10rpx;
  letter-spacing: 2rpx;
  position: relative;
  z-index: 1;
}

.header-subtitle {
  font-size: 24rpx;
  color: rgba(250, 247, 242, 0.7);
  letter-spacing: 1rpx;
  position: relative;
  z-index: 1;
}

.pref-tip {
  background: #FBF1E6;
  border-radius: 14rpx;
  padding: 16rpx 26rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid rgba(200, 118, 58, 0.15);
}

.pref-tip-text {
  font-size: 26rpx;
  color: #8A5A2E;
  letter-spacing: 1rpx;
}

.cuisine-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  margin-bottom: 28rpx;
}

.cuisine-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx 26rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.cuisine-header {
  display: flex;
  align-items: center;
  margin-bottom: 22rpx;
}

.cuisine-emoji {
  font-size: 52rpx;
  margin-right: 20rpx;
}

.cuisine-title-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.cuisine-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.cuisine-desc {
  font-size: 22rpx;
  color: #8A8275;
  margin-top: 6rpx;
  letter-spacing: 0.5rpx;
}

.preferred-tag {
  background: #1F3D2E;
  color: #FAF7F2;
  font-size: 20rpx;
  padding: 6rpx 16rpx;
  border-radius: 6rpx;
  letter-spacing: 1rpx;
}

.keyword-section {
  margin-bottom: 20rpx;
}

.keyword-label {
  font-size: 22rpx;
  color: #8A8275;
  display: block;
  margin-bottom: 14rpx;
  letter-spacing: 2rpx;
}

.keyword-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.keyword-tag {
  background: #F4EFE6;
  color: #5A5042;
  padding: 12rpx 24rpx;
  border-radius: 8rpx;
  font-size: 26rpx;
  letter-spacing: 1rpx;
}

.copy-btn {
  background: #1F3D2E;
  border-radius: 12rpx;
  padding: 18rpx;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.copy-btn::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6rpx;
  background: #C8763A;
}

.copy-btn-text {
  color: #FAF7F2;
  font-size: 26rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.tips-card {
  background: #FBF1E6;
  border-radius: 20rpx;
  padding: 26rpx;
  display: flex;
  border: 1rpx solid rgba(200, 118, 58, 0.15);
}

.tips-icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.tips-content {
  display: flex;
  flex-direction: column;
}

.tips-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #8A5A2E;
  margin-bottom: 10rpx;
  letter-spacing: 1rpx;
}

.tips-text {
  font-size: 24rpx;
  color: #5A5042;
  line-height: 1.6;
  letter-spacing: 0.5rpx;
}
</style>
