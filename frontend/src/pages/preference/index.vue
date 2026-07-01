<template>
  <view class="container">
    <view class="nav-bar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="nav-title">选择偏好</text>
      <text class="nav-placeholder"></text>
    </view>

    <view class="content">
      <view class="section">
        <text class="section-title">🍽️ 今天做几道？</text>
        <view class="counter-row">
          <text class="counter-label">菜</text>
          <view class="counter">
            <text class="counter-btn" @click="adjustDish(-1)">−</text>
            <input
              class="counter-input"
              type="number"
              v-model="dishCount"
              @blur="clampDish"
            />
            <text class="counter-btn" @click="adjustDish(1)">+</text>
          </view>
        </view>
        <view class="counter-row">
          <text class="counter-label">汤</text>
          <view class="counter">
            <text class="counter-btn" @click="adjustSoup(-1)">−</text>
            <input
              class="counter-input"
              type="number"
              v-model="soupCount"
              @blur="clampSoup"
            />
            <text class="counter-btn" @click="adjustSoup(1)">+</text>
          </view>
        </view>
        <text class="section-hint">共推荐 {{ dishCount + soupCount }} 道（{{ dishCount }}菜{{ soupCount }}汤）</text>
      </view>

      <view class="section">
        <text class="section-title">👥 用餐人数</text>
        <view class="options">
          <text
            v-for="opt in peopleCountOptions"
            :key="opt.value"
            class="option"
            :class="{ selected: selectedPeopleCount === opt.value }"
            @click="selectedPeopleCount = opt.value"
          >{{ opt.label }}</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">👨‍👩‍👧‍👦 特殊人群</text>
        <view class="options">
          <text
            v-for="option in peopleOptions"
            :key="option.value"
            class="option"
            :class="{ selected: selectedPeople.includes(option.value) }"
            @click="togglePeople(option.value)"
          >{{ option.label }}</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">🍽️ 口味偏好</text>
        <view class="options">
          <text
            v-for="option in tasteOptions"
            :key="option.value"
            class="option"
            :class="{ selected: selectedTaste === option.value }"
            @click="selectedTaste = option.value"
          >{{ option.label }}</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">⏱️ 烹饪时间</text>
        <view class="options">
          <text
            v-for="option in timeOptions"
            :key="option.value"
            class="option"
            :class="{ selected: selectedTime === option.value }"
            @click="selectedTime = option.value"
          >{{ option.label }}</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">⚠️ 饮食禁忌</text>
        <view class="options">
          <text
            v-for="option in restrictionOptions"
            :key="option.value"
            class="option"
            :class="{ selected: selectedRestrictions.includes(option.value) }"
            @click="toggleRestriction(option.value)"
          >{{ option.label }}</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">👩‍🍳 烹饪难度</text>
        <view class="options">
          <text
            v-for="option in difficultyOptions"
            :key="option.value"
            class="option"
            :class="{ selected: selectedDifficulty === option.value }"
            @click="selectedDifficulty = option.value"
          >{{ option.label }}</text>
        </view>
      </view>
    </view>

    <view class="footer">
      <view class="skip-btn" @click="skipPreference">跳过</view>
      <view class="confirm-btn" @click="confirmPreference">确认偏好</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRecipeStore } from "../../stores/recipe";
import { useUserStore } from "../../stores/user";

const recipeStore = useRecipeStore();
const userStore = useUserStore();

// 菜数/汤数计数器（可手动输入，可 +/- 调整）
const dishCount = ref(2);
const soupCount = ref(1);

function adjustDish(delta: number) {
  const next = Number(dishCount.value) + delta;
  dishCount.value = Math.max(0, Math.min(9, next));
}
function adjustSoup(delta: number) {
  const next = Number(soupCount.value) + delta;
  soupCount.value = Math.max(0, Math.min(9, next));
}
function clampDish() {
  let v = Number(dishCount.value);
  if (isNaN(v) || v < 0) v = 0;
  if (v > 9) v = 9;
  dishCount.value = v;
}
function clampSoup() {
  let v = Number(soupCount.value);
  if (isNaN(v) || v < 0) v = 0;
  if (v > 9) v = 9;
  soupCount.value = v;
}

const peopleCountOptions = [
  { label: "1人", value: 1 },
  { label: "2人", value: 2 },
  { label: "3人", value: 3 },
  { label: "4人", value: 4 },
  { label: "5人+", value: 5 },
];
const selectedPeopleCount = ref(2);

const peopleOptions = [
  { label: "老人", value: "老人" },
  { label: "小孩", value: "小孩" },
  { label: "健身", value: "健身" },
  { label: "孕妇", value: "孕妇" },
];

const tasteOptions = [
  { label: "清淡", value: "清淡" },
  { label: "微辣", value: "微辣" },
  { label: "香辣", value: "香辣" },
  { label: "酸甜", value: "酸甜" },
  { label: "咸鲜", value: "咸鲜" },
];

