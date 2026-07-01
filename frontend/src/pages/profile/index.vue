<!-- 个人中心页：用户信息、收藏/历史统计、默认偏好设置入口、协议/隐私/清除缓存 -->
<template>
  <view class="container">
    <view class="header">
      <view class="user-info">
        <view class="avatar">👤</view>
        <view class="user-detail">
          <text class="user-name">{{ userInfo.nickname || "用户" }}</text>
          <text class="user-id">ID: {{ userInfo.id?.substring(0, 8) || "******" }}</text>
        </view>
      </view>
    </view>

    <view class="content">
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-value">{{ favoritesCount }}</text>
          <text class="stat-label">收藏</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ historyCount }}</text>
          <text class="stat-label">历史</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ recommendationCount }}</text>
          <text class="stat-label">推荐</text>
        </view>
      </view>

      <!-- 默认偏好预览卡片 -->
      <view class="pref-card" v-if="defaultPrefs" @click="openPreference">
        <view class="pref-header">
          <text class="pref-title">⚙️ 默认偏好</text>
          <text class="pref-arrow">→</text>
        </view>
        <view class="pref-tags">
          <text class="pref-tag" v-if="defaultPrefs.taste">{{ defaultPrefs.taste }}</text>
          <text class="pref-tag" v-if="defaultPrefs.cookingTime">{{ defaultPrefs.cookingTime }}</text>
          <text class="pref-tag" v-if="defaultPrefs.difficulty">{{ defaultPrefs.difficulty }}</text>
          <text class="pref-tag" v-for="p in (defaultPrefs.peopleTags || [])" :key="p">{{ p }}</text>
          <text class="pref-tag" v-for="r in (defaultPrefs.restrictions || [])" :key="r">{{ r }}</text>
          <text class="pref-tag pref-tag-empty" v-if="!hasAnyPref">点击设置</text>
        </view>
      </view>

      <view class="menu-card">
        <view class="menu-item" @click="goToFavorites">
          <text class="menu-icon">❤️</text>
          <text class="menu-text">我的收藏</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item" @click="goToHistory">
          <text class="menu-icon">📜</text>
          <text class="menu-text">历史记录</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item" @click="openPreference">
          <text class="menu-icon">⚙️</text>
          <text class="menu-text">默认偏好设置</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item" @click="goToAgreement">
          <text class="menu-icon">📄</text>
          <text class="menu-text">用户协议</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item" @click="goToPrivacy">
          <text class="menu-icon">🔒</text>
          <text class="menu-text">隐私政策</text>
          <text class="menu-arrow">→</text>
        </view>
      </view>

      <view class="setting-card">
        <view class="menu-item" @click="clearCache">
          <text class="menu-icon">🗑️</text>
          <text class="menu-text">清除缓存</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item" @click="showAbout">
          <text class="menu-icon">ℹ️</text>
          <text class="menu-text">关于我们</text>
          <text class="menu-arrow">→</text>
        </view>
      </view>

      <view class="logout-btn" @click="logout">退出登录</view>
    </view>

    <!-- 默认偏好弹窗 -->
    <view class="pref-modal-mask" v-if="showPrefModal" @click="showPrefModal = false">
      <view class="pref-modal" @click.stop>
        <view class="pref-modal-title">默认偏好设置</view>
        <scroll-view scroll-y class="pref-modal-body">
          <view class="pref-section">
            <text class="pref-section-title">口味</text>
            <view class="pref-options">
              <text v-for="t in tasteOpts" :key="t" class="pref-opt" :class="{active: prefForm.taste === t}" @click="prefForm.taste = t">{{ t }}</text>
            </view>
          </view>
          <view class="pref-section">
            <text class="pref-section-title">特殊人群</text>
            <view class="pref-options">
              <text v-for="p in peopleOpts" :key="p" class="pref-opt" :class="{active: prefForm.peopleTags.includes(p)}" @click="toggleArr(prefForm.peopleTags, p)">{{ p }}</text>
            </view>
          </view>
          <view class="pref-section">
            <text class="pref-section-title">烹饪时间</text>
            <view class="pref-options">
              <text v-for="t in timeOpts" :key="t" class="pref-opt" :class="{active: prefForm.cookingTime === t}" @click="prefForm.cookingTime = t">{{ t || '不限' }}</text>
            </view>
          </view>
          <view class="pref-section">
            <text class="pref-section-title">饮食禁忌</text>
            <view class="pref-options">
              <text v-for="r in restrictOpts" :key="r" class="pref-opt" :class="{active: prefForm.restrictions.includes(r)}" @click="toggleArr(prefForm.restrictions, r)">{{ r }}</text>
            </view>
          </view>
          <view class="pref-section">
            <text class="pref-section-title">烹饪难度</text>
            <view class="pref-options">
              <text v-for="d in diffOpts" :key="d" class="pref-opt" :class="{active: prefForm.difficulty === d}" @click="prefForm.difficulty = d">{{ d || '不限' }}</text>
            </view>
          </view>
        </scroll-view>
        <view class="pref-modal-footer">
          <view class="pref-modal-btn pref-modal-btn-cancel" @click="showPrefModal = false">取消</view>
          <view class="pref-modal-btn pref-modal-btn-save" @click="savePref">保存</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
