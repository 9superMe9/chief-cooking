<!-- 首页：品牌头 + 场景条(在家/愿意补货/在超市) + 食材录入(拍照/手动/常用标签) + 开始配菜。flexible/any 点击直接进入推荐流程，any 弹窗分流「选菜谱/帮我推荐」。 -->
<template>
  <view class="container">
    <view class="header">
      <view class="brand">
        <text class="brand-mark">厨</text>
        <view class="brand-text">
          <text class="title">饭点小厨</text>
          <text class="subtitle">AI 私厨助手 · 今日做什么菜</text>
        </view>
      </view>
    </view>

    <view class="scene-bar">
      <view
        v-for="opt in sceneOptions"
        :key="opt.value"
        class="scene-card"
        :class="{ active: recipeStore.recommendMode === opt.value }"
        @click="onSceneTap(opt.value)"
      >
        <text class="scene-icon">{{ opt.icon }}</text>
        <view class="scene-text">
          <text class="scene-label">{{ opt.label }}</text>
          <text class="scene-desc">{{ opt.desc }}</text>
        </view>
      </view>
    </view>

    <view class="main-content">
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
          <text class="clear-btn" v-if="selectedIngredients.length > 0" @click="clearSelected">清空</text>
        </view>
        <view class="tags">
          <text
            v-for="tag in commonIngredients"
            :key="tag"
            class="tag"
            :class="{ active: selectedIngredients.includes(tag) }"
            @click="toggleIngredient(tag)"
          >{{ tag }}</text>
        </view>
      </view>

      <view class="selected-area" v-if="selectedIngredients.length > 0">
        <view class="section-head">
          <text class="section-title">已选 {{ selectedIngredients.length }} 种</text>
        </view>
        <view class="selected-list">
          <view v-for="(item, index) in selectedIngredients" :key="index" class="selected-item">
            <text class="selected-name">{{ item }}</text>
            <text class="remove" @click="removeIngredient(index)">×</text>
          </view>
        </view>
        <view class="next-btn" @click="goToConfirm">
          <text class="next-text">开始配菜</text>
          <text class="next-arrow">→</text>
        </view>
      </view>

      <text class="skip-link" @click="goToTakeout">今天不想做饭 ›</text>
    </view>

    <view class="market-overlay" v-if="showMarketPopup" @click="closeMarketPopup">
      <view class="market-card" @click.stop>
        <text class="market-close" @click="closeMarketPopup">×</text>
        <text class="market-icon">🛒</text>
        <text class="market-title">在超市买菜</text>
        <text class="market-subtitle">有想做的菜谱吗？</text>
        <view class="market-actions">
          <view class="market-btn primary" @click="onMarketHasRecipe">有，选菜谱</view>
          <view class="market-btn" @click="onMarketNoRecipe">没有，帮我推荐</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRecipeStore } from "../../stores/recipe";
import { uploadImage, recognizeIngredients } from "../../api/ingredients";

const recipeStore = useRecipeStore();
const inputText = ref("");
const selectedIngredients = ref<string[]>([]);
const showMarketPopup = ref(false);

const sceneOptions = [
  { icon: "🏠", label: "在家做饭", desc: "只用现有食材", value: "strict" as const },
  { icon: "🛒", label: "愿意补货", desc: "缺1-2样也行", value: "flexible" as const },
  { icon: "🛒", label: "在超市", desc: "看菜谱选购", value: "any" as const },
];

const commonIngredients = [
  "鸡蛋", "番茄", "米饭", "青菜", "豆腐", "猪肉", "鸡肉", "鱼",
  "土豆", "黄瓜", "青椒", "胡萝卜", "西兰花", "虾仁", "牛肉"
];

function toggleIngredient(tag: string) {
  const index = selectedIngredients.value.indexOf(tag);
  if (index > -1) {
    selectedIngredients.value.splice(index, 1);
  } else {
    selectedIngredients.value.push(tag);
  }
}

function removeIngredient(index: number) {
  selectedIngredients.value.splice(index, 1);
}

function clearSelected() {
  selectedIngredients.value = [];
}

function handleManualInput() {
  if (!inputText.value.trim()) return;
  
  const items = inputText.value.split(/[,，、\s]+/).filter(item => item.trim());
  items.forEach(item => {
    if (!selectedIngredients.value.includes(item.trim())) {
      selectedIngredients.value.push(item.trim());
    }
  });
  inputText.value = "";
}

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sourceType: ["album", "camera"],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0];
      uni.showLoading({ title: "上传中...", mask: true });
      try {
        // 1. 上传图片到后端
        const uploadRes = await uploadImage(tempFilePath);
        uni.showLoading({ title: "识别中...", mask: true });
        // 2. 调用 AI 识别
        const recognizeRes = await recognizeIngredients(uploadRes.file_id, uploadRes.image_url);
        uni.hideLoading();

        if (!recognizeRes.ingredients || recognizeRes.ingredients.length === 0) {
          uni.showToast({ title: recognizeRes.message || "未识别到食材，请手动输入", icon: "none" });
          return;
        }

        // 3. 填充识别结果（去重）
        const names = recognizeRes.ingredients.map(i => i.name);
        selectedIngredients.value = Array.from(new Set(names));
        uni.showToast({ title: `识别到${selectedIngredients.value.length}种食材`, icon: "success" });
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

function goToConfirm() {
  if (selectedIngredients.value.length === 0) {
    uni.showToast({ title: "请选择食材", icon: "none" });
    return;
  }

  recipeStore.setIngredients(
    selectedIngredients.value.map((name, index) => ({
      id: `ing-${index}`,
      name
    }))
  );
  // 在家做饭(strict)：食材已确认，直接进偏好页；
  // 愿意补货/在超市：先进确认食材页，再进偏好。
  const target = recipeStore.recommendMode === "strict"
    ? "/pages/preference/index"
    : "/pages/confirm/index";
  uni.navigateTo({ url: target });
}

function onSceneTap(mode: "strict" | "flexible" | "any") {
  recipeStore.setRecommendMode(mode);
  if (mode === "flexible") {
    enterConfirmFlow();
  } else if (mode === "any") {
    showMarketPopup.value = true;
  }
}

function enterConfirmFlow() {
  recipeStore.setIngredients(
    selectedIngredients.value.map((name, index) => ({
      id: `ing-${index}`,
      name,
    }))
  );
  uni.navigateTo({ url: "/pages/confirm/index" });
}

function onMarketHasRecipe() {
  showMarketPopup.value = false;
  uni.navigateTo({ url: "/pages/recipe-browse/index" });
}

function onMarketNoRecipe() {
  showMarketPopup.value = false;
  enterConfirmFlow();
}

function closeMarketPopup() {
  showMarketPopup.value = false;
}

function goToTakeout() {
  uni.navigateTo({ url: "/pages/takeout/index" });
}
</script>

<style lang="scss" scoped>
/* 现代食器主题：深墨绿 + 暖米白 + 琥珀点缀 */
.container {
  min-height: 100vh;
  background: #FAF7F2;
  background-image:
    radial-gradient(circle at 15% 10%, rgba(31, 61, 46, 0.04) 0%, transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(200, 118, 58, 0.05) 0%, transparent 45%);
  padding: 50rpx 30rpx 40rpx;
}

/* 紧凑头部：横向品牌行 */
.header {
  margin-bottom: 36rpx;
}

.brand {
  display: flex;
  align-items: center;
}

.brand-mark {
  width: 72rpx;
  height: 72rpx;
  line-height: 72rpx;
  text-align: center;
  background: #1F3D2E;
  color: #FAF7F2;
  font-size: 36rpx;
  font-weight: 600;
  border-radius: 18rpx;
  margin-right: 22rpx;
  letter-spacing: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 38rpx;
  font-weight: 600;
  color: #1F3D2E;
  line-height: 1.2;
  letter-spacing: 1rpx;
}

.subtitle {
  font-size: 22rpx;
  color: #8A8275;
  margin-top: 4rpx;
  letter-spacing: 0.5rpx;
}

/* 场景选择条 */
.scene-bar {
  display: flex;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.scene-card {
  flex: 1;
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 14rpx;
  padding: 18rpx 16rpx;
  border: 2rpx solid transparent;
  box-shadow: 0 2rpx 12rpx rgba(31, 61, 46, 0.05);

  &.active {
    background: #1F3D2E;
    border-color: #C8763A;

    .scene-icon,
    .scene-label,
    .scene-desc {
      color: #FAF7F2;
    }

    .scene-desc {
      color: rgba(250, 247, 242, 0.7);
    }
  }
}

.scene-icon {
  font-size: 32rpx;
  margin-right: 12rpx;
}

.scene-text {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.scene-label {
  font-size: 24rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.scene-desc {
  font-size: 18rpx;
  color: #8A8275;
  margin-top: 2rpx;
}

/* 主卡片 */
.main-content {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 36rpx 32rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

/* 拍照区：横向卡片式 */
.upload-area {
  display: flex;
  align-items: center;
  background: #1F3D2E;
  border-radius: 18rpx;
  padding: 32rpx 28rpx;
  margin-bottom: 28rpx;
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
  margin-right: 24rpx;
}

.upload-icon {
  font-size: 44rpx;
  display: block;
}

.upload-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.upload-text {
  font-size: 30rpx;
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

/* 输入框：底线式 */
.input-area {
  margin-bottom: 32rpx;
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

/* 区块标题 */
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

/* 标签 */
.quick-tags {
  margin-bottom: 28rpx;
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
  transition: all 0.2s;
  
  &.active {
    background: #1F3D2E;
    color: #FAF7F2;
    border-color: #1F3D2E;
  }
}

/* 已选区 */
.selected-area {
  background: #FBF8F1;
  border-radius: 16rpx;
  padding: 24rpx;
  border: 1rpx solid #E8E2D6;
}

.selected-list {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
  margin-bottom: 24rpx;
}

.selected-item {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  padding: 12rpx 18rpx 12rpx 22rpx;
  border-radius: 8rpx;
  font-size: 26rpx;
  color: #1F3D2E;
  border: 1rpx solid #1F3D2E;
  
  .selected-name {
    letter-spacing: 1rpx;
  }
  
  .remove {
    margin-left: 14rpx;
    color: #C8763A;
    font-size: 32rpx;
    line-height: 1;
    font-weight: 300;
  }
}

/* 主 CTA */
.next-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1F3D2E;
  padding: 26rpx;
  border-radius: 12rpx;
  position: relative;
  overflow: hidden;
}

.next-btn::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6rpx;
  background: #C8763A;
}

.next-text {
  color: #FAF7F2;
  font-size: 30rpx;
  font-weight: 600;
  letter-spacing: 4rpx;
}

.next-arrow {
  color: #C8763A;
  font-size: 32rpx;
  margin-left: 16rpx;
}

/* 跳过：小字链接，非按钮 */
.skip-link {
  display: block;
  text-align: center;
  margin-top: 20rpx;
  color: #B5AC9B;
  font-size: 22rpx;
  letter-spacing: 1rpx;
}

/* 超市弹窗 */
.market-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(31, 61, 46, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.market-card {
  position: relative;
  width: 580rpx;
  background: #FAF7F2;
  border-radius: 24rpx;
  padding: 56rpx 48rpx 44rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 20rpx 60rpx rgba(31, 61, 46, 0.25);
  border: 1rpx solid rgba(200, 118, 58, 0.15);
}

.market-close {
  position: absolute;
  top: 18rpx;
  right: 26rpx;
  font-size: 40rpx;
  color: #8A8275;
  font-weight: 300;
  line-height: 1;
  padding: 6rpx;
}

.market-icon {
  font-size: 72rpx;
  margin-bottom: 18rpx;
}

.market-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #1F3D2E;
  letter-spacing: 2rpx;
  margin-bottom: 12rpx;
}

.market-subtitle {
  font-size: 26rpx;
  color: #5A5042;
  letter-spacing: 1rpx;
  margin-bottom: 40rpx;
}

.market-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.market-btn {
  text-align: center;
  padding: 24rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  letter-spacing: 2rpx;
  background: #F4EFE6;
  color: #5A5042;
  border: 1rpx solid #E8E2D6;

  &.primary {
    background: #1F3D2E;
    color: #FAF7F2;
    border-color: #1F3D2E;
    position: relative;
    overflow: hidden;

    &::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 6rpx;
      background: #C8763A;
    }
  }
}
</style>
