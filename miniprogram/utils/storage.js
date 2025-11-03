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
    const data = typeof value === 'string' ? value : JSON.stringify(value);
    wx.setStorageSync(key, data);
  } catch (error) {
    console.error('Storage setItem error:', error);
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
    if (!data) return null;
    
    // 尝试解析 JSON
    try {
      return JSON.parse(data);
    } catch {
      return data;
    }
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
    console.error('Storage removeItem error:', error);
  }
}

/**
 * 清空所有存储
 */
function clear() {
  try {
    wx.clearStorageSync();
  } catch (error) {
    console.error('Storage clear error:', error);
  }
}

module.exports = {
  setItem,
  getItem,
  removeItem,
  clear
};
