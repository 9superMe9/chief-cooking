<!-- 推荐结果页：展示基于食材+偏好的推荐菜谱列表，含匹配度/缺失食材/风险标签；flexible/any 模式下额外展示汇总「补货/采购清单」供用户勾选。 -->
<template>
  <view class="container">
    <view class="nav-bar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="nav-title">推荐菜谱</text>
      <text class="nav-placeholder"></text>
    </view>

    <view class="loading" v-if="loading">
      <text class="loading-icon">🔍</text>
      <text class="loading-text">AI正在为您推荐...</text>
    </view>

    <view class="content" v-else>
      <view class="ingredients-summary">
        <text class="summary-title">已选食材：</text>
        <text class="summary-items">{{ ingredientNames }}</text>
        <text class="summary-mode">{{ modeLabel }}</text>
      </view>

      <view class="soup-warning" v-if="soupWarning">
        <text class="warning-icon">🍲</text>
        <text class="warning-text">{{ soupWarning }}</text>
      </view>

      <view class="shopping-summary" v-if="shoppingList.length > 0">
        <view class="shopping-header">
          <text class="shopping-title">{{ shoppingTitle }}</text>
          <text class="shopping-count">共 {{ shoppingList.length }} 样 · 已勾 {{ checkedCount }}/{{ shoppingList.length }}</text>
        </view>
        <view class="shopping-items">
          <view
            v-for="item in shoppingList"
            :key="item"
            class="shopping-item"
            :class="{ checked: checkedItems.has(item) }"
            @click="toggleShoppingItem(item)"
          >
            <view class="shopping-checkbox">
              <text v-if="checkedItems.has(item)">✓</text>
            </view>
            <text class="shopping-name">{{ item }}</text>
          </view>
        </view>
      </view>

      <view class="recipe-list" v-if="recipes.length > 0">
        <view
          v-for="(recipe, index) in recipes"
          :key="recipe.id"
          class="recipe-card"
          :class="{ 'fully-matched': recipe.missing_ingredients.length === 0 }"
          @click="goToDetail(recipe.id)"
        >
          <view class="recipe-rank">
            <text v-if="index === 0" class="rank gold">🥇</text>
            <text v-else-if="index === 1" class="rank silver">🥈</text>
            <text v-else-if="index === 2" class="rank bronze">🥉</text>
            <text v-else class="rank">{{ index + 1 }}</text>
          </view>

          <view class="recipe-info">
            <view class="recipe-header">
              <text class="recipe-name">{{ recipe.name }}</text>
              <text
                class="match-badge"
                :class="recipe.missing_ingredients.length === 0 ? 'badge-full' : 'badge-missing'"
              >
                {{ recipe.missing_ingredients.length === 0 ? '✓ 食材齐全' : `需补${recipe.missing_ingredients.length}样` }}
              </text>
            </view>

            <text class="recipe-reason">{{ recipe.recommendation_reason }}</text>

            <view class="recipe-tags">
              <text class="tag taste">{{ recipe.taste }}</text>
              <text class="tag time">{{ recipe.cooking_time }}</text>
              <text class="tag difficulty">{{ recipe.difficulty }}</text>
            </view>

            <view class="ingredients-match">
              <text class="matched">✅ 已有: {{ recipe.matched_ingredients.join(", ") }}</text>
              <text class="missing" v-if="recipe.missing_ingredients.length">🛒 需补: {{ recipe.missing_ingredients.join(", ") }}</text>
            </view>

            <view class="risk-warning" v-if="recipe.risk_tags.length > 0">
              <text class="risk-icon">⚠️</text>
              <text class="risk-text">风险提醒: {{ recipe.risk_tags.join(", ") }}</text>
            </view>
          </view>

          <view class="recipe-arrow">→</view>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="empty-icon">🍽️</text>
        <text class="empty-title">当前食材没有完全匹配的菜谱</text>
        <text class="empty-hint">试试允许补 1-2 样食材，或换个场景</text>
        <view class="empty-btn" @click="switchToFlexible" v-if="recipeStore.recommendMode === 'strict'">允许补 1-2 样食材 →</view>
        <view class="empty-btn" @click="goBack" v-else>重新选择食材</view>
      </view>

      <view
        class="downgrade-tip"
        v-if="recipes.length > 0 && recipes.length < 3 && recipeStore.recommendMode === 'strict'"
      >
        <text class="downgrade-text">匹配结果较少？可以允许补 1-2 样食材</text>
        <view class="downgrade-btn" @click="switchToFlexible">放宽条件 →</view>
      </view>
    </view>

    <view class="footer" v-if="!loading && recipes.length > 0">
      <view class="refresh-btn" :class="{ refreshing: refreshing }" @click="refreshRecommendations">
        <text>{{ refreshing ? "推荐中..." : "🔄 重新推荐" }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRecipeStore } from "../../stores/recipe";
