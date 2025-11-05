/**
 * 用户相关 API
 */

const request = require('../utils/request');

/**
 * 微信小程序登录
 * POST /api/users/wechat/login
 * @param {object} data - { code, encrypted_data, iv }
 * @returns {Promise<object>} { access_token, refresh_token, user }
 */
function wechatLogin(data) {
  return request.post('/api/users/wechat/login', data, { skipAuth: true });
}

/**
 * 获取当前用户信息
 * GET /api/users/me
 * @returns {Promise<object>} 用户信息
 */
function getCurrentUser() {
  return request.get('/api/users/me');
}

/**
 * 更新用户资料
 * PUT /api/users/me/profile
 * @param {object} data - { real_name, gender, age, education, province, city, phone }
 * @returns {Promise<object>} 更新后的用户信息
 */
function updateProfile(data) {
  return request.put('/api/users/me/profile', data);
}

module.exports = {
  wechatLogin,
  getCurrentUser,
  updateProfile
};
