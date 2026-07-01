<!-- 菜谱浏览页：在超市「有想做的菜谱」分支入口。拉取全部菜谱，支持按菜名搜索与分类筛选，点击菜谱进入 detail 页的采购清单模式（shopping=1）。 -->
<template>
  <view class="container">
    <view class="nav-bar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="nav-title">选择菜谱</text>
      <text class="nav-placeholder"></text>
    </view>

    <view class="search-area">
      <view class="search-box">
        <text class="search-icon">🔍</text>
        <input
          v-model="keyword"
          class="search-input"
          placeholder="搜索菜名，如：番茄炒蛋"
          placeholder-class="search-placeholder"
        />
        <text class="clear-btn" v-if="keyword" @click="keyword = ''">×</text>
      </view>
    </view>

    <scroll-view scroll-x class="category-bar" show-scrollbar="false">
      <view
        v-for="cat in categories"
        :key="cat"
        class="category-chip"
        :class="{ active: activeCategory === cat }"
        @click="activeCategory = cat"
      >{{ cat }}</view>
    </scroll-view>

    <view class="loading" v-if="loading">
      <text class="loading-text">加载菜谱中...</text>
    </view>

    <scroll-view scroll-y class="recipe-scroll" v-else>
      <view class="recipe-list" v-if="filteredRecipes.length > 0">
        <view
          v-for="recipe in filteredRecipes"
          :key="recipe.id"
          class="recipe-card"
          @click="goToShopping(recipe.id)"
        >
          <image v-if="recipe.image_url" class="recipe-image" :src="recipe.image_url" mode="aspectFill" />
          <view v-else class="recipe-image recipe-image-placeholder">
            <text class="placeholder-emoji">🍽️</text>
          </view>
          <view class="recipe-info">
            <view class="recipe-header">
              <text class="recipe-name">{{ recipe.name }}</text>
              <text class="recipe-category" v-if="recipe.category">{{ recipe.category }}</text>
            </view>
            <text class="recipe-desc">{{ recipe.description }}</text>
            <view class="recipe-tags">
              <text class="tag taste" v-if="recipe.taste">{{ recipe.taste }}</text>
              <text class="tag time" v-if="recipe.cooking_time">{{ recipe.cooking_time }}</text>
              <text class="tag difficulty" v-if="recipe.difficulty">{{ recipe.difficulty }}</text>
            </view>
          </view>
          <text class="recipe-arrow">→</text>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="empty-icon">🍽️</text>
        <text class="empty-text">没有找到相关菜谱</text>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { getRecipes, type RecipeResponse } from "../../api/recipes";

const loading = ref(true);
const recipes = ref<RecipeResponse[]>([]);
const keyword = ref("");
const activeCategory = ref("全部");

const categories = computed(() => {
  const set = new Set<string>();
  recipes.value.forEach(r => {
    if (r.category) set.add(r.category);
  });
  return ["全部", ...Array.from(set)];
});

const filteredRecipes = computed(() => {
  const kw = keyword.value.trim();
  return recipes.value.filter(r => {
    const matchCat = activeCategory.value === "全部" || r.category === activeCategory.value;
    const matchKw = !kw || (r.name || "").includes(kw);
    return matchCat && matchKw;
  });
});

function goBack() {
  uni.navigateBack();
}

function goToShopping(recipeId: string) {
  uni.navigateTo({ url: `/pages/detail/index?id=${recipeId}&shopping=1` });
}

async function fetchRecipes() {
  loading.value = true;
  try {
    const res = await getRecipes();
    recipes.value = res || [];
  } catch (error) {
    console.error("获取菜谱失败:", error);
    uni.showToast({ title: "加载失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchRecipes();
});
</script>

<style lang="scss" scoped>
/* 现代食器主题：与全项目统一 */
.container {
  min-height: 100vh;
  background: #FAF7F2;
  background-image:
    radial-gradient(circle at 15% 10%, rgba(31, 61, 46, 0.04) 0%, transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(200, 118, 58, 0.05) 0%, transparent 45%);
  display: flex;
  flex-direction: column;
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

.search-area {
  padding: 10rpx 30rpx 20rpx;
}

.search-box {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 10rpx 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.search-icon {
  font-size: 28rpx;
  margin-right: 14rpx;
  color: #8A8275;
}

.search-input {
  flex: 1;
  height: 72rpx;
  font-size: 28rpx;
  color: #2A2A2A;
}

.search-placeholder {
  color: #B5AC9B;
  font-size: 26rpx;
}

.clear-btn {
  font-size: 36rpx;
  color: #B5AC9B;
  padding: 0 6rpx;
  line-height: 1;
}

.category-bar {
  white-space: nowrap;
  padding: 0 24rpx 22rpx;
}

.category-chip {
  display: inline-block;
  background: #FFFFFF;
  color: #5A5042;
  padding: 14rpx 30rpx;
  border-radius: 10rpx;
  font-size: 26rpx;
  margin-right: 14rpx;
  border: 1rpx solid rgba(31, 61, 46, 0.08);
  letter-spacing: 1rpx;

  &.active {
    background: #1F3D2E;
    color: #FAF7F2;
    border-color: #1F3D2E;
  }
}

.loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-text {
  font-size: 28rpx;
  color: #8A8275;
  letter-spacing: 2rpx;
}

.recipe-scroll {
  flex: 1;
  padding: 0 30rpx;
}

.recipe-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.recipe-card {
  display: flex;
  align-items: stretch;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 20rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.recipe-image {
  width: 160rpx;
  height: 160rpx;
  border-radius: 14rpx;
  flex-shrink: 0;
  background: #F4EFE6;
}

.recipe-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #F4EFE6 0%, #E8DDC8 100%);
}

.placeholder-emoji {
  font-size: 64rpx;
}

.recipe-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 22rpx;
  min-width: 0;
  justify-content: space-between;
}

.recipe-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.recipe-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.recipe-category {
  font-size: 20rpx;
  color: #C8763A;
  background: #FBF1E6;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
}

.recipe-desc {
  font-size: 24rpx;
  color: #8A8275;
  line-height: 1.5;
  margin-top: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.recipe-tags {
  display: flex;
  gap: 10rpx;
  margin-top: 10rpx;
  flex-wrap: wrap;
}

.tag {
  font-size: 20rpx;
  padding: 4rpx 14rpx;
  border-radius: 6rpx;
  letter-spacing: 0.5rpx;

  &.taste {
    background: #EAF0EC;
    color: #1F3D2E;
  }

  &.time {
    background: #FBF1E6;
    color: #8A5A2E;
  }

  &.difficulty {
    background: #F4EFE6;
    color: #5A5042;
  }
}

.recipe-arrow {
  display: flex;
  align-items: center;
  font-size: 32rpx;
  color: #C8763A;
  padding-left: 12rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #8A8275;
  letter-spacing: 1rpx;
}

.bottom-space {
  height: 40rpx;
}
</style>
