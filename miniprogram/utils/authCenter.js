/**
 * 认证中心
 * 1. 唯一可信源：token + refreshToken
 * 2. 全局单例锁，防止并发刷新
 * 3. 失败熔断，3 次刷新失败即标记“永久失效”
 * 4. 统一跳转，只跳一次登录页
 */
const storage = require('./storage');

// --------- 私有变量 ---------
let _access = null;               // 内存 token
let _refresh = null;              // 内存 refresh
let _refreshLock = false;         // 刷新锁
let _refreshFailCount = 0;        // 连续刷新失败次数
const MAX_REFRESH_FAIL = 3;       // 熔断阈值
let _loginPromise = null;         // 刷新 promise（队列复用）
let _hasNavigated = false;        // 本次生命周期是否已跳转登录页

// --------- 私有方法 ---------
const KEY_ACCESS = 'access_token';
const KEY_REFRESH = 'refresh_token';

/* 统一跳登录页（仅一次） */
function _navigateToLogin() {
  if (_hasNavigated) return;
  _hasNavigated = true;
  wx.reLaunch({ url: '/pages/login/login' });
}

/* 熔断处理 */
function _breakdown() {
  _refreshFailCount = MAX_REFRESH_FAIL;
  storage.clearToken();
  _access = null;
  _refresh = null;
  _navigateToLogin();
}

/* 同时写内存 + storage */
function _persist(access, refresh) {
  _access = access;
  if (refresh) _refresh = refresh;
  storage.setToken(access, refresh);
}

// --------- 对外 API ---------
const authCenter = {
  /* 初始读缓存 */
  init() {
    if (_access === null) _access = storage.getToken();
    if (_refresh === null) _refresh = storage.getRefreshToken();
  },

  get access() {
    return _access;
  },

  get refresh() {
    return _refresh;
  },

  get logined() {
    return !!_access;
  },

  /* 供上层短路：是否已熔断 */
  get breakdown() {
    return _refreshFailCount >= MAX_REFRESH_FAIL;
  },

  /* 登录成功后写入 */
  login(access, refresh) {
    _refreshFailCount = 0;
    _hasNavigated = false;
    _persist(access, refresh);
  },

  /* 退出 / 失效清理 */
  logout(localOnly = false) {
    _access = null;
    _refresh = null;
    storage.clearToken();
    if (!localOnly) _navigateToLogin();
  },

  /* 刷新 token（带锁 + 队列 + 熔断） */
  async refreshToken() {
    authCenter.init(); // 兜底读缓存
    if (_refreshFailCount >= MAX_REFRESH_FAIL) throw new Error('refresh breakdown');

    // 复用同一刷新 promise
    if (_refreshLock) return _loginPromise;
    _refreshLock = true;

    _loginPromise = new Promise(async (resolve, reject) => {
      try {
        const refreshToken = _refresh;
        if (!refreshToken) throw new Error('no refresh token');

        const { request } = require('./request'); // 延迟引用，避免循环
        const res = await request({
          url: '/api/token/refresh',
          method: 'POST',
          data: { refresh: refreshToken },
          skipAuth: true
        });
        const { access, refresh } = res;
        _persist(access, refresh || refreshToken);
        _refreshFailCount = 0;
        resolve(access);
      } catch (e) {
        _refreshFailCount++;
        if (_refreshFailCount >= MAX_REFRESH_FAIL) {
          _breakdown();
        } else {
          // 立即标记熔断，防止后续并发请求继续重试
          _refreshFailCount = MAX_REFRESH_FAIL;
        }
        reject(e);
      } finally {
        _refreshLock = false;
        _loginPromise = null;
      }
    });

    return _loginPromise;
  }
};

module.exports = authCenter;