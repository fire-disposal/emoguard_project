/**
 * 鉴权工具
 * 管理用户登录状态和 Token，同时同步全局数据。
 */
const storage = require('./storage');

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
 * 清除本地和全局用户信息
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
 * 统一清除所有认证相关的本地和全局数据（Token & UserInfo）
 */
function clearAuth() {
  try {
    storage.clearToken();
    clearUserInfo();
    
    // 同时清除 app.js 中的全局 token/refreshToken (虽然 storage.clearToken 已经清除本地，但全局仍需清空)
    const app = getApp();
    if (app && app.globalData) {
        app.globalData.token = null;
        app.globalData.refreshToken = null;
    }
    
  } catch (error) {
    console.error('Auth clearAuth error:', error);
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
 * 跳转登录页 (常用于强制鉴权失败，需要重定向)
 * @param {string} redirect - 登录成功后跳转的路径
 */
function navigateToLogin(redirect) {
  try {
    clearAuth(); // 登录跳转前先清除所有旧状态
    
    const url = redirect
      ? `/pages/login/login?redirect=${encodeURIComponent(redirect)}`
      : '/pages/login/login';
    
    // 使用 reLaunch 确保登录页在页面栈底部
    wx.reLaunch({ url });
  } catch (error) {
    console.error('Auth navigateToLogin error:', error);
  }
}

/**
 * 退出登录 (用户主动操作)
 */
function logout() {
  try {
    clearAuth(); // 清除所有状态
    wx.reLaunch({ url: '/pages/login/login' });
  } catch (error) {
    console.error('Auth logout error:', error);
  }
}

/**
 * 导出接口
 */
module.exports = {
  getUserInfo,
  setUserInfo,
  clearUserInfo,
  clearAuth, // 导出 clearAuth 供 app.js 401 错误处理使用
  isLogined,
  navigateToLogin,
  logout
};