/**
 * 本地存储封装
 * 提供类型安全的读写方法，支持 JSON 序列化/反序列化
 */

/**
 * 存储数据
 * @param {string} key - 存储键
 * @param {any} value - 存储值（自动序列化）
 */
function setItem(key, value) {
  try {
    // 仅对对象和数组序列化，字符串/数字/布尔直接存储
    let data;
    if (typeof value === 'object' && value !== null) {
      data = JSON.stringify(value);
    } else {
      data = value;
    }
    wx.setStorageSync(key, data);
    return true;
  } catch (error) {
    console.error('Storage setItem error:', error);
    // 仅警告，不抛出，避免主流程被阻断
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
