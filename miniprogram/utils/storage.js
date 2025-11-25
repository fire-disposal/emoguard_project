/**
 * 极简本地存储（适配新版authCenter）
 * 1. 仅支持JSON序列化
 * 2. 只暴露必要API
 * 3. Token操作与用户信息操作分离
 */
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_INFO_KEY = 'user_info';

function setItem(key, value) {
  try {
    wx.setStorageSync(key, JSON.stringify(value));
    return true;
  } catch (e) {
    console.warn('[Storage] setItem error', key, e);
    return false;
  }
}

function getItem(key) {
  try {
    const data = wx.getStorageSync(key);
    if (data === undefined || data === null) return null;
    return JSON.parse(data);
  } catch (e) {
    return null;
  }
}

function removeItem(key) {
  try {
    wx.removeStorageSync(key);
  } catch (e) {}
}

function clear() {
  try {
    wx.clearStorageSync();
  } catch (e) {}
}

// Token专用
function setToken(access, refresh) {
  setItem(TOKEN_KEY, access);
  if (refresh) setItem(REFRESH_TOKEN_KEY, refresh);
}
function getToken() {
  return getItem(TOKEN_KEY);
}
function getRefreshToken() {
  return getItem(REFRESH_TOKEN_KEY);
}
function clearToken() {
  removeItem(TOKEN_KEY);
  removeItem(REFRESH_TOKEN_KEY);
}

// 用户信息专用
function setUserInfo(userInfo) {
  setItem(USER_INFO_KEY, userInfo);
}
function getUserInfo() {
  return getItem(USER_INFO_KEY);
}
function clearUserInfo() {
  removeItem(USER_INFO_KEY);
}

module.exports = {
  setItem,
  getItem,
  removeItem,
  clear,
  setToken,
  getToken,
  getRefreshToken,
  clearToken,
  setUserInfo,
  getUserInfo,
  clearUserInfo
};
