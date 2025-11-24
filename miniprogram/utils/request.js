/**
 * 网络请求封装（401 风暴终结版）
 * 1. 自动带 token
 * 2. 401 时统一走 authCenter.refreshToken()（自带锁/队列/熔断）
 * 3. 刷新成功自动重试原请求；刷新失败直接 reject，不再二次跳转
 * 4. 网络/超时异常默认静默 1 次重试
 */
const authCenter = require('./authCenter');

//-------------后端接口地址----------------
// const BASE_URL = 'http://127.0.0.1:8000';
const BASE_URL = 'https://cg.aoxintech.com';
//------------------------------------

/* 网络异常静默重试 */
async function _requestWithRetry(options, retry = 1) {
  return new Promise((resolve, reject) => {
    const { url, method = 'GET', data = {}, header = {}, skipAuth = false } = options;
    const fullUrl = url.startsWith('http') ? url : `${BASE_URL}${url}`;
    const headers = { 'Content-Type': 'application/json', ...header };

    if (!skipAuth) {
      const token = authCenter.access;
      if (!token) {
        reject(new Error('Missing access token'));
        return;
      }
      headers.Authorization = `Bearer ${token}`;
    }

    wx.request({
      url: fullUrl,
      method,
      data,
      header: headers,
      success: async (res) => {
        const { statusCode, data: body } = res;
        if (statusCode >= 200 && statusCode < 300) return resolve(body);

        // --- 统一 401 处理 ---
        if (statusCode === 401 && !skipAuth) {
          // 如果已经熔断，直接失败
          if (!authCenter.access) {
            reject(new Error('Token expired and refresh breakdown'));
            return;
          }
          try {
            await authCenter.refreshToken();
            const result = await _requestWithRetry({ ...options, retry: 0 });
            resolve(result);
          } catch (e) {
            // 刷新失败 => 直接失败，不再二次重试
            reject(e);
          }
          return;
        }

        // 其他业务错误
        const msg = body?.detail || body?.message || `Request Error ${statusCode}`;
        wx.showToast({ title: msg, icon: 'none' });
        reject(new Error(msg));
      },
      fail: (err) => {
        // 网络层失败：静默重试一次
        if (retry > 0) {
          _requestWithRetry(options, retry - 1).then(resolve).catch(reject);
        } else {
          wx.showToast({ title: '网络连接不稳定', icon: 'none' });
          reject(err);
        }
      }
    });
  });
}

/* 统一出口 */
function request(options) {
  return _requestWithRetry(options);
}

/* 语法糖 */
['get', 'post', 'put', 'delete'].forEach((m) => {
  request[m] = (url, data, opts) => request({ url, method: m.toUpperCase(), data, ...opts });
});

/* 供登录成功后重置刷新锁（authCenter 内部已处理，这里留空即可） */
request.resetRefreshState = () => {};

module.exports = {
  request,
  get: request.get,
  post: request.post,
  put: request.put,
  delete: request.delete,
  resetRefreshState: request.resetRefreshState,
  BASE_URL
};