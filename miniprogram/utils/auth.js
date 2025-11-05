/**
 * 鉴权工具
 * 管理用户登录状态和 Token
 */

const storage = require('./storage');
const request = require('./request');

const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_INFO_KEY = 'user_info';

/**
 * 获取 access_token
 * @returns {string|null}
 */
function getToken() {
  return storage.getItem(TOKEN_KEY);
}

/**
 * 获取 refresh_token
 * @returns {string|null}
 */
function getRefreshToken() {
  return storage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * 设置 token
 * @param {string} accessToken - 访问令牌
 * @param {string} refreshToken - 刷新令牌
 */
function setToken(accessToken, refreshToken) {
  storage.setItem(TOKEN_KEY, accessToken);
  if (refreshToken) {
    storage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
  
  // 重置token刷新状态，避免之前的失败标记影响新token
  if (request.resetRefreshState) {
    request.resetRefreshState();
  }
}

/**
 * 清除 token
 */
function clearToken() {
  storage.removeItem(TOKEN_KEY);
  storage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * 获取用户信息
 * @returns {object|null}
 */
function getUserInfo() {
  return storage.getItem(USER_INFO_KEY);
}

/**
 * 设置用户信息
 * @param {object} userInfo - 用户信息
 */
function setUserInfo(userInfo) {
  storage.setItem(USER_INFO_KEY, userInfo);
  
  // 同步到全局数据
  const app = getApp();
  if (app && app.globalData) {
    app.globalData.userInfo = userInfo;
  }
}

/**
 * 清除用户信息
 */
function clearUserInfo() {
  storage.removeItem(USER_INFO_KEY);
  
  // 清除全局数据
  const app = getApp();
  if (app && app.globalData) {
    app.globalData.userInfo = null;
  }
}

/**
 * 检查是否已登录
 * @returns {boolean}
 */
function isLogined() {
  const token = getToken();
  return !!token;
}

/**
 * 跳转登录页
 * @param {string} redirect - 登录成功后跳转的路径
 */
function navigateToLogin(redirect) {
  clearToken();
  clearUserInfo();
  
  const url = redirect 
    ? `/pages/login/login?redirect=${encodeURIComponent(redirect)}`
    : '/pages/login/login';
  
  wx.reLaunch({ url });
}

/**
 * 退出登录
 */
function logout() {
  clearToken();
  clearUserInfo();
  wx.reLaunch({ url: '/pages/login/login' });
}

module.exports = {
  getToken,
  getRefreshToken,
  setToken,
  clearToken,
  getUserInfo,
  setUserInfo,
  clearUserInfo,
  isLogined,
  navigateToLogin,
  logout
};