/**
 * 个人中心页：展示用户信息、收藏/历史/推荐统计，
 * 提供默认偏好设置入口（弹窗形式，保存到后端 user.preferences），
 * 以及协议/隐私/清除缓存/退出登录。
 */
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "../../stores/user";
import { getUserInfo, updateUserInfo } from "../../api/auth";

const userStore = useUserStore();

const userInfo = ref<any>({ nickname: "", id: "" });
const favoritesCount = ref(0);
const historyCount = ref(0);
const recommendationCount = ref(0);

// 偏好选项
const tasteOpts = ["清淡", "微辣", "香辣", "酸甜", "咸鲜"];
const peopleOpts = ["老人", "小孩", "健身", "孕妇"];
const timeOpts = ["15分钟", "30分钟", "45分钟", ""];
const restrictOpts = ["不吃辣", "不吃葱蒜", "少盐", "少糖", "少油"];
const diffOpts = ["简单", "中等", "困难", ""];

const defaultPrefs = ref<any>(null);
const showPrefModal = ref(false);
const prefForm = ref({
  taste: "",
  peopleTags: [] as string[],
  cookingTime: "",
  restrictions: [] as string[],
  difficulty: "",
});

const hasAnyPref = computed(() => {
  const p = defaultPrefs.value;
  if (!p) return false;
  return !!(p.taste || p.cookingTime || p.difficulty ||
    (p.peopleTags && p.peopleTags.length) || (p.restrictions && p.restrictions.length));
});

function toggleArr(arr: string[], val: string) {
  const idx = arr.indexOf(val);
  if (idx > -1) arr.splice(idx, 1);
  else arr.push(val);
}

function openPreference() {
  // 从 defaultPrefs 填充表单
  const p = defaultPrefs.value || {};
  prefForm.value = {
    taste: p.taste || "",
    peopleTags: [...(p.peopleTags || [])],
    cookingTime: p.cookingTime || "",
    restrictions: [...(p.restrictions || [])],
    difficulty: p.difficulty || "",
  };
  showPrefModal.value = true;
}

async function savePref() {
  try {
    const res = await updateUserInfo({ preferences: { ...prefForm.value } });
    defaultPrefs.value = { ...prefForm.value };
    if (userStore.userInfo) {
      userStore.setUserInfo({ ...userStore.userInfo, preferences: { ...prefForm.value } });
    }
    showPrefModal.value = false;
    uni.showToast({ title: "偏好已保存", icon: "success" });
  } catch {
    uni.showToast({ title: "保存失败", icon: "none" });
  }
}

async function loadUserInfo() {
  try {
    const res = await getUserInfo();
    userInfo.value = res;
    defaultPrefs.value = res.preferences || {};
    if (userStore.userInfo) {
      userStore.setUserInfo(res);
    }
  } catch {
    // 未登录等
  }
}

function goToFavorites() {
  uni.navigateTo({ url: "/pages/favorites/index" });
}

function goToHistory() {
  uni.navigateTo({ url: "/pages/history/index" });
}

function goToAgreement() {
  uni.navigateTo({ url: "/pages/agreement/index" });
}

function goToPrivacy() {
  uni.navigateTo({ url: "/pages/privacy/index" });
}

function clearCache() {
  uni.showModal({
    title: "提示",
    content: "确定要清除缓存吗？",
    success: (res) => {
      if (res.confirm) {
        uni.clearStorageSync();
        uni.showToast({ title: "清除成功", icon: "success" });
      }
    }
  });
}

function showAbout() {
  uni.showModal({
    title: "关于我们",
    content: "饭点小厨 v1.0\nAI私厨助手，帮你轻松做饭！",
    showCancel: false
  });
}

function logout() {
  uni.showModal({
    title: "提示",
    content: "确定要退出登录吗？",
    success: (res) => {
      if (res.confirm) {
        userStore.logout();
        uni.reLaunch({ url: "/pages/index/index" });
      }
    }
  });
}

