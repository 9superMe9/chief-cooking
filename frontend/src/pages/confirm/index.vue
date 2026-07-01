<template>
  <view class="container">
    <view class="nav-bar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="nav-title">确认食材</text>
      <text class="nav-placeholder"></text>
    </view>

    <view class="content">
      <view class="page-intro">
        <text class="intro-icon">🥬</text>
        <view class="intro-text">
          <text class="intro-title">家里现在有什么食材？</text>
          <text class="intro-desc">确认现有食材，推荐菜谱后会告诉你还缺什么要买</text>
        </view>
      </view>

      <view class="upload-area" @click="chooseImage">
        <view class="upload-left">
          <text class="upload-icon">📷</text>
        </view>
        <view class="upload-body">
          <text class="upload-text">拍照识别食材</text>
          <text class="upload-hint">拍一张冰箱照片，AI 帮你认</text>
        </view>
        <text class="upload-arrow">›</text>
      </view>

      <view class="input-area">
        <view class="input-box">
          <input
            v-model="inputText"
            class="ingredient-input"
            placeholder="或手动输入，逗号分隔"
            placeholder-class="input-placeholder"
            @confirm="handleManualInput"
          />
          <text class="join-btn" @click="handleManualInput">加入</text>
        </view>
      </view>

      <view class="quick-tags">
        <view class="section-head">
          <text class="section-title">常用食材</text>
          <text class="clear-btn" v-if="ingredients.length > 0" @click="clearAll">清空</text>
        </view>
        <view class="tags">
          <text
            v-for="tag in commonIngredients"
            :key="tag"
            class="tag"
            :class="{ active: hasIngredient(tag) }"
            @click="toggleIngredient(tag)"
          >{{ tag }}</text>
        </view>
      </view>

      <view class="ingredient-list" v-if="ingredients.length > 0">
        <view v-for="item in ingredients" :key="item.id" class="ingredient-item">
          <view class="checkbox" :class="{ checked: item.status !== 'pending' }">
            <text v-if="item.status !== 'pending'">✓</text>
          </view>
          <text class="ingredient-name">{{ item.name }}</text>
          <text class="ingredient-category" v-if="item.category">{{ item.category }}</text>
          <text class="confidence" v-if="item.confidence">置信度: {{ Math.round(item.confidence * 100) }}%</text>
          <text class="remove-btn" @click="removeItem(item.id)">删除</text>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="empty-icon">🍽️</text>
        <text class="empty-text">还没有添加食材</text>
        <text class="empty-hint">用上方拍照识别或点常用标签快速添加</text>
      </view>

      <view class="status-hint" v-if="hasPending">
        <text class="pending-icon">⚠️</text>
        <text>以上为AI识别结果，请确认是否正确</text>
      </view>
    </view>

    <view class="footer">
      <view class="confirm-btn" @click="confirmIngredients">确认并继续</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRecipeStore } from "../../stores/recipe";
import { uploadImage, recognizeIngredients } from "../../api/ingredients";

const recipeStore = useRecipeStore();
const inputText = ref("");

const ingredients = computed(() => recipeStore.ingredients);

const commonIngredients = [
  "鸡蛋", "番茄", "米饭", "青菜", "豆腐", "猪肉", "鸡肉", "鱼",
  "土豆", "黄瓜", "青椒", "胡萝卜", "西兰花", "虾仁", "牛肉"
];

const hasPending = computed(() =>
  ingredients.value.some(item => item.status === "pending")
);

function goBack() {
  uni.navigateBack();
}

function hasIngredient(name: string): boolean {
  return !!ingredients.value.find(i => i.name === name);
}

function toggleIngredient(tag: string) {
  const existing = ingredients.value.find(i => i.name === tag);
  if (existing) {
    recipeStore.removeIngredient(existing.id);
  } else {
    recipeStore.addIngredient({
      id: `ing-${Date.now()}`,
      name: tag,
      status: "confirmed"
    });
  }
}

function handleManualInput() {
  if (!inputText.value.trim()) return;
  const items = inputText.value.split(/[,，、\s]+/).filter(item => item.trim());
  items.forEach(item => {
    const name = item.trim();
    if (!hasIngredient(name)) {
      recipeStore.addIngredient({
        id: `ing-${Date.now()}-${name}`,
        name,
        status: "confirmed"
      });
    }
  });
  inputText.value = "";
}

function clearAll() {
  [...ingredients.value].forEach(i => recipeStore.removeIngredient(i.id));
}

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sourceType: ["album", "camera"],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0];
      uni.showLoading({ title: "上传中...", mask: true });
      try {
        const uploadRes = await uploadImage(tempFilePath);
        uni.showLoading({ title: "识别中...", mask: true });
        const recognizeRes = await recognizeIngredients(uploadRes.file_id, uploadRes.image_url);
        uni.hideLoading();

        if (!recognizeRes.ingredients || recognizeRes.ingredients.length === 0) {
          uni.showToast({ title: recognizeRes.message || "未识别到食材，请手动输入", icon: "none" });
          return;
        }

        const names = recognizeRes.ingredients.map(i => i.name);
        names.forEach(name => {
          if (!hasIngredient(name)) {
            recipeStore.addIngredient({
              id: `ing-${Date.now()}-${name}`,
              name,
              status: "confirmed"
            });
          }
        });
        uni.showToast({ title: `识别到${names.length}种食材`, icon: "success" });
      } catch (e) {
        uni.hideLoading();
        uni.showToast({ title: "识别失败，请手动输入", icon: "none" });
      }
    },
    fail: () => {
      uni.showToast({ title: "请选择图片", icon: "none" });
    }
  });
}

function removeItem(id: string) {
  recipeStore.removeIngredient(id);
}

