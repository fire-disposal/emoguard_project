/**
 * 鉴权工具
 * 管理用户登录状态和 Token
 */

const storage = require('./storage');
const request = require('./request');

const USER_INFO_KEY = 'user_info';

/**
 * 获取用户信息
 * @returns {object|null}
 */
function getUserInfo() {
  try {
    return storage.getItem(USER_INFO_KEY);
  } catch (error) {
    console.error('Auth getUserInfo error:', error);
    return null;
  }
}

/**
 * 设置用户信息
 * @param {object} userInfo - 用户信息
 */
function setUserInfo(userInfo) {
  try {
    storage.setItem(USER_INFO_KEY, userInfo);
  } catch (error) {
    console.warn('存储用户信息失败:', error);
  }
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
  try {
    storage.removeItem(USER_INFO_KEY);
  } catch (error) {
    console.warn('清除本地用户信息失败:', error);
  }
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
  try {
    const token = storage.getToken();
    return !!token;
  } catch (error) {
    console.error('Auth isLogined error:', error);
    return false;
  }
}

/**
 * 跳转登录页
 * @param {string} redirect - 登录成功后跳转的路径
 */
function navigateToLogin(redirect) {
  try {
    storage.clearToken();
    clearUserInfo();
    
    const url = redirect
      ? `/pages/login/login?redirect=${encodeURIComponent(redirect)}`
      : '/pages/login/login';
    
    wx.reLaunch({ url });
  } catch (error) {
    console.error('Auth navigateToLogin error:', error);
  }
}

/**
 * 退出登录
 */
function logout() {
  try {
    storage.clearToken();
    clearUserInfo();
    wx.reLaunch({ url: '/pages/login/login' });
  } catch (error) {
    console.error('Auth logout error:', error);
  }
}

// 确保模块正确导出
/**
 * 导出接口
 * resetRequestState 由外部直接 require('utils/request').resetRefreshState 使用，不在此重复导入
 */
module.exports = {
  getUserInfo,
  setUserInfo,
  clearUserInfo,
  isLogined,
  navigateToLogin,
  logout
};