onMounted(() => {
  loadUserInfo();
});
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: #FAF7F2;
  background-image:
    radial-gradient(circle at 15% 10%, rgba(31, 61, 46, 0.04) 0%, transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(200, 118, 58, 0.05) 0%, transparent 45%);
}

.header {
  background: #1F3D2E;
  padding: 80rpx 30rpx 60rpx;
  position: relative;
  overflow: hidden;
}

.header::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 240rpx;
  height: 100%;
  background: linear-gradient(135deg, transparent 40%, rgba(200, 118, 58, 0.25) 100%);
}

.user-info {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  background: rgba(200, 118, 58, 0.35);
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60rpx;
  margin-right: 26rpx;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 38rpx;
  font-weight: 600;
  color: #FAF7F2;
  margin-bottom: 8rpx;
  letter-spacing: 1rpx;
}

.user-id {
  font-size: 22rpx;
  color: rgba(250, 247, 242, 0.6);
  letter-spacing: 1rpx;
}

.content {
  padding: 30rpx;
  margin-top: -30rpx;
  position: relative;
  z-index: 2;
}

.stats-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 38rpx;
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-bottom: 26rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 46rpx;
  font-weight: 600;
  color: #1F3D2E;
  margin-bottom: 10rpx;
  letter-spacing: 1rpx;
}

.stat-label {
  font-size: 22rpx;
  color: #8A8275;
  letter-spacing: 2rpx;
}

.stat-divider {
  width: 1rpx;
  height: 56rpx;
  background: #E8E2D6;
}

/* 偏好预览卡片 */
.pref-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx 32rpx;
  margin-bottom: 22rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.pref-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.pref-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F3D2E;
}

.pref-arrow {
  font-size: 28rpx;
  color: #C8763A;
}

.pref-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.pref-tag {
  background: rgba(31, 61, 46, 0.06);
  color: #1F3D2E;
  font-size: 22rpx;
  padding: 8rpx 18rpx;
  border-radius: 12rpx;
}

.pref-tag-empty {
  color: #8A8275;
  font-style: italic;
}

.menu-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  margin-bottom: 22rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1rpx solid #E8E2D6;

  &:last-child {
    border-bottom: none;
  }
}

.menu-icon {
  font-size: 36rpx;
  margin-right: 22rpx;
}

.menu-text {
  flex: 1;
  font-size: 30rpx;
  color: #1F3D2E;
  letter-spacing: 1rpx;
}

.menu-arrow {
  font-size: 28rpx;
  color: #C8763A;
  font-weight: 300;
}

.setting-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  margin-bottom: 36rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

.logout-btn {
  background: #FFFFFF;
  color: #B0533A;
  text-align: center;
  padding: 30rpx;
  border-radius: 24rpx;
  font-size: 30rpx;
  letter-spacing: 2rpx;
  box-shadow: 0 4rpx 24rpx rgba(31, 61, 46, 0.06);
  border: 1rpx solid rgba(31, 61, 46, 0.05);
}

/* 偏好弹窗 */
.pref-modal-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 999;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.pref-modal {
  width: 100%;
  max-height: 80vh;
  background: #FAF7F2;
  border-radius: 32rpx 32rpx 0 0;
  display: flex;
  flex-direction: column;
}

.pref-modal-title {
  text-align: center;
  font-size: 32rpx;
  font-weight: 600;
  color: #1F3D2E;
  padding: 36rpx 0 20rpx;
}

.pref-modal-body {
  flex: 1;
  padding: 0 36rpx 24rpx;
  max-height: 60vh;
}

.pref-section {
  margin-bottom: 28rpx;
}

.pref-section-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1F3D2E;
  margin-bottom: 16rpx;
}

.pref-options {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.pref-opt {
  font-size: 24rpx;
  padding: 12rpx 26rpx;
  border-radius: 12rpx;
  background: #FFFFFF;
  color: #5A5549;
  border: 1rpx solid #E8E2D6;

  &.active {
    background: #1F3D2E;
    color: #FAF7F2;
    border-color: #1F3D2E;
  }
}

.pref-modal-footer {
  display: flex;
  gap: 20rpx;
  padding: 24rpx 36rpx;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid #E8E2D6;
}

.pref-modal-btn {
  flex: 1;
  text-align: center;
  padding: 24rpx;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 500;
}

.pref-modal-btn-cancel {
  background: #FFFFFF;
  color: #5A5549;
  border: 1rpx solid #E8E2D6;
}

.pref-modal-btn-save {
  background: #1F3D2E;
  color: #FAF7F2;
}
</style>
