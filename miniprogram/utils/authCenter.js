/**
 * 认证中心（极简重构版，不兼容旧接口）
 * 1. 唯一可信源：token + refreshToken
 * 2. 全局锁防并发刷新
 * 3. 熔断：3次刷新失败即永久失效
 * 4. 用户信息统一管理
 * 5. 只暴露必要API
 */
const storage = require('./storage');
const USER_INFO_KEY = 'user_info';

let access = null;
let refresh = null;
let refreshLock = false;
let refreshFailCount = 0;
const MAX_REFRESH_FAIL = 3;
let loginPromise = null;
let hasNavigated = false;

function navigateToLogin() {
  if (hasNavigated) return;
  hasNavigated = true;
  wx.reLaunch({ url: '/pages/login/login' });
}

function persistTokens(newAccess, newRefresh) {
  access = newAccess;
  refresh = newRefresh || refresh;
  storage.setToken(access, refresh);
}

function breakdown() {
  refreshFailCount = MAX_REFRESH_FAIL;
  storage.clearToken();
  access = null;
  refresh = null;
  navigateToLogin();
}

function getUserInfo() {
  const app = getApp();
  if (app && app.globalData && app.globalData.userInfo) {
    return app.globalData.userInfo;
  }
  try {
    return storage.getItem(USER_INFO_KEY);
  } catch {
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

function clearAuth() {
  logout(true);
  clearUserInfo();
  const app = getApp();
  if (app && app.globalData) {
    app.globalData.token = null;
    app.globalData.refreshToken = null;
    app.globalData.loginPromise = null;
  }
}

function init() {
  if (access === null) access = storage.getToken();
  if (refresh === null) refresh = storage.getRefreshToken();
}

function login(newAccess, newRefresh) {
  refreshFailCount = 0;
  hasNavigated = false;
  persistTokens(newAccess, newRefresh);
}

function logout(localOnly = false) {
  access = null;
  refresh = null;
  storage.clearToken();
  if (!localOnly) navigateToLogin();
}

async function refreshToken() {
  init();
  if (refreshFailCount >= MAX_REFRESH_FAIL) throw new Error('refresh breakdown');
  if (refreshLock) return loginPromise;
  refreshLock = true;

  loginPromise = new Promise(async (resolve, reject) => {
    try {
      if (!refresh) throw new Error('no refresh token');
      const { request } = require('./request');
      const res = await request({
        url: '/api/token/refresh/',
        method: 'POST',
        data: { refresh },
        skipAuth: true
      });
      persistTokens(res.access, res.refresh || refresh);
      refreshFailCount = 0;
      resolve(access);
    } catch (e) {
      refreshFailCount++;
      if (refreshFailCount >= MAX_REFRESH_FAIL) {
        breakdown();
      } else {
        refreshFailCount = MAX_REFRESH_FAIL;
      }
      reject(e);
    } finally {
      refreshLock = false;
      loginPromise = null;
    }
  });

  return loginPromise;
}

module.exports = {
  get access() { return access; },
  get refresh() { return refresh; },
  get logined() { return !!access; },
  get breakdown() { return refreshFailCount >= MAX_REFRESH_FAIL; },
  init,
  login,
  logout,
  refreshToken,
  getUserInfo,
  setUserInfo,
  clearUserInfo,
  clearAuth
};