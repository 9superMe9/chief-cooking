<!-- 菜谱详情页：展示菜谱图片/食材清单/烹饪步骤/替代建议/风险/收藏；支持「采购模式」(shopping=1 或手动开关)，将食材清单变为可勾选采购清单并显示已买进度。 -->
<template>
  <view class="container">
    <view class="nav-bar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="nav-title">菜谱详情</text>
      <view class="nav-actions">
        <text class="nav-shopping" :class="{ active: shoppingMode }" @click="toggleShoppingMode">采购</text>
        <text class="nav-action" @click="toggleFavorite">{{ isFavorited ? "❤️" : "🤍" }}</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-content">
      <view class="recipe-header">
        <image v-if="recipe.image_url" class="recipe-image" :src="recipe.image_url" mode="aspectFill" />
        <view v-else class="recipe-image recipe-image-placeholder">
          <text class="placeholder-emoji">🍽️</text>
        </view>
        <view class="recipe-badge" v-if="recipe.category">{{ recipe.category }}</view>
      </view>

      <view class="recipe-info">
        <text class="recipe-name">{{ recipe.name }}</text>
        <text class="recipe-description" v-if="recipe.description">{{ recipe.description }}</text>

        <view class="recipe-stats">
          <view class="stat-item">
            <text class="stat-icon">⏱️</text>
            <text class="stat-value">{{ recipe.cooking_time }}</text>
          </view>
          <view class="stat-item">
            <text class="stat-icon">🍽️</text>
            <text class="stat-value">{{ recipe.servings }}</text>
          </view>
          <view class="stat-item">
            <text class="stat-icon">👨‍🍳</text>
            <text class="stat-value">{{ recipe.difficulty }}</text>
          </view>
          <view class="stat-item">
            <text class="stat-icon">😋</text>
            <text class="stat-value">{{ recipe.taste }}</text>
          </view>
        </view>

        <view class="reason-card">
          <text class="reason-title">💡 AI推荐理由</text>
          <text class="reason-content">{{ recipe.recommendation_reason }}</text>
        </view>
      </view>

      <view class="section">
        <view class="section-head-row">
          <text class="section-title">📝 食材清单</text>
          <text class="shopping-progress" v-if="shoppingMode">已买 {{ boughtCount }}/{{ (recipe.ingredients || []).length }}</text>
        </view>
        <view class="ingredient-list">
          <view
            v-for="(ing, index) in recipe.ingredients"
            :key="index"
            class="ingredient-item"
            :class="{ 'item-bought': shoppingMode && boughtSet.has(ing), 'item-clickable': shoppingMode }"
            @click="onIngredientTap(ing)"
          >
            <view
              class="checkbox"
              :class="{ 'checkbox-shop': shoppingMode, 'checkbox-bought': shoppingMode && boughtSet.has(ing) }"
            >
              <text v-if="!shoppingMode || boughtSet.has(ing)">✓</text>
            </view>
            <text class="ingredient-name">{{ ing }}</text>
            <text v-if="!shoppingMode" class="ingredient-status" :class="{ missing: !isIngredientAvailable(ing) }">
              {{ isIngredientAvailable(ing) ? "已有" : "缺少" }}
            </text>
            <text v-else class="ingredient-status" :class="{ missing: !isIngredientAvailable(ing) }">
              {{ isIngredientAvailable(ing) ? "已有" : "待买" }}
            </text>
          </view>
        </view>
      </view>

      <view class="section">
        <text class="section-title">👩‍🍳 烹饪步骤</text>
        <view class="steps-list">
          <view v-for="(step, index) in recipe.steps" :key="index" class="step-item">
            <view class="step-number">{{ index + 1 }}</view>
            <text class="step-content">{{ step }}</text>
          </view>
        </view>
      </view>

      <view class="section" v-if="recipe.alternative_suggestions && Object.keys(recipe.alternative_suggestions).length > 0">
        <text class="section-title">🔄 替代食材建议</text>
        <view class="alternative-list">
          <view v-for="(suggestions, missing) in recipe.alternative_suggestions" :key="missing" class="alternative-item">
            <text class="missing-item">{{ missing }} →</text>
            <text class="suggestions">{{ suggestions.join(", ") }}</text>
          </view>
        </view>
      </view>

      <view class="section" v-if="recipe.risk_tags && recipe.risk_tags.length > 0">
        <text class="section-title">⚠️ 风险提醒</text>
        <view class="risk-list">
          <text v-for="tag in recipe.risk_tags" :key="tag" class="risk-tag">{{ tag }}</text>
        </view>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>

    <view class="footer">
      <view class="share-btn" @click="shareRecipe">📤 分享</view>
      <view class="cook-btn" @click="startCooking">👨‍🍳 开始烹饪</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRecipeStore } from "../../stores/recipe";