async function confirmIngredients() {
  if (ingredients.value.length === 0) {
    uni.showToast({ title: "请至少选择一种食材", icon: "none" });
    return;
  }

  try {
    await recipeStore.saveSession();
    uni.navigateTo({ url: "/pages/preference/index" });
  } catch (error) {
    console.error("保存会话失败:", error);
    uni.showToast({ title: "保存失败，请重试", icon: "none" });
  }
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

.content {
  flex: 1;
  padding: 12rpx 30rpx 30rpx;
}

.page-intro {
  display: flex;
  align-items: center;
  background: #FBF1E6;
  border-radius: 18rpx;
  padding: 24rpx 28rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid rgba(200, 118, 58, 0.15);

  .intro-icon {
    font-size: 44rpx;
    margin-right: 20rpx;
  }

  .intro-text {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .intro-title {
    font-size: 28rpx;
    font-weight: 600;
    color: #8A5A2E;
    letter-spacing: 1rpx;
    margin-bottom: 6rpx;
  }

  .intro-desc {
    font-size: 22rpx;
    color: #5A5042;
    line-height: 1.5;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 70rpx 0;
  margin-bottom: 28rpx;

  .empty-icon {
    font-size: 72rpx;
    margin-bottom: 18rpx;
  }

  .empty-text {
    font-size: 28rpx;
    color: #1F3D2E;
    letter-spacing: 1rpx;
    margin-bottom: 8rpx;
  }

  .empty-hint {
    font-size: 22rpx;
    color: #8A8275;
    letter-spacing: 1rpx;
  }
}

.ingredient-list {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 12rpx 32rpx;
  margin-bottom: 28rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.ingredient-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #E8E2D6;

  &:last-child {
    border-bottom: none;
  }
}

.checkbox {
  width: 44rpx;
  height: 44rpx;
  border: 2rpx solid #D9D2C4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 22rpx;
  font-size: 24rpx;
  color: #FAF7F2;

  &.checked {
    background: #1F3D2E;
    border-color: #1F3D2E;
  }
}

.ingredient-name {
  flex: 1;
  font-size: 30rpx;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.ingredient-category {
  font-size: 22rpx;
  color: #8A8275;
  margin-right: 18rpx;
}

.confidence {
  font-size: 22rpx;
  color: #C8763A;
  margin-right: 18rpx;
  letter-spacing: 0.5rpx;
}

.remove-btn {
  font-size: 24rpx;
  color: #B0533A;
  letter-spacing: 1rpx;
}

/* 拍照识别区（复用首页） */
.upload-area {
  display: flex;
  align-items: center;
  background: #1F3D2E;
  border-radius: 18rpx;
  padding: 28rpx 26rpx;
  margin-bottom: 24rpx;
  position: relative;
  overflow: hidden;
}

.upload-area::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 120rpx;
  height: 100%;
  background: linear-gradient(135deg, transparent 40%, rgba(200, 118, 58, 0.25) 100%);
}

.upload-left {
  margin-right: 22rpx;
}

.upload-icon {
  font-size: 42rpx;
  display: block;
}

.upload-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.upload-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #FAF7F2;
  letter-spacing: 1rpx;
}

.upload-hint {
  font-size: 22rpx;
  color: rgba(250, 247, 242, 0.6);
  margin-top: 6rpx;
}

.upload-arrow {
  font-size: 40rpx;
  color: #C8763A;
  font-weight: 300;
  z-index: 1;
}

/* 手动批量输入（复用首页） */
.input-area {
  margin-bottom: 24rpx;
  border-bottom: 1rpx solid #E8E2D6;
  padding-bottom: 4rpx;
}

.input-box {
  display: flex;
  align-items: center;
  padding: 0 4rpx;
}

.ingredient-input {
  flex: 1;
  height: 76rpx;
  font-size: 28rpx;
  color: #2A2A2A;
}

.input-placeholder {
  color: #B5AC9B;
  font-size: 26rpx;
}

.join-btn {
  background: #C8763A;
  color: #FAF7F2;
  font-size: 26rpx;
  font-weight: 600;
  padding: 14rpx 28rpx;
  border-radius: 10rpx;
  letter-spacing: 2rpx;
  line-height: 1;
  flex-shrink: 0;
}

.join-btn:active {
  opacity: 0.8;
}

/* 常用食材标签（复用首页） */
.quick-tags {
  margin-bottom: 24rpx;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18rpx;
}

.section-title {
  font-size: 24rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 2rpx;
}

.clear-btn {
  font-size: 22rpx;
  color: #8A8275;
  padding: 4rpx 8rpx;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.tag {
  background: #F4EFE6;
  color: #5A5042;
  padding: 14rpx 28rpx;
  border-radius: 8rpx;
  font-size: 26rpx;
  letter-spacing: 1rpx;
  border: 1rpx solid transparent;

  &.active {
    background: #1F3D2E;
    color: #FAF7F2;
    border-color: #1F3D2E;
  }
}

.status-hint {
  display: flex;
  align-items: center;
  background: #FBF1E6;
  padding: 22rpx 26rpx;
  border-radius: 14rpx;
  font-size: 26rpx;
  color: #8A5A2E;
  letter-spacing: 1rpx;
  border: 1rpx solid rgba(200, 118, 58, 0.15);

  .pending-icon {
    margin-right: 14rpx;
  }
}

.footer {
  padding: 12rpx 30rpx 40rpx;
}

.confirm-btn {
  background: #1F3D2E;
  color: #FAF7F2;
  text-align: center;
  padding: 26rpx;
  border-radius: 14rpx;
  font-size: 30rpx;
  font-weight: 600;
  letter-spacing: 4rpx;
  position: relative;
  overflow: hidden;
}

.confirm-btn::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6rpx;
  background: #C8763A;
}
</style>