/**
 * 鉴权工具
 * 仅保留业务语义，所有状态托管到 authCenter
 */
const authCenter = require('./authCenter');
const storage = require('./storage');

const USER_INFO_KEY = 'user_info';

/* 获取 token（内存优先） */
function getToken() {
  authCenter.init();
  return authCenter.access;
}

/* 用户信息（内存 + storage 双写） */
function getUserInfo() {
  const app = getApp();
  if (app && app.globalData && app.globalData.userInfo) {
    return app.globalData.userInfo;
  }
  try {
    return storage.getItem(USER_INFO_KEY);
  } catch (e) {
    return null;
  }
}

function setUserInfo(userInfo) {
  storage.setItem(USER_INFO_KEY, userInfo);
  const app = getApp();
  if (app && app.globalData) app.globalData.userInfo = userInfo;
}

function clearUserInfo() {
  storage.removeItem(USER_INFO_KEY);
  const app = getApp();
  if (app && app.globalData) app.globalData.userInfo = null;
}

/* 完全退出 */
function clearAuth() {
  authCenter.logout(true); // 先清本地
  clearUserInfo();
  const app = getApp();
  if (app && app.globalData) {
    app.globalData.token = null;
    app.globalData.refreshToken = null;
    app.globalData.loginPromise = null;
  }
}

/* 是否已登录 */
function isLogined() {
  return authCenter.logined;
}

/* 跳转登录页（统一收口） */
function navigateToLogin(redirect) {
  authCenter.logout(); // 触发清态 + 跳转（内部已防抖）
}

/* 主动退出 */
function logout() {
  authCenter.logout();
}

module.exports = {
  getToken,
  getUserInfo,
  setUserInfo,
  clearUserInfo,
  clearAuth,
  isLogined,
  navigateToLogin,
  logout
};