import { getRecipe, addFavorite, removeFavorite, getFavoriteStatus, type RecipeResponse } from "../../api/recipes";

const recipeStore = useRecipeStore();
const recipe = ref<RecipeResponse>({} as RecipeResponse);
const isFavorited = ref(false);
const shoppingMode = ref(false);
const boughtSet = ref<Set<string>>(new Set());

const ingredientNames = computed(() => recipeStore.ingredients.map(i => i.name));

function goBack() {
  uni.navigateBack();
}

function isIngredientAvailable(ingredient: string): boolean {
  return ingredientNames.value.some(name =>
    ingredient.includes(name) || name.includes(ingredient)
  );
}

const boughtCount = computed(() =>
  (recipe.value.ingredients || []).filter(i => boughtSet.value.has(i)).length
);

function initBoughtSet() {
  const next = new Set<string>();
  (recipe.value.ingredients || []).forEach(ing => {
    if (isIngredientAvailable(ing)) next.add(ing);
  });
  boughtSet.value = next;
}

function toggleShoppingMode() {
  shoppingMode.value = !shoppingMode.value;
  if (shoppingMode.value) initBoughtSet();
}

function onIngredientTap(ing: string) {
  if (!shoppingMode.value) return;
  const next = new Set(boughtSet.value);
  if (next.has(ing)) next.delete(ing);
  else next.add(ing);
  boughtSet.value = next;
}

async function fetchRecipe() {
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1] as { options?: { id?: string; shopping?: string } };
  const recipeId = currentPage.options?.id;
  const wantShopping = currentPage.options?.shopping === "1";

  if (!recipeId) {
    const recommended = recipeStore.recommendedRecipes[0];
    if (recommended) {
      recipe.value = recommended;
      if (wantShopping) {
        shoppingMode.value = true;
        initBoughtSet();
      }
    }
    return;
  }

  try {
    const res = await getRecipe(recipeId);
    recipe.value = res;
    if (wantShopping) {
      shoppingMode.value = true;
      initBoughtSet();
    }
  } catch (error) {
    console.error("获取菜谱失败:", error);
    uni.showToast({ title: "获取失败", icon: "none" });
  }
}

async function checkFavoriteStatus() {
  if (!recipe.value.id) return;
  try {
    const res = await getFavoriteStatus(recipe.value.id);
    isFavorited.value = res.data.is_favorited;
  } catch {
    isFavorited.value = false;
  }
}

async function toggleFavorite() {
  if (!recipe.value.id) return;
  
  try {
    if (isFavorited.value) {
      await removeFavorite(recipe.value.id);
      isFavorited.value = false;
      uni.showToast({ title: "已取消收藏", icon: "none" });
    } else {
      await addFavorite(recipe.value.id);
      isFavorited.value = true;
      uni.showToast({ title: "收藏成功", icon: "success" });
    }
  } catch {
    uni.showToast({ title: "操作失败", icon: "none" });
  }
}

function shareRecipe() {
  uni.showToast({ title: "分享功能开发中", icon: "none" });
}

function startCooking() {
  uni.showToast({ title: "开始烹饪！", icon: "success" });
}

onMounted(() => {
  fetchRecipe();
  setTimeout(checkFavoriteStatus, 100);
});
</script>

