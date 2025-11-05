/**
 * 网络请求封装
 * 统一管理 API 调用，自动添加 Token，处理错误
 */

const auth = require('./auth');

// API 基础地址

// 本地调试环境
const BASE_URL = 'http://127.0.0.1:8000';
// 正式环境
// const BASE_URL = 'https://cg.aoxintech.com';

// 是否正在刷新 token
let isRefreshing = false;
// 刷新 token 期间的请求队列
let requestQueue = [];
// 刷新token失败标记，防止无限重试
let refreshFailed = false;

/**
 * 刷新 Token
 * @returns {Promise<string>} 新的 access_token
 */
function refreshToken() {
  return new Promise((resolve, reject) => {
    // 如果已经标记为刷新失败，直接拒绝，避免无限循环
    if (refreshFailed) {
      reject(new Error('Token refresh already failed'));
      return;
    }

    const refreshToken = auth.getRefreshToken();
    
    if (!refreshToken) {
      refreshFailed = true;
      reject(new Error('No refresh token'));
      return;
    }
    
    wx.request({
      url: `${BASE_URL}/api/token/refresh`,
      method: 'POST',
      data: { refresh: refreshToken },
      success: (res) => {
        if (res.statusCode === 200 && res.data.access) {
          // 刷新成功，重置失败标记
          refreshFailed = false;
          auth.setToken(res.data.access, res.data.refresh || refreshToken);
          resolve(res.data.access);
        } else {
          // 刷新失败，标记失败状态
          refreshFailed = true;
          reject(new Error('Refresh token failed'));
        }
      },
      fail: (error) => {
        // 网络请求失败，标记失败状态
        refreshFailed = true;
        reject(error);
      }
    });
  });
}

/**
 * 发起网络请求
 * @param {object} options - 请求配置
 * @param {string} options.url - 请求路径（相对路径）
 * @param {string} options.method - 请求方法（GET/POST/PUT/DELETE）
 * @param {object} options.data - 请求参数
 * @param {object} options.header - 额外请求头
 * @param {boolean} options.skipAuth - 是否跳过认证（登录接口使用）
 * @returns {Promise}
 */
function request(options) {
  return new Promise((resolve, reject) => {
    const {
      url,
      method = 'GET',
      data = {},
      header = {},
      skipAuth = false
    } = options;
    
    // 构建完整 URL
    const fullUrl = url.startsWith('http') ? url : `${BASE_URL}${url}`;
    
    // 构建请求头
    const headers = {
      'Content-Type': 'application/json',
      ...header
    };
    
    // 添加 Authorization 头
    if (!skipAuth) {
      const token = auth.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    
    // 发起请求
    wx.request({
      url: fullUrl,
      method,
      data,
      header: headers,
      success: (res) => {
        const { statusCode, data } = res;
        
        // 成功响应
        if (statusCode >= 200 && statusCode < 300) {
          resolve(data);
          return;
        }
        
        // 401 未授权 - 尝试刷新 token
        if (statusCode === 401 && !skipAuth) {
          // 如果已经标记为刷新失败，直接跳转到登录页，不再重试
          if (refreshFailed) {
            auth.navigateToLogin();
            reject(new Error('Token refresh failed, please login again'));
            return;
          }

          if (!isRefreshing) {
            isRefreshing = true;
            
            refreshToken()
              .then((newToken) => {
                isRefreshing = false;
                
                // 重试所有队列中的请求
                requestQueue.forEach(cb => cb(newToken));
                requestQueue = [];
                
                // 重试当前请求
                request(options).then(resolve).catch(reject);
              })
              .catch((error) => {
                isRefreshing = false;
                requestQueue = [];
                
                // Token 刷新失败，清除本地缓存并跳转登录
                auth.clearToken();
                auth.clearUserInfo();
                auth.navigateToLogin();
                reject(error);
              });
          } else {
            // 将请求加入队列
            requestQueue.push(() => {
              request(options).then(resolve).catch(reject);
            });
          }
          return;
        }
        
        // 403 禁止访问
        if (statusCode === 403) {
          wx.showToast({
            title: '无权限访问',
            icon: 'none'
          });
          reject(new Error('Forbidden'));
          return;
        }
        
        // 404 资源不存在
        if (statusCode === 404) {
          wx.showToast({
            title: '请求的资源不存在',
            icon: 'none'
          });
          reject(new Error('Not Found'));
          return;
        }
        
        // 500 服务器错误
        if (statusCode >= 500) {
          wx.showToast({
            title: '服务器异常，请稍后重试',
            icon: 'none'
          });
          reject(new Error('Server Error'));
          return;
        }
        
        // 其他错误
        const errorMsg = data?.detail || data?.message || '请求失败';
        wx.showToast({
          title: errorMsg,
          icon: 'none'
        });
        reject(new Error(errorMsg));
      },
      fail: (error) => {
        console.error('Request failed:', error);
        wx.showToast({
          title: '网络超时，请检查网络',
          icon: 'none'
        });
        reject(error);
      }
    });
  });
}

/**
 * GET 请求
 */
function get(url, data, options = {}) {
  return request({
    url,
    method: 'GET',
    data,
    ...options
  });
}

/**
 * POST 请求
 */
function post(url, data, options = {}) {
  return request({
    url,
    method: 'POST',
    data,
    ...options
  });
}

/**
 * PUT 请求
 */
function put(url, data, options = {}) {
  return request({
    url,
    method: 'PUT',
    data,
    ...options
  });
}

/**
 * DELETE 请求
 */
function del(url, data, options = {}) {
  return request({
    url,
    method: 'DELETE',
    data,
    ...options
  });
}

/**
 * 重置token刷新状态
 * 在用户登录成功后调用，清除刷新失败标记
 */
function resetRefreshState() {
  refreshFailed = false;
  isRefreshing = false;
  requestQueue = [];
}

module.exports = {
  request,
  get,
  post,
  put,
  delete: del,
  resetRefreshState
};
