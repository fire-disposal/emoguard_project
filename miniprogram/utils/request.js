/**
 * 网络请求封装
 * 统一管理 API 调用，自动添加 Token，处理错误，实现 Token 自动刷新和重试。
 */

const storage = require('./storage');
const auth = require('./auth'); 

//-------------后端接口地址----------------
// const BASE_URL = 'http://127.0.0.1:8000';
const BASE_URL = 'https://cg.aoxintech.com';
//------------------------------------

// 是否正在刷新 token
let isRefreshing = false;
// 刷新 token 期间的请求队列
let requestQueue = [];
// 刷新 token 失败标记，防止无限重试
let refreshFailed = false;

/**
 * 刷新 Token
 * @returns {Promise<string>} 新的 access_token
 */
function refreshToken() {
  return new Promise((resolve, reject) => {
    // 如果已经标记为刷新失败，直接拒绝，不再发起请求
    if (refreshFailed) {
      reject(new Error('Token refresh already failed'));
      return;
    }

    // 获取 refresh token (通常仅存在 storage 中)
    const refreshTokenStr = storage.getRefreshToken();

    if (!refreshTokenStr) {
      handleRefreshFail('No refresh token locally');
      reject(new Error('No refresh token'));
      return;
    }

    console.log('正在尝试刷新 Token...');

    wx.request({
      url: `${BASE_URL}/api/token/refresh`, // 请确认后端接口路径
      method: 'POST',
      data: { refresh: refreshTokenStr },
      header: { 'Content-Type': 'application/json' }, // 显式声明
      success: (res) => {
        if (res.statusCode === 200 && res.data.access) {
          console.log('Token 刷新成功');
          refreshFailed = false;
          
          const newAccess = res.data.access;
          const newRefresh = res.data.refresh || refreshTokenStr; // 后端可能不返回新的 refresh

          // [关键优化 1]：刷新成功后，必须同时更新 Storage 和 GlobalData
          // 确保 auth.getToken() 能立即获取到最新值
          storage.setToken(newAccess, newRefresh);
          
          const app = getApp();
          if (app && app.globalData) {
            app.globalData.token = newAccess;
            app.globalData.refreshToken = newRefresh;
          }

          resolve(newAccess);
        } else {
          handleRefreshFail(`Refresh rejected by server: ${res.statusCode}`);
          reject(new Error('Refresh token failed'));
        }
      },
      fail: (error) => {
        // 网络层面的失败（断网等），不应该清除登录态，而是让用户重试
        console.error('刷新 Token 网络请求失败:', error);
        // 这里不置 refreshFailed = true，允许下次网络恢复后继续尝试
        reject(error);
      }
    });
  });
}

/**
 * 辅助函数：统一处理刷新失败
 */
function handleRefreshFail(reason) {
  console.warn('Token 刷新最终失败:', reason);
  refreshFailed = true;
  isRefreshing = false;
  requestQueue = [];
  
  // 清理所有状态并跳转
  auth.clearAuth(); 
  auth.navigateToLogin();
}

/**
 * 发起网络请求
 * @param {object} options - 请求配置
 * @returns {Promise<object>} Promise，成功时 resolve(res.data)，失败时 reject(Error)
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

    // [关键优化 2]：使用 auth.getToken() (内存优先)
    // 避免频繁读取 Storage，且保证与 app.js 状态一致
    if (!skipAuth) {
      const token = auth.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        // [关键优化 3]：没有 Token 时，不强制跳转，而是 Reject
        // 原因：app.js 的 onShow 已经在做鉴权跳转了。如果 request 这里也跳转，
        // 可能会导致页面刚打开就跳两次。这里只负责拦截请求。
        console.warn('Request blocked: No token found');
        
        // 如果你确定某些接口必须在有 Token 时才能调用，可以保留跳转，
        // 但建议加一个防抖或由页面 catch 处理
        // auth.navigateToLogin(); 
        
        reject(new Error('Missing access token'));
        return; 
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

        // --- 401 处理逻辑 ---
        if (statusCode === 401 && !skipAuth) {
          // 如果已经标记为刷新失败，直接退出
          if (refreshFailed) {
            reject(new Error('Token refresh failed previously'));
            return;
          }

          if (!isRefreshing) {
            isRefreshing = true;

            refreshToken()
              .then((newToken) => {
                isRefreshing = false;
                // Token 刷新成功，处理队列
                console.log(`重试队列中的 ${requestQueue.length} 个请求`);
                requestQueue.forEach(callback => callback());
                requestQueue = [];

                // 重试当前请求
                // 注意：这里递归调用 request，它会重新调用 auth.getToken()，
                // 因为我们在 refreshToken 中已经更新了 GlobalData，所以能拿到新的
                request(options).then(resolve).catch(reject);
              })
              .catch((error) => {
                // 刷新过程中发生错误（如 Refresh Token 也失效了）
                handleRefreshFail('Refresh process crashed');
                reject(error);
              });
          } else {
            // 正在刷新，将当前请求加入队列
            // 使用闭包保存 resolve/reject
            requestQueue.push(() => {
              request(options).then(resolve).catch(reject);
            });
          }
          return;
        }
        // --- End 401 ---

        // 403 禁止访问
        if (statusCode === 403) {
          wx.showToast({ title: '无权限访问', icon: 'none' });
          reject(new Error('Forbidden (403)'));
          return;
        }

        // 404 资源不存在
        if (statusCode === 404) {
          // 可选：屏蔽 404 toast，交给页面处理
          // wx.showToast({ title: '资源不存在', icon: 'none' });
          reject(new Error('Not Found (404)'));
          return;
        }

        // 500 服务器错误
        if (statusCode >= 500) {
          wx.showToast({ title: '服务器繁忙', icon: 'none' });
          reject(new Error('Server Error (5xx)'));
          return;
        }

        // 其他业务错误 (根据后端规范调整)
        const errorMsg = data?.detail || data?.message || `请求错误 (${statusCode})`;
        wx.showToast({ title: errorMsg, icon: 'none' });
        reject(new Error(errorMsg));
      },
      fail: (error) => {
        // 网络物理故障 (DNS, Timeout)
        console.error('Network Error:', error);
        wx.showToast({ title: '网络连接不稳定', icon: 'none' });
        reject(error);
      }
    });
  });
}

// 简便方法封装
const get = (url, data, options = {}) => request({ url, method: 'GET', data, ...options });
const post = (url, data, options = {}) => request({ url, method: 'POST', data, ...options });
const put = (url, data, options = {}) => request({ url, method: 'PUT', data, ...options });
const del = (url, data, options = {}) => request({ url, method: 'DELETE', data, ...options });

/**
 * 重置 token 刷新状态
 * [必须] 在 login.js 登录成功后调用
 */
function resetRefreshState() {
  refreshFailed = false;
  isRefreshing = false;
  requestQueue = [];
  console.log('Request 状态已重置');
}

module.exports = {
  request,
  get,
  post,
  put,
  delete: del,
  resetRefreshState,
  BASE_URL // 导出 URL 方便其他地方引用（如上传文件）
};