<style lang="scss" scoped>
/* 现代食器主题：与首页统一 */
.container {
  min-height: 100vh;
  background: #FAF7F2;
  display: flex;
  flex-direction: column;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 50rpx 30rpx 20rpx;
  background: rgba(250, 247, 242, 0.92);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  backdrop-filter: blur(8rpx);
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

.nav-action {
  font-size: 40rpx;
  padding: 10rpx;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.nav-shopping {
  font-size: 24rpx;
  color: #8A8275;
  padding: 8rpx 18rpx;
  border-radius: 8rpx;
  border: 1rpx solid #E8E2D6;
  letter-spacing: 1rpx;

  &.active {
    background: #C8763A;
    color: #FAF7F2;
    border-color: #C8763A;
  }
}

.scroll-content {
  flex: 1;
  padding-top: 100rpx;
}

.recipe-header {
  position: relative;
}

.recipe-image {
  width: 100%;
  height: 400rpx;
  border-radius: 0 0 30rpx 30rpx;
}

.recipe-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #F4EFE6 0%, #E8DDC8 100%);
}

.placeholder-emoji {
  font-size: 120rpx;
}

.recipe-badge {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  background: rgba(31, 61, 46, 0.92);
  color: #FAF7F2;
  padding: 10rpx 22rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
  letter-spacing: 1rpx;
}

.recipe-info {
  background: #FFFFFF;
  padding: 32rpx;
  margin: -30rpx 20rpx 20rpx;
  border-radius: 24rpx;
  position: relative;
  z-index: 10;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.recipe-name {
  font-size: 40rpx;
  font-weight: 600;
  color: #1F3D2E;
  display: block;
  margin-bottom: 14rpx;
  letter-spacing: 1rpx;
}

.recipe-description {
  font-size: 28rpx;
  color: #5A5042;
  line-height: 1.6;
  margin-bottom: 24rpx;
  display: block;
}

.recipe-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24rpx;
  padding: 20rpx 0;
  border-top: 1rpx solid #E8E2D6;
  border-bottom: 1rpx solid #E8E2D6;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.stat-icon {
  font-size: 36rpx;
}

.stat-value {
  font-size: 24rpx;
  color: #5A5042;
  letter-spacing: 1rpx;
}

.reason-card {
  background: #FBF1E6;
  padding: 22rpx 24rpx;
  border-radius: 14rpx;
  border: 1rpx solid rgba(200, 118, 58, 0.15);
}

.reason-title {
  font-size: 24rpx;
  font-weight: 600;
  color: #8A5A2E;
  margin-bottom: 10rpx;
  display: block;
  letter-spacing: 2rpx;
}

.reason-content {
  font-size: 28rpx;
  color: #5A5042;
  line-height: 1.6;
}

.section {
  background: #FFFFFF;
  margin: 0 20rpx 20rpx;
  padding: 32rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.section-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1F3D2E;
  margin-bottom: 24rpx;
  display: block;
  letter-spacing: 2rpx;
}

.section-head-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 24rpx;

  .section-title {
    margin-bottom: 0;
  }
}

.shopping-progress {
  font-size: 22rpx;
  color: #C8763A;
  letter-spacing: 1rpx;
}

.ingredient-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.ingredient-item {
  display: flex;
  align-items: center;
  padding: 14rpx 0;
  border-bottom: 1rpx solid #E8E2D6;

  &:last-child {
    border-bottom: none;
  }
}

.ingredient-item.item-clickable {
  cursor: pointer;
}

.ingredient-item.item-bought {
  opacity: 0.55;
}

.ingredient-item.item-bought .ingredient-name {
  text-decoration: line-through;
  color: #8A8275;
}

.checkbox {
  width: 38rpx;
  height: 38rpx;
  border-radius: 50%;
  background: #EAF0EC;
  color: #1F3D2E;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  margin-right: 20rpx;
  box-sizing: border-box;
}

.checkbox.checkbox-shop {
  background: #FFFFFF;
  border: 2rpx solid #C8763A;
}

.checkbox.checkbox-bought {
  background: #C8763A;
  color: #FAF7F2;
  border: 2rpx solid #C8763A;
}

.ingredient-name {
  flex: 1;
  font-size: 30rpx;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.ingredient-status {
  font-size: 22rpx;
  color: #4A7C59;
  letter-spacing: 1rpx;

  &.missing {
    color: #B0533A;
  }
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.step-item {
  display: flex;
}

.step-number {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  background: #1F3D2E;
  color: #FAF7F2;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 600;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  font-size: 28rpx;
  color: #2A2A2A;
  line-height: 1.6;
  padding-top: 8rpx;
}

.alternative-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.alternative-item {
  display: flex;
  align-items: center;
}

.missing-item {
  font-size: 28rpx;
  color: #B0533A;
  margin-right: 14rpx;
  letter-spacing: 1rpx;
}

.suggestions {
  font-size: 28rpx;
  color: #4A7C59;
  letter-spacing: 1rpx;
}

.risk-list {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.risk-tag {
  background: #FBF1E6;
  color: #8A5A2E;
  padding: 12rpx 26rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  letter-spacing: 1rpx;
  border: 1rpx solid rgba(200, 118, 58, 0.15);
}

.bottom-space {
  height: 150rpx;
}

.footer {
  display: flex;
  gap: 22rpx;
  padding: 16rpx 30rpx 36rpx;
  background: rgba(250, 247, 242, 0.96);
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  backdrop-filter: blur(8rpx);
}

.share-btn {
  flex: 1;
  background: #F4EFE6;
  color: #5A5042;
  text-align: center;
  padding: 26rpx;
  border-radius: 12rpx;
  font-size: 30rpx;
  letter-spacing: 2rpx;
}

.cook-btn {
  flex: 2;
  background: #1F3D2E;
  color: #FAF7F2;
  text-align: center;
  padding: 26rpx;
  border-radius: 12rpx;
  font-size: 30rpx;
  font-weight: 600;
  letter-spacing: 4rpx;
  position: relative;
  overflow: hidden;
}

.cook-btn::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6rpx;
  background: #C8763A;
}
</style>