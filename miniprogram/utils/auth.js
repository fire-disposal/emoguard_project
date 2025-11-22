/**
 * 鉴权工具
 * 管理用户登录状态和 Token，同时同步全局数据。
 */
const storage = require('./storage');

const USER_INFO_KEY = 'user_info';

/**
 * 获取全局 App 实例（带安全检查）
 * @returns {App|null}
 */
function getGlobalApp() {
  try {
    return getApp();
  } catch (e) {
    console.error('getApp 调用失败:', e);
    return null;
  }
}

/**
 * 获取当前有效的 Token
 * 策略：优先读取内存(globalData)，其次读取缓存(Storage)
 * @returns {string|null}
 */
function getToken() {
  const app = getGlobalApp();
  // 1. 优先查内存
  if (app && app.globalData && app.globalData.token) {
    return app.globalData.token;
  }
  // 2. 内存没有，查 Storage
  return storage.getToken();
}

/**
 * 获取用户信息
 * @returns {object|null}
 */
function getUserInfo() {
  const app = getGlobalApp();
  // 1. 优先查内存
  if (app && app.globalData && app.globalData.userInfo) {
    return app.globalData.userInfo;
  }
  // 2. 查 Storage
  try {
    return storage.getItem(USER_INFO_KEY);
  } catch (error) {
    console.error('Auth getUserInfo error:', error);
    return null;
  }
}

/**
 * 设置用户信息
 * 同时更新 Storage 和 globalData
 * @param {object} userInfo - 用户信息
 */
function setUserInfo(userInfo) {
  // 1. 存 Storage
  try {
    storage.setItem(USER_INFO_KEY, userInfo);
  } catch (error) {
    console.warn('存储用户信息失败:', error);
  }

  // 2. 同步 globalData
  const app = getGlobalApp();
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
  
  const app = getGlobalApp();
  if (app && app.globalData) {
    app.globalData.userInfo = null;
  }
}

/**
 * 统一清除所有认证相关的本地和全局数据（Token & UserInfo & Configs）
 * 通常用于 退出登录 或 Token 401 失效
 */
function clearAuth() {
  try {
    // 1. 清除 Token (Storage)
    storage.clearToken();
    
    // 2. 清除用户信息 (Storage + Global)
    clearUserInfo();
    
    const app = getGlobalApp();
    if (app) {
        // 3. 清除内存中的 Token
        if (app.globalData) {
            app.globalData.token = null;
            app.globalData.refreshToken = null;
            // 清除可能存在的自动登录 Promise，防止后续逻辑继续执行
            app.globalData.loginPromise = null;
        }

        // 4. 清除自动登录配置 (调用 app.js 中的方法以保持逻辑统一)
        if (typeof app.clearAutoLoginState === 'function') {
            app.clearAutoLoginState();
        }
    }
    console.log('Auth: 登录状态已完全清除');
  } catch (error) {
    console.error('Auth clearAuth error:', error);
  }
}

/**
 * 检查是否已登录
 * @returns {boolean}
 */
function isLogined() {
  const token = getToken();
  return !!token; // 只要 token 存在即视为已登录（具体有效性由接口 401 决定）
}

/**
 * 跳转登录页
 * @param {string} redirect - 登录成功后需要返回的页面路径 (e.g. "pages/order/detail?id=1")
 */
function navigateToLogin(redirect) {
  try {
    console.log('Auth: 准备跳转登录页, 重定向至:', redirect || '首页');
    
    // 跳转前务必清除旧状态，防止登录页 onShow 中读取到脏数据
    clearAuth(); 
    
    let url = '/pages/login/login';
    
    // 处理重定向参数
    if (redirect) {
      // 确保 redirect 字符串是安全的 URL 编码
      // 注意：redirect 应该包含开头的 / 吗？视你的业务逻辑而定，通常 pages/xxx 不需要开头 /
      // 但为了稳妥，建议调用方传完整路径，这里只负责 encode
      url += `?redirect=${encodeURIComponent(redirect)}`;
    }
    
    // 使用 reLaunch 清空页面栈，防止用户安卓物理返回键回到上一个需要权限的页面
    wx.reLaunch({ url });
    
  } catch (error) {
    console.error('Auth navigateToLogin error:', error);
    // 兜底：如果 reLaunch 失败（极少见），尝试 redirectTo
    wx.redirectTo({ url: '/pages/login/login' });
  }
}

/**
 * 用户主动退出登录
 */
function logout() {
  try {
    clearAuth(); 
    wx.reLaunch({ url: '/pages/login/login' });
  } catch (error) {
    console.error('Auth logout error:', error);
  }
}

module.exports = {
  getToken,      // 导出供 request.js 使用，确保获取 Token 逻辑一致
  getUserInfo,
  setUserInfo,
  clearUserInfo,
  clearAuth,
  isLogined,
  navigateToLogin,
  logout
};