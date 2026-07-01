<template>
  <view class="container">
    <view class="nav-bar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="nav-title">历史记录</text>
      <text class="refresh-btn" v-if="!loading" @click="fetchHistory">刷新</text>
    </view>

    <view class="content">
      <view class="history-list" v-if="groupedHistory.length > 0">
        <view v-for="(record, index) in groupedHistory" :key="index" class="history-card">
          <view class="history-header">
            <text class="history-date">{{ record.date }}</text>
            <text class="history-count">{{ record.recipes.length }}道菜谱</text>
          </view>
          <view class="recipe-list">
            <view
              v-for="recipe in record.recipes"
              :key="recipe.id"
              class="recipe-item"
              @click="goToDetail(recipe.id)"
            >
              <text class="recipe-name">{{ recipe.name }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="empty-state" v-else-if="!loading">
        <text class="empty-icon">📜</text>
        <text class="empty-title">暂无历史记录</text>
        <text class="empty-hint">快去探索美味菜谱吧</text>
        <view class="empty-btn" @click="goHome">去逛逛</view>
      </view>

      <view class="loading-state" v-else>
        <text class="loading-text">加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getRecommendationHistory, type HistoryItem, type RecipeResponse } from "../../api/recipes";

interface HistoryRecord {
  date: string;
  recipes: RecipeResponse[];
}

const groupedHistory = ref<HistoryRecord[]>([]);
const loading = ref(false);

function formatDate(iso: string): string {
  const date = new Date(iso);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const dateOnly = new Date(date);
  dateOnly.setHours(0, 0, 0, 0);

  if (dateOnly.getTime() === today.getTime()) return "今天";
  if (dateOnly.getTime() === yesterday.getTime()) return "昨天";
  return `${date.getMonth() + 1}月${date.getDate()}日`;
}

function groupByDate(items: HistoryItem[]): HistoryRecord[] {
  const groups: Record<string, RecipeResponse[]> = {};
  const order: string[] = [];
  items.forEach(item => {
    const label = formatDate(item.created_at);
    if (!groups[label]) {
      groups[label] = [];
      order.push(label);
    }
    groups[label].push(...item.recipes);
  });
  return order.map(date => ({ date, recipes: groups[date] }));
}

async function fetchHistory() {
  loading.value = true;
  try {
    const res = await getRecommendationHistory(20);
    groupedHistory.value = groupByDate(res.history || []);
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goBack() {
  uni.navigateBack();
}

function goHome() {
  uni.reLaunch({ url: "/pages/index/index" });
}

function goToDetail(recipeId: string) {
  uni.navigateTo({ url: `/pages/detail/index?id=${recipeId}` });
}

onMounted(() => {
  fetchHistory();
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

.refresh-btn {
  font-size: 26rpx;
  color: #C8763A;
  letter-spacing: 2rpx;
  font-weight: 600;
}

.content {
  padding: 20rpx 30rpx 40rpx;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.history-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx 26rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #E8E2D6;
}

.history-date {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.history-count {
  font-size: 22rpx;
  color: #8A8275;
  letter-spacing: 1rpx;
}

.recipe-list {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.recipe-item {
  background: #F4EFE6;
  padding: 14rpx 28rpx;
  border-radius: 8rpx;
}

.recipe-name {
  font-size: 26rpx;
  color: #5A5042;
  letter-spacing: 1rpx;
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

.loading-state {
  display: flex;
  justify-content: center;
  padding: 100rpx 0;
}

.loading-text {
  font-size: 28rpx;
  color: #8A8275;
  letter-spacing: 2rpx;
}
</style>
