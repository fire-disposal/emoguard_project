// 情绪四维度 API - 与后端完全匹配的实现
const request = require('../utils/request');

// 创建或更新当日情绪记录 (POST /api/emotiontracker/)
function upsertEmotionRecord(data) {
  return request.post('/api/emotiontracker/', data);
}

// 获取用户情绪趋势 (GET /api/emotiontracker/trend?days={days})
function getEmotionTrend(days = 30) {
  return request.get('/api/emotiontracker/trend', { days });
}

// 获取今日早晚填写状态 (GET /api/emotiontracker/status)
function getTodayStatus() {
  return request.get('/api/emotiontracker/status');
}

module.exports = {
  upsertEmotionRecord,
  getEmotionTrend,
  getTodayStatus
};