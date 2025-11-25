/**
 * 防抖工具函数
 * 用于控制函数在一定时间内只执行一次
 */

/**
 * 创建防抖函数
 * @param {Function} func - 需要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @param {boolean} immediate - 是否立即执行
 * @returns {Function} 防抖后的函数
 */
function debounce(func, wait, immediate = false) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(this, args);
  };
}

/**
 * 创建节流函数
 * @param {Function} func - 需要节流的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} 节流后的函数
 */
function throttle(func, limit) {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * 全局请求队列管理器
 * 用于管理并发请求，避免重复请求
 */
class RequestQueue {
  constructor() {
    this.queue = new Map();
    this.pending = new Map();
  }

  /**
   * 添加请求到队列
   * @param {string} key - 请求唯一标识
   * @param {Function} requestFunc - 请求函数
   * @returns {Promise} 请求结果
   */
  async add(key, requestFunc) {
    // 如果已有相同的请求在进行中，返回等待中的promise
    if (this.pending.has(key)) {
      return this.pending.get(key);
    }

    // 如果队列中有相同请求，直接返回缓存结果
    if (this.queue.has(key)) {
      return this.queue.get(key);
    }

    // 执行请求并缓存结果
    const promise = requestFunc().finally(() => {
      this.pending.delete(key);
      // 请求完成后，从队列中移除（延迟移除，避免瞬间重复）
      setTimeout(() => this.queue.delete(key), 1000);
    });

    this.pending.set(key, promise);
    this.queue.set(key, promise);

    return promise;
  }

  /**
   * 清除指定请求的缓存
   * @param {string} key - 请求唯一标识
   */
  clear(key) {
    this.queue.delete(key);
    this.pending.delete(key);
  }

  /**
   * 清空所有缓存
   */
  clearAll() {
    this.queue.clear();
    this.pending.clear();
  }
}

// 创建全局请求队列实例
const globalRequestQueue = new RequestQueue();

/**
 * 创建带缓存的请求函数
 * @param {Function} requestFunc - 原始请求函数
 * @param {string} cacheKey - 缓存键
 * @param {number} cacheTime - 缓存时间（毫秒）
 * @returns {Function} 带缓存的请求函数
 */
const authCenter = require('./authCenter'); // 延迟引用

function createCachedRequest(requestFunc, cacheKey, cacheTime = 60000) {
  let cache = null;
  let cacheTimestamp = 0;

  return async function cachedRequest(...args) {
    /* 熔断后不再发请求 */
    if (authCenter.breakdown) {
      // 熔断后直接拒绝请求，防止401风暴
      throw new Error('Auth breakdown, stop requesting');
    }
    // 防止重复401风暴：如有pending的同类请求，直接返回pending promise
    if (globalRequestQueue.pending.has(cacheKey)) {
      return globalRequestQueue.pending.get(cacheKey);
    }

    const now = Date.now();
    if (cache && (now - cacheTimestamp) < cacheTime) return cache;

    return globalRequestQueue.add(cacheKey, async () => {
      const result = await requestFunc.apply(this, args);
      cache = result;
      cacheTimestamp = now;
      return result;
    });
  };
}

module.exports = {
  debounce,
  throttle,
  RequestQueue,
  globalRequestQueue,
  createCachedRequest
};