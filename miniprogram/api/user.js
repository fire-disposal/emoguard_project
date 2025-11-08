// 用户相关 API
const request = require('../utils/request');

// 微信小程序登录
function wechatLogin(data) {
  return request.post('/api/users/wechat/login', data, { skipAuth: true });
}

// 获取当前用户信息
function getCurrentUser() {
  return request.get('/api/users/me');
}

// 更新用户资料
function updateProfile(data) {
  return request.put('/api/users/me/profile', data);
}

module.exports = {
  wechatLogin,
  getCurrentUser,
  updateProfile
};
