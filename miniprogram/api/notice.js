// 通知订阅相关 API
const request = require('../utils/request');

// 同步订阅状态到后端
function syncSubscribeStatus(data) {
  return request.post('/api/notice/subscribe', data);
}

// 获取用户订阅额度
function getUserQuota() {
  return request.get('/api/notice/quota');
}

module.exports = {
  syncSubscribeStatus,
  getUserQuota
};