import { recommendRecipes, type RecipeResponse } from "../../api/recipes";

const recipeStore = useRecipeStore();
const loading = ref(true);
const refreshing = ref(false);
const recipes = ref<RecipeResponse[]>([]);
const soupWarning = ref("");

const ingredientNames = computed(() => 
  recipeStore.ingredients.map(i => i.name).join(", ")
);

const modeLabel = computed(() => {
  const mode = recipeStore.recommendMode;
  if (mode === "strict") return "🏠 在家做饭 · 只用现有食材";
  if (mode === "flexible") return "🛒 愿意补货 · 缺1-2样也行";
  return "🛒 在超市 · 看菜谱选购";
});

// 汇总补货/采购清单：聚合所有推荐菜的缺失食材并去重
const shoppingList = computed(() => {
  const set = new Set<string>();
  recipes.value.forEach(r => {
    (r.missing_ingredients || []).forEach(i => set.add(i));
  });
  return Array.from(set);
});

const shoppingTitle = computed(() =>
  recipeStore.recommendMode === "any" ? "🛒 采购清单" : "🛒 补货清单"
);

const checkedItems = ref<Set<string>>(new Set());

const checkedCount = computed(() =>
  shoppingList.value.filter(i => checkedItems.value.has(i)).length
);

function toggleShoppingItem(item: string) {
  const next = new Set(checkedItems.value);
  if (next.has(item)) next.delete(item);
  else next.add(item);
  checkedItems.value = next;
}

function goBack() {
  uni.navigateBack();
}

async function fetchRecommendations() {
  loading.value = true;
  try {
    const ingredients = recipeStore.ingredients.map(i => i.name);
    const preferences = recipeStore.preferences;
    
    const res = await recommendRecipes({
      ingredients,
      preferences,
      mode: recipeStore.recommendMode
    });
    
    recipes.value = res.recipes;
    soupWarning.value = res.soup_warning || "";
    recipeStore.setRecommendedRecipes(res.recipes);
  } catch (error) {
    console.error("推荐失败:", error);
    uni.showToast({ title: "推荐失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function switchToFlexible() {
  recipeStore.setRecommendMode("flexible");
  fetchRecommendations();
}

function refreshRecommendations() {
  if (refreshing.value) return;
  refreshing.value = true;
  fetchRecommendations().finally(() => {
    refreshing.value = false;
  });
}

function goToDetail(recipeId: string) {
  uni.navigateTo({ url: `/pages/detail/index?id=${recipeId}` });
}

onMounted(() => {
  fetchRecommendations();
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

.loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-icon {
  font-size: 100rpx;
  margin-bottom: 30rpx;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 28rpx;
  color: #8A8275;
  letter-spacing: 2rpx;
}

.content {
  flex: 1;
  padding: 20rpx 30rpx 30rpx;
}

.ingredients-summary {
  background: #FBF8F1;
  border-radius: 16rpx;
  padding: 22rpx 26rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #E8E2D6;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.summary-title {
  font-size: 22rpx;
  color: #8A8275;
  letter-spacing: 2rpx;
}

.summary-items {
  font-size: 28rpx;
  color: #1F3D2E;
  font-weight: 600;
  letter-spacing: 1rpx;
}

.summary-mode {
  font-size: 22rpx;
  color: #C8763A;
  margin-top: 4rpx;
  letter-spacing: 1rpx;
}

/* 汤类不足提示 */
.soup-warning {
  display: flex;
  align-items: center;
  background: #FBF1E6;
  border-left: 6rpx solid #C8763A;
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 22rpx;
  gap: 12rpx;
}

.warning-icon {
  font-size: 32rpx;
}

.warning-text {
  font-size: 24rpx;
  color: #8A5A2E;
  line-height: 1.5;
  letter-spacing: 1rpx;
  flex: 1;
}

/* 汇总补货/采购清单 */
.shopping-summary {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx 26rpx;
  margin-bottom: 22rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
  border-left: 6rpx solid #C8763A;
}

.shopping-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 18rpx;
}

.shopping-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.shopping-count {
  font-size: 22rpx;
  color: #8A8275;
  letter-spacing: 0.5rpx;
}

.shopping-items {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.shopping-item {
  display: flex;
  align-items: center;
  background: #FBF8F1;
  border: 1rpx solid #E8E2D6;
  padding: 12rpx 20rpx 12rpx 16rpx;
  border-radius: 10rpx;

  &.checked {
    background: #EAF0EC;
    border-color: #1F3D2E;

    .shopping-name {
      color: #1F3D2E;
      text-decoration: line-through;
      opacity: 0.7;
    }
  }
}

.shopping-checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid #D9D2C4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14rpx;
  font-size: 22rpx;
  color: #FAF7F2;

  .checked & {
    background: #1F3D2E;
    border-color: #1F3D2E;
  }
}

.shopping-name {
  font-size: 26rpx;
  color: #5A5042;
  letter-spacing: 1rpx;
}

.recipe-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.recipe-card {
  display: flex;
  align-items: stretch;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx 26rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);

  &.fully-matched {
    border-left: 6rpx solid #1F3D2E;
  }
}

.recipe-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 22rpx;
}

.rank {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F4EFE6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 600;
  color: #5A5042;

  &.gold {
    background: #F4D9A6;
    font-size: 32rpx;
  }

  &.silver {
    background: #E0DACE;
    font-size: 32rpx;
  }

  &.bronze {
    background: #E8C9A6;
    font-size: 32rpx;
  }
}

.recipe-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.recipe-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.recipe-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.match-badge {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  letter-spacing: 1rpx;
  font-weight: 600;
}

.badge-full {
  background: #EAF0EC;
  color: #1F3D2E;
}

.badge-missing {
  background: #FBF1E6;
  color: #C8763A;
}

.recipe-reason {
  font-size: 26rpx;
  color: #5A5042;
  line-height: 1.6;
}

.recipe-tags {
  display: flex;
  gap: 10rpx;
}

.tag {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
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

.ingredients-match {
  display: flex;
  flex-direction: column;
  gap: 5rpx;
}

.matched {
  font-size: 24rpx;
  color: #4A7C59;
  letter-spacing: 0.5rpx;
}

.missing {
  font-size: 24rpx;
  color: #B0533A;
  letter-spacing: 0.5rpx;
}

.risk-warning {
  display: flex;
  align-items: center;
  background: #FBF1E6;
  padding: 12rpx 18rpx;
  border-radius: 8rpx;
  border: 1rpx solid rgba(200, 118, 58, 0.15);

  .risk-icon {
    margin-right: 12rpx;
  }

  .risk-text {
    font-size: 24rpx;
    color: #8A5A2E;
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

.downgrade-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #FBF8F1;
  border: 1rpx dashed #C8763A;
  border-radius: 14rpx;
  padding: 24rpx;
  margin-top: 22rpx;
  gap: 14rpx;
}

.downgrade-text {
  font-size: 24rpx;
  color: #8A5A2E;
  letter-spacing: 1rpx;
}

.downgrade-btn {
  background: #C8763A;
  color: #FAF7F2;
  padding: 14rpx 40rpx;
  border-radius: 10rpx;
  font-size: 26rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.footer {
  padding: 12rpx 30rpx 40rpx;
}

.refresh-btn {
  background: #F4EFE6;
  color: #5A5042;
  text-align: center;
  padding: 26rpx;
  border-radius: 12rpx;
  font-size: 30rpx;
  letter-spacing: 2rpx;

  &.refreshing {
    opacity: 0.6;
    pointer-events: none;
  }
}
</style>