const timeOptions = [
  { label: "15分钟", value: "15分钟" },
  { label: "30分钟", value: "30分钟" },
  { label: "45分钟", value: "45分钟" },
  { label: "不限", value: "" },
];

const restrictionOptions = [
  { label: "不吃辣", value: "不吃辣" },
  { label: "不吃葱蒜", value: "不吃葱蒜" },
  { label: "少盐", value: "少盐" },
  { label: "少糖", value: "少糖" },
  { label: "少油", value: "少油" },
];

const difficultyOptions = [
  { label: "简单", value: "简单" },
  { label: "中等", value: "中等" },
  { label: "困难", value: "困难" },
  { label: "不限", value: "" },
];

const selectedPeople = ref<string[]>([]);
const selectedTaste = ref("");
const selectedTime = ref("");
const selectedRestrictions = ref<string[]>([]);
const selectedDifficulty = ref("");

function goBack() {
  uni.navigateBack();
}

function togglePeople(value: string) {
  const index = selectedPeople.value.indexOf(value);
  if (index > -1) {
    selectedPeople.value.splice(index, 1);
  } else {
    selectedPeople.value.push(value);
  }
}

function toggleRestriction(value: string) {
  const index = selectedRestrictions.value.indexOf(value);
  if (index > -1) {
    selectedRestrictions.value.splice(index, 1);
  } else {
    selectedRestrictions.value.push(value);
  }
}

function buildPreferences() {
  return {
    peopleTags: selectedPeople.value,
    taste: selectedTaste.value,
    cookingTime: selectedTime.value,
    restrictions: selectedRestrictions.value,
    difficulty: selectedDifficulty.value,
    dishCount: Number(dishCount.value),
    soupCount: Number(soupCount.value),
    peopleCount: selectedPeopleCount.value,
    recommendCount: Number(dishCount.value) + Number(soupCount.value),
  };
}

function skipPreference() {
  recipeStore.setPreferences(buildPreferences());
  uni.navigateTo({ url: "/pages/result/index" });
}

function confirmPreference() {
  recipeStore.setPreferences(buildPreferences());
  uni.navigateTo({ url: "/pages/result/index" });
}

// 从用户保存的默认偏好预填（个人中心设置过则自动带入）
onMounted(() => {
  const prefs = userStore.userInfo?.preferences;
  if (!prefs) return;
  if (prefs.taste) selectedTaste.value = prefs.taste;
  if (Array.isArray(prefs.peopleTags)) selectedPeople.value = [...prefs.peopleTags];
  if (prefs.cookingTime) selectedTime.value = prefs.cookingTime;
  if (Array.isArray(prefs.restrictions)) selectedRestrictions.value = [...prefs.restrictions];
  if (prefs.difficulty) selectedDifficulty.value = prefs.difficulty;
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

.content {
  flex: 1;
  padding: 20rpx 30rpx 30rpx;
}

.section {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 22rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.section-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1F3D2E;
  margin-bottom: 22rpx;
  display: block;
  letter-spacing: 2rpx;
}

.section-hint {
  display: block;
  font-size: 22rpx;
  color: #C8763A;
  margin-top: 16rpx;
  letter-spacing: 1rpx;
}

/* 菜/汤计数器 */
.counter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14rpx 0;
  border-bottom: 1rpx solid rgba(31, 61, 46, 0.06);
}

.counter-row:last-of-type {
  border-bottom: none;
}

.counter-label {
  font-size: 28rpx;
  color: #1F3D2E;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.counter {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.counter-btn {
  width: 56rpx;
  height: 56rpx;
  line-height: 52rpx;
  text-align: center;
  background: #F4EFE6;
  color: #1F3D2E;
  border-radius: 10rpx;
  font-size: 36rpx;
  font-weight: 600;
}

.counter-input {
  width: 80rpx;
  height: 56rpx;
  text-align: center;
  font-size: 30rpx;
  color: #1F3D2E;
  background: #FAF7F2;
  border-radius: 10rpx;
  border: 1rpx solid rgba(31, 61, 46, 0.1);
}

.options {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.option {
  background: #F4EFE6;
  padding: 16rpx 32rpx;
  border-radius: 10rpx;
  font-size: 28rpx;
  color: #5A5042;
  border: 1rpx solid transparent;
  letter-spacing: 1rpx;
  transition: all 0.2s;

  &.selected {
    background: #1F3D2E;
    color: #FAF7F2;
    border-color: #1F3D2E;
  }
}

.footer {
  display: flex;
  gap: 22rpx;
  padding: 12rpx 30rpx 40rpx;
}

.skip-btn {
  flex: 1;
  background: #F4EFE6;
  color: #5A5042;
  text-align: center;
  padding: 26rpx;
  border-radius: 12rpx;
  font-size: 30rpx;
  letter-spacing: 2rpx;
}

.confirm-btn {
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