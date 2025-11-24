/**
 * 本地存储封装
 * 1. 类型安全、JSON 自动序列化
 * 2. 容量超限降级（warn 后返回 false）
 * 3. 统一日志 tag，方便过滤
 */
const TAG = '[Storage]';

/**
 * 存储数据（带容量降级）
 * @param {string} key - 存储键
 * @param {any} value - 存储值（自动序列化）
 * @returns {boolean} 成功/失败
 */
function setItem(key, value) {
  try {
    const data = (typeof value === 'object' && value !== null) ? JSON.stringify(value) : value;
    wx.setStorageSync(key, data);
    return true;
  } catch (e) {
    // 容量超限会抛 e.errMsg.includes("quota")
    if (e.errMsg && e.errMsg.includes('quota')) {
      console.warn(TAG, '容量超限，写入失败', key);
    } else {
      console.error(TAG, 'setItem 异常', key, e);
    }
    return false;
  }
}

/**
 * 读取数据
 * @param {string} key - 存储键
 * @returns {any} 存储值（自动反序列化）
 */
function getItem(key) {
  try {
    const data = wx.getStorageSync(key);
    if (data === undefined || data === null) return null;
    // 优先尝试解析 JSON
    if (typeof data === 'string') {
      try {
        return JSON.parse(data);
      } catch {
        return data;
      }
    }
    return data;
  } catch (error) {
    console.error('Storage getItem error:', error);
    return null;
  }
}

/**
 * 删除数据
 * @param {string} key - 存储键
 */
function removeItem(key) {
  try {
    wx.removeStorageSync(key);
  } catch (error) {
    console.warn('Storage removeItem error:', error);
    // 不抛出异常，避免影响主流程
  }
}

/**
 * 清空所有存储
 */
function clear() {
  try {
    wx.clearStorageSync();
  } catch (error) {
    console.warn('Storage clear error:', error);
    // 不抛出异常，避免影响主流程
  }
}

/**
 * token 专用操作
 */
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

function setToken(accessToken, refreshToken) {
  const result1 = setItem(TOKEN_KEY, accessToken);
  const result2 = refreshToken ? setItem(REFRESH_TOKEN_KEY, refreshToken) : true;
  return result1 && result2;
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

module.exports = {
  setItem,
  getItem,
  removeItem,
  clear,
  setToken,
  getToken,
  getRefreshToken,
  clearToken